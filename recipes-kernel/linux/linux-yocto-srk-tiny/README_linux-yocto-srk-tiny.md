# Linux Yocto SRK Tiny Kernel

## Overview

This is a custom Linux kernel recipe based on `linux-yocto` 6.6, optimized for the BeagleBone Black board with a focus on minimal boot time and reduced power consumption. The kernel disables unused peripherals and includes custom device tree configurations.

## Key Features

### Device Tree Customizations

- **Custom DTS**: `am335x-yocto-srk-tiny.dts`
- **Disabled Peripherals**:
  - HDMI output (saves ~100ms boot time)
  - Unused USB ports
  - Audio interfaces
  - LCD controller
  - Unused GPIO pins
  - SPI interfaces (except SPI0)
  - I2C interfaces (except I2C2)
  - CAN bus
  - PRU (Programmable Real-time Units)

### Kernel Configuration

- **Base**: `linux-yocto` 6.6 standard configuration
- **Custom Configs**:
  - `printk_time.cfg`: Adds timestamps to kernel messages
  - `disable_scsi_debug.cfg`: Disables SCSI debugging
  - `patches/disable-audio.patch`: Removes audio driver support

### Initramfs Integration

- Bundled with `core-image-tiny-initramfs-srk-9-nobusybox`
- Minimal initramfs for fast boot

## Machine Compatibility

This kernel is compatible with:

- `beaglebone-yocto-srk-tiny` (primary target)

## Build Instructions

### Prerequisites

1. Yocto Project environment set up
2. `meta-srk` layer added to `bblayers.conf`
3. Machine set to `beaglebone-yocto-srk-tiny` in `local.conf`

### Building the Kernel

```bash
# Set up the build environment
cd /path/to/poky
source oe-init-build-env build

# Configure for SRK tiny machine
echo 'MACHINE = "beaglebone-yocto-srk-tiny"' >> conf/local.conf

# Build the kernel
bitbake linux-yocto-srk-tiny

# Build with initramfs
bitbake core-image-tiny-initramfs-srk-9-nobusybox
```

### Alternative: Using with Other Machines

To use this kernel with other BeagleBone machines, update the kernel recipe's `COMPATIBLE_MACHINE`:

```bash
COMPATIBLE_MACHINE = "beaglebone-yocto beaglebone-yocto-srk beaglebone-yocto-srk-tiny"
```

Then set in `local.conf`:

```bash
PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-tiny"
```

## File Structure

```text
linux-yocto-srk-tiny/
├── linux-yocto-srk-tiny_6.6.bb          # Main recipe file
├── am335x-yocto-srk-tiny.dts            # Custom device tree
├── defconfig                            # Kernel defconfig
├── printk_time.cfg                      # Kernel config fragment
├── disable_scsi_debug.cfg               # Kernel config fragment
├── patches/
│   └── disable-audio.patch              # Audio driver removal patch
└── README_linux-yocto-srk-tiny.md       # This file
```

## Device Tree Details

The custom device tree `am335x-yocto-srk-tiny.dts` is based on:

- `am33xx.dtsi` (AM335x SoC definitions)
- `am335x-bone-common.dtsi` (BeagleBone common settings)
- `am335x-boneblack-common.dtsi` (BeagleBone Black specific)

### Enabled Interfaces

- **UART0** (console)
- **Ethernet** (CPSW)
- **MMC1** (microSD card)
- **USB0** (host mode)
- **I2C2** (for cape EEPROMs)
- **SPI0** (for SPI flash)
- **Power Management** (TPS65217 PMIC)

### Disabled Interfaces

- HDMI (display, audio, CEC)
- LCD controller
- USB1
- I2C1
- SPI1
- CAN0/CAN1
- PRU-ICSS
- Audio (McASP, TLV320AIC)
- Unused GPIOs

## Performance Optimizations

### Boot Time Improvements

