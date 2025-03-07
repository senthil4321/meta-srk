#!/bin/bash

# Check if the version and password arguments are provided or set as environment variables
if [ -z "$1" ] || ([ -z "$2" ] && [ -z "$SCP_PASSWORD" ]); then
    echo "Usage: $0 <version (2 or 3)> <scp_password> or set SCP_PASSWORD environment variable"
    exit 1
fi

# Define the input filename based on the version argument
VERSION="$1"
if [[ "$VERSION" != "2" && "$VERSION" != "3" ]]; then
    echo "Invalid version. Please provide either '2' or '3'."
    exit 1
fi
INPUT_FILENAME="core-image-tiny-initramfs-srk-${VERSION}-beaglebone-yocto.rootfs.cpio.gz"

# Define the source file and destination
SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
DESTINATION="pi@srk.local:/tmp/"
PASSWORD=${2:-$SCP_PASSWORD}

# Copy the file using scp
echo "1. Copying $INPUT_FILENAME to $DESTINATION"
sshpass -p $PASSWORD scp $SOURCE_FILE $DESTINATION

# Check if the copy was successful
if [ $? -eq 0 ];  then
    echo "2. $INPUT_FILENAME copied successfully to $DESTINATION"
    # Delete the content of the NFS folder before extraction
    sshpass -p $PASSWORD ssh pi@srk.local "sudo rm -rf /srv/nfs/*"
    if [ $? -eq 0 ]; then
        echo "3. NFS folder content deleted successfully"
        echo "4. Extracting $INPUT_FILENAME to /srv/nfs/"
        # Extract the file in the remote folder /srv/nfs/
        sshpass -p $PASSWORD ssh pi@srk.local "gunzip -c /tmp/$INPUT_FILENAME | sudo cpio -idmv -D /srv/nfs/"
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