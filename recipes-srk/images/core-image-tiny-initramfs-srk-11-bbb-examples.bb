SUMMARY = "BBB EEPROM Reader Image with BusyBox - SRK Examples"
DESCRIPTION = "Minimal image with BusyBox init system and BBB EEPROM reader utility - Part of SRK examples series"
LICENSE = "MIT"

inherit core-image

# Include BusyBox
IMAGE_INSTALL = "busybox bbb-01-eeprom"

# Basic system packages
IMAGE_INSTALL += "base-files base-passwd"

# Networking (optional, for testing)
IMAGE_INSTALL += "netbase i2c-tools"

# Don't pull in unnecessary packages
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""

# Remove unnecessary features
DISTRO_FEATURES:remove = "x11 wayland opengl vulkan bluetooth wifi usbhost usbgadget pcmcia pci 3g nfc zeroconf pulseaudio alsa ptest gobject-introspection-data debuginfod nfs"

# Minimal init system
VIRTUAL-RUNTIME_init_manager = "busybox"
VIRTUAL-RUNTIME_initscripts = "busybox"

# Set root filesystem size (optional)
IMAGE_ROOTFS_SIZE = "8192"

# Enable initramfs
IMAGE_FSTYPES = "cpio.gz"