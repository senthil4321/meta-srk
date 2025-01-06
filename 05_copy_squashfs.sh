#!/bin/bash

# Check if the password argument is provided or set as an environment variable
if [ -z "$1" ] && [ -z "$SCP_PASSWORD" ]; then
    echo "Usage: $0 <scp_password> or set SCP_PASSWORD environment variable"
    exit 1
fi

# Define the input filename and destination
INPUT_FILENAME="core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
DESTINATION="pi@srk.local:/tmp/"
PASSWORD=${1:-$SCP_PASSWORD}

# Copy the file using scp
echo "1. Copying $INPUT_FILENAME to $DESTINATION"
sshpass -p $PASSWORD scp $SOURCE_FILE $DESTINATION

# Check if the copy was successful
if [ $? -eq 0 ];  then
    echo "2. $INPUT_FILENAME copied successfully to $DESTINATION"
    echo "3. Moving $INPUT_FILENAME to /srv/nfs/"
    # Move the file to the NFS folder
    sshpass -p $PASSWORD ssh pi@srk.local "sudo mv /tmp/$INPUT_FILENAME /srv/nfs/"
    if [ $? -eq 0 ]; then
        echo "4. $INPUT_FILENAME moved successfully to /srv/nfs/"
    else
        echo "4. Failed to move $INPUT_FILENAME to /srv/nfs/"
    fi
else
    echo "2. Failed to copy $INPUT_FILENAME to $DESTINATION"
fi
