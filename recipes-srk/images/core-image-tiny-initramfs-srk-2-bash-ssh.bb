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
# Add util-linux for login utilities and systemd support
IMAGE_INSTALL:append = " util-linux"
# Add packages needed for systemd-logind to work properly
IMAGE_INSTALL:append = " systemd-serialgetty"
# Add dbus for proper systemd communication
IMAGE_INSTALL:append = " dbus"
# Add PAM for proper authentication
IMAGE_INSTALL:append = " libpam"
# Add cgroup utilities for systemd-logind resource management
IMAGE_INSTALL:append = " util-linux-mount"

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
ROOTFS_POSTPROCESS_COMMAND += "fix_shell_prompt; configure_ssh; install_bash_completions; fix_systemd_services; "

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
    # Create /etc/shells with valid login shells
    cat > ${IMAGE_ROOTFS}/etc/shells << 'EOF'
# /etc/shells: valid login shells
/bin/sh
/bin/bash
/usr/bin/bash
EOF
    
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
    echo 'DROPBEAR_EXTRA_ARGS=""' > ${IMAGE_ROOTFS}/etc/default/dropbear
    echo 'DROPBEAR_PORT=22' >> ${IMAGE_ROOTFS}/etc/default/dropbear
    
    # Create .ssh directories for users
    mkdir -p ${IMAGE_ROOTFS}/root/.ssh
    mkdir -p ${IMAGE_ROOTFS}/home/srk/.ssh
    
    chmod 700 ${IMAGE_ROOTFS}/root/.ssh
    chmod 700 ${IMAGE_ROOTFS}/home/srk/.ssh
    
    # Set ownership for srk user
    chown -R 1000:1000 ${IMAGE_ROOTFS}/home/srk/.ssh 2>/dev/null || true
    
    # Create runtime directories needed by systemd-logind and proper permissions
    mkdir -p ${IMAGE_ROOTFS}/run/systemd/users
    mkdir -p ${IMAGE_ROOTFS}/run/systemd/sessions
    mkdir -p ${IMAGE_ROOTFS}/run/systemd/seats
    mkdir -p ${IMAGE_ROOTFS}/var/lib/systemd/linger
    mkdir -p ${IMAGE_ROOTFS}/var/lib/systemd/pstore
    mkdir -p ${IMAGE_ROOTFS}/run/user
    mkdir -p ${IMAGE_ROOTFS}/run/lock
    
    # Create proper device directory structure for systemd
    mkdir -p ${IMAGE_ROOTFS}/dev/pts
    mkdir -p ${IMAGE_ROOTFS}/dev/shm
    
    # Ensure proper permissions for runtime directories
    chmod 755 ${IMAGE_ROOTFS}/run/systemd
    chmod 755 ${IMAGE_ROOTFS}/run/user
    chmod 1777 ${IMAGE_ROOTFS}/run/lock
    
    # Create a simple banner
    echo "Welcome to SRK Embedded Device" > ${IMAGE_ROOTFS}/etc/issue.net
    echo "SSH access enabled via Dropbear" >> ${IMAGE_ROOTFS}/etc/issue.net
    
    # Create basic PAM configuration for SSH authentication
    mkdir -p ${IMAGE_ROOTFS}/etc/pam.d
    cat > ${IMAGE_ROOTFS}/etc/pam.d/dropbear << 'EOF'
#%PAM-1.0
auth       required     pam_unix.so
account    required     pam_unix.so
password   required     pam_unix.so
session    required     pam_unix.so
session    optional     pam_systemd.so
EOF

    # Create common-auth for system authentication
    cat > ${IMAGE_ROOTFS}/etc/pam.d/common-auth << 'EOF'
#%PAM-1.0
auth    [success=1 default=ignore]      pam_unix.so nullok_secure
auth    requisite                       pam_deny.so
auth    required                        pam_permit.so
EOF

    # Create common-account for account management
    cat > ${IMAGE_ROOTFS}/etc/pam.d/common-account << 'EOF'
#%PAM-1.0
account [success=1 new_authtok_reqd=done default=ignore] pam_unix.so
account requisite                       pam_deny.so
account required                        pam_permit.so
EOF

    # Create common-password for password management
    cat > ${IMAGE_ROOTFS}/etc/pam.d/common-password << 'EOF'
#%PAM-1.0
password [success=1 default=ignore]     pam_unix.so obscure sha512
password requisite                      pam_deny.so
password required                       pam_permit.so
EOF

    # Create common-session for session management
    cat > ${IMAGE_ROOTFS}/etc/pam.d/common-session << 'EOF'
