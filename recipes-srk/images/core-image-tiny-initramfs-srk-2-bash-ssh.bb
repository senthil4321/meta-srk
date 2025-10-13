SUMMARY = "Tiny image with bash shell and SSH support capable of booting a device."
DESCRIPTION = "Tiny image with bash shell and SSH support capable of booting a device."

LICENSE = "MIT"

# Specify the filesystem types for the initramfs
IMAGE_FSTYPES = "cpio.gz"

inherit core-image

# Include systemd, busybox, bash, and shadow in the rootfs
IMAGE_INSTALL = "systemd busybox bash bash-completion shadow nfs-utils bbb-02-led-blink bbb-03-led-blink-nolibc"

# Add SSH support packages (using Dropbear for lighter footprint)
IMAGE_INSTALL:append = " dropbear"

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

# Fix shell prompt for bash and configure SSH
ROOTFS_POSTPROCESS_COMMAND += "fix_shell_prompt; configure_ssh; "

fix_shell_prompt() {
    # Set hostname
    echo "srk-device" > ${IMAGE_ROOTFS}/etc/hostname
    
    # Create /etc/profile for bash with proper prompt
    echo '#!/bin/bash' > ${IMAGE_ROOTFS}/etc/profile
    echo 'export PATH="/bin:/sbin:/usr/bin:/usr/sbin"' >> ${IMAGE_ROOTFS}/etc/profile
    echo 'export TERM=linux' >> ${IMAGE_ROOTFS}/etc/profile
    echo 'export PS1="\u@\h:\w\$ "' >> ${IMAGE_ROOTFS}/etc/profile
    echo '# Enable bash completion globally' >> ${IMAGE_ROOTFS}/etc/profile
    echo 'if [ -f /etc/bash_completion ]; then' >> ${IMAGE_ROOTFS}/etc/profile
    echo '    . /etc/bash_completion' >> ${IMAGE_ROOTFS}/etc/profile
    echo 'elif [ -f /usr/share/bash-completion/bash_completion ]; then' >> ${IMAGE_ROOTFS}/etc/profile
    echo '    . /usr/share/bash-completion/bash_completion' >> ${IMAGE_ROOTFS}/etc/profile
    echo 'fi' >> ${IMAGE_ROOTFS}/etc/profile
    
    chmod +x ${IMAGE_ROOTFS}/etc/profile
    
    # Set bash as default shell for root and srk users
    # Update /etc/passwd to use /bin/bash instead of /bin/sh
    sed -i 's|root:.*:/bin/sh|root:x:0:0:root:/root:/bin/bash|' ${IMAGE_ROOTFS}/etc/passwd
    
    # Create root directory and .bashrc for root
    mkdir -p ${IMAGE_ROOTFS}/root
    echo 'export PS1="\u@\h:\w\$ "' > ${IMAGE_ROOTFS}/root/.bashrc
    echo 'export PATH="/bin:/sbin:/usr/bin:/usr/sbin"' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo 'export TERM=linux' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo '# Enable bash completion' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo 'if [ -f /etc/bash_completion ]; then' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo '    . /etc/bash_completion' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo 'elif [ -f /usr/share/bash-completion/bash_completion ]; then' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo '    . /usr/share/bash-completion/bash_completion' >> ${IMAGE_ROOTFS}/root/.bashrc
    echo 'fi' >> ${IMAGE_ROOTFS}/root/.bashrc
    
    # Create home directory for srk user and setup .bashrc
    mkdir -p ${IMAGE_ROOTFS}/home/srk
    echo 'export PS1="\u@\h:\w\$ "' > ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo 'export PATH="/bin:/sbin:/usr/bin:/usr/sbin"' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo 'export TERM=linux' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo '# Enable bash completion' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo 'if [ -f /etc/bash_completion ]; then' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo '    . /etc/bash_completion' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo 'elif [ -f /usr/share/bash-completion/bash_completion ]; then' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo '    . /usr/share/bash-completion/bash_completion' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    echo 'fi' >> ${IMAGE_ROOTFS}/home/srk/.bashrc
    
    # Set proper ownership for srk home directory (will be applied at runtime)
    chown -R 1000:1000 ${IMAGE_ROOTFS}/home/srk 2>/dev/null || true
}

configure_ssh() {
    # Create SSH configuration directory for Dropbear
    mkdir -p ${IMAGE_ROOTFS}/etc/dropbear
    
    # Configure Dropbear SSH (lightweight SSH server)
    # Allow root login and password authentication
    mkdir -p ${IMAGE_ROOTFS}/etc/default
    echo 'DROPBEAR_EXTRA_ARGS="-w -g -B"' > ${IMAGE_ROOTFS}/etc/default/dropbear
    echo 'DROPBEAR_PORT=22' >> ${IMAGE_ROOTFS}/etc/default/dropbear
    
    # Create .ssh directories for users
    mkdir -p ${IMAGE_ROOTFS}/root/.ssh
    mkdir -p ${IMAGE_ROOTFS}/home/srk/.ssh
    
    chmod 700 ${IMAGE_ROOTFS}/root/.ssh
    chmod 700 ${IMAGE_ROOTFS}/home/srk/.ssh
    
    # Set ownership for srk user
    chown -R 1000:1000 ${IMAGE_ROOTFS}/home/srk/.ssh 2>/dev/null || true
    
    # Create a simple banner
    echo "Welcome to SRK Embedded Device" > ${IMAGE_ROOTFS}/etc/issue.net
    echo "SSH access enabled via Dropbear" >> ${IMAGE_ROOTFS}/etc/issue.net
    
    # Enable Dropbear service at boot
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants
    
    # Create Dropbear systemd service file
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/dropbear.service << 'EOF'
[Unit]
Description=Dropbear SSH server
After=syslog.target network.target
Requires=dropbear-keygen.service
After=dropbear-keygen.service

[Service]
Type=notify
ExecStart=/usr/sbin/dropbear -F -E
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Create Dropbear key generation service
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/dropbear-keygen.service << 'EOF'
[Unit]
Description=Generate Dropbear SSH keys
Before=dropbear.service
ConditionPathExists=!/etc/dropbear/dropbear_rsa_host_key

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'test -f /etc/dropbear/dropbear_rsa_host_key || /usr/bin/dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key -s 2048'
ExecStart=/bin/sh -c 'test -f /etc/dropbear/dropbear_dss_host_key || /usr/bin/dropbearkey -t dss -f /etc/dropbear/dropbear_dss_host_key'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    # Enable the services
    ln -sf ../dropbear-keygen.service ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/dropbear-keygen.service
    ln -sf ../dropbear.service ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/dropbear.service
}

# Enable essential systemd services
SYSTEMD_AUTO_ENABLE = "enable"
IMAGE_INSTALL:append = " systemd-serialgetty"
IMAGE_INSTALL:append = " kernel-modules"

# Set default systemd target
SYSTEMD_DEFAULT_TARGET = "multi-user.target"