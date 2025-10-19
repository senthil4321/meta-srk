# Core Image Tiny InitramFS SRK-2 with Bash and SSH

## Overview
This is a minimal Yocto/OpenEmbedded initramfs image for BeagleBone Black that includes:
- **Bash shell** with completion support
- **SSH server** (Dropbear) for remote access
- **systemd** init system
- **NFS root filesystem** support

## Image Details

### Recipe Information
- **Recipe Name**: `core-image-tiny-initramfs-srk-2-bash-ssh.bb`
- **Location**: `/home/srk2cob/project/poky/meta-srk/recipes-srk/images/`
- **Image Format**: `cpio.gz` (initramfs format)
- **Target Machine**: `beaglebone-yocto-srk`
- **Distro**: `srk-minimal-squashfs-distro`

### Build Information
- **Last Build Date**: October 19, 2025
- **Build System**: Yocto Project (Styhead)
- **Total Tasks**: 4371 (4350 from cache on clean rebuild)
- **Build Status**: ✅ Successful

## Features

### 1. User Authentication
- **Root User**: 
  - Username: `root`
  - Shell: `/bin/bash`
  - Home: `/root`
  - Password: Pre-configured (hashed)
  
- **SRK User**:
  - Username: `srk`
  - Shell: `/bin/bash`
  - Home: `/home/srk`
  - Password: Pre-configured (hashed)

### 2. SSH Access
- **Server**: Dropbear (lightweight SSH daemon)
- **Port**: 22
- **Authentication**: Password-based
- **Root Login**: Enabled
- **Status**: ✅ Fully operational for both users

### 3. Shell Configuration
- **Default Shell**: `/bin/bash`
- **Valid Shells** (defined in `/etc/shells`):
  - `/bin/sh`
  - `/bin/bash`
  - `/usr/bin/bash`
  
- **Bash Features**:
  - Custom PS1 prompt: `user@host:path$ `
  - PATH configured: `/bin:/sbin:/usr/bin:/usr/sbin`
  - TERM set to `linux`
  - `.bashrc` files for both root and srk users

### 4. Bash Completion
- **Status**: ✅ Installed
- **Location**: `/usr/share/bash-completion/completions/`
- **Available Completions**:
  - `ls` - File listing completion (922 bytes)
  - `cd` - Directory change completion (353 bytes)
- **Activation**: Automatic via `/etc/profile` and `.bashrc` files

### 5. System Services
- **Init System**: systemd
- **Enabled Services**:
  - `dropbear.service` - SSH server
  - `dbus.service` - D-Bus message bus
  - `systemd-serialgetty` - Serial console
  
- **Disabled Services**:
  - `systemd-logind.service` - Not required for minimal embedded system

## Network Configuration

### NFS Root Setup
- **NFS Server**: Raspberry Pi at `192.168.1.100`
- **NFS Export**: `/srv/nfs`
- **Target IP**: `192.168.1.200`
- **Mount**: Target boots and mounts root filesystem via NFS

### Deployment Script
Use the `03_copy_initramfs.sh` script to deploy the image:
```bash
./03_copy_initramfs.sh 2-bash-ssh beaglebone-yocto-srk
```

This extracts the `cpio.gz` image to `/srv/nfs/` on the Raspberry Pi.

## File Structure

### Important Directories
```
/
├── bin/                      # Essential binaries
├── sbin/                     # System binaries
├── usr/
│   ├── bin/                  # User binaries (including bash.bash)
│   ├── sbin/                 # System administration binaries
│   └── share/
│       └── bash-completion/
│           └── completions/  # Bash completion scripts
├── etc/
│   ├── shells               # Valid login shells
│   ├── profile              # System-wide bash profile
│   ├── hostname             # Set to "srk-device"
│   ├── dropbear/            # Dropbear SSH configuration
│   ├── pam.d/               # PAM configuration files
│   └── systemd/
│       └── system/          # systemd service configurations
├── root/                     # Root user home directory
│   └── .bashrc              # Root bash configuration
├── home/
│   └── srk/                 # SRK user home directory
│       └── .bashrc          # SRK bash configuration
├── run/                      # Runtime data
├── var/                      # Variable data
└── dev/                      # Device files
```

### Key Configuration Files

#### `/etc/shells`
```bash
# /etc/shells: valid login shells
/bin/sh
/bin/bash
/usr/bin/bash
```

