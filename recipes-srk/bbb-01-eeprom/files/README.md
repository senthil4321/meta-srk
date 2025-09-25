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

## Usage

After building and installing the package, run:

```bash
bbb-01-eeprom
```

## Example Output

```text
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
bitbake bbb-eeprom
```

## Installation

The program installs to `/usr/bin/bbb-eeprom`.