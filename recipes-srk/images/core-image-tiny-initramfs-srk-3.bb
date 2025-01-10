SUMMARY = "Tiny image capable of booting a device."
DESCRIPTION = "Tiny image capable of booting a device."

LICENSE = "MIT"

# Specify the filesystem types for the initramfs
IMAGE_FSTYPES = "cpio.gz"

inherit core-image

# Include only busybox and shadow in the rootfs
IMAGE_INSTALL = "busybox shadow cryptsetup util-linux-mount srk-init"
# IMAGE_INSTALL:append = " srk-init-folder"
IMAGE_INSTALL:append = " srk-init"

# Do not include any additional features
IMAGE_FEATURES = ""

# Use the same restriction as initramfs-live-install
COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

# Set default root password
inherit extrausers
PASSWD = "\$1\$WUwXnz3s\$dCRM7MUDP8/0wPAef1XfO1" 
SRKPWD = "\$1\$V9izHbFg\$z8ZfBeREgRqdOP3AuHGn51" 
inherit extrausers
EXTRA_USERS_PARAMS = "\
    usermod -p '${PASSWD}' root; \
    useradd -p '${SRKPWD}' srk; \
    "

# Enable essential kernel modules
# DISTRO_FEATURES:remove = "systemd"
# DISTRO_FEATURES:append = " sysvinit"
# VIRTUAL-RUNTIME_init_manager = "busybox"
