SUMMARY = "SRK minimal image for Raspberry Pi Zero"
DESCRIPTION = "Minimal image for Raspberry Pi Zero with SRK customizations"

LICENSE = "MIT"

# Inherit minimal image
inherit core-image

# Base packages
IMAGE_INSTALL = "packagegroup-core-boot ${CORE_IMAGE_EXTRA_INSTALL}"

# Add essential tools
IMAGE_INSTALL += "\
    openssh \
    dropbear \
    kernel-modules \
    linux-firmware-bcm43430 \
    linux-firmware-bcm43455 \
    wpa-supplicant \
    iw \
    wireless-tools \
    dhcpcd \
    ifupdown \
"

# Development and debugging tools
IMAGE_INSTALL += "\
    gdb \
    gdbserver \
    strace \
    tcpdump \
    netcat \
    socat \
    screen \
    vim \
    nano \
"

# SRK specific packages
IMAGE_INSTALL += "\
    srk-init \
    srk-crypt \
    silentloop \
"

# Set root password for development
inherit extrausers
EXTRA_USERS_PARAMS = "usermod -P raspberry root;"

# SSH root login
IMAGE_FEATURES += "ssh-server-openssh"

# Package management
IMAGE_FEATURES += "package-management"

# Additional space for development
IMAGE_ROOTFS_EXTRA_SPACE = "512000"

# Enable read-write filesystem
IMAGE_FEATURES += "read-only-rootfs"
IMAGE_FEATURES:remove = "read-only-rootfs"

# Serial console configuration for debugging
append_serial_console() {
    # Enable serial console on both UART interfaces
    echo "console=serial0,115200 console=tty1" >> ${IMAGE_ROOTFS}/boot/cmdline.txt || true
}

ROOTFS_POSTPROCESS_COMMAND += "append_serial_console; "

# WiFi configuration placeholder
setup_wifi_config() {
    mkdir -p ${IMAGE_ROOTFS}/etc/wpa_supplicant
    cat > ${IMAGE_ROOTFS}/etc/wpa_supplicant/wpa_supplicant.conf << EOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

# Example WiFi network configuration
# network={
#     ssid="your_network_name"
#     psk="your_password"
# }
EOF
}

ROOTFS_POSTPROCESS_COMMAND += "setup_wifi_config; "

# Enable SSH on boot
enable_ssh_on_boot() {
    touch ${IMAGE_ROOTFS}/boot/ssh
    systemctl --root=${IMAGE_ROOTFS} enable ssh || true
    systemctl --root=${IMAGE_ROOTFS} enable dropbear || true
}

ROOTFS_POSTPROCESS_COMMAND += "enable_ssh_on_boot; "