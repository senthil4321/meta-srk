# Linux Capabilities Demo

This recipe demonstrates Linux capabilities on the BeagleBone Black.

## What are Linux Capabilities?

Linux capabilities divide the privileges traditionally associated with superuser (root) into distinct units. This allows fine-grained control over what privileged operations a process can perform, without needing full root access.

## Contents

- **cap-demo**: C program that shows and tests Linux capabilities
- **cap-examples.sh**: Shell script demonstrating capability usage
- **libcap**: Library for manipulating POSIX 1003.1e capabilities
- **libcap-bin**: Utilities (setcap, getcap) for managing capabilities

## User Accounts

The image includes a dedicated user for testing capabilities:

- **Username**: `capuser`
- **Password**: `capability`
- **UID**: 1001
- **Home**: `/home/capuser`
- **Shell**: `/bin/bash`

Other users:
- **root** / password: `root`
- **srk** / password: `srk`

## Usage

### Basic Commands

```bash
# Show current capabilities
cap-demo show

# List all effective capabilities
cap-demo list

# Test network capabilities
cap-demo test-net

# Test system time capability
cap-demo test-time

# Show process information
cap-demo info
```

### Run Examples Script

```bash
# Run all examples (requires root for setcap)
sudo cap-examples.sh

# Or run as normal user to see what's possible
cap-examples.sh
```

### Managing Capabilities

```bash
# View capabilities of a binary
getcap /usr/bin/cap-demo

# Grant network capabilities (as root)
sudo setcap cap_net_raw,cap_net_admin=ep /usr/bin/cap-demo

# Grant system time capability (as root)
sudo setcap cap_sys_time=ep /usr/bin/cap-demo

# Remove all capabilities (as root)
sudo setcap -r /usr/bin/cap-demo
```

## Common Capabilities

| Capability | Description |
|-----------|-------------|
| `CAP_NET_RAW` | Use RAW and PACKET sockets (ping, tcpdump) |
| `CAP_NET_ADMIN` | Perform network administration tasks |
| `CAP_NET_BIND_SERVICE` | Bind to ports below 1024 |
| `CAP_SYS_TIME` | Set system clock |
| `CAP_DAC_OVERRIDE` | Bypass file read/write/execute permission checks |
| `CAP_CHOWN` | Make arbitrary changes to file UIDs and GIDs |
| `CAP_SETUID` | Make arbitrary manipulations of process UIDs |
| `CAP_SETGID` | Make arbitrary manipulations of process GIDs |
| `CAP_SYS_ADMIN` | Perform system administration operations |
| `CAP_SYS_MODULE` | Load and unload kernel modules |

## Capability Sets

Each process has three capability sets:

- **Permitted (p)**: Capabilities the process may acquire
- **Effective (e)**: Capabilities currently in effect
- **Inheritable (i)**: Capabilities preserved across execve()

Format: `cap_name=epi` (any combination of e, p, i)

## Example Scenarios

### 1. Non-root ping (CAP_NET_RAW)

Normally ping requires root for raw sockets:

```bash
# Grant CAP_NET_RAW to ping
sudo setcap cap_net_raw=ep /bin/ping

# Now non-root users can ping
ping 192.168.1.1
```

### 2. Web server on port 80 (CAP_NET_BIND_SERVICE)

Allow non-root process to bind to privileged ports:

```bash
# Grant capability to Python web server
sudo setcap cap_net_bind_service=ep /usr/bin/python3

# Now can run server on port 80 without root
python3 -m http.server 80
```

### 3. Time management (CAP_SYS_TIME)

Allow specific program to set system time:

```bash
# Grant time capability to custom program
sudo setcap cap_sys_time=ep /usr/bin/my-time-setter

# Program can now set time without root
```

## Testing as capuser

```bash
# Login as capuser
su - capuser
# Password: capability

# Run capability demo
cap-demo show
cap-demo list

# Try running with elevated capabilities (needs root to set)
exit
sudo setcap cap_net_raw=ep /usr/bin/cap-demo
su - capuser
cap-demo test-net
```

## Security Notes

1. **File Capabilities Persist**: Once set with `setcap`, capabilities remain until explicitly removed
2. **No SUID Needed**: Capabilities provide safer alternative to SUID root binaries
3. **Minimal Privilege**: Grant only the specific capabilities needed
4. **File System Support**: Capabilities require file system with xattr support (ext4, xfs, etc.)
5. **Kernel Support**: Requires `CONFIG_SECURITY_CAPABILITIES=y` in kernel

## Building

```bash
# Build the capabilities demo
bitbake capabilities-demo

# Rebuild the image with capabilities support
bitbake core-image-tiny-initramfs-srk-2-bash-ssh-key-recipe
```

## Troubleshooting

### Capabilities not working?

```bash
# Check kernel support
grep CAPABILITIES /proc/config.gz | zcat

# Check file system support (must have "user_xattr" option)
mount | grep ext4

# Verify libcap is installed
ldconfig -p | grep libcap
```

### Can't set capabilities?

```bash
# Must be root to set capabilities
sudo setcap ...

# Check if file system mounted with nosuid (prevents capabilities)
mount | grep nosuid
```

## References

- Linux man pages: `man 7 capabilities`
- libcap documentation: `man cap_get_proc`, `man cap_set_proc`
- setcap/getcap: `man 8 setcap`, `man 8 getcap`
- POSIX 1003.1e capabilities specification

## Version

Version: 1.0  
Date: October 30, 2025  
Author: SRK Embedded Systems