#%PAM-1.0
session [default=1]                     pam_permit.so
session requisite                       pam_deny.so
session required                        pam_permit.so
session optional                        pam_systemd.so
EOF

    # Create system-auth PAM file
    cat > ${IMAGE_ROOTFS}/etc/pam.d/system-auth << 'EOF'
#%PAM-1.0
auth       include      common-auth
account    include      common-account
password   include      common-password
session    include      common-session
EOF

    # Fix Dropbear PAM configuration to use proper includes
    cat > ${IMAGE_ROOTFS}/etc/pam.d/dropbear << 'EOF'
#%PAM-1.0
auth       include      system-auth
account    include      system-auth
password   include      system-auth
session    include      system-auth
EOF
    
    # Enable Dropbear service at boot
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants
    
    # Create a simple startup script that starts dropbear directly
    mkdir -p ${IMAGE_ROOTFS}/usr/local/bin
    cat > ${IMAGE_ROOTFS}/usr/local/bin/start-sshd.sh << 'EOF'
#!/bin/bash
# Start SSH server directly (bypass systemd issues)

# Generate Dropbear SSH keys if they don't exist
if [ ! -f /etc/dropbear/dropbear_rsa_host_key ]; then
    echo "Generating Dropbear RSA host key..."
    /usr/bin/dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key -s 2048 2>/dev/null
fi

if [ ! -f /etc/dropbear/dropbear_dss_host_key ]; then
    echo "Generating Dropbear DSS host key..."
    /usr/bin/dropbearkey -t dss -f /etc/dropbear/dropbear_dss_host_key 2>/dev/null
fi

# Start dropbear in background
echo "Starting Dropbear SSH server..."
/usr/sbin/dropbear -F -E -w -g &
EOF
    chmod +x ${IMAGE_ROOTFS}/usr/local/bin/start-sshd.sh

    # Create Dropbear systemd service file (simplified)
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/dropbear.service << 'EOF'
[Unit]
Description=Dropbear SSH server
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/start-sshd.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd-logind configuration to fix login management
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/logind.conf.d
    cat > ${IMAGE_ROOTFS}/etc/systemd/logind.conf.d/10-srk.conf << 'EOF'
[Login]
NAutoVTs=0
ReserveVT=0
KillUserProcesses=no
KillOnlyUsers=
KillExcludeUsers=root
InhibitDelayMaxSec=5
HandlePowerKey=ignore
HandleSuspendKey=ignore
HandleHibernateKey=ignore
HandleLidSwitch=ignore
IdleAction=ignore
IdleActionSec=30min
RuntimeDirectorySize=10%
RemoveIPC=no
UserTasksMax=infinity
InhibitorsMax=8192
SessionsMax=8192
EOF

    # Ensure systemd-logind service is properly enabled
    # The service file is provided by systemd package, just ensure it's enabled
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/dbus-org.freedesktop.login1.service.wants
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants
    
    # Create machine-id for systemd (required for logind)
    systemd-machine-id-setup --root=${IMAGE_ROOTFS} || echo "dummy-machine-id-$(date +%s)" > ${IMAGE_ROOTFS}/etc/machine-id

    # Enable D-Bus (required for systemd-logind)
    ln -sf ../dbus.service ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/dbus.service 2>/dev/null || true
    
    # Enable systemd-tmpfiles to create runtime directories
    ln -sf ../systemd-tmpfiles-setup.service ${IMAGE_ROOTFS}/etc/systemd/system/sysinit.target.wants/systemd-tmpfiles-setup.service 2>/dev/null || true
    
    # Create an early setup service for systemd-logind directories
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/systemd-logind-dirs.service << 'EOF'
[Unit]
Description=Create systemd-logind runtime directories
DefaultDependencies=false
Before=systemd-logind.service
Before=sysinit.target

[Service]
Type=oneshot
ExecStart=/bin/mkdir -p /run/systemd/seats
ExecStart=/bin/mkdir -p /run/systemd/users
ExecStart=/bin/mkdir -p /run/systemd/sessions
ExecStart=/bin/mkdir -p /run/user
ExecStart=/bin/chmod 755 /run/systemd
ExecStart=/bin/chmod 755 /run/user
RemainAfterExit=yes

