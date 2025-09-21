#!/bin/bash

set -o pipefail

VERSION="1.1.0"
QUIET=0

# Define the input filenames and destination
DESTINATION="p:/tmp/"

have_cmd() { command -v "$1" >/dev/null 2>&1; }

log() {
    [ "$QUIET" -eq 0 ] && echo "$@"
}

copy_file() {
    local FILE="$1"
    local SOURCE_DIR="$2"
    local SOURCE_FILE="${SOURCE_DIR}${FILE}"

    if [ ! -f "$SOURCE_FILE" ]; then
        [ "$QUIET" -eq 0 ] && echo "[ERROR] Source file not found: $SOURCE_FILE" >&2
        return 1
    fi

    log "1. Copying $FILE to $DESTINATION"

    # Prefer rsync for a clean progress bar if available
    if have_cmd rsync; then
        # --info=progress2 gives a single consolidated progress line (rsync >= 3.1)
        rsync -ah --progress "$SOURCE_FILE" "$DESTINATION"
        rc=$?
    else
        [ "$QUIET" -eq 0 ] && echo "[INFO] rsync not found; falling back to scp." >&2
        # scp shows a progress meter when stderr is a TTY; force it with -v for feedback
        scp -v "$SOURCE_FILE" "$DESTINATION"
        rc=$?
    fi

    if [ $rc -eq 0 ]; then
        log "2. $FILE copied successfully to $DESTINATION"
        log "3. Moving $FILE to /srv/nfs/"
        if ssh p "sudo mv /tmp/'$FILE' /srv/nfs/"; then
            log "4. $FILE moved successfully to /srv/nfs/"
        else
            [ "$QUIET" -eq 0 ] && echo "4. Failed to move $FILE to /srv/nfs/" >&2
            return 1
        fi
    else
        [ "$QUIET" -eq 0 ] && echo "2. Failed to copy $FILE to $DESTINATION" >&2
        return $rc
    fi
}

print_help() {
        cat <<EOF
Usage: $0 [options]

Options:
    -s             Copy core-image-minimal-squashfs-srk-beaglebone-yocto.rootfs.squashfs
    -k             Copy keyfile from script directory
    -i             Copy encrypted.img from script directory
    -q             Quiet mode (suppress normal output; errors still shown)
    -V             Show version and exit
    -h             This help

Examples:
    $0 -s -k -i
    $0 -s -q

Notes:
    - Uses SSH alias 'p' configured in ~/.ssh/config
    - SSH key-based authentication is used (no password required)

Version: $VERSION
EOF
}

# Parse command line arguments
while getopts "skiqVh" opt; do
    case $opt in
        s)
            SOURCE_FOLDER="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
            INPUT_FILES="core-image-minimal-squashfs-srk-beaglebone-yocto.rootfs.squashfs"
            copy_file $INPUT_FILES $SOURCE_FOLDER
            ;;
        k)
            SCRIPT_DIR="$(dirname "$(realpath "$0")")/"
            copy_file "keyfile" $SCRIPT_DIR
            ;;
        i)
            SCRIPT_DIR="$(dirname "$(realpath "$0")")/"
            copy_file "encrypted.img" $SCRIPT_DIR
            ;;
        q)
            QUIET=1
            ;;
        V)
            echo "$(basename "$0") version $VERSION"
            exit 0
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

# SSH key-based authentication is used - no password required
