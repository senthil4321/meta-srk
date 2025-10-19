# Core Image Tiny InitramFS SRK-2 with Bash and SSH Key Authentication

## Overview

This is an enhanced version of the minimal Yocto/OpenEmbedded initramfs image for BeagleBone Black that includes:

- **Bash shell** with completion support
- **SSH server** (Dropbear) for remote access
- **Dual authentication**: Password + SSH key-based authentication
- **systemd** init system
- **NFS root filesystem** support

## Key Differences from base image

| Feature | base (ssh) | key version |
|---------|------------|-------------|
| Password Auth | ✅ Yes | ✅ Yes |
| SSH Key Auth | ❌ No | ✅ Yes |
| authorized_keys | ❌ Not installed | ✅ Pre-installed |
| Convenience | Password required | Passwordless login |

## Image Details

### Recipe Information

- **Recipe Name**: `core-image-tiny-initramfs-srk-2-bash-ssh-key.bb`
- **Location**: `/home/srk2cob/project/poky/meta-srk/recipes-srk/images/`
- **Based On**: `core-image-tiny-initramfs-srk-2-bash-ssh.bb`
- **Image Format**: `cpio.gz` (initramfs format)
- **Target Machine**: `beaglebone-yocto-srk`

### SSH Key Configuration

The image comes pre-configured with SSH public keys for passwordless authentication:

- **Key Type**: RSA 2048-bit
- **Source**: Build host's `~/.ssh/id_rsa.pub`
- **Installed For**: root and srk users
- **Fallback**: Password authentication still available

## Build Instructions

### Build the Image

```bash
cd /home/srk2cob/project/poky/build
bitbake core-image-tiny-initramfs-srk-2-bash-ssh-key
```

### Deploy to NFS

```bash
cd /home/srk2cob/project/poky/meta-srk
./03_copy_initramfs.sh 2-bash-ssh-key beaglebone-yocto-srk
```

## SSH Access

### Key-based Authentication (Passwordless)

```bash
# Login as root (no password needed)
ssh root@192.168.1.200

# Login as srk (no password needed)
ssh srk@192.168.1.200
```

### Password Authentication (Fallback)

If key authentication fails or is not available:

```bash
# Login as root with password
ssh root@192.168.1.200
# Password: root

# Login as srk with password
ssh srk@192.168.1.200
# Password: srk
```

## Customizing SSH Keys

### Using Your Own SSH Key

To use a different SSH public key:

1. Open the recipe file:
   ```bash
   vim /home/srk2cob/project/poky/meta-srk/recipes-srk/images/core-image-tiny-initramfs-srk-2-bash-ssh-key.bb
   ```

2. Find the `install_ssh_keys()` function

3. Replace the `SSH_PUBLIC_KEY` variable value with your public key:
   ```bash
   SSH_PUBLIC_KEY="ssh-rsa YOUR_PUBLIC_KEY_HERE your_email@your_host"
   ```

4. Rebuild the image

### Adding Multiple Keys

To add multiple authorized keys, modify the function to append instead of overwrite:

```bash
echo "${SSH_PUBLIC_KEY_1}" >> ${IMAGE_ROOTFS}/root/.ssh/authorized_keys
echo "${SSH_PUBLIC_KEY_2}" >> ${IMAGE_ROOTFS}/root/.ssh/authorized_keys
```

### Runtime SSH Key Management

You can also add/remove keys on the running system:

```bash
# Add a new key to root
ssh root@192.168.1.200 "echo 'ssh-rsa YOUR_KEY...' >> /root/.ssh/authorized_keys"

# View authorized keys
ssh root@192.168.1.200 "cat /root/.ssh/authorized_keys"

# Remove all keys (reset to password-only)
ssh root@192.168.1.200 "rm /root/.ssh/authorized_keys"
```

## Security Considerations

### Advantages of Key-based Authentication

- **No password transmission** over network
- **Stronger authentication** (2048-bit RSA keys)
- **Convenient** for automation and scripts
- **Audit trail** through key fingerprints
- **Revocable** without changing passwords

### Best Practices

1. **Protect Private Keys**: Never share your private key (`~/.ssh/id_rsa`)
2. **Use Strong Passphrases**: Protect private keys with passphrases
3. **Limit Key Distribution**: Only install keys on trusted systems
4. **Regular Key Rotation**: Periodically update SSH keys
5. **Disable Root Password Login** (for production):
   - Remove password from root account
   - Keep key-based auth only

### Production Hardening

For production deployments, consider:

```bash
# Disable password authentication in Dropbear
# Modify configure_ssh() in recipe to add:
echo 'DROPBEAR_EXTRA_ARGS="-s"' > ${IMAGE_ROOTFS}/etc/default/dropbear

# This disables password auth, allowing only key-based
```

## Testing

### Verify Key-based Authentication

```bash
# Force key-based auth (will fail if keys not working)
ssh -o PreferredAuthentications=publickey root@192.168.1.200 "whoami"
# Expected output: root

ssh -o PreferredAuthentications=publickey srk@192.168.1.200 "whoami"
# Expected output: srk
```

### Verify Password Authentication Still Works

```bash
# Force password auth
ssh -o PreferredAuthentications=password root@192.168.1.200 "whoami"
# Prompts for password, then outputs: root
```

### Check Authorized Keys

```bash
# View root's authorized keys
ssh root@192.168.1.200 "cat /root/.ssh/authorized_keys"

# View srk's authorized keys
ssh root@192.168.1.200 "cat /home/srk/.ssh/authorized_keys"
```

### Verify File Permissions

