#!/bin/bash

set -o pipefail

# Define the input filenames and destination
DESTINATION="pi@srk.local:/tmp/"
PASSWORD="${SCP_PASSWORD:-}" 

have_cmd() { command -v "$1" >/dev/null 2>&1; }

copy_file() {
    local FILE="$1"
    local SOURCE_DIR="$2"
    local SOURCE_FILE="${SOURCE_DIR}${FILE}"

    if [ ! -f "$SOURCE_FILE" ]; then
        echo "[ERROR] Source file not found: $SOURCE_FILE" >&2
        return 1
    fi

    echo "1. Copying $FILE to $DESTINATION"

    # Prefer rsync for a clean progress bar if available
    if have_cmd rsync; then
        # --info=progress2 gives a single consolidated progress line (rsync >= 3.1)
        sshpass -p "$PASSWORD" rsync -ah --progress "$SOURCE_FILE" "$DESTINATION"
        rc=$?
    else
        echo "[INFO] rsync not found; falling back to scp (showing verbose progress)." >&2
        # scp shows a progress meter when stderr is a TTY; force it with -v for feedback
        sshpass -p "$PASSWORD" scp -v "$SOURCE_FILE" "$DESTINATION"
        rc=$?
    fi

    if [ $rc -eq 0 ]; then
        echo "2. $FILE copied successfully to $DESTINATION"
        echo "3. Moving $FILE to /srv/nfs/"
        if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no pi@srk.local "sudo mv /tmp/'$FILE' /srv/nfs/"; then
            echo "4. $FILE moved successfully to /srv/nfs/"
        else
            echo "4. Failed to move $FILE to /srv/nfs/" >&2
            return 1
        fi
    else
        echo "2. Failed to copy $FILE to $DESTINATION" >&2
        return $rc
    fi
}

print_help() {
    echo "Usage: $0 -p <password> [-s] [-k] [-i]"
    echo "Options:"
    echo "  -p <password>        : Password for scp and ssh"
    echo "  -s                   : Copy core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
    echo "  -k                   : Copy keyfile from script directory"
    echo "  -i                   : Copy encrypted.img from script directory"
    echo "Example:"
    echo "  $0 -p mypassword -s -k -i"
}

# Parse command line arguments
while getopts "p:skih" opt; do
    case $opt in
        s)
            SOURCE_FOLDER="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
            INPUT_FILES="core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
            copy_file $INPUT_FILES $SOURCE_FOLDER
            ;;
        p)
            PASSWORD=$OPTARG
            ;;
        k)
            SCRIPT_DIR="$(dirname "$(realpath "$0")")/"
            copy_file "keyfile" $SCRIPT_DIR
            ;;
        i)
            SCRIPT_DIR="$(dirname "$(realpath "$0")")/"
            copy_file "encrypted.img" $SCRIPT_DIR
            ;;
        h)
            print_help
            exit 0
            ;;
        *)
            echo "Invalid option: -$OPTARG" >&2
            print_help
            exit 1
            ;;
    esac
done

if [ -z "$PASSWORD" ]; then
    echo "Password is required. Use -p option to provide the password or set SCP_PASSWORD environment variable."
    print_help
    exit 1
fi
