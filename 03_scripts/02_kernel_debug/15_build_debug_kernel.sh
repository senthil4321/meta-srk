#!/bin/bash

# Build script for debuggable kernel
# This script builds the debug variant of the optimized kernel

set -e

echo "=== Building Debuggable Kernel ==="
echo "This will build linux-yocto-srk-tiny-debug with debugging features enabled"
echo

# Check if we're in the right directory
if [ ! -f "meta-srk/recipes-kernel/linux/linux-yocto-srk-tiny-debug_6.6.bb" ]; then
    echo "Error: Please run this script from the poky directory"
    echo "Expected to find: meta-srk/recipes-kernel/linux/linux-yocto-srk-tiny-debug_6.6.bb"
    exit 1
fi

# Source the build environment
if [ ! -f "build/conf/local.conf" ]; then
    echo "Setting up build environment..."
    source oe-init-build-env
else
    echo "Using existing build environment..."
    cd build
fi

echo "=== Updating local.conf for debug kernel ==="

# Backup current local.conf
cp conf/local.conf conf/local.conf.backup.$(date +%Y%m%d_%H%M%S)

# Update PREFERRED_PROVIDER_virtual/kernel
if grep -q "PREFERRED_PROVIDER_virtual/kernel" conf/local.conf; then
    sed -i 's/^PREFERRED_PROVIDER_virtual\/kernel.*$/PREFERRED_PROVIDER_virtual\/kernel = "linux-yocto-srk-tiny-debug"/' conf/local.conf
    echo "Updated existing PREFERRED_PROVIDER_virtual/kernel setting"
else
    echo 'PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-tiny-debug"' >> conf/local.conf
    echo "Added PREFERRED_PROVIDER_virtual/kernel setting"
fi

echo
echo "=== Current kernel configuration ==="
grep "PREFERRED_PROVIDER_virtual/kernel" conf/local.conf

echo
echo "=== Cleaning previous builds ==="
bitbake -c cleansstate linux-yocto-srk-tiny-debug

echo
echo "=== Building debug kernel ==="
bitbake linux-yocto-srk-tiny-debug

echo
echo "=== Building complete image with debug kernel ==="
bitbake core-image-tiny-initramfs-srk-9-nobusybox

echo
echo "=== Build completed! ==="
echo
echo "Debug kernel features enabled:"
echo "- Debug info (DWARF symbols)"
echo "- Debug filesystem (/sys/kernel/debug/)"
echo "- Magic SysRq keys"
echo "- KGDB remote debugging"
echo "- Kallsyms (full symbol table)"
echo "- Function tracer"
echo "- Dynamic debug"
echo "- Memory debugging"
echo "- Lock debugging"
echo
echo "To deploy to SD card, run:"
echo "  cd .."
echo "  ./02_prepare_sdcard.sh"
echo
echo "For debugging instructions, see:"
echo "  meta-srk/DEBUGGING_GUIDE.md"
echo
echo "To switch back to ultra-minimal kernel, change local.conf:"
echo "  PREFERRED_PROVIDER_virtual/kernel = \"linux-yocto-srk-tiny\""