SUMMARY = "Tiny image capable of booting a device."
DESCRIPTION = "Tiny image capable of booting a device."

LICENSE = "MIT"

# Specify the filesystem types for the initramfs
IMAGE_FSTYPES = "cpio.gz"

inherit core-image

# Include only systemd, busybox, and shadow in the rootfs
IMAGE_INSTALL = "systemd busybox shadow nfs-utils"

# Do not include any additional features
IMAGE_FEATURES = ""

# Use the same restriction as initramfs-live-install
COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

# Set default root password
inherit extrausers
PASSWD = "\$6\$6ce3bbe55510f53b\$AJ.SC2nRGeqQa9DSsS1ZtQTMIvoKFFdnFF9j6E8WSXxc1I73fyM7BOA2u.FyfhcCZR.Fd0johBQemiqc3Uj3E." 
SRKPWD = "\$6\$aab45c9549d33a6c\$QZTIyCbqHKNsmndsq9j/fXY8Ex6rUmR2Jpnr0LXYNIGWJ9f90dR8ZbQFJ1G6m8oDjc0.e1sbBXKXknYq.CRsT0" 
inherit extrausers
EXTRA_USERS_PARAMS = "\
    usermod -p '${PASSWD}' root; \
    useradd -p '${SRKPWD}' srk; \
    "

# Enable essential systemd services
SYSTEMD_AUTO_ENABLE = "enable"
IMAGE_INSTALL:append = " systemd-serialgetty"
IMAGE_INSTALL:append = " kernel-modules"