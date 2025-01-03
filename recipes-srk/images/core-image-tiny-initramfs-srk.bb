# Simple initramfs image artifact generation for tiny images.
SUMMARY = "Tiny image capable of booting a device."
DESCRIPTION = "Tiny image capable of booting a device. The kernel includes \
the Minimal RAM-based Initial Root Filesystem (initramfs), which finds the \
first 'init' program more efficiently. core-image-tiny-initramfs doesn't \
actually generate an image but rather generates boot and rootfs artifacts \
that can subsequently be picked up by external image generation tools such as wic."

VIRTUAL-RUNTIME_dev_manager ?= " "
INIT_MANAGER = "systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"
# VIRTUAL-RUNTIME_base-utils = "busybox"
# PACKAGE_INSTALL = "packagegroup-core-boot ${VIRTUAL-RUNTIME_base-utils} ${VIRTUAL-RUNTIME_dev_manager} base-passwd ${ROOTFS_BOOTSTRAP_INSTALL}"
PACKAGE_INSTALL = "packagegroup-core-boot ${VIRTUAL-RUNTIME_base-utils} ${VIRTUAL-RUNTIME_dev_manager} base-passwd ${ROOTFS_BOOTSTRAP_INSTALL} systemd systemd-analyze"
#PACKAGE_INSTALL = "packagegroup-core-boot "
# Do not pollute the initrd image with rootfs features
IMAGE_FEATURES = ""

IMAGE_NAME_SUFFIX ?= ""
IMAGE_LINGUAS = ""

LICENSE = "MIT"

# don't actually generate an image, just the artifacts needed for one
IMAGE_FSTYPES = "${INITRAMFS_FSTYPES}"

inherit core-image

IMAGE_ROOTFS_SIZE = "8192"
IMAGE_ROOTFS_EXTRA_SPACE = "0"

# Use the same restriction as initramfs-live-install
COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

# python tinyinitrd () {
#     import pdb
#     pdb.set_trace()  # Add this line to start the debugger
#     print("hello")
# }

# IMAGE_PREPROCESS_COMMAND += "tinyinitrd"

QB_KERNEL_CMDLINE_APPEND += "debugshell=3 init=/bin/busybox sh init"
