# Kernel Size Optimization Summary

## Project Overview

- **Target**: Minimal Linux kernel for BeagleBone Black (UART-only operation)
- **Base Kernel**: Linux 6.6.75 with Yocto/OpenEmbedded build system
- **Goal**: Minimize kernel size while maintaining essential functionality

## Optimization Steps and Results

### 1. Initial State (Before Optimizations)

- **Total vmlinux**: ~4.6 MB
- **Drivers section**: ~778 KB
- **Kernel section**: ~1.0 MB (including full PRINTK support)

### 2. Timestamp Removal

- **Change**: Removed build timestamp from `KERNEL_LOCALVERSION`
- **Impact**: Minimal size reduction (~few KB)
- **Purpose**: Clean version string, avoid filesystem issues

### 3. PRINTK Subsystem Removal

- **Change**: Added `CONFIG_PRINTK=n` to disable kernel printing
- **Impact**: Major size reduction
- **Results**:
  - **Total vmlinux**: 2.76 MB (40% reduction from initial)
  - **Kernel section**: 415.18 KB (58% reduction)
  - **Printk component**: 6.33 KB (99% reduction from 559.83 KB)
  - **Drivers section**: 708.12 KB (9% reduction)

### 4. Serial and TTY Driver Removal

- **Change**: Added `CONFIG_SERIAL_8250=n`, `CONFIG_SERIAL_8250_CONSOLE=n`, `CONFIG_SERIAL_OF_PLATFORM=n`, `CONFIG_TTY=n`, `CONFIG_VT=n`, `CONFIG_UNIX98_PTYS=n`, `CONFIG_LEGACY_PTYS=n` to disable serial and TTY subsystems
- **Impact**: Significant size reduction
- **Results**:
  - **Total vmlinux**: 2.63 MB (120 KB reduction from previous)
  - **Drivers section**: 574.60 KB (124.65 KB reduction, mainly TTY)
  - **TTY component**: Completely removed (was 124.24 KB)
  - **Purpose**: Remove terminal/console dependencies, LED-only status

## Final Optimized Kernel Composition (After TTY Removal)

```text
Linux Kernel                          total |       text       data        bss |      Bytes
--------------------------------------------------------------------------------
vmlinux                             2760616 |    2415996     258732      85888 |    2.63 MB
--------------------------------------------------------------------------------
drivers/built-in.a                   588392 |     569495      14556       4341 |  574.60 KB
kernel/built-in.a                    425034 |     392303      23108       9623 |  415.07 KB
fs/built-in.a                        519189 |     498883       6066      14240 |  507.02 KB
mm/built-in.a                        384114 |     354526      10175      19413 |  375.11 KB
lib/built-in.a                       282134 |     247420       1894      32820 |  275.52 KB
block/built-in.a                     160676 |     155816       3292       1568 |  156.91 KB
arch/arm/built-in.a                  113447 |      98326      14541        580 |  110.79 KB
io_uring/built-in.a                   91594 |      91438        148          8 |   89.45 KB
crypto/built-in.a                     24737 |      23765        972          0 |   24.16 KB
init/built-in.a                       22092 |      14602       7414         76 |   21.57 KB
security/built-in.a                    5571 |       5555          8          8 |    5.44 KB
usr/built-in.a                          516 |        516          0          0 |   516.00 B
```

## Key Achievements

- **Total Size Reduction**: 1.97 MB (43% smaller than initial)
- **Drivers Optimization**: Reduced to 574.60 KB (26% reduction from initial)
- **Kernel Core**: Reduced to 415.07 KB (58% reduction)
- **Silent Operation**: No kernel messages, serial, or TTY output
- **LED Status Indication**: 4 BBB LEDs provide boot progress indication

## Configuration Files Used

- `disable-printk.cfg`: `CONFIG_PRINTK=n`
- `disable-serial-tty.cfg`: Serial and TTY driver disabling
- Multiple optimization fragments for drivers, filesystem, networking, etc.
- Custom DTS for BeagleBone Black minimal configuration
- Modified `srk-init.sh`: LED toggling for boot status

## Build Status

- **Yocto Recipe**: `linux-yocto-srk-tiny_6.6.bb`
- **Machine**: `beaglebone-yocto-srk-tiny`
- **Build Success**: All tasks completed successfully
- **Warnings**: Minor config warnings (non-critical)

## Initramfs Modifications

- **LED Control**: Added LED toggling throughout init process
- **Boot Sequence**:
  - **LED0**: Init start
  - **LED1**: Loop device setup
  - **LED2**: Cryptsetup decryption
  - **LED3**: Encrypted mount
  - **LED0**: Squashfs mount
  - **All LEDs**: Success before pivot_root

## Conclusion

The optimized kernel achieves a 2.63 MB footprint while maintaining all essential functionality for encrypted root filesystem boot on BeagleBone Black. Serial console, TTY subsystem, and kernel printing have been completely removed, with LED status indication providing visual feedback during the boot process. This represents a significant size reduction through targeted driver and subsystem elimination.

**Date**: October 3, 2025
**Kernel Version**: 6.6.75-srk-tiny
**Final Size**: 2.63 MB
**Status Indication**: 4x BBB LEDs