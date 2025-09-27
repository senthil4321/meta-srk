# SRK Kernel Variants Documentation

This document describes the custom Linux kernel variants developed for the SRK (Security Research Kernel) project, focusing on minimal initramfs optimization and security features.

## Overview

The SRK project maintains multiple kernel variants optimized for different use cases:

- **linux-yocto-srk**: Base custom kernel with minimal configuration
- **linux-yocto-srk-bbb**: BeagleBone Black optimized kernel with hardware support
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
- **KCONFIG_MODE**: alldefconfig
- **Machine**: beaglebone-yocto

#### Base Kernel Features

- Optimized for embedded systems
- Minimal feature set for initramfs
- BeagleBone Black support
- Standard Yocto kernel configuration approach

### linux-yocto-srk-bbb (BBB-Specific Kernel)

**Recipe**: `linux-yocto-srk-bbb_6.6.bb`
**Description**: BeagleBone Black optimized kernel with hardware support
**Base**: linux-yocto 6.6 with BBB-specific enhancements

#### BBB Kernel Configuration

- **defconfig**: Custom minimal configuration in `recipes-kernel/linux/linux-yocto-srk-bbb/defconfig`
- **bbb-eeprom.cfg**: BBB EEPROM and I2C support configuration
- **bbb-led.cfg**: BBB LED subsystem support configuration
- **KCONFIG_MODE**: alldefconfig
- **Machine**: beaglebone-yocto

#### BBB Kernel Features

- **BBB EEPROM Support**: I2C and AT24 EEPROM drivers enabled for board identification
- **BBB LED Support**: GPIO-based LED class support with triggers for user LEDs
- **I2C Support**: Full I2C subsystem with OMAP drivers and character device access
- **GPIO Support**: GPIO library for hardware control
- Optimized for BeagleBone Black hardware

#### BBB EEPROM Configuration Details

```config
# I2C Core Support
CONFIG_I2C=y
CONFIG_I2C_BOARDINFO=y
CONFIG_I2C_COMPAT=y
CONFIG_I2C_OMAP=y

# EEPROM Drivers
CONFIG_EEPROM_AT24=y

# User-space I2C tools support
CONFIG_I2C_CHARDEV=y
```

#### BBB LED Configuration Details

```config
# LED Class Support
CONFIG_LEDS_CLASS=y
CONFIG_LEDS_GPIO=y
CONFIG_LEDS_TRIGGERS=y
CONFIG_OF_OVERLAY=y
```

### linux-yocto-srk-selinux (SELinux Kernel)

**Recipe**: `linux-yocto-srk-selinux_6.6.bb`
**Description**: SELinux-enabled kernel for security research and enforcement
**Base**: linux-yocto-srk with SELinux extensions

#### Configuration

- **defconfig**: Inherited from linux-yocto-srk
- **selinux.cfg**: SELinux-specific configuration fragment
- **localversion.cfg**: Custom kernel version string
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

#### Boot Time Optimizations

To achieve faster boot times, the following optimizations have been implemented:

- **HDMI Disable in Device Tree**: The HDMI DTS include (`am335x-boneblack-hdmi.dtsi`) is commented out in the main BeagleBone Black DTS to prevent HDMI hardware initialization.
- **Audio Disable in Device Tree**: The sound node in the HDMI DTS include is commented out to avoid audio subsystem setup.
- **Audio Disable in Kernel Config**: Kernel configuration fragments disable sound support (`CONFIG_SOUND=n`, `CONFIG_SND=n`) to remove audio drivers from the build.

These changes reduce boot time by skipping unnecessary peripheral initialization while maintaining core functionality for the no-busybox initramfs environment.

#### Tiny Kernel Runtime Configuration

**Avoid Delay Calibration at Boot:**
To prevent the kernel from performing delay loop calibration at boot time (which can take several seconds), configure the loops per jiffy (lpj) value in U-Boot:

```bash
# Set the pre-calculated lpj value
setenv bootargs "${bootargs} lpj=4980736"
saveenv
```

This bypasses the calibration process and uses the pre-calculated value for better boot performance.

**Boot Time Reduction via Device Tree:**
Disabling unused pinmux nodes or modules in the device tree can shave off additional boot delay. The tiny kernel includes a device tree overlay (`bbb-disable-unneeded.dtbo`) that disables unnecessary peripherals and pin configurations to optimize boot time.

## Build Information

### Current Build Status

- **Kernel Version**: 6.6.52+git (latest stable)
- **Build Date**: September 25, 2025
- **Git Commit**: 5cefbe3e27_01b1f32be4
- **Last Build**: linux-yocto-srk-bbb (successful)
- **Last Deployment**: September 25, 2025 (via 04_copy_zImage.sh)

### Artifact Sizes (BBB Kernel)

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

#### Build BBB Kernel (Recommended)

```bash
bitbake linux-yocto-srk-bbb
```

*Note*: The BBB kernel is recommended for most BeagleBone Black deployments as it includes essential hardware support for EEPROM and LED access.

#### Build SELinux Kernel

```bash
# Set preferred provider in local.conf
echo 'PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-selinux"' >> conf/local.conf

# Build the kernel
bitbake linux-yocto-srk-selinux
```

#### Build Tiny Kernel

```bash
bitbake linux-yocto-srk-tiny -c clean
bitbake linux-yocto-srk-tiny

# Then rebuild your image
bitbake core-image-tiny-initramfs-srk-9-nobusybox
```

### Deploying Kernels

Use the provided deployment scripts:

#### Copy Kernel Image

```bash
# Copy standard kernel (default)
./04_copy_zImage.sh -i

# Copy tiny kernel (minimal configuration)
./04_copy_zImage.sh -i -tiny

# Copy with verbose output
./04_copy_zImage.sh -i -tiny -v
```

**Last Deployment**:

- Standard kernel: linux-yocto kernel and am335x-boneblack.dtb successfully copied to TFTP server on September 27, 2025
- Tiny kernel: linux-yocto-srk-tiny kernel and am335x-yocto-srk-tiny.dtb successfully copied to TFTP server on September 28, 2025

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
- **linux-yocto-srk-bbb**: Compatible with all SRK images, optimized for BBB hardware features
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

### BBB Kernel

- Standard Linux security features
- Hardware-specific security (EEPROM access control)
- GPIO and LED security considerations
- Suitable for embedded hardware security research

### Base Kernel

- Standard Linux security features
- No mandatory access control
- Suitable for minimal/trusted environments

## Development Notes

### Kernel Configuration

- All kernels use `alldefconfig` mode for maximum compatibility
- Custom defconfig provides minimal base configuration
- BBB kernel adds hardware-specific configuration fragments (EEPROM, LED)
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
- Enhanced BBB hardware support (PRU, CAN, etc.)
- Advanced LED and GPIO features

## Troubleshooting

### Build Issues

- Ensure `meta-selinux` layer is included for SELinux kernel
- Check that defconfig exists in recipe directory
- Verify machine compatibility (beaglebone-yocto)
- For BBB kernel, ensure bbb-eeprom.cfg and bbb-led.cfg fragments exist

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
