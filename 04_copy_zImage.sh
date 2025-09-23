#!/bin/bash

# Define the input filenames and destination
INPUT_FILES=("zImage" "am335x-boneblack.dtb")
SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
USERNAME="pi"
HOSTNAME="srk.local"
SERVER_NAME="$USERNAME@$HOSTNAME"
DESTINATION="$SERVER_NAME:/tmp/"

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -v) VERBOSE="-v" ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Copy the files using rsync
for INPUT_FILENAME in "${INPUT_FILES[@]}"; do
    SOURCE_FILE="$SOURCE_DIR$INPUT_FILENAME"
    echo "1. Copying $INPUT_FILENAME to $DESTINATION"
    START_TIME=$(date +%s)
    rsync -aLv --progress $SOURCE_FILE $DESTINATION
    # Check if the copy was successful
    if [ $? -eq 0 ];  then
        echo "2. $INPUT_FILENAME copied successfully to $DESTINATION"
        # Move the file to the TFTP folder
        ssh $VERBOSE $SERVER_NAME "sudo mv /tmp/$INPUT_FILENAME /srv/tftp/"
        if [ $? -eq 0 ]; then
            echo "3. $INPUT_FILENAME moved successfully to /srv/tftp/"
        else
            echo "3. Failed to move $INPUT_FILENAME to /srv/tftp/"
        fi
    else
        echo "2. Failed to copy $INPUT_FILENAME to $DESTINATION"
    fi
    END_TIME=$(date +%s)
    TIME_TAKEN=$(($END_TIME - $START_TIME))
    echo "Time taken to copy $INPUT_FILENAME: $TIME_TAKEN seconds"
done