#### `/etc/profile`
- Sets environment variables (PATH, TERM, PS1)
- Sources bash completion from `/etc/bash_completion` or `/usr/share/bash-completion/bash_completion`
- Applied system-wide for all bash sessions

#### `/etc/hostname`
```
srk-device
```

## Installed Packages

### Core Packages
- `systemd` - System and service manager
- `busybox` - Minimal Unix utilities
- `bash` - Bourne Again Shell
- `bash-completion` - Programmable completion for bash
- `shadow` - User and group management utilities
- `nfs-utils` - NFS client utilities

### Network & SSH
- `dropbear` - Lightweight SSH server

### Utilities
- `util-linux` - Essential Linux utilities
- `util-linux-mount` - Mount utilities for systemd

### Authentication
- `libpam` - Pluggable Authentication Modules
- `dbus` - D-Bus message bus system

### Custom Packages
- `bbb-02-led-blink` - BeagleBone Black LED blink example
- `bbb-03-led-blink-nolibc` - BeagleBone Black LED blink (no libc)

## Build Instructions

### Prerequisites
1. Yocto build environment set up
2. `meta-srk` layer added to `bblayers.conf`
3. Machine set to `beaglebone-yocto-srk` in `local.conf`

### Building the Image

#### Clean Build
```bash
cd /home/srk2cob/project/poky/build
bitbake -c cleansstate core-image-tiny-initramfs-srk-2-bash-ssh
bitbake core-image-tiny-initramfs-srk-2-bash-ssh
```

#### Regular Build
```bash
cd /home/srk2cob/project/poky/build
bitbake core-image-tiny-initramfs-srk-2-bash-ssh
```

### Build Output
- **Location**: `/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto-srk/`
- **Filename**: `core-image-tiny-initramfs-srk-2-bash-ssh-beaglebone-yocto-srk.rootfs.cpio.gz`
- **Size**: Approximately 173,547 blocks (extracted)

## Deployment

### Manual Deployment
1. Copy the image to NFS server:
```bash
scp tmp/deploy/images/beaglebone-yocto-srk/core-image-tiny-initramfs-srk-2-bash-ssh-beaglebone-yocto-srk.rootfs.cpio.gz pi@192.168.1.100:/tmp/
```

2. Extract on NFS server:
```bash
ssh pi@192.168.1.100 "sudo rm -rf /srv/nfs/* && cd /srv/nfs && sudo gunzip -c /tmp/core-image-tiny-initramfs-srk-2-bash-ssh-beaglebone-yocto-srk.rootfs.cpio.gz | sudo cpio -idmv"
```

### Using Deployment Script
```bash
cd /home/srk2cob/project/poky/meta-srk
./03_copy_initramfs.sh 2-bash-ssh beaglebone-yocto-srk
```

## Testing & Verification

### SSH Access Testing

#### Test Root Login
```bash
ssh root@192.168.1.200
```
Expected: Successful login with bash prompt

#### Test SRK User Login
```bash
ssh srk@192.168.1.200
```
Expected: Successful login with bash prompt

### Verification Commands

#### Check Shell Configuration
```bash
ssh srk@192.168.1.200 "cat /etc/shells"
```

#### Check Bash Completion
```bash
ssh srk@192.168.1.200 "ls /usr/share/bash-completion/completions/"
```

#### Check Running Services
```bash
ssh srk@192.168.1.200 "ps | grep dropbear"
```

#### Check System Status
```bash
ssh srk@192.168.1.200 "systemctl status"
```

## Serial Console Access

Use the `16_serial_command_monitor.sh` script to execute commands via serial console:

```bash
./16_serial_command_monitor.sh -c "command_here" -t 5
```

Example:
```bash
./16_serial_command_monitor.sh -c "ls -la /etc/shells" -t 5
```

## Troubleshooting

### Common Issues

#### 1. SSH Connection Refused
**Problem**: Cannot connect to SSH on port 22

**Solution**:
- Check if Dropbear is running: `ps | grep dropbear`
- Start manually if needed: `/usr/sbin/dropbear -F -E -w -g &`
- Verify network connectivity: `ping 192.168.1.200`

#### 2. User Has Invalid Shell
**Problem**: "User 'xxx' has invalid shell, rejected"

