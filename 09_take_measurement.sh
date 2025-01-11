#!/bin/bash

# Check if FOLDER_NAME is provided as a parameter
if [ -z "$1" ]; then
    echo "Usage: $0 <FOLDER_NAME>"
    exit 1
fi

# Define variables for the paths
FOLDER_NAME=$1
BACKUP_DIR_SHORT=~/project/srk-linux/beaglebone/backup
BACKUP_DIR=${BACKUP_DIR_SHORT}/${FOLDER_NAME}/
BUILD_DIR=~/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto/6.6.21+git/linux-beaglebone_yocto-standard-build
KSIZE_OUTPUT=${BACKUP_DIR}${FOLDER_NAME}_ksize.txt
ZIMAGE_SIZE_LOG=${BACKUP_DIR_SHORT}/zImageSize.txt

# Print progress
echo "Creating backup directory: ${BACKUP_DIR}"
mkdir -p ${BACKUP_DIR}

# Print progress
echo "Running ksize.py and saving output to ${KSIZE_OUTPUT}"
cd ${BUILD_DIR}
ksize.py > ${KSIZE_OUTPUT}

# Print progress
echo "Copying .config file to ${BACKUP_DIR}"
cp .config ${BACKUP_DIR}

# Add date to the zImageSize log file
echo "Adding date to ${ZIMAGE_SIZE_LOG}"
echo $FOLDER_NAME >> ${ZIMAGE_SIZE_LOG}
date >> ${ZIMAGE_SIZE_LOG}

INPUT_FILENAME="zImage"
SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
ls -lahL $SOURCE_FILE >> ${ZIMAGE_SIZE_LOG}
ls -laL $SOURCE_FILE >> ${ZIMAGE_SIZE_LOG}
ls -la $SOURCE_FILE >> ${ZIMAGE_SIZE_LOG}

# Print completion message
echo "Measurement and backup completed successfully."

cat ${ZIMAGE_SIZE_LOG}