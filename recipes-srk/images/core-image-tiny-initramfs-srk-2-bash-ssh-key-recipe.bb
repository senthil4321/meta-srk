SUMMARY = "Tiny image with bash and SSH key authentication"
DESCRIPTION = "Modular image with bash shell and SSH key-based authentication"

LICENSE = "MIT"

inherit core-image

IMAGE_FSTYPES = "cpio.gz"

IMAGE_INSTALL = "\
    systemd \
    busybox \
    bash \
    bash-completion \
    shadow \
    nfs-utils \
    bbb-02-led-blink \
    bbb-03-led-blink-nolibc \
    bbb-03-rtc \
    dropbear \
    util-linux \
    util-linux-mount \
    systemd-serialgetty \
    dbus \
    libpam \
    kernel-modules \
    srk-system-config \
    srk-user-config \
    openssl \
    openssl-bin \
    libkcapi \
    bc \
    coreutils \
    procps \
    curl \
    iproute2 \
    python3-core \
    system-monitor-web \
    boot-banner \
    build-info \
    systemd-logging-config \
    libcap \
    libcap-bin \
    capabilities-demo \
    strongswan \
    ipsec-config \
    ipsec-modules-loader \
    acl \
    acl-demo \
"

# Allow larger initramfs for additional tools and Python
INITRAMFS_MAXSIZE = "524288"


IMAGE_FEATURES = ""

COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

inherit extrausers
PASSWD = "\$6\$6ce3bbe55510f53b\$AJ.SC2nRGeqQa9DSsS1ZtQTMIvoKFFdnFF9j6E8WSXxc1I73fyM7BOA2u.FyfhcCZR.Fd0johBQemiqc3Uj3E." 
SRKPWD = "\$6\$aab45c9549d33a6c\$QZTIyCbqHKNsmndsq9j/fXY8Ex6rUmR2Jpnr0LXYNIGWJ9f90dR8ZbQFJ1G6m8oDjc0.e1sbBXKXknYq.CRsT0" 
CAPPWD = "\$6\$7c8d3ac7b8e4c31f\$vXJi8qF7B0y9zT3H1pQ8.jK6L2nM4oP5rS6tU7vW8xY9zA0bC1dE2fG3hI4jK5lM6nO7pQ8rS9tU0vW1xY2zA3" 

EXTRA_USERS_PARAMS = "\
    usermod -p '${PASSWD}' root; \
    usermod -d /root root; \
    usermod -s /bin/bash root; \
    useradd -p '${SRKPWD}' -u 1000 -d /home/srk -s /bin/bash srk; \
    useradd -p '${CAPPWD}' -u 1001 -d /home/capuser -s /bin/bash capuser; \
"

SYSTEMD_AUTO_ENABLE = "enable"
SYSTEMD_DEFAULT_TARGET = "multi-user.target"

ROOTFS_POSTPROCESS_COMMAND += "customize_system_files; "
ROOTFS_POSTPROCESS_COMMAND += "configure_dropbear; "
ROOTFS_POSTPROCESS_COMMAND += "enable_systemd_services; "
ROOTFS_POSTPROCESS_COMMAND += "update_build_info_rootfs; "

# Update build-info with rootfs-specific information
update_build_info_rootfs() {
    if [ -f ${IMAGE_ROOTFS}/etc/build-info ]; then
        # Update rootfs image name and build time (without quotes)
        ROOTFS_BUILD_TIME="$(date '+%Y-%m-%d %H:%M:%S %Z')"
        sed -i "s|^ROOTFS_IMAGE=.*|ROOTFS_IMAGE=${IMAGE_BASENAME}|" ${IMAGE_ROOTFS}/etc/build-info
        sed -i "s|^ROOTFS_BUILD_TIME=.*|ROOTFS_BUILD_TIME=${ROOTFS_BUILD_TIME}|" ${IMAGE_ROOTFS}/etc/build-info
    fi
}

# Customize system configuration files that are provided by base-files
customize_system_files() {
    # Update hostname
    echo "srk-device" > ${IMAGE_ROOTFS}/etc/hostname
    
    # Update /etc/shells to include bash
    cat > ${IMAGE_ROOTFS}/etc/shells <<EOF
/bin/sh
/bin/bash
/usr/bin/bash
EOF

    # Update /etc/profile with our custom profile
    cat > ${IMAGE_ROOTFS}/etc/profile <<'EOF'
# Global bash profile for SRK embedded system

# Set reasonable defaults
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin
export PS1='\u@\h:\w\$ '

# Enable bash completion if available
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# Make sure /tmp exists and is writable
[ -d /tmp ] || mkdir -p /tmp
chmod 1777 /tmp

# Load profile fragments if they exist
for i in /etc/profile.d/*.sh ; do
    if [ -r "$i" ]; then
        . $i
    fi
done
unset i
EOF
    chmod 755 ${IMAGE_ROOTFS}/etc/profile
}

# Configure Dropbear to allow root login
configure_dropbear() {
    # Override the default Dropbear configuration to allow root login
    cat > ${IMAGE_ROOTFS}/etc/default/dropbear <<EOF
# Dropbear configuration for SRK system
# Allow root login with password and key-based authentication
DROPBEAR_EXTRA_ARGS=""
DROPBEAR_PORT=22
EOF
    chmod 644 ${IMAGE_ROOTFS}/etc/default/dropbear
}

# Enable and configure systemd services
enable_systemd_services() {
    if [ -e ${IMAGE_ROOTFS}${systemd_system_unitdir}/systemd-networkd.service ]; then
        ln -sf ${systemd_system_unitdir}/systemd-networkd.service \
            ${IMAGE_ROOTFS}${sysconfdir}/systemd/system/multi-user.target.wants/systemd-networkd.service
    fi
    
    if [ -e ${IMAGE_ROOTFS}${systemd_system_unitdir}/dbus.service ]; then
        ln -sf ${systemd_system_unitdir}/dbus.service \
            ${IMAGE_ROOTFS}${sysconfdir}/systemd/system/multi-user.target.wants/dbus.service
    fi
}