[Install]
WantedBy=sysinit.target
EOF

    # Enable the early setup service
    ln -sf ../systemd-logind-dirs.service ${IMAGE_ROOTFS}/etc/systemd/system/sysinit.target.wants/systemd-logind-dirs.service
    
    # Create simple environment for systemd-logind to work
    # Create utmp/wtmp files for login tracking
    touch ${IMAGE_ROOTFS}/var/log/wtmp
    touch ${IMAGE_ROOTFS}/var/log/btmp
    touch ${IMAGE_ROOTFS}/var/run/utmp
    chmod 664 ${IMAGE_ROOTFS}/var/log/wtmp
    chmod 600 ${IMAGE_ROOTFS}/var/log/btmp
    chmod 664 ${IMAGE_ROOTFS}/var/run/utmp
    
    # Create additional required directories and files for systemd-logind
    mkdir -p ${IMAGE_ROOTFS}/var/lib/systemd/linger
    mkdir -p ${IMAGE_ROOTFS}/var/lib/systemd/pstore
    mkdir -p ${IMAGE_ROOTFS}/run/systemd/seats
    mkdir -p ${IMAGE_ROOTFS}/run/systemd/users
    mkdir -p ${IMAGE_ROOTFS}/run/systemd/sessions
    mkdir -p ${IMAGE_ROOTFS}/run/user
    mkdir -p ${IMAGE_ROOTFS}/sys/fs/cgroup/systemd
    
    # Create systemd-logind required files
    touch ${IMAGE_ROOTFS}/var/lib/systemd/linger/.keep
    touch ${IMAGE_ROOTFS}/run/systemd/seats/.keep
    touch ${IMAGE_ROOTFS}/run/systemd/users/.keep
    touch ${IMAGE_ROOTFS}/run/systemd/sessions/.keep
    
    # Ensure proper permissions for systemd directories
    chmod 755 ${IMAGE_ROOTFS}/run/systemd
    chmod 755 ${IMAGE_ROOTFS}/var/lib/systemd
    chmod 755 ${IMAGE_ROOTFS}/run/user
    
    # Create systemd override directory and configuration
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/systemd-logind.service.d
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/systemd-logind.service.d/override.conf << 'EOF'
[Unit]
# Completely clear all conditions to bypass problematic checks
ConditionPathExists=
ConditionPathIsDirectory=
ConditionDirectoryNotEmpty=
ConditionVirtualization=
ConditionCapability=
# Remove problematic dependencies
After=dbus.service
Wants=dbus.service

[Service]
# Create all required directories before starting the service with error tolerance
ExecStartPre=-/bin/mkdir -p /run/systemd/seats
ExecStartPre=-/bin/mkdir -p /run/systemd/users
ExecStartPre=-/bin/mkdir -p /run/systemd/sessions
ExecStartPre=-/bin/mkdir -p /run/user
ExecStartPre=-/bin/mkdir -p /var/lib/systemd/linger
ExecStartPre=-/bin/mkdir -p /var/lib/systemd/pstore
ExecStartPre=-/bin/mkdir -p /sys/fs/cgroup/systemd
ExecStartPre=-/bin/chmod 755 /run/systemd
ExecStartPre=-/bin/chmod 755 /run/user
ExecStartPre=-/bin/chmod 755 /var/lib/systemd
# Reduce security restrictions for embedded environment
PrivateDevices=no
ProtectSystem=no
ProtectHome=no
RestrictRealtime=no
SystemCallFilter=
MemoryDenyWriteExecute=no
LockPersonality=no
RestrictNamespaces=no
# Increase resource limits
TasksMax=infinity
DefaultTasksMax=infinity
# Set restart policy
Restart=no
EOF

    # Create a helper service to prepare systemd-logind environment
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/prepare-systemd-logind.service << 'EOF'
[Unit]
Description=Prepare systemd-logind environment
Before=systemd-logind.service
DefaultDependencies=no

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'mkdir -p /run/systemd/{seats,users,sessions} /run/user /var/lib/systemd/{linger,pstore} /sys/fs/cgroup/systemd && chmod 755 /run/systemd /run/user /var/lib/systemd'

[Install]
WantedBy=multi-user.target
EOF

    # Enable systemd-logind service
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants
    ln -sf /usr/lib/systemd/system/systemd-logind.service ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/systemd-logind.service
    ln -sf /etc/systemd/system/prepare-systemd-logind.service ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/prepare-systemd-logind.service
    
    # Create systemd preset to ensure service is enabled
    mkdir -p ${IMAGE_ROOTFS}/usr/lib/systemd/system-preset
    cat > ${IMAGE_ROOTFS}/usr/lib/systemd/system-preset/90-systemd-logind-srk.preset << 'EOF'
