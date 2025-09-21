#!/bin/bash

# Copy initramfs image to target device
# Uses SSH alias 'p' configured in ~/.ssh/config for pi@srk.local
# Uses SSH key-based authentication (no password required)

VERSION="1.0.0"

VERSION="1.0.0"

print_help() {
    cat <<EOF
Usage: $0 <version (2 or 3)> [options]

Options:
    -V             Show version and exit
    -h             This help

Examples:
    $0 2
    $0 3

Notes:
    - Uses SSH alias 'p' configured in ~/.ssh/config
    - SSH key-based authentication is used (no password required)

Version: $VERSION
EOF
}

# Parse command line arguments
while getopts "Vh" opt; do
    case $opt in
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

# Shift parsed options
shift $((OPTIND-1))

# Check if the version argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <version (2 or 3)>"
    echo "Uses SSH key-based authentication (no password required)"
    exit 1
fi

# Define the input filename based on the version argument
INITRAMFS_VERSION="$1"
if [[ "$INITRAMFS_VERSION" != "2" && "$INITRAMFS_VERSION" != "3" ]]; then
    echo "Invalid version. Please provide either '2' or '3'."
    exit 1
fi
INPUT_FILENAME="core-image-tiny-initramfs-srk-${INITRAMFS_VERSION}-beaglebone-yocto.rootfs.cpio.gz"

# Define the source file and destination
SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
DESTINATION="p:/tmp/"

# Copy the file using scp
echo "1. Copying $INPUT_FILENAME to $DESTINATION"
scp $SOURCE_FILE $DESTINATION

# Check if the copy was successful
if [ $? -eq 0 ];  then
    echo "2. $INPUT_FILENAME copied successfully to $DESTINATION"
    # Delete the content of the NFS folder before extraction
    ssh p "sudo rm -rf /srv/nfs/*"
    if [ $? -eq 0 ]; then
        echo "3. NFS folder content deleted successfully"
        echo "4. Extracting $INPUT_FILENAME to /srv/nfs/"
        # Extract the file in the remote folder /srv/nfs/
        ssh p "gunzip -c /tmp/$INPUT_FILENAME | sudo cpio -idmv -D /srv/nfs/"
        if [ $? -eq 0 ]; then
            echo "5. $INPUT_FILENAME extracted successfully to /srv/nfs/"
        else
            echo "5. Failed to extract $INPUT_FILENAME to /srv/nfs/"
        fi
    else
        echo "3. Failed to delete NFS folder content"
    fi
else
    echo "2. Failed to copy $INPUT_FILENAME to $DESTINATION"
fi