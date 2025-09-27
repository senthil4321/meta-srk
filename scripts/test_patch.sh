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
bitbake linux-yocto-srk-tiny

echo "Kernel build completed successfully. Patch test passed."