# SRK Kernel Variants Documentation

This document describes the custom Linux kernel variants developed for the SRK (Security Research Kernel) project, focusing on minimal initramfs optimization and security features.

## Overview

The SRK project maintains multiple kernel variants optimized for different use cases:

- **linux-yocto-srk**: Base custom kernel with minimal configuration
- **linux-yocto-srk-selinux**: SELinux-enabled variant for security experimentation
- **linux-yocto-srk-tiny**: Tiny kernel optimized for no-busybox initramfs

All kernels are based on Linux 6.6 LTS with Yocto Project integration.

## Kernel Variants

### linux-yocto-srk (Base Kernel)

**Recipe**: `linux-yocto-srk_6.6.bb`
**Description**: Minimal custom kernel optimized for initramfs usage
**Base**: linux-yocto 6.6 from Yocto Project

#### Base Kernel Configuration

- **defconfig**: Custom minimal configuration in `recipes-kernel/linux/linux-yocto-srk/defconfig`
- **bbb-eeprom.cfg**: BBB EEPROM and I2C support configuration
- **KCONFIG_MODE**: alldefconfig
- **Machine**: beaglebone-yocto

#### Base Kernel Features

- Optimized for embedded systems
- Minimal feature set for initramfs
- BeagleBone Black support
- **BBB EEPROM Support**: I2C and AT24 EEPROM drivers enabled for board identification
- Standard Yocto kernel configuration approach

### linux-yocto-srk-selinux (SELinux Kernel)

**Recipe**: `linux-yocto-srk-selinux_6.6.bb`
**Description**: SELinux-enabled kernel for security research and enforcement
**Base**: linux-yocto-srk with SELinux extensions

#### Configuration

- **defconfig**: Inherited from linux-yocto-srk
- **selinux.cfg**: SELinux-specific configuration fragment
- **KCONFIG_MODE**: alldefconfig
- **Machine**: beaglebone-yocto

#### SELinux Configuration Details

```config
CONFIG_SECURITY=y
CONFIG_SECURITYFS=y
CONFIG_LSM="landlock,lockdown,yama,integrity,selinux,bpf"
CONFIG_SECURITY_SELINUX=y
CONFIG_SECURITY_SELINUX_BOOTPARAM=y
CONFIG_SECURITY_SELINUX_DISABLE=y
CONFIG_SECURITY_SELINUX_DEVELOP=y
CONFIG_SECURITY_SELINUX_AVC_STATS=y
CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE=0
```

#### SELinux Features

- **LSM Stack**: landlock, lockdown, yama, integrity, selinux, bpf
- **Boot Parameters**: SELinux can be disabled at boot time
- **Development Mode**: Enabled for policy development
- **AVC Statistics**: Access Vector Cache statistics collection
- **Check Request Protection**: Set to 0 (strict checking)

### linux-yocto-srk-tiny (No-BusyBox Kernel)

**Recipe**: `linux-yocto-srk-tiny_6.6.bb`
**Description**: Ultra-minimal kernel optimized for no-busybox initramfs
**Base**: linux-yocto 6.6 with minimal configuration

#### Tiny Kernel Configuration

- **defconfig**: Custom minimal configuration in `recipes-kernel/linux/linux-yocto-srk-tiny/defconfig`
- **KCONFIG_MODE**: alldefconfig
- **Machine**: beaglebone-yocto
- **INITRAMFS_IMAGE**: core-image-tiny-initramfs-srk-9-nobusybox
- **INITRAMFS_IMAGE_BUNDLE**: 1 (built-in initramfs)

#### Tiny Kernel Features

- Built-in initramfs bundle
- Optimized for BusyBox-free environments
- Minimal kernel footprint
- BeagleBone Black support

## Build Information

### Current Build Status

- **Kernel Version**: 6.6.52+git (latest stable)
- **Build Date**: September 25, 2025
- **Git Commit**: 5cefbe3e27_01b1f32be4
- **Last Build**: linux-yocto-srk (successful)
- **Last Deployment**: September 25, 2025 (via 04_copy_zImage.sh)

### Artifact Sizes (SELinux Kernel)

- **Kernel Image (zImage)**: 8.3 MB compressed
- **Kernel Modules**: 52 MB (tar.gz compressed)
- **Device Trees**: ~70 KB each (am335x-bone, am335x-boneblack, etc.)

