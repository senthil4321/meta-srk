# BBB RTC Recipe

This recipe provides a Real Time Clock (RTC) read/write utility for the BeagleBone Black that demonstrates RTC access through the Linux RTC subsystem.

## What it does

The `bbb-03-rtc` program provides comprehensive RTC functionality:

- **Read RTC time**: Display current RTC time
- **Write RTC time**: Set RTC to a specific time
- **Sync system from RTC**: Set system time from RTC
- **Sync RTC from system**: Set RTC time from system time
- **RTC information**: Show RTC device capabilities

## Building the Recipe

The recipe is named `bbb-03-rtc.bb` and follows the BBB example naming convention.

To build just this recipe:

```bash
bitbake bbb-03-rtc
```

## Including in the Image

The recipe is automatically included in the `core-image-tiny-initramfs-srk-11-bbb-examples` image. To build the complete image:

```bash
bitbake core-image-tiny-initramfs-srk-11-bbb-examples
```

## Usage

After booting the image, the program will be installed at `/usr/bin/bbb-03-rtc`.

### Read RTC Time

```bash
bbb-03-rtc read
```

### Write RTC Time

```bash
bbb-03-rtc write "2025-09-27 15:30:00"
```

### Set System Time from RTC

```bash
bbb-03-rtc set-system
```

### Set RTC Time from System

```bash
bbb-03-rtc set-rtc
```

### Show RTC Information

```bash
bbb-03-rtc info
```

## Hardware Requirements

- BeagleBone Black with RTC chip (typically DS3231)
- RTC device accessible at `/dev/rtc0`
- Proper device tree configuration for RTC

## Dependencies

- Linux RTC subsystem support
- RTC device driver loaded
- Proper permissions for RTC device access

## Files

- `bbb-03-rtc.bb` - The recipe file
- `files/bbb-03-rtc.c` - Main C program
- `files/Makefile` - Build configuration

## Troubleshooting

### RTC Device Not Found

- Ensure RTC hardware is connected and detected
- Check `dmesg` for RTC-related messages
- Verify device tree has RTC configuration

### Permission Denied

- Ensure program has access to `/dev/rtc0`
- Check file permissions on RTC device

### Invalid Time Format

- Use format: `YYYY-MM-DD HH:MM:SS`
- Example: `2025-09-27 15:30:00`
