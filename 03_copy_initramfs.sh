#!/bin/bash

# Define the input filename and destination
INPUT_FILENAME="core-image-tiny-initramfs-srk-beaglebone-yocto.cpio.gz"
SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
DESTINATION="pi@srk.local:/tmp/"

# Copy the file using scp
scp $SOURCE_FILE $DESTINATION

# Check if the copy was successful
if [ $? -eq 0 ];  then
    echo "File copied successfully to $DESTINATION"
    # Extract the file in the remote to folder /srv/nfs2/
    ssh pi@srk.local "gunzip -c /tmp/$INPUT_FILENAME | sudo cpio -idmv -D /srv/nfs3/"
    if [ $? -eq 0 ]; then
        echo "File extracted successfully to /srv/nfs/"
    else
        echo "Failed to extract file to /srv/nfs/"
    fi
else
    echo "Failed to copy file to $DESTINATION"
fi