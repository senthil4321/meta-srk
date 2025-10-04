#!/bin/bash

# Copy zImage and DTB files to target device
# Uses SSH alias 'p' configured in ~/.ssh/config for pi@srk.local
# Uses SSH key-based authentication (no password required)
# Supports both standard and tiny kernel configurations
# KAN-17 Fix am335x-yocto-srk-tiny.dtb copy
VERSION="1.1.0"

print_help() {
    cat <<EOF
Usage: $0 [options]

Copy zImage and device tree files to the target device for TFTP boot.

Options:
    -i             Use initramfs-embedded zImage
    -tiny          Use tiny kernel configuration (beaglebone-yocto-srk-tiny)
    -v             Verbose output
    -V             Show version and exit
    -h             This help

Examples:
    $0 -i                    # Standard kernel with initramfs
    $0 -i -tiny              # Tiny kernel with initramfs
    $0 -i -tiny -v           # Tiny kernel with initramfs and verbose output

Notes:
    - Uses SSH alias 'p' configured in ~/.ssh/config
    - SSH key-based authentication is used (no password required)
    - By default, uses regular zImage if available, otherwise initramfs version
    - Default: standard beaglebone-yocto machine with am335x-boneblack.dtb
    - With -tiny: beaglebone-yocto-srk-tiny machine with am335x-yocto-srk-tiny.dtb

Version: $VERSION
EOF
}

# Define the input filenames and destination
USERNAME="pi"
HOSTNAME="srk.local"
SERVER_NAME="$USERNAME@$HOSTNAME"
DESTINATION="$SERVER_NAME:/tmp/"

# Initialize variables
USE_INITRAMFS=false
USE_TINY=false
VERBOSE=""

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i) USE_INITRAMFS=true ;;
        -tiny) USE_TINY=true ;;
        -v) VERBOSE="-v" ;;
        -V)
            echo "$(basename "$0") version $VERSION"
            exit 0
            ;;
        -h)
            print_help
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; print_help; exit 1 ;;
    esac
    shift
done

# Set configuration based on -tiny flag
if [ "$USE_TINY" = true ]; then
    INPUT_FILES=("am335x-yocto-srk-tiny.dtb") # TODO [KAN-17] Fix
    SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto-srk-tiny/"
    MACHINE_SUFFIX="-srk-tiny"
    DTB_NAME="am335x-yocto-srk-tiny.dtb"
    echo "Using tiny kernel configuration (beaglebone-yocto-srk-tiny)"
else
    INPUT_FILES=("am335x-boneblack.dtb")
    SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
    MACHINE_SUFFIX=""
    DTB_NAME="am335x-boneblack.dtb"
    echo "Using standard kernel configuration (beaglebone-yocto)"
fi

# Determine which zImage to use based on -i flag
if [ "$USE_INITRAMFS" = true ]; then
    if [ -f "${SOURCE_DIR}zImage-initramfs-beaglebone-yocto${MACHINE_SUFFIX}.bin" ]; then
        ZIMAGE_FILE="zImage-initramfs-beaglebone-yocto${MACHINE_SUFFIX}.bin"
        ZIMAGE_TARGET="zImage"
        echo "Using embedded initramfs zImage: $ZIMAGE_FILE"
    else
        echo "Error: Initramfs zImage not found: ${SOURCE_DIR}zImage-initramfs-beaglebone-yocto${MACHINE_SUFFIX}.bin"
        exit 1
    fi
else
    # Default behavior: prefer regular zImage, fallback to initramfs
    if [ -f "${SOURCE_DIR}zImage" ]; then
        ZIMAGE_FILE="zImage"
        ZIMAGE_TARGET="zImage"
        echo "Using regular zImage: $ZIMAGE_FILE"
    elif [ -f "${SOURCE_DIR}zImage-initramfs-beaglebone-yocto${MACHINE_SUFFIX}.bin" ]; then
        ZIMAGE_FILE="zImage-initramfs-beaglebone-yocto${MACHINE_SUFFIX}.bin"
        ZIMAGE_TARGET="zImage"
        echo "Using embedded initramfs zImage (fallback): $ZIMAGE_FILE"
    else
        echo "Error: No zImage found in $SOURCE_DIR"
        exit 1
    fi
fi

INPUT_FILES=("$ZIMAGE_FILE" "${INPUT_FILES[@]}")

# Copy all files directly to TFTP directory using rsync with sudo
echo "Copying files directly to TFTP directory..."
START_TIME=$(date +%s)
for INPUT_FILENAME in "${INPUT_FILES[@]}"; do
    SOURCE_FILE="$SOURCE_DIR$INPUT_FILENAME"
    echo "1. Copying $INPUT_FILENAME to TFTP directory"
    
    # Determine target name
    if [ "$INPUT_FILENAME" = "$ZIMAGE_FILE" ]; then
        TARGET_NAME="$ZIMAGE_TARGET"
    else
        # For tiny DTB, rename to standard name as workaround
        if [ "$USE_TINY" = true ] && [ "$INPUT_FILENAME" = "am335x-yocto-srk-tiny.dtb" ]; then
            TARGET_NAME="am335x-boneblack.dtb"
            echo "4. Will rename $INPUT_FILENAME to am335x-boneblack.dtb as workaround"
        else
            TARGET_NAME="$INPUT_FILENAME"
        fi
    fi
    
    # Use rsync with sudo to copy directly to TFTP directory
    rsync -aL $VERBOSE --rsync-path="sudo rsync" $SOURCE_FILE $SERVER_NAME:/srv/tftp/$TARGET_NAME
    if [ $? -eq 0 ]; then
        echo "2. $INPUT_FILENAME copied successfully to /srv/tftp/ as $TARGET_NAME"
    else
        echo "2. Failed to copy $INPUT_FILENAME to /srv/tftp/"
        exit 1
    fi
done

END_TIME=$(date +%s)
TIME_TAKEN=$(($END_TIME - $START_TIME))
echo "Time taken to copy all files: $TIME_TAKEN seconds"
