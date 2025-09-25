# BBB EEPROM Reader

This program reads and displays the contents of the BeagleBone Black's EEPROM, which contains important board information.

## Features

- Reads board name and version
- Displays serial number
- Shows all four MAC addresses stored in EEPROM
- Validates EEPROM header

## Requirements

- BeagleBone Black board
- EEPROM device accessible at `/sys/bus/i2c/devices/0-0050/eeprom`
- `at24` kernel module loaded (run `modprobe at24` if needed)
- Kernel configured with I2C and AT24 EEPROM support
- `i2c-tools` package for debugging (included in the image)

## Setup

If the EEPROM device is not automatically detected, run the setup script:

```bash
setup-eeprom.sh
```

This script will:

- Check if the I2C bus is available
- Load the AT24 kernel module if needed  
- Instantiate the EEPROM device on the I2C bus
- Provide detailed debugging output

For debugging I2C issues, use the included `i2c-tools`:

```bash
i2cdetect -l  # List I2C buses
i2cdetect 0   # Scan I2C bus 0 for devices
```

## Usage

After building and installing the package, run:

```bash
bbb-01-eeprom
```

## Example Output

```
BBB EEPROM Reader
=================

Board Name: A335BNLT
Serial Number: 123456789012
Version: 0.0
MAC Address 1: 12:34:56:78:9A:BC
MAC Address 2: 12:34:56:78:9A:BD
MAC Address 3: 12:34:56:78:9A:BE
MAC Address 4: 12:34:56:78:9A:BF

EEPROM read successfully!
```

## EEPROM Structure

The BBB EEPROM contains:

- Header (4 bytes): AA5533EE
- Board name (8 bytes): A335BNLT
- Version (4 bytes)
- Serial number (12 bytes)
- Pin options (6 bytes)
- DC specification (2 bytes)
- Four MAC addresses (6 bytes each)
- CRC (2 bytes)

## Building

This is a Yocto recipe. To build:

```bash
bitbake bbb-01-eeprom
```

## Kernel Configuration

The kernel must be configured with the following options for EEPROM support:

- `CONFIG_I2C=y`
- `CONFIG_I2C_OMAP=y` (for BeagleBone)
- `CONFIG_EEPROM_AT24=y`

These are included in the `bbb-eeprom.cfg` kernel config fragment.

## Image Integration

The BBB EEPROM utility is included in the `core-image-tiny-initramfs-srk-11-bbb-examples` image, which also includes:

- `i2c-tools` for I2C debugging
- Kernel config fragment for EEPROM support
- Setup script for device instantiation

## Files

The program installs to `/usr/bin/bbb-01-eeprom`.
The setup script installs to `/usr/bin/setup-eeprom.sh`.
