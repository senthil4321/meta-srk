SUMMARY = "Minimal squashfs image capable of booting a device."
DESCRIPTION = "Minimal squashfs image with optimized compression and read-only filesystem support."

LICENSE = "MIT"

# Use the SRK Minimal SquashFS distro configuration
DISTRO = "srk-minimal-squashfs-distro"

# Specify the filesystem types for the initramfs and root filesystem
# TODO: Future change - Focus on squashfs as the primary filesystem type
IMAGE_FSTYPES += "squashfs"

inherit core-image

# Include systemd, busybox, shadow, and squashfs tools in the rootfs
# Added additional squashfs utilities for better squashfs support
IMAGE_INSTALL = "systemd busybox shadow squashfs-tools srk-seccomp"

# Add hello package and remove kernel/u-boot from image
IMAGE_INSTALL:append = " hello"
IMAGE_INSTALL:remove = "kernel u-boot"

# Do not include any additional features to keep image minimal
IMAGE_FEATURES = ""

# Use the same restriction as initramfs-live-install
COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

# Set default root password
inherit extrausers
PASSWD = "\$1\$1.BURo5Y\$QI5ij4TNpxJB7p0WbIouS." 
SRKPWD = "\$1\$Lgfdhcj4\$c63Yh3BP7PTnOSB55JdJL0" 
inherit extrausers
EXTRA_USERS_PARAMS = "\
    usermod -p '${PASSWD}' root; \
    useradd -p '${SRKPWD}' srk; \
    "

# Enable essential systemd services
SYSTEMD_AUTO_ENABLE = "enable"
IMAGE_INSTALL:append = " systemd-serialgetty"

# TODO: Future change - Squashfs-specific optimizations
# Set compression algorithm and block size for squashfs
# EXTRA_IMAGECMD:squashfs = "-comp xz -b 1048576"

# Generate the root filesystem image
# TODO: Future change - Reduce size since squashfs provides better compression
IMAGE_ROOTFS_SIZE = "8192"
IMAGE_ROOTFS_EXTRA_SPACE = "0"

# TODO: Future change - Read-only filesystem optimizations
# IMAGE_FEATURES:append = " read-only-rootfs"

# Additional squashfs mount options can be configured here if needed
# SQUASHFS_MOUNT_OPTIONS = "ro,noatime"