# Enable systemd-logind for SSH authentication
enable systemd-logind.service
enable dbus.service
EOF

    # Create tmpfiles configuration for systemd-logind
    mkdir -p ${IMAGE_ROOTFS}/usr/lib/tmpfiles.d
    cat > ${IMAGE_ROOTFS}/usr/lib/tmpfiles.d/systemd-logind-srk.conf << 'EOF'
# Runtime directories for systemd-logind
d /run/systemd/seats 0755 root root -
d /run/systemd/users 0755 root root -
d /run/systemd/sessions 0755 root root -
d /run/user 0755 root root -
d /var/lib/systemd/linger 0755 root root -

# Login tracking files
f /var/log/wtmp 0664 root utmp -
f /var/log/btmp 0600 root utmp -
f /run/utmp 0664 root utmp -
EOF

    # Enable the services
    ln -sf ../dropbear.service ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/dropbear.service
}

install_bash_completions() {
    # Install basic bash completion scripts for common commands
    mkdir -p ${IMAGE_ROOTFS}/usr/share/bash-completion/completions
    
    # Create ls completion
    cat > ${IMAGE_ROOTFS}/usr/share/bash-completion/completions/ls << 'EOF'
# ls(1) completion

_ls()
{
    local cur prev words cword
    _init_completion || return

    case $prev in
        --help|--version)
            return
            ;;
        --color)
            COMPREPLY=( $( compgen -W 'always never auto' -- "$cur" ) )
            return
            ;;
        --sort)
            COMPREPLY=( $( compgen -W 'none time size extension version' -- "$cur" ) )
            return
            ;;
        --time)
            COMPREPLY=( $( compgen -W 'atime access mtime modify ctime status' -- "$cur" ) )
            return
            ;;
        --format)
            COMPREPLY=( $( compgen -W 'verbose long commasep horizontal across vertical single-column' -- "$cur" ) )
            return
            ;;
    esac

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $( compgen -W '$( _parse_help "$1" --help )' -- "$cur" ) )
        return
    fi

    _filedir
} &&
complete -F _ls ls
EOF

    # Create cd completion
    cat > ${IMAGE_ROOTFS}/usr/share/bash-completion/completions/cd << 'EOF'
# cd(1) completion

_cd()
{
    local cur prev words cword
    _init_completion || return

    case $prev in
        --help|--version)
            return
            ;;
    esac

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $( compgen -W '$( _parse_help "$1" --help )' -- "$cur" ) )
        return
    fi

    _filedir -d
} &&
complete -F _cd cd
EOF

    # Set proper permissions
    chmod 644 ${IMAGE_ROOTFS}/usr/share/bash-completion/completions/ls
    chmod 644 ${IMAGE_ROOTFS}/usr/share/bash-completion/completions/cd
}

fix_systemd_services() {
    # Fix systemd journal permissions
    mkdir -p ${IMAGE_ROOTFS}/var/volatile/log/journal
    chmod 2755 ${IMAGE_ROOTFS}/var/volatile/log/journal
    chown root:systemd-journal ${IMAGE_ROOTFS}/var/volatile/log/journal 2>/dev/null || true
    
    # Simplify systemd-logind override
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/systemd-logind.service.d
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/systemd-logind.service.d/override.conf << 'EOF'
[Unit]
ConditionPathExists=
After=dbus.service
Wants=dbus.service

[Service]
ExecStartPre=-/bin/mkdir -p /run/systemd/seats
ExecStartPre=-/bin/mkdir -p /run/systemd/users  
ExecStartPre=-/bin/mkdir -p /run/systemd/sessions
ExecStartPre=-/bin/mkdir -p /run/user
ExecStartPre=-/bin/chmod 755 /run/systemd
ExecStartPre=-/bin/chmod 755 /run/user
Restart=always
RestartSec=5
EOF

    # Enable D-Bus service
    ln -sf /usr/lib/systemd/system/dbus.service ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/dbus.service
}

# Enable essential systemd services
SYSTEMD_AUTO_ENABLE = "enable"
IMAGE_INSTALL:append = " systemd-serialgetty"
IMAGE_INSTALL:append = " kernel-modules"

# Set default systemd target
SYSTEMD_DEFAULT_TARGET = "multi-user.target"