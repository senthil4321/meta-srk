#!/bin/bash

# Check if the password argument is provided or set as an environment variable
if [ -z "$1" ] && [ -z "$SCP_PASSWORD" ]; then
    echo "Usage: $0 <scp_password> or set SCP_PASSWORD environment variable"
    exit 1
fi

# Define the input filename and destination
INPUT_FILENAME="zImage"
SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
DESTINATION="pi@srk.local:/tmp/"
PASSWORD=${1:-$SCP_PASSWORD}

# Copy the file using scp
echo "1. Copying file to  $DESTINATION"
sshpass -p $PASSWORD scp $SOURCE_FILE $DESTINATION

# Check if the copy was successful
if [ $? -eq 0 ];  then
    echo "2. File copied successfully to $DESTINATION"
    # Delete the content of the NFS folder before extraction
    sshpass -p $PASSWORD ssh pi@srk.local "sudo mv /tmp/zImage /srv/tftp/"
    if [ $? -eq 0 ]; then
        echo "3. NFS folder content deleted successfully"
    else
        echo "3. Failed to delete NFS folder content"
    fi
else
    echo "2. Failed to copy file to $DESTINATION"
fi