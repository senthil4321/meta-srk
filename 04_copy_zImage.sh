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
echo "1. Copying $INPUT_FILENAME to $DESTINATION"
sshpass -p $PASSWORD scp $SOURCE_FILE $DESTINATION

# Check if the copy was successful
if [ $? -eq 0 ];  then
    echo "2. $INPUT_FILENAME copied successfully to $DESTINATION"
    # Move the file to the TFTP folder
    sshpass -p $PASSWORD ssh pi@srk.local "sudo mv /tmp/$INPUT_FILENAME /srv/tftp/"
    if [ $? -eq 0 ]; then
        echo "3. $INPUT_FILENAME moved successfully to /srv/tftp/"
    else
        echo "3. Failed to move $INPUT_FILENAME to /srv/tftp/"
    fi
else
    echo "2. Failed to copy $INPUT_FILENAME to $DESTINATION"
fi