### Build Warnings

```text
[kernel config]: This BSP contains fragments with warnings:
[INFO]: the following symbols were not found in the active configuration:
     - CONFIG_SECURITY_SELINUX_DISABLE
     - CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE
```

*Note*: These warnings indicate that some SELinux config options from fragments may not be active in the final kernel config.

## Usage Instructions

### Building Kernels

#### Build Base Kernel

```bash
bitbake linux-yocto-srk
```

#### Build SELinux Kernel

```bash
# Set preferred provider in local.conf
echo 'PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-selinux"' >> conf/local.conf

# Build the kernel
bitbake linux-yocto-srk-selinux
```

### Deploying Kernels

Use the provided deployment scripts:

#### Copy Kernel Image

```bash
# Copy regular kernel (default)
./04_copy_zImage.sh

# Copy initramfs-embedded kernel (when available)
./04_copy_zImage.sh -i

# Copy with verbose output
./04_copy_zImage.sh -i -v
```

**Last Deployment**: linux-yocto-srk kernel and am335x-boneblack.dtb successfully copied to TFTP server on September 25, 2025.

#### Copy Kernel Modules (if needed)

```bash
./05_copy_squashfs.sh  # Can be adapted for modules
```

### SELinux Boot Parameters

When booting with SELinux kernel, you can control SELinux behavior:

- `selinux=0`: Disable SELinux
- `selinux=1`: Enable SELinux (default)
- `enforcing=0`: Enable permissive mode
- `enforcing=1`: Enable enforcing mode (default)

## Integration with Initramfs

### Compatible Images

The kernels are designed to work with SRK initramfs variants:

- **linux-yocto-srk**: Compatible with all SRK images (srk-3 through srk-11-bbb-examples)
- **linux-yocto-srk-selinux**: Optimized for srk-10-selinux (includes SELinux userspace)
- **linux-yocto-srk-tiny**: Bundled with srk-9-nobusybox (built-in initramfs)

### Initramfs Loading

Kernels are configured to load initramfs via:

- Built-in initramfs (when CONFIG_INITRAMFS_SOURCE is set)
- Separate cpio archive loaded by bootloader

## Security Considerations

### SELinux Kernel

- **Development Mode**: Enabled for policy experimentation
- **Permissive Mode**: Can be set at boot for policy development
- **Disable Option**: SELinux can be completely disabled if needed
- **Policy**: Requires SELinux policy in initramfs (provided by srk-10-selinux)

### Base Kernel

- Standard Linux security features
- No mandatory access control
- Suitable for minimal/trusted environments

## Development Notes

### Kernel Configuration

- All kernels use `alldefconfig` mode for maximum compatibility
- Custom defconfig provides minimal base configuration
- SELinux adds security-focused configuration fragments

### Yocto Integration

- Recipes follow Yocto kernel recipe patterns
- Compatible with beaglebone-yocto machine
- Supports standard Yocto kernel workflow

### Future Enhancements

- Additional security modules (AppArmor, SMACK)
- Real-time patches
- Custom security modules
- Performance optimizations

## Troubleshooting

### Build Issues

- Ensure `meta-selinux` layer is included for SELinux kernel
- Check that defconfig exists in recipe directory
- Verify machine compatibility (beaglebone-yocto)

### Runtime Issues

- SELinux kernel requires SELinux-enabled initramfs
- Check kernel boot logs for SELinux status
- Use `dmesg | grep -i selinux` to check SELinux initialization
- If "can't access tty" error occurs, ensure initramfs has proper console setup

### SELinux Initramfs Console Issues

The srk-10-selinux initramfs includes proper console device setup:

- Mounts devtmpfs for device nodes
- Creates /dev/console if missing (major 5, minor 1)
- Redirects shell I/O to console device
- Runs in permissive mode by default for experimentation

### Configuration Issues

- SELinux config warnings are normal during development
- Verify final .config has expected SELinux options
- Check `/sys/fs/selinux` mount point for SELinux status

## References

- [Yocto Project Linux Kernel Development](https://docs.yoctoproject.org/kernel-dev/index.html)
- [SELinux Project](https://selinuxproject.org/)
- [BeagleBone Black Documentation](https://beagleboard.org/black)
- [SRK Initramfs Documentation](./initramfs_size_optimization.md)
- [SELinux Commands Guide](./selinux_commands_guide.md)