**Solution**:
- Verify `/etc/shells` contains `/bin/bash`
- Check user's shell in `/etc/passwd`
- This issue has been fixed in current build

#### 3. Bash Completion Not Working
**Problem**: TAB completion doesn't work

**Solution**:
- Check if bash-completion is installed
- Verify `/etc/profile` sources completion scripts
- Ensure completion scripts exist in `/usr/share/bash-completion/completions/`
- Log out and log back in to reload profile

#### 4. systemd-logind Failures
**Problem**: systemd-logind service fails to start

**Status**: Service disabled - not required for this minimal system
**Impact**: None - SSH and core functionality work without it

### Host Key Changed Warning
If you rebuild and deploy a new image, you may see:
```
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

**Solution**:
```bash
ssh-keygen -f "/home/srk2cob/.ssh/known_hosts" -R "192.168.1.200"
```

## Technical Notes

### systemd Configuration
- Default target: `multi-user.target`
- Auto-enable policy: enabled
- Journal location: `/var/volatile/log/journal`
- Machine ID: Generated during build

### PAM Configuration
- System authentication via `pam_unix.so`
- Password encryption: SHA512
- Session management with optional `pam_systemd.so`

### Security Considerations
- **Root login via SSH**: Enabled (for development/testing)
- **Password authentication**: Enabled
- **Production use**: Consider disabling root SSH and using SSH keys

### Bash Binary Structure
- **Actual binary**: `/usr/bin/bash.bash`
- **Symlink**: `/usr/bin/bash` → `/usr/bin/bash.bash`
- **Size**: 1,137,184 bytes

## Customization

### Adding More Bash Completions
Edit the `install_bash_completions()` function in the recipe to add more completion scripts.

### Changing Passwords
Modify the `PASSWD` and `SRKPWD` variables in the recipe:
```bash
# Generate new password hash
mkpasswd -m sha-512
```

### Adding More Users
Extend `EXTRA_USERS_PARAMS` in the recipe:
```bash
EXTRA_USERS_PARAMS = "\
    usermod -p '${PASSWD}' root; \
    useradd -p '${SRKPWD}' -s /bin/bash srk; \
    useradd -p '${NEWPWD}' -s /bin/bash newuser; \
    "
```

### Enabling More Services
Add to `IMAGE_INSTALL` and enable in systemd:
```bash
IMAGE_INSTALL:append = " your-package"
```

## Maintenance

### Updating the Image
1. Modify the recipe as needed
2. Clean build: `bitbake -c cleansstate core-image-tiny-initramfs-srk-2-bash-ssh`
3. Build: `bitbake core-image-tiny-initramfs-srk-2-bash-ssh`
4. Deploy: `./03_copy_initramfs.sh 2-bash-ssh beaglebone-yocto-srk`
5. Reboot target or manually start services

### Version Control
This recipe is maintained in the `meta-srk` layer:
- **Repository**: senthil4321/meta-srk
- **Branch**: main
- **Last Updated**: October 19, 2025

## Success Criteria

All objectives have been met:
- ✅ SSH connectivity working for root and srk users
- ✅ Bash shell with proper configuration
- ✅ Bash completion infrastructure installed
- ✅ Shell validation fixed (/etc/shells configured)
- ✅ System boots successfully from NFS
- ✅ Dropbear SSH server runs automatically
- ✅ User authentication working correctly
- ✅ Clean builds complete without errors

## References

### Related Documentation
- Yocto Project Documentation: https://docs.yoctoproject.org/
- Dropbear SSH: https://matt.ucc.asn.au/dropbear/dropbear.html
- systemd Documentation: https://www.freedesktop.org/software/systemd/man/
- Bash Completion: https://github.com/scop/bash-completion

### Related Files
- `03_copy_initramfs.sh` - Deployment script
- `16_serial_command_monitor.sh` - Serial console command executor
- `recipes-srk/images/core-image-tiny-initramfs-srk-2-bash-ssh.bb` - Main recipe

### Layer Configuration
- `conf/layer.conf` - Layer configuration
- `conf/machine/beaglebone-yocto-srk.conf` - Machine configuration
- `conf/distro/srk-distro.conf` - Distribution configuration

## Contact & Support
For issues or questions related to this image, refer to the meta-srk repository or consult the Yocto Project community.

---
**Document Version**: 1.0  
**Last Updated**: October 19, 2025  
**Status**: Production Ready ✅
