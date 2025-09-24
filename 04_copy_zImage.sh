#!/bin/bash

# Define the input filenames and destination
INPUT_FILES=("am335x-boneblack.dtb")
SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
USERNAME="pi"
HOSTNAME="srk.local"
SERVER_NAME="$USERNAME@$HOSTNAME"
DESTINATION="$SERVER_NAME:/tmp/"

# Determine which zImage to use (prefer embedded initramfs version)
if [ -f "${SOURCE_DIR}zImage-initramfs-beaglebone-yocto.bin" ]; then
    ZIMAGE_FILE="zImage-initramfs-beaglebone-yocto.bin"
    ZIMAGE_TARGET="zImage"
    echo "Using embedded initramfs zImage: $ZIMAGE_FILE"
elif [ -f "${SOURCE_DIR}zImage" ]; then
    ZIMAGE_FILE="zImage"
    ZIMAGE_TARGET="zImage"
    echo "Using regular zImage: $ZIMAGE_FILE"
else
    echo "Error: No zImage found in $SOURCE_DIR"
    exit 1
fi

INPUT_FILES=("$ZIMAGE_FILE" "${INPUT_FILES[@]}")

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
        # Move the file to the TFTP folder with appropriate naming
        if [ "$INPUT_FILENAME" = "$ZIMAGE_FILE" ]; then
            ssh $VERBOSE $SERVER_NAME "sudo mv /tmp/$INPUT_FILENAME /srv/tftp/$ZIMAGE_TARGET"
            TARGET_NAME="$ZIMAGE_TARGET"
        else
            ssh $VERBOSE $SERVER_NAME "sudo mv /tmp/$INPUT_FILENAME /srv/tftp/"
            TARGET_NAME="$INPUT_FILENAME"
        fi
        if [ $? -eq 0 ]; then
            echo "3. $INPUT_FILENAME moved successfully to /srv/tftp/ as $TARGET_NAME"
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