```bash
# Check .ssh directory permissions
ssh root@192.168.1.200 "ls -la /root/.ssh/"
# Should show: drwx------ (700)

# Check authorized_keys permissions
ssh root@192.168.1.200 "ls -l /root/.ssh/authorized_keys"
# Should show: -rw------- (600)
```

## Troubleshooting

### Key Authentication Not Working

**Problem**: SSH still prompts for password even with key installed

**Solutions**:

1. **Check file permissions**:
   ```bash
   ssh root@192.168.1.200 "chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys"
   ```

2. **Verify key format**:
   ```bash
   # Key should be on a single line with no line breaks
   cat ~/.ssh/id_rsa.pub
   ```

3. **Check Dropbear logs** (via serial console):
   ```bash
   ./16_serial_command_monitor.sh -c "tail /var/log/messages | grep -i dropbear" -t 5
   ```

4. **Verify correct key is being offered**:
   ```bash
   ssh -v root@192.168.1.200 2>&1 | grep "Offering public key"
   ```

### Permission Denied with Correct Key

**Problem**: "Permission denied (publickey)"

**Check**:

1. Private key permissions on client:
   ```bash
   chmod 600 ~/.ssh/id_rsa
   ```

2. authorized_keys ownership on target:
   ```bash
   ssh -o PreferredAuthentications=password root@192.168.1.200 \
     "chown root:root /root/.ssh/authorized_keys"
   ```

3. SELinux/AppArmor (if enabled):
   ```bash
   # Usually not an issue on embedded systems
   ```

### Wrong Key Installed

**Problem**: Different key needed

**Solution**:

```bash
# Direct fix on NFS rootfs
cat ~/.ssh/id_rsa.pub | ssh pi@192.168.1.100 \
  "sudo tee /srv/nfs/root/.ssh/authorized_keys > /dev/null && \
   sudo chmod 600 /srv/nfs/root/.ssh/authorized_keys && \
   sudo chown root:root /srv/nfs/root/.ssh/authorized_keys"

# Then update recipe for future builds
```

## Advanced Usage

### Automated Deployments

With key-based auth, you can automate deployments:

```bash
#!/bin/bash
# deploy_script.sh

# No password needed!
ssh root@192.168.1.200 "systemctl stop my_service"
scp /path/to/app root@192.168.1.200:/usr/bin/
ssh root@192.168.1.200 "systemctl start my_service"
```

### SSH Agent Forwarding

Use SSH agent to avoid entering key passphrase repeatedly:

```bash
# Start SSH agent
eval $(ssh-agent)

# Add your key
ssh-add ~/.ssh/id_rsa

# Now SSH without passphrase prompt
ssh root@192.168.1.200
```

### SSH Config File

Simplify SSH commands with config:

```bash
# ~/.ssh/config
Host beaglebone
    HostName 192.168.1.200
    User root
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no

# Now just use:
ssh beaglebone
```

## Comparison with Base Image

### Authentication Methods

| Method | Base Image | Key Image | Recommendation |
|--------|------------|-----------|----------------|
| Password | Only option | Available | Use for recovery |
| SSH Key | Not available | Preferred | Use for daily work |
| Security | Basic | Enhanced | Key auth is more secure |
| Automation | Limited | Excellent | Scripts work seamlessly |

### Use Cases

**Use Base Image (password-only) when**:

- Quick testing/development
- Shared development environment
- Learning/educational purposes
- No automation needed

**Use Key Image (dual auth) when**:

- Production deployment
- Automated CI/CD pipelines
- Multiple developers with own keys
- Security is a priority
- Frequent SSH access needed

## Migration Guide

### From Password-only to Key-based

1. **Build new image**:
   ```bash
   bitbake core-image-tiny-initramfs-srk-2-bash-ssh-key
   ```

2. **Deploy**:
   ```bash
   ./03_copy_initramfs.sh 2-bash-ssh-key srk
   ```

3. **Test both methods work**:
   ```bash
   # Test key auth
   ssh root@192.168.1.200 "whoami"
   
   # Test password still works
   ssh -o PreferredAuthentications=password root@192.168.1.200 "whoami"
   ```

4. **Update documentation/scripts** to use key-based auth

5. **Consider disabling password auth** for production

## Files Modified in Recipe

### New Function Added

```bash
install_ssh_keys() {
    # Installs SSH public keys for root and srk users
    # Enables passwordless SSH authentication
}
```

### Files Created at Build Time

- `/root/.ssh/authorized_keys` - Root user's authorized keys
- `/home/srk/.ssh/authorized_keys` - SRK user's authorized keys

Both files:
- Permissions: 600 (rw-------)
- Owner: Respective user
- Content: SSH public key from build host

## Related Documentation

- [Base Image Documentation](../core-image-tiny-initramfs-srk-2-bash-ssh/README.md)
- [SSH Key Generation Guide](https://www.ssh.com/academy/ssh/keygen)
- [Dropbear Documentation](https://matt.ucc.asn.au/dropbear/dropbear.html)

## Quick Reference

### Build Commands

```bash
# Build
bitbake core-image-tiny-initramfs-srk-2-bash-ssh-key

# Deploy
./03_copy_initramfs.sh 2-bash-ssh-key srk

# Test
ssh root@192.168.1.200
```

### Network Configuration

- **NFS Server**: 192.168.1.100 (Raspberry Pi)
- **Target**: 192.168.1.200 (BeagleBone Black)
- **SSH Port**: 22

---

**Document Version**: 1.0  
**Last Updated**: October 19, 2025  
**Status**: Production Ready ✅  
**Authentication**: Password + Key ✅
