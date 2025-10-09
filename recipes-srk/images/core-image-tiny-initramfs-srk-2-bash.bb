SUMMARY = "Tiny image capable of booting a device."
DESCRIPTION = "Tiny image capable of booting a device."

LICENSE = "MIT"

# Specify the filesystem types for the initramfs
IMAGE_FSTYPES = "cpio.gz"

inherit core-image

# Include systemd, busybox, bash, and shadow in the rootfs
IMAGE_INSTALL = "systemd busybox bash shadow nfs-utils"

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
    useradd -p '${SRKPWD}' -s /bin/bash srk; \
    "

# Fix shell prompt for bash
ROOTFS_POSTPROCESS_COMMAND += "fix_shell_prompt; "

fix_shell_prompt() {
    # Set hostname
    echo "srk-device" > ${IMAGE_ROOTFS}/etc/hostname
    
    # Create /etc/profile for bash with proper prompt
    echo '#!/bin/bash' > ${IMAGE_ROOTFS}/etc/profile
    echo 'export PATH="/bin:/sbin:/usr/bin:/usr/sbin"' >> ${IMAGE_ROOTFS}/etc/profile
    echo 'export TERM=linux' >> ${IMAGE_ROOTFS}/etc/profile
    echo 'export PS1="\u@\h:\w\$ "' >> ${IMAGE_ROOTFS}/etc/profile
    
    chmod +x ${IMAGE_ROOTFS}/etc/profile
    
    # Set bash as default shell for root and srk users
    # Update /etc/passwd to use /bin/bash instead of /bin/sh
    sed -i 's|root:.*:/bin/sh|root:x:0:0:root:/root:/bin/bash|' ${IMAGE_ROOTFS}/etc/passwd
    
    # Create root directory and .bashrc for root
    mkdir -p ${IMAGE_ROOTFS}/root
    echo 'export PS1="\u@\h:\w\$ "' > ${IMAGE_ROOTFS}/root/.bashrc
    echo 'export PATH="/bin:/sbin:/usr/bin:/usr/sbin"' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo 'export TERM=linux' >> ${IMAGE_ROOTFS}/root/.bashrc
    
    # Create home directory for srk user and setup .bashrc
    mkdir -p ${IMAGE_ROOTFS}/home/srk
    echo 'export PS1="\u@\h:\w\$ "' > ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo 'export PATH="/bin:/sbin:/usr/bin:/usr/sbin"' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo 'export TERM=linux' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    
    # Set proper ownership for srk home directory (will be applied at runtime)
    chown -R 1000:1000 ${IMAGE_ROOTFS}/home/srk 2>/dev/null || true
}

# Enable essential systemd services
SYSTEMD_AUTO_ENABLE = "enable"
IMAGE_INSTALL:append = " systemd-serialgetty"
IMAGE_INSTALL:append = " kernel-modules"