# Yocto Kernel Build with Embedded Initramfs

## Overview

This document outlines the process of building a minimal Yocto kernel with an embedded initramfs for the BeagleBone Black board. The goal is to create a self-contained kernel image that includes the initial ramdisk, eliminating the need for separate initramfs loading and resolving boot issues like "No working init found".

## Prerequisites

- Yocto Project (Poky 5.1)
- meta-srk layer
- BeagleBone Black target machine
- Basic understanding of Yocto build system

## Process Steps

### 1. Kernel Configuration Verification

**Objective**: Ensure the kernel supports initramfs compression formats.

**Verification**:

- Checked kernel config for compression support
- Confirmed support for: gzip, bzip2, lzma, xz, lzo, lz4, zstd

**Command**:

```bash
grep -i initramfs /path/to/.config
```

### 2. Initramfs Image Preparation

**Objective**: Create a minimal initramfs with a proper `/init` binary.

**Key Requirements**:

- `/init` must be a binary, not a symlink
- Minimal footprint for embedded use
- Compatible with kernel architecture

**Recipe**: `core-image-tiny-initramfs-srk-9-nobusybox.bb`

- Removes BusyBox entirely
- Provides static `/init` replacement
- Sets `IMAGE_FSTYPES = "cpio.gz cpio.xz cpio.lz4"`

### 3. Kernel Recipe Configuration

**File**: `linux-yocto-srk-tiny_6.6.bb`

**Essential Settings**:

```bitbake
INITRAMFS_IMAGE = "core-image-tiny-initramfs-srk-9-nobusybox"
INITRAMFS_IMAGE_BUNDLE = "1"
INITRAMFS_IMAGE_NAME = "core-image-tiny-initramfs-srk-9-nobusybox-beaglebone-yocto.rootfs"
INSANE_SKIP:kernel-dev = "buildpaths"
```

**Explanation**:

- `INITRAMFS_IMAGE`: Specifies the initramfs image to embed
- `INITRAMFS_IMAGE_BUNDLE = "1"`: Enables embedding initramfs into kernel image
- `INITRAMFS_IMAGE_NAME`: Correct filename including `.rootfs` suffix
- `INSANE_SKIP`: Bypasses QA checks for build paths

### 4. Build Process

**Commands**:

```bash
cd /home/srk2cob/project/poky
source oe-init-build-env build
bitbake linux-yocto-srk-tiny
```

**Expected Output**:

- Regular kernel: `zImage` (~2.1MB)
- Embedded kernel: `zImage-initramfs` (~2.6MB, +~500KB for initramfs)

### 5. Verification

**Size Check**:

```bash
ls -lh /path/to/deploy/images/beaglebone-yocto/zImage*
```

**Embedded Content Verification**:

- Size increase should match initramfs archive size
- Kernel config should show initramfs source properly set

## Troubleshooting

### Common Issues

1. **"Could not find initramfs archive"**

   - **Cause**: Incorrect `INITRAMFS_IMAGE_NAME`
   - **Solution**: Ensure `.rootfs` suffix is included

2. **QA Buildpaths Error**

   - **Cause**: Kernel package contains TMPDIR references
   - **Solution**: Add `INSANE_SKIP:kernel-dev = "buildpaths"`

3. **"No working init found" Panic**

   - **Cause**: `/init` is a symlink or missing
   - **Solution**: Ensure initramfs provides binary `/init`

4. **Kernel Config Warnings**

   - **Cause**: Fragment mismatches
   - **Solution**: Review and adjust kernel config fragments

### Debug Commands

```bash
# Check kernel config
grep -i initramfs /path/to/.config

# Verify initramfs content
ls -la /path/to/rootfs/

# Check build logs
bitbake -c devshell linux-yocto-srk-tiny
```

## Deployment

### Copy to SD Card

Use the provided scripts:

```bash
./04_copy_zImage.sh
./05_copy_squashfs.sh
```

Or manually:

```bash
cp zImage-initramfs-beaglebone-yocto.bin /path/to/sdcard/boot/zImage
```

### Boot Testing

1. Insert SD card into BeagleBone Black
2. Power on and monitor serial console
3. Verify kernel boots without initramfs loading errors

## Key Files Modified

- `recipes-kernel/linux/linux-yocto-srk-tiny_6.6.bb`: Kernel recipe
- `recipes-srk/images/core-image-tiny-initramfs-srk-9-nobusybox.bb`: Initramfs recipe
- `recipes-kernel/linux/linux-yocto-srk/defconfig`: Kernel configuration

## Results

- ✅ Kernel builds successfully with embedded initramfs
- ✅ Size increase matches initramfs content
- ✅ Resolves "No working init found" boot issues
- ✅ Maintains minimal footprint for embedded systems

## Notes

- The process uses Yocto's built-in initramfs bundling mechanism
- Compression format can be changed via `IMAGE_FSTYPES` in initramfs recipe
- Kernel config fragments should be reviewed for consistency
- QA skips are necessary for certain build environments