- Disabled HDMI initialization (~100ms saved)
- Minimal device tree (fewer devices to probe)
- Reduced kernel size through config optimizations

### Power Consumption

- Disabled unused peripherals
- Optimized GPIO configurations
- Minimal kernel features

## Troubleshooting

### Build Issues

**Problem**: `Unable to get checksum for SRC_URI entry`
**Solution**: Ensure all patch files exist in the correct locations

**Problem**: `No rule to make target am335x-yocto-srk-tiny.dtb`
**Solution**: Check that the DTS file is properly added to SRC_URI with correct subdir

**Problem**: `INITRAMFS_IMAGE_NAME` mismatch
**Solution**: Ensure the initramfs image name matches the MACHINE variable

### Runtime Issues

**Problem**: No console output
**Solution**: Check UART0 pinmux and serial console configuration

**Problem**: Network not working
**Solution**: Verify CPSW Ethernet configuration in device tree

## Development Notes

### Adding New Device Tree Changes

1. Edit `am335x-yocto-srk-tiny.dts`
2. Test compilation: `bitbake linux-yocto-srk-tiny -c compile`
3. Deploy and test on hardware

### Modifying Kernel Configuration

1. Add new `.cfg` files to the recipe directory
2. Update SRC_URI in the recipe
3. Rebuild kernel: `bitbake linux-yocto-srk-tiny -c configure`

### Updating to New Kernel Versions

1. Change `require recipes-kernel/linux/linux-yocto_6.6.bb` to new version
2. Update recipe filename: `linux-yocto-srk-tiny_<version>.bb`
3. Test compatibility of custom patches and configs

## Version History

- **6.6**: Initial version based on linux-yocto 6.6
  - Custom device tree with disabled peripherals
  - Minimal kernel configuration
  - Initramfs bundling support

## Summary

The Linux Yocto SRK Tiny Kernel represents a highly optimized, minimal Linux kernel configuration specifically designed for the BeagleBone Black board. This custom kernel achieves significant improvements in boot time and power efficiency through strategic disabling of unused hardware peripherals and careful kernel configuration tuning.

### Key Achievements

**Boot Time Optimization:**

- HDMI output disabled: ~100ms boot time reduction
- Minimal device tree: Reduced hardware probing overhead
- Streamlined kernel configuration: Faster initialization

**Power Consumption Reduction:**

- Disabled unused peripherals (USB ports, audio interfaces, LCD controller)
- Optimized GPIO configurations
- Minimal kernel feature set

**Hardware Customization:**

- Custom device tree (`am335x-yocto-srk-tiny.dts`) with board-specific optimizations
- Disabled PRU (Programmable Real-time Units) for reduced complexity
- Selective SPI/I2C interface enabling (only essential interfaces active)

**Build System Integration:**

- Dedicated machine configuration (`beaglebone-yocto-srk-tiny`)
- Automated kernel configuration management
- Initramfs bundling for unified deployment
- Comprehensive build scripts and documentation

### Configuration Philosophy

This kernel follows a "less is more" approach, starting with a minimal base configuration and only enabling features that are essential for the target application. This results in:

- **Faster boot times**: Reduced hardware initialization
- **Lower power consumption**: Fewer active peripherals
- **Smaller attack surface**: Minimal kernel features
- **Easier maintenance**: Focused configuration management
- **Predictable behavior**: Consistent hardware interface

### Development Workflow

The kernel development process includes:

- Automated configuration validation
- Fragment-based customization
- Hardware testing verification
- Comprehensive documentation
- Version-controlled configuration management

This kernel serves as a foundation for embedded applications requiring fast boot times, minimal power consumption, and predictable hardware behavior on the BeagleBone Black platform.

## Contributing

When making changes to this kernel recipe:

1. Test builds on target hardware
2. Update this README with any new features or changes
3. Ensure backward compatibility where possible
4. Document any new configuration options

## License

This kernel recipe and associated files are licensed under the MIT license (see COPYING.MIT in the meta-srk root directory).
