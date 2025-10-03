#!/bin/bash

# Build and deploy script for BBB LED blink initramfs
# Builds the initramfs image, kernel, copies files, and resets BBB

echo "=== Building core-image-tiny-initramfs-srk-9-nobusybox ==="
cd /home/srk2cob/project/poky
source oe-init-build-env build
bitbake core-image-tiny-initramfs-srk-9-nobusybox

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build initramfs image"
    exit 1
fi

echo "=== Building linux-yocto-srk-tiny ==="
bitbake linux-yocto-srk-tiny

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build kernel"
    exit 1
fi

echo "=== Copying zImage and device tree ==="
cd /home/srk2cob/project/poky/meta-srk
./04_copy_zImage.sh -i -tiny

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to copy zImage"
    exit 1
fi

echo "=== Resetting BBB and monitoring logs ==="
./14_reset_bbb_and_log_monitor.py

echo "=== Build and deploy complete ==="