SUMMARY = "Tiny image capable of booting a device."
DESCRIPTION = "Tiny image capable of booting a device. The kernel includes \
the Minimal RAM-based Initial Root Filesystem (initramfs), which finds the \
first 'init' program more efficiently. core-image-tiny-initramfs doesn't \
actually generate an image but rather generates boot and rootfs artifacts \
that can subsequently be picked up by external image generation tools such as wic."

LICENSE = "MIT"

# Specify the filesystem types for the initramfs
IMAGE_FSTYPES = "cpio.gz"

inherit core-image

# Include only systemd, busybox, and shadow in the rootfs
IMAGE_INSTALL = "systemd busybox shadow"

# Do not include any additional features
IMAGE_FEATURES = ""

# Set the size of the root filesystem image in kilobytes
IMAGE_ROOTFS_SIZE = "8192"
IMAGE_ROOTFS_EXTRA_SPACE = "0"

# Use the same restriction as initramfs-live-install
COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"


# Enable essential systemd services
SYSTEMD_AUTO_ENABLE = "enable"
IMAGE_INSTALL:append = " systemd-serialgetty"
