#!/bin/bash

# Script: 24_deploy_rpi_zero_debug.sh
# Purpose: Deploy Raspberry Pi Zero debugging setup
# Author: SRK Development Team

set -e

# Configuration
POKY_DIR="/home/srk2cob/project/poky"
BUILD_DIR="${POKY_DIR}/build-rpi-zero"
MACHINE="raspberrypi-zero"
DEPLOY_DIR="${BUILD_DIR}/tmp/deploy/images/${MACHINE}"
TFTP_ROOT="/srv/tftp"

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

# Check if deploy directory exists
if [ ! -d "$DEPLOY_DIR" ]; then
    print_error "Deploy directory not found: $DEPLOY_DIR"
    print_info "Please run 23_build_rpi_zero_image.sh first"
    exit 1
fi

print_header "Deploying Raspberry Pi Zero Debug Setup"

# Create TFTP directory if it doesn't exist
if [ ! -d "$TFTP_ROOT" ]; then
    print_info "Creating TFTP root directory: $TFTP_ROOT"
    sudo mkdir -p "$TFTP_ROOT"
    sudo chown $USER:$USER "$TFTP_ROOT"
fi

# Copy kernel and initramfs to TFTP
print_info "Copying files to TFTP server..."

if [ -f "${DEPLOY_DIR}/zImage" ]; then
    cp "${DEPLOY_DIR}/zImage" "${TFTP_ROOT}/zImage-rpi-zero"
    KERNEL_SIZE=$(du -h "${TFTP_ROOT}/zImage-rpi-zero" | cut -f1)
    print_info "✓ Copied kernel: zImage-rpi-zero ($KERNEL_SIZE)"
else
    print_error "Kernel image not found: ${DEPLOY_DIR}/zImage"
    exit 1
fi

# Find and copy initramfs
INITRAMFS_FILE=$(ls "${DEPLOY_DIR}"/core-image-tiny-initramfs-rpi-zero-debug-*.cpio.gz 2>/dev/null | head -1)
if [ -f "$INITRAMFS_FILE" ]; then
    cp "$INITRAMFS_FILE" "${TFTP_ROOT}/initramfs-rpi-zero-debug.cpio.gz"
    INITRAMFS_SIZE=$(du -h "${TFTP_ROOT}/initramfs-rpi-zero-debug.cpio.gz" | cut -f1)
    print_info "✓ Copied initramfs: initramfs-rpi-zero-debug.cpio.gz ($INITRAMFS_SIZE)"
else
    print_error "Initramfs not found in: $DEPLOY_DIR"
    exit 1
fi

# Copy device tree blobs
DTB_FILES=$(ls "${DEPLOY_DIR}"/bcm2708-rpi-zero*.dtb 2>/dev/null || true)
if [ -n "$DTB_FILES" ]; then
    for dtb in $DTB_FILES; do
        DTB_NAME=$(basename "$dtb")
        cp "$dtb" "${TFTP_ROOT}/"
        print_info "✓ Copied DTB: $DTB_NAME"
    done
else
    print_warning "No device tree blobs found"
fi

# Create debug vmlinux symlink if available
VMLINUX_PATH="${BUILD_DIR}/tmp/work/${MACHINE}-poky-linux-gnueabi/linux-yocto"
VMLINUX_DEBUG=$(find "$VMLINUX_PATH" -name "vmlinux" -type f 2>/dev/null | head -1)

if [ -f "$VMLINUX_DEBUG" ]; then
    ln -sf "$VMLINUX_DEBUG" "${TFTP_ROOT}/vmlinux-rpi-zero-debug"
    VMLINUX_SIZE=$(du -h "$VMLINUX_DEBUG" | cut -f1)
    print_info "✓ Linked debug symbols: vmlinux-rpi-zero-debug ($VMLINUX_SIZE)"
else
    print_warning "Debug vmlinux not found - limited debugging capabilities"
fi

# Create U-Boot script for network boot
print_info "Creating U-Boot network boot script..."

cat > "${TFTP_ROOT}/boot-rpi-zero-debug.txt" << 'EOF'
# U-Boot commands for Raspberry Pi Zero network debugging
# 
# Manual commands to type in U-Boot console:
# 
# 1. Set network parameters:
setenv serverip 192.168.1.100
setenv ipaddr 192.168.1.201
setenv netmask 255.255.255.0
setenv gatewayip 192.168.1.1

# 2. Load kernel and initramfs via TFTP:
tftp 0x00008000 zImage-rpi-zero
tftp 0x02000000 initramfs-rpi-zero-debug.cpio.gz
tftp 0x00000100 bcm2708-rpi-zero.dtb

