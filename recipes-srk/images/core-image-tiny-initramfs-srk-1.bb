SUMMARY = "Tiny image capable of booting a device."
DESCRIPTION = "Tiny image capable of booting a device. The kernel includes \
the Minimal RAM-based Initial Root Filesystem (initramfs), which finds the \
first 'init' program more efficiently. core-image-tiny-initramfs doesn't \
actually generate an image but rather generates boot and rootfs artifacts \
that can subsequently be picked up by external image generation tools such as wic."

LICENSE = "MIT"

# Specify the filesystem types for the initramfs
IMAGE_FSTYPES = "${INITRAMFS_FSTYPES}"

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

# Set root password
ROOTFS_POSTPROCESS_COMMAND += "set_root_password; "

# Enable essential systemd services
SYSTEMD_AUTO_ENABLE = "enable"
IMAGE_INSTALL:append = " systemd-serialgetty"

python set_root_password() {
    import subprocess
    rootfs_dir = d.getVar('IMAGE_ROOTFS')
    passwd_cmd = "echo 'root:password' | chroot {} /usr/sbin/chpasswd".format(rootfs_dir)
    subprocess.run(passwd_cmd, shell=True, check=True)
}