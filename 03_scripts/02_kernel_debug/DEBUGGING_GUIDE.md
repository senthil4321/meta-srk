# Debuggable Kernel Build and Debugging Setup Guide

## Overview

This guide covers creating and using the debuggable kernel variant that re-enables debugging features while maintaining most optimizations from the ultra-minimal kernel.

## Building the Debuggable Kernel

### 1. Update local.conf

Edit your `build/conf/local.conf` to use the debug kernel:

```bash
PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-tiny-debug"

```

### 2. Build the Debug Kernel

```bash

# Clean previous builds if needed

bitbake -c cleansstate linux-yocto-srk-tiny-debug

# Build the debug kernel

bitbake linux-yocto-srk-tiny-debug

# Build the complete image

bitbake core-image-tiny-initramfs-srk-9-nobusybox

```

### 3. Deploy to SD Card

Use the same deployment scripts but with the new debug kernel:

```bash
./02_prepare_sdcard.sh

```

## Debugging Capabilities Enabled

### Core Debug Features

- **Debug Info**: DWARF debug information included in kernel

- **Debug FS**: `/sys/kernel/debug/` filesystem for runtime debugging

- **Magic SysRq**: Emergency key combinations for system control

- **KGDB**: Remote kernel debugging over serial

- **Kallsyms**: Full symbol table for stack traces

- **Frame Pointers**: Better stack unwinding

- **Dynamic Debug**: Runtime control of debug messages

### Tracing Features

- **Function Tracer**: Trace kernel function calls

- **IRQ-off Tracer**: Monitor interrupt latency

- **Preemption Tracer**: Monitor preemption latency

- **Ftrace**: Comprehensive kernel tracing framework

### Memory Debugging

- **Page Alloc Debug**: Detect memory corruption

- **Stack Overflow Debug**: Detect kernel stack overflows

### Lock Debugging

- **Lockdep**: Detect potential deadlocks

- **Lock Proving**: Verify locking correctness

## Debugging Tools and Setup Requirements

### 1. Serial Console Setup

The debug kernel maintains serial console access:

- **Port**: `/dev/ttyUSB0` (or similar FTDI adapter)

- **Settings**: 115200 baud, 8N1

- **Tools**: minicom, picocom, or screen

```bash

# Using screen

screen /dev/ttyUSB0 115200

# Using minicom

minicom -D /dev/ttyUSB0 -b 115200

```

### 2. GDB Cross-Debugging Setup

#### Install Cross-GDB

```bash

# Install arm-linux-gnueabihf-gdb

sudo apt-get install gdb-multiarch

# or

sudo apt-get install gdb-arm-linux-gnueabihf

```

#### Extract vmlinux with Debug Symbols

```bash

# Find the vmlinux file with debug symbols

find tmp/work/beaglebone_yocto_srk_tiny-poky-linux-gnueabi/linux-yocto-srk-tiny-debug/ -name "vmlinux" -type f

# Copy to debugging workspace

cp tmp/work/beaglebone_yocto_srk_tiny-poky-linux-gnueabi/linux-yocto-srk-tiny-debug/*/linux-*/vmlinux ./vmlinux-debug

```

#### KGDB Remote Debugging

1. **Boot with KGDB enabled** (already configured in kernel)

2. **Connect via serial for KGDB**:

```bash

# On target (via serial console), trigger KGDB

echo g > /proc/sysrq-trigger

# On host, connect GDB

gdb-multiarch vmlinux-debug
(gdb) set serial baud 115200
(gdb) target remote /dev/ttyUSB0

```

### 3. JTAG Debugging (Optional)

#### Hardware Requirements

- **JTAG Adapter**: J-Link, OpenOCD-compatible adapter

- **Connection**: BeagleBone Black JTAG header (P2)

#### OpenOCD Setup

```bash

# Install OpenOCD

sudo apt-get install openocd

# Create OpenOCD config for BBB

cat > bbb-debug.cfg << EOF
source [find board/ti_beaglebone_black.cfg]
init
halt
EOF

# Run OpenOCD

openocd -f bbb-debug.cfg

```

#### GDB + OpenOCD Connection

```bash

# In another terminal

gdb-multiarch vmlinux-debug
(gdb) target remote localhost:3333
(gdb) load
(gdb) continue

```

### 4. Ftrace Usage

#### Basic Ftrace Commands (on target)

