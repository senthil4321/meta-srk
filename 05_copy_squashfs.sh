#!/bin/bash

# Define the input filenames and destination


DESTINATION="pi@srk.local:/tmp/"
PASSWORD=${SCP_PASSWORD:-""}

copy_file() {
    local FILE=$1
    local SOURCE_DIR=$2
    local SOURCE_FILE="$SOURCE_DIR$FILE"
    echo "1. Copying $FILE to $DESTINATION"
    sshpass -p $PASSWORD scp $SOURCE_FILE $DESTINATION

    # Check if the copy was successful
    if [ $? -eq 0 ]; then
        echo "2. $FILE copied successfully to $DESTINATION"
        echo "3. Moving $FILE to /srv/nfs/"
        # Move the file to the NFS folder
        sshpass -p $PASSWORD ssh pi@srk.local "sudo mv /tmp/$FILE /srv/nfs/"
        if [ $? -eq 0 ]; then
            echo "4. $FILE moved successfully to /srv/nfs/"
        else
            echo "4. Failed to move $FILE to /srv/nfs/"
        fi
    else
        echo "2. Failed to copy $FILE to $DESTINATION"
    fi
}

copy_encrypted_files() {
    local SOURCE_DIR=$1
    for FILE in "${INPUT_FILES[@]}"; do
        copy_file $FILE $SOURCE_DIR
    done
}

print_help() {
    echo "Usage: $0 -p <password> -d <source_directory> [-s y] [-k y] [-i y]"
    echo "Options:"
    echo "  -p <password>        : Password for scp and ssh"
    echo "  -s y                 : Copy core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
    echo "  -k y                 : Copy keyfile from script directory"
    echo "  -i y                 : Copy encrypted.img from script directory"
    echo "Example:"
    echo "  $0 -p mypassword -d /path/to/source -s y -k y -i y"
}

# Parse command line arguments
SOURCE_DIR=""
while getopts "s:p:k:i:d:h" opt; do
    case $opt in
        s)
            if [ "$OPTARG" = "y" ]; then
            SOURCE_FOLDER="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
            INPUT_FILES="core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
            copy_file $INPUT_FILES $SOURCE_FOLDER

            fi
            ;;
        p)
            PASSWORD=$OPTARG
            ;;
        k)
            if [ "$OPTARG" = "y" ]; then
                SCRIPT_DIR="$(dirname "$(realpath "$0")")/"
                copy_file "keyfile" $SCRIPT_DIR
            fi
            ;;
        i)
            if [ "$OPTARG" = "y" ]; then
                SCRIPT_DIR="$(dirname "$(realpath "$0")")/"
                copy_file "encrypted.img" $SCRIPT_DIR
            fi
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
