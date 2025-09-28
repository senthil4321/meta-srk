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

# Check git status and clean up if necessary
if git status --porcelain | grep -q .; then
    echo "Warning: Kernel source has uncommitted changes. Resetting..."
    git reset --hard HEAD
    git clean -fd
fi

# Check if in middle of rebase/am session
if [ -d .git/rebase-apply ] || [ -d .git/rebase-merge ]; then
    echo "Warning: Git is in middle of rebase/am session. Aborting..."
    git rebase --abort 2>/dev/null || git am --abort 2>/dev/null || true
fi

# Reset the DTS files to original state
git checkout arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi
git checkout arch/arm/boot/dts/ti/omap/am335x-boneblack-common.dtsi

# Apply the patch
if ! git apply "$PATCH_FILE"; then
    echo "Error: Patch failed to apply."
    echo "Possible causes:"
    echo "  - Kernel source is modified"
    echo "  - Patch was generated from different kernel version"
    echo "  - Check git status and reset if necessary"
    exit 1
fi

echo "Patch applied successfully."