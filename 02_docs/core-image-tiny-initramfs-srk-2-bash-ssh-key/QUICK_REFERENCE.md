# Quick Reference - SSH Key Authentication

## Quick Start

### Connect Without Password

```bash
# Root user
ssh root@192.168.1.200

# SRK user
ssh srk@192.168.1.200
```

No password needed! ✅

## Build and Deploy

### Build Image

```bash
cd /home/srk2cob/project/poky/build
bitbake core-image-tiny-initramfs-srk-2-bash-ssh-key
```

### Deploy to NFS

```bash
cd /home/srk2cob/project/poky/meta-srk
./03_copy_initramfs.sh 2-bash-ssh-key srk
```

## Verify Authentication

### Test Key-Based Auth

```bash
# Force key authentication
ssh -o PreferredAuthentications=publickey root@192.168.1.200 "whoami"
# Output: root ✅

ssh -o PreferredAuthentications=publickey srk@192.168.1.200 "whoami"
# Output: srk ✅
```

### Test Password Auth (Fallback)

```bash
# Force password authentication
ssh -o PreferredAuthentications=password root@192.168.1.200
# Prompts for password, then logs in ✅
```

## Manage Keys

### View Authorized Keys

```bash
# Root's keys
ssh root@192.168.1.200 "cat /root/.ssh/authorized_keys"

# SRK's keys
ssh root@192.168.1.200 "cat /home/srk/.ssh/authorized_keys"
```

### Add New Key

```bash
# Add key for root
cat ~/.ssh/id_rsa.pub | ssh root@192.168.1.200 \
  "cat >> /root/.ssh/authorized_keys"

# Add key for srk
cat ~/.ssh/id_rsa.pub | ssh root@192.168.1.200 \
  "cat >> /home/srk/.ssh/authorized_keys && chown srk:srk /home/srk/.ssh/authorized_keys"
```

### Replace Key

```bash
# Replace root's keys
cat ~/.ssh/id_rsa.pub | ssh pi@192.168.1.100 \
  "sudo tee /srv/nfs/root/.ssh/authorized_keys > /dev/null"

# Replace srk's keys
cat ~/.ssh/id_rsa.pub | ssh pi@192.168.1.100 \
  "sudo tee /srv/nfs/home/srk/.ssh/authorized_keys > /dev/null && \
   sudo chown 1000:1000 /srv/nfs/home/srk/.ssh/authorized_keys"
```

### Remove All Keys (Reset to Password-Only)

```bash
# Remove root's keys
ssh root@192.168.1.200 "rm /root/.ssh/authorized_keys"

# Remove srk's keys
ssh root@192.168.1.200 "rm /home/srk/.ssh/authorized_keys"
```

## Troubleshooting

### Key Auth Not Working

```bash
# Check permissions
ssh root@192.168.1.200 "ls -la /root/.ssh/"
# Should show: drwx------ (700) for .ssh
# Should show: -rw------- (600) for authorized_keys

# Fix permissions
ssh root@192.168.1.200 "chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys"
```

### Verify Key Format

```bash
# Key should be single line, starts with ssh-rsa
ssh root@192.168.1.200 "head -n 1 /root/.ssh/authorized_keys | cut -c 1-50"
# Should show: ssh-rsa AAAAB3NzaC...
```

### Debug SSH Connection

```bash
# Verbose SSH to see what's happening
ssh -vvv root@192.168.1.200 2>&1 | grep -E "(Offering|Authentication|publickey)"
```

### Check Dropbear Status

```bash
# Via serial console
./16_serial_command_monitor.sh -c "ps | grep dropbear" -t 5
```

## Network Info

- **Build Host**: `srk2cob-vm`
- **NFS Server**: `pi@192.168.1.100` (Raspberry Pi)
- **Target Device**: `192.168.1.200` (BeagleBone Black)
- **SSH Port**: 22
- **NFS Path**: `/srv/nfs`

## Key Information

- **Type**: RSA 2048-bit
- **Location**: `~/.ssh/id_rsa.pub` (build host)
- **Installed On**: Root and SRK users
- **Format**: OpenSSH public key

## Common Commands

### SSH Config (Optional)

Add to `~/.ssh/config`:

```text
Host beaglebone
    HostName 192.168.1.200
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no

Host beaglebone-srk
    HostName 192.168.1.200
    User srk
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
```

Then use:

```bash
ssh beaglebone       # Connects as root
ssh beaglebone-srk   # Connects as srk
```

### SSH Agent (Avoid Passphrase Prompts)

```bash
# Start agent
eval $(ssh-agent)

# Add key
ssh-add ~/.ssh/id_rsa

# Now SSH without passphrase
ssh root@192.168.1.200
```

### Copy Files

```bash
# Copy to target
scp file.txt root@192.168.1.200:/tmp/

# Copy from target
scp root@192.168.1.200:/var/log/messages ./

# Recursive copy
scp -r folder/ root@192.168.1.200:/home/
```

## Recipe Location

```text
/home/srk2cob/project/poky/meta-srk/recipes-srk/images/
└── core-image-tiny-initramfs-srk-2-bash-ssh-key.bb
```

## Documentation

- **Full Guide**: [README.md](./README.md)
- **Summary**: [SUMMARY.md](./SUMMARY.md)
- **Base Image**: [../core-image-tiny-initramfs-srk-2-bash-ssh/](../core-image-tiny-initramfs-srk-2-bash-ssh/)

## Status

- ✅ Key-based authentication working
- ✅ Password authentication available
- ✅ Both users supported
- ✅ Recipe created
- ✅ Documentation complete
- ✅ Tested and verified

---

**Quick Reference Version**: 1.0  
**Last Updated**: October 19, 2025
