#!/bin/bash

# Script to apply disable-peripherals.patch
# This script applies the patch to the kernel source.

set -e

# Define paths
KERNEL_SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/work-shared/beaglebone-yocto/kernel-source"
PATCH_FILE="/home/srk2cob/project/poky/meta-srk/recipes-kernel/linux/linux-yocto-srk-tiny/patches/disable-peripherals.patch"

echo "Applying disable-peripherals.patch..."

# Change to kernel source directory
cd "$KERNEL_SOURCE_DIR"

# Reset the DTS files to original state
git checkout arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi
git checkout arch/arm/boot/dts/ti/omap/am335x-boneblack-common.dtsi

# Apply the patch
git apply "$PATCH_FILE"

echo "Patch applied successfully."