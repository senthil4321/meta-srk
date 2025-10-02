#!/bin/bash

# Script: 23_build_rpi_zero_image.sh
# Purpose: Build Raspberry Pi Zero image with SRK customizations
# Author: SRK Development Team

set -e

# Configuration
POKY_DIR="/home/srk2cob/project/poky"
BUILD_DIR="${POKY_DIR}/build-rpi-zero"
MACHINE="raspberrypi-zero"
DISTRO="srk-distro"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "$POKY_DIR" ]; then
    print_error "Poky directory not found: $POKY_DIR"
    exit 1
fi

cd "$POKY_DIR"

print_header "Building Raspberry Pi Zero Image"

# Source the build environment
print_info "Setting up build environment..."
if [ ! -f "oe-init-build-env" ]; then
    print_error "oe-init-build-env not found in $POKY_DIR"
    exit 1
fi

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Source environment (this changes directory to build dir)
source oe-init-build-env "$BUILD_DIR"

print_info "Build directory: $(pwd)"

# Configure local.conf for Raspberry Pi Zero
print_info "Configuring build for Raspberry Pi Zero..."

# Backup existing local.conf if it exists
if [ -f conf/local.conf ]; then
    cp conf/local.conf conf/local.conf.backup.$(date +%s)
fi

# Create local.conf for RPi Zero
cat > conf/local.conf << EOF
# Local configuration for Raspberry Pi Zero build

# Machine selection
MACHINE = "${MACHINE}"

# Distribution
DISTRO = "${DISTRO}"

# Package manager
PACKAGE_CLASSES ?= "package_rpm"

# Download directory
DL_DIR ?= "\${TOPDIR}/../downloads"

# Shared state cache
SSTATE_DIR ?= "\${TOPDIR}/../sstate-cache"

# Temporary directory
TMPDIR = "\${TOPDIR}/tmp"

# Additional features
EXTRA_IMAGE_FEATURES ?= "debug-tweaks ssh-server-openssh"

# Parallel build settings
BB_NUMBER_THREADS ?= "4"
PARALLEL_MAKE ?= "-j 4"

# Disk space monitoring
BB_DISKMON_DIRS ??= "\\
    STOPTASKS,\${TMPDIR},1G,100M \\
    STOPTASKS,\${DL_DIR},1G,100M \\
    STOPTASKS,\${SSTATE_DIR},1G,100M \\
    STOPTASKS,/tmp,100M,100M \\
    HALT,\${TMPDIR},100M,1K \\
    HALT,\${DL_DIR},100M,1K \\
    HALT,\${SSTATE_DIR},100M,1K \\
    HALT,/tmp,10M,1K"

# Hash equivalence
BB_HASHSERVE = "auto"
BB_SIGNATURE_HANDLER = "OEEquivHash"

# Version information
CONF_VERSION = "2"

# Raspberry Pi specific settings
LICENSE_FLAGS_ACCEPTED = "synaptics-killswitch"
ENABLE_UART = "1"
GPU_MEM = "16"

# Serial console
SERIAL_CONSOLES = "115200;ttyS0 115200;ttyAMA0"

# Boot configuration
KERNEL_IMAGETYPE = "zImage"
KERNEL_DEVICETREE = "bcm2708-rpi-zero.dtb bcm2708-rpi-zero-w.dtb"

# Image types
IMAGE_FSTYPES += "tar.bz2 ext3 rpi-sdimg"

# Development settings
ROOT_HOME = "/home/root"
EXTRA_IMAGE_FEATURES += "package-management"

# Debug kernel support
PREFERRED_VERSION_linux-yocto = "6.6%"
KERNEL_FEATURES:append = " cfg/debug/printk.scc"

# SRK customizations
INHERIT += "rm_work"
RM_WORK_EXCLUDE += "core-image-minimal-rpi-zero core-image-tiny-initramfs-rpi-zero-debug"
EOF

# Configure bblayers.conf to include meta-srk
print_info "Configuring layers..."

if [ -f conf/bblayers.conf ]; then
    cp conf/bblayers.conf conf/bblayers.conf.backup.$(date +%s)
fi

cat > conf/bblayers.conf << EOF
# POKY_BBLAYERS_CONF_VERSION is increased each time build/conf/bblayers.conf
# changes incompatibly
POKY_BBLAYERS_CONF_VERSION = "2"

BBPATH = "\${TOPDIR}"
BBFILES ?= ""

