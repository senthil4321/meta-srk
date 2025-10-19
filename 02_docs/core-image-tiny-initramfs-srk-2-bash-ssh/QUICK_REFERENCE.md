# Build and Deployment Quick Reference

## Quick Start

### Build Commands
```bash
# Navigate to build directory
cd /home/srk2cob/project/poky/build

# Clean build (recommended after recipe changes)
bitbake -c cleansstate core-image-tiny-initramfs-srk-2-bash-ssh
bitbake core-image-tiny-initramfs-srk-2-bash-ssh

# Regular build
bitbake core-image-tiny-initramfs-srk-2-bash-ssh
```

### Deploy to NFS
```bash
# Navigate to meta-srk directory
cd /home/srk2cob/project/poky/meta-srk

# Deploy using script
./03_copy_initramfs.sh 2-bash-ssh beaglebone-yocto-srk
```

### SSH Access
```bash
# Login as root
ssh root@192.168.1.200

# Login as srk user
ssh srk@192.168.1.200
```

### Serial Console
```bash
# Execute command via serial
./16_serial_command_monitor.sh -c "your_command" -t 5

# Examples
./16_serial_command_monitor.sh -c "ls -la" -t 5
./16_serial_command_monitor.sh -c "cat /etc/shells" -t 5
./16_serial_command_monitor.sh -c "systemctl status" -t 10
```

## Network Configuration

- **NFS Server**: 192.168.1.100 (Raspberry Pi)
- **NFS Path**: /srv/nfs
- **Target Device**: 192.168.1.200 (BeagleBone Black)
- **SSH Port**: 22

## Verification Commands

### Check SSH is working
```bash
ssh -o StrictHostKeyChecking=no srk@192.168.1.200 "echo 'SSH works!' && whoami"
```

### Check bash completion files
```bash
ssh srk@192.168.1.200 "ls -lh /usr/share/bash-completion/completions/"
```

### Check shell configuration
```bash
ssh srk@192.168.1.200 "cat /etc/shells"
```

### Check Dropbear status
```bash
ssh srk@192.168.1.200 "ps | grep dropbear"
```

## Common Operations

### Remove old SSH host key
```bash
ssh-keygen -f "/home/srk2cob/.ssh/known_hosts" -R "192.168.1.200"
```

### View build output location
```bash
ls -lh /home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto-srk/
```

### Check NFS deployment
```bash
ssh pi@192.168.1.100 "ls -lh /srv/nfs/"
```

## Troubleshooting

### Cannot connect via SSH
```bash
# Check if target is reachable
ping 192.168.1.200

# Check Dropbear via serial console
./16_serial_command_monitor.sh -c "ps | grep dropbear" -t 5

# Start Dropbear manually if needed
./16_serial_command_monitor.sh -c "/usr/sbin/dropbear -F -E -w -g &" -t 5
```

### Tab completion not working
```bash
# Verify completion files exist
ssh srk@192.168.1.200 "ls /usr/share/bash-completion/completions/"

# Check profile sources completion
ssh srk@192.168.1.200 "cat /etc/profile | grep completion"

# Log out and back in to reload
```

## Build Times

- **Clean build**: ~10-15 minutes (depends on system)
- **Incremental build**: ~1-2 minutes
- **Cache hit rate**: ~99% on clean rebuild

## Output Files

### Image Location
```
/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto-srk/
└── core-image-tiny-initramfs-srk-2-bash-ssh-beaglebone-yocto-srk.rootfs.cpio.gz
```

### Extracted Size
- **Blocks**: ~173,547 blocks
- **Files**: Thousands of files and directories

---
**Quick Reference Version**: 1.0  
**Last Updated**: October 19, 2025
