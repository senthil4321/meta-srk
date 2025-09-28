#!/bin/bash

# Script to test disable-peripherals.patch
# This script builds the kernel to verify the patch applies correctly.

set -e

# Define paths
POKY_DIR="/home/srk2cob/project/poky"
BUILD_DIR="$POKY_DIR/build"

echo "Testing disable-peripherals.patch by building the kernel..."

# Change to Poky directory and setup environment
cd "$POKY_DIR"
source oe-init-build-env build

# Clean the kernel build state
bitbake linux-yocto-srk-tiny -c cleansstate

# Build the kernel
if bitbake linux-yocto-srk-tiny; then
    echo "Kernel build completed successfully. Patch test passed."
    echo "Note: CONFIG_* warnings are normal and don't indicate patch issues."
else
    echo "Error: Kernel build failed. Check the patch for issues."
    echo "Common issues:"
    echo "  - Patch syntax errors"
    echo "  - DTS compilation failures"
    echo "  - Missing dependencies"
    exit 1
fi