BBLAYERS ?= " \\
  ${POKY_DIR}/meta \\
  ${POKY_DIR}/meta-poky \\
  ${POKY_DIR}/meta-yocto-bsp \\
  ${POKY_DIR}/meta-openembedded/meta-oe \\
  ${POKY_DIR}/meta-openembedded/meta-python \\
  ${POKY_DIR}/meta-openembedded/meta-networking \\
  ${POKY_DIR}/meta-raspberrypi \\
  ${POKY_DIR}/meta-srk \\
  "
EOF

# Check if meta-raspberrypi exists
if [ ! -d "${POKY_DIR}/meta-raspberrypi" ]; then
    print_warning "meta-raspberrypi layer not found"
    print_info "Cloning meta-raspberrypi layer..."
    cd "${POKY_DIR}"
    git clone https://github.com/agherzan/meta-raspberrypi.git
    cd "$BUILD_DIR"
fi

# Build the images
print_header "Building Images"

print_info "Building core-image-minimal-rpi-zero..."
if bitbake core-image-minimal-rpi-zero; then
    print_info "✓ core-image-minimal-rpi-zero built successfully"
else
    print_error "Failed to build core-image-minimal-rpi-zero"
    exit 1
fi

print_info "Building core-image-tiny-initramfs-rpi-zero-debug..."
if bitbake core-image-tiny-initramfs-rpi-zero-debug; then
    print_info "✓ core-image-tiny-initramfs-rpi-zero-debug built successfully"
else
    print_error "Failed to build core-image-tiny-initramfs-rpi-zero-debug"
    exit 1
fi

# Show build results
print_header "Build Results"

DEPLOY_DIR="${BUILD_DIR}/tmp/deploy/images/${MACHINE}"

if [ -d "$DEPLOY_DIR" ]; then
    print_info "Images available in: $DEPLOY_DIR"
    echo ""
    print_info "Available files:"
    ls -lh "$DEPLOY_DIR"/*.img "$DEPLOY_DIR"/*.cpio.gz 2>/dev/null || true
    echo ""
    
    # Check for specific files
    if [ -f "${DEPLOY_DIR}/core-image-minimal-rpi-zero-${MACHINE}.rpi-sdimg" ]; then
        IMG_SIZE=$(du -h "${DEPLOY_DIR}/core-image-minimal-rpi-zero-${MACHINE}.rpi-sdimg" | cut -f1)
        print_info "✓ SD card image: core-image-minimal-rpi-zero-${MACHINE}.rpi-sdimg ($IMG_SIZE)"
    fi
    
    if [ -f "${DEPLOY_DIR}/core-image-tiny-initramfs-rpi-zero-debug-${MACHINE}.cpio.gz" ]; then
        INITRAMFS_SIZE=$(du -h "${DEPLOY_DIR}/core-image-tiny-initramfs-rpi-zero-debug-${MACHINE}.cpio.gz" | cut -f1)
        print_info "✓ Debug initramfs: core-image-tiny-initramfs-rpi-zero-debug-${MACHINE}.cpio.gz ($INITRAMFS_SIZE)"
    fi
    
    if [ -f "${DEPLOY_DIR}/zImage" ]; then
        KERNEL_SIZE=$(du -h "${DEPLOY_DIR}/zImage" | cut -f1)
        print_info "✓ Kernel image: zImage ($KERNEL_SIZE)"
    fi
    
else
    print_warning "Deploy directory not found: $DEPLOY_DIR"
fi

print_header "Next Steps"
echo ""
print_info "1. Flash SD card image to microSD card:"
echo "   sudo dd if=${DEPLOY_DIR}/core-image-minimal-rpi-zero-${MACHINE}.rpi-sdimg of=/dev/sdX bs=4M status=progress"
echo ""
print_info "2. For debugging, copy files to TFTP server:"
echo "   cp ${DEPLOY_DIR}/zImage /path/to/tftp/root/"
echo "   cp ${DEPLOY_DIR}/core-image-tiny-initramfs-rpi-zero-debug-${MACHINE}.cpio.gz /path/to/tftp/root/"
echo ""
print_info "3. Enable UART in config.txt on SD card:"
echo "   echo 'enable_uart=1' >> /path/to/sdcard/config.txt"
echo ""
print_info "4. Configure WiFi (if using Pi Zero W):"
echo "   Edit /path/to/sdcard/rootfs/etc/wpa_supplicant/wpa_supplicant.conf"

print_header "Build Complete!"