# 3. Set kernel command line for debugging:
setenv bootargs 'console=ttyS0,115200 console=ttyAMA0,115200 kgdboc=ttyS0,115200 kgdbwait debug earlyprintk initrd=0x02000000,${filesize}'

# 4. Boot with debugging enabled:
bootz 0x00008000 0x02000000 0x00000100

# Alternative without KGDB wait:
# setenv bootargs 'console=ttyS0,115200 console=ttyAMA0,115200 kgdboc=ttyS0,115200 debug earlyprintk initrd=0x02000000,${filesize}'

# Save environment (optional):
# saveenv
EOF

# Create GDB script for debugging
print_info "Creating GDB debugging script..."

cat > "${TFTP_ROOT}/gdb-rpi-zero-debug.sh" << 'EOF'
#!/bin/bash

# GDB debugging script for Raspberry Pi Zero
# Usage: ./gdb-rpi-zero-debug.sh [serial_device]

SERIAL_DEVICE=${1:-/dev/ttyUSB0}
VMLINUX_PATH="/srv/tftp/vmlinux-rpi-zero-debug"

if [ ! -f "$VMLINUX_PATH" ]; then
    echo "Error: vmlinux debug symbols not found at $VMLINUX_PATH"
    exit 1
fi

if [ ! -c "$SERIAL_DEVICE" ]; then
    echo "Error: Serial device not found: $SERIAL_DEVICE"
    exit 1
fi

echo "Starting GDB debugging session for Raspberry Pi Zero..."
echo "Target: $VMLINUX_PATH"
echo "Serial: $SERIAL_DEVICE"
echo ""
echo "GDB will connect via serial port for KGDB debugging"
echo "Make sure the target is booted with kgdbwait parameter"
echo ""

gdb-multiarch "$VMLINUX_PATH" -ex "set remotebaud 115200" -ex "target remote $SERIAL_DEVICE"
EOF

chmod +x "${TFTP_ROOT}/gdb-rpi-zero-debug.sh"

# Create serial console script
print_info "Creating serial console access script..."

cat > "${TFTP_ROOT}/serial-console-rpi-zero.sh" << 'EOF'
#!/bin/bash

# Serial console access for Raspberry Pi Zero
# Usage: ./serial-console-rpi-zero.sh [serial_device] [baud_rate]

SERIAL_DEVICE=${1:-/dev/ttyUSB0}
BAUD_RATE=${2:-115200}

if [ ! -c "$SERIAL_DEVICE" ]; then
    echo "Error: Serial device not found: $SERIAL_DEVICE"
    echo "Available serial devices:"
    ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "No serial devices found"
    exit 1
fi

echo "Connecting to Raspberry Pi Zero serial console..."
echo "Device: $SERIAL_DEVICE"
echo "Baud rate: $BAUD_RATE"
echo ""
echo "Press Ctrl+A then X to exit screen session"
echo ""

# Use screen for serial console
screen "$SERIAL_DEVICE" "$BAUD_RATE"
EOF

chmod +x "${TFTP_ROOT}/serial-console-rpi-zero.sh"

# Show deployment summary
print_header "Deployment Summary"

print_info "Files deployed to TFTP server ($TFTP_ROOT):"
ls -lh "$TFTP_ROOT" | grep -E "(zImage|initramfs|dtb|vmlinux)" || true

echo ""
print_info "Boot scripts created:"
echo "  - boot-rpi-zero-debug.txt (U-Boot commands)"
echo "  - gdb-rpi-zero-debug.sh (GDB debugging)"
echo "  - serial-console-rpi-zero.sh (Serial console)"

print_header "Hardware Setup"
echo ""
print_info "1. Raspberry Pi Zero connections:"
echo "   - GPIO 14 (TX) → FTDI RX"
echo "   - GPIO 15 (RX) → FTDI TX"
echo "   - GND → FTDI GND"
echo ""
print_info "2. Enable UART in config.txt:"
echo "   enable_uart=1"
echo "   dtoverlay=disable-bt"
echo ""
print_info "3. Network setup (if using Ethernet over USB):"
echo "   - Connect USB cable to data port (not power port)"
echo "   - Enable USB gadget mode in config.txt"

print_header "Usage Instructions"
echo ""
print_info "Serial Console Access:"
echo "  ${TFTP_ROOT}/serial-console-rpi-zero.sh /dev/ttyUSB0"
echo ""
print_info "KGDB Debugging:"
echo "  1. Boot Pi Zero with kgdbwait parameter"
echo "  2. Run: ${TFTP_ROOT}/gdb-rpi-zero-debug.sh /dev/ttyUSB0"
echo ""
print_info "Network Boot (if supported):"
echo "  1. Set up TFTP server with files"
echo "  2. Follow commands in boot-rpi-zero-debug.txt"

print_header "Deployment Complete!"