```bash

# Mount debugfs (should be auto-mounted)

mount -t debugfs none /sys/kernel/debug

# Enable function tracer

echo function > /sys/kernel/debug/tracing/current_tracer

# Start tracing

echo 1 > /sys/kernel/debug/tracing/tracing_on

# View trace

cat /sys/kernel/debug/tracing/trace

# Stop tracing

echo 0 > /sys/kernel/debug/tracing/tracing_on

```

#### Function Graph Tracer

```bash

# Enable function graph tracer

echo function_graph > /sys/kernel/debug/tracing/current_tracer

# Set specific functions to trace

echo sys_open > /sys/kernel/debug/tracing/set_graph_function

# View trace

cat /sys/kernel/debug/tracing/trace

```

### 5. Dynamic Debug

#### Enable Dynamic Debug Messages

```bash

# Enable all debug messages for a specific file

echo 'file kernel/sched/core.c +p' > /sys/kernel/debug/dynamic_debug/control

# Enable debug for specific function

echo 'func schedule +p' > /sys/kernel/debug/dynamic_debug/control

# View current settings

cat /sys/kernel/debug/dynamic_debug/control

```

### 6. Magic SysRq Keys

#### Common SysRq Commands (via serial console)

- **Alt+SysRq+h**: Help (show all commands)

- **Alt+SysRq+t**: Show all tasks

- **Alt+SysRq+m**: Show memory usage

- **Alt+SysRq+p**: Show current CPU registers

- **Alt+SysRq+c**: Crash system (for debugging)

- **Alt+SysRq+s**: Sync filesystems

- **Alt+SysRq+u**: Remount filesystems read-only

- **Alt+SysRq+b**: Reboot system

#### Enable SysRq via proc

```bash

# Enable all SysRq functions

echo 1 > /proc/sys/kernel/sysrq

```

## Performance Impact

### Size Comparison

- **Ultra-minimal kernel**: ~1.6MB

- **Debug kernel**: ~3-4MB (due to debug info and symbols)

### Boot Time Impact

- **Additional boot time**: ~2-5 seconds (due to symbol loading)

- **Runtime overhead**: Minimal when tracers not active

### Memory Usage

- **Additional RAM**: ~2-4MB for symbols and debug structures

- **Debugging overhead**: Only when actively debugging

## Best Practices

### 1. Development Workflow

1. **Use ultra-minimal for production**: Fastest boot, smallest size

2. **Use debug kernel for development**: Full debugging capabilities

3. **Switch between kernels**: Update `local.conf` as needed

### 2. Debugging Strategy

1. **Start with dmesg**: Check kernel messages first

2. **Use serial console**: Primary debugging interface

3. **Enable specific tracers**: Only when needed to reduce overhead

4. **Use KGDB for complex issues**: Remote debugging for difficult problems

### 3. Common Debug Scenarios

#### Boot Issues

```bash

# Add to kernel command line for verbose boot

console=ttyO0,115200n8 earlyprintk=serial,ttyO0,115200 loglevel=8

```

#### Memory Issues

```bash

# Enable page allocation debugging

echo 1 > /sys/kernel/debug/pagealloc/enabled

```

#### Performance Issues

```bash

# Use function graph tracer to identify slow functions

echo function_graph > /sys/kernel/debug/tracing/current_tracer

```

## Troubleshooting

### Common Issues

1. **Serial console not working**: Check baud rate and cable

2. **KGDB not responding**: Ensure kernel compiled with KGDB support

3. **Debug FS not mounted**: Mount manually or check init scripts

4. **GDB connection fails**: Verify cross-GDB installation and target arch

### Debug Commands Quick Reference

```bash

# Check debug features

cat /proc/config.gz | gunzip | grep DEBUG

# Check available tracers

cat /sys/kernel/debug/tracing/available_tracers

# Check symbol table

cat /proc/kallsyms | head

# Check memory info

cat /proc/meminfo

# Check kernel version

uname -a

```

## Summary

The debuggable kernel provides comprehensive debugging capabilities while maintaining most optimizations. It's ideal for:

- **Kernel development and debugging**

- **Performance analysis and optimization**

- **Troubleshooting boot and runtime issues**

- **Learning kernel internals**

Switch between ultra-minimal and debug kernels based on your current needs:

- Production/demo: Use ultra-minimal kernel

- Development/debugging: Use debug kernel
