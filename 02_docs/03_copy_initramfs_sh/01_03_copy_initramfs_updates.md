# 03_copy_initramfs.sh Script Updates

## Summary of Changes

I've successfully updated the `03_copy_initramfs.sh` script according to your specifications:

### ✅ **1. Changed Default Machine**
- **Before**: `beaglebone-yocto-srk` 
- **After**: `beaglebone-yocto` (default when no `-m` specified)

### ✅ **2. Added Machine Short Aliases**
- **`-m -srk`** → `beaglebone-yocto-srk`
- **`-m -tiny`** → `beaglebone-yocto-srk-tiny`
- Full names still supported: `-m beaglebone-yocto-srk`, `-m beaglebone-yocto-srk-tiny`

### ✅ **3. Implemented Number-to-Image Mapping**
Complete mapping for all existing images (excluding debug variant as requested):

| Number | Maps to |
|--------|---------|
| 1 | core-image-tiny-initramfs-srk-1 |
| 2 | core-image-tiny-initramfs-srk-2 |
| 3 | core-image-tiny-initramfs-srk-3 |
| 4 | core-image-tiny-initramfs-srk-4-nocrypt |
| 5 | core-image-tiny-initramfs-srk-5 |
| 6 | core-image-tiny-initramfs-srk-6 |
| 7 | core-image-tiny-initramfs-srk-7-sizeopt |
| 8 | core-image-tiny-initramfs-srk-8-nonet |
| 9 | core-image-tiny-initramfs-srk-9-nobusybox |
| 10 | core-image-tiny-initramfs-srk-10-selinux |
| 11 | core-image-tiny-initramfs-srk-11-bbb-examples |

### ✅ **4. Flexible Argument Order**
Both command formats now work:
```bash
./03_copy_initramfs.sh 11 -m -srk          # Version first
./03_copy_initramfs.sh -m -srk 11          # Options first
```

## Usage Examples

### **Basic Usage (Default Machine: beaglebone-yocto)**
```bash
./03_copy_initramfs.sh 11                  # BBB examples with default machine
./03_copy_initramfs.sh 4                   # No-crypt variant with default machine
```

### **With Machine Aliases**
```bash
./03_copy_initramfs.sh 11 -m -srk          # BBB examples with beaglebone-yocto-srk
./03_copy_initramfs.sh 9 -m -tiny          # No-busybox with beaglebone-yocto-srk-tiny
```

### **With Full Machine Names**
```bash
./03_copy_initramfs.sh 10 -m beaglebone-yocto-srk        # SELinux with full name
./03_copy_initramfs.sh 3 -m beaglebone-yocto-srk-tiny    # Version 3 with tiny
```

### **Flexible Argument Order**
```bash
./03_copy_initramfs.sh -m -srk 11          # Options first
./03_copy_initramfs.sh 11 -m -srk          # Version first
```

## Technical Implementation

### **Argument Parsing**
- Replaced `getopts` with manual parsing to support flexible argument order
- Validates machine names and aliases
- Provides clear error messages for invalid options

### **Image Mapping Function**
```bash
map_version_to_image() {
    case "$version" in
        1) echo "core-image-tiny-initramfs-srk-1" ;;
        4) echo "core-image-tiny-initramfs-srk-4-nocrypt" ;;
        # ... complete mapping table
    esac
}
```

### **Machine Support**
- **Default**: `beaglebone-yocto`
- **Full Names**: `beaglebone-yocto-srk`, `beaglebone-yocto-srk-tiny`
- **Aliases**: `-srk`, `-tiny`

## Validation Tests

### ✅ **Default Behavior**
```bash
$ ./03_copy_initramfs.sh 11
# Uses: core-image-tiny-initramfs-srk-11-bbb-examples-beaglebone-yocto.rootfs.cpio.gz
# Machine: beaglebone-yocto
```

### ✅ **Machine Aliases**
```bash
$ ./03_copy_initramfs.sh 11 -m -srk
# Uses: core-image-tiny-initramfs-srk-11-bbb-examples-beaglebone-yocto-srk.rootfs.cpio.gz
# Machine: beaglebone-yocto-srk
```

### ✅ **Number Mapping**
```bash
$ ./03_copy_initramfs.sh 4 -m -srk
# Looks for: core-image-tiny-initramfs-srk-4-nocrypt-beaglebone-yocto-srk.rootfs.cpio.gz
```

### ✅ **Error Handling**
- Invalid machine names show clear error messages
- Missing version arguments detected
- Non-existent images show helpful source directory info

## Script Features Preserved

- ✅ SSH-based deployment to remote target
- ✅ Automatic NFS extraction 
- ✅ Fallback file matching for suffixed variants
- ✅ Comprehensive help system
- ✅ Version information display

## Help Output

The script now shows complete mapping information:
```bash
$ ./03_copy_initramfs.sh -h

Usage: ./03_copy_initramfs.sh <version> [options]

<version> can be one of:
    1              -> core-image-tiny-initramfs-srk-1
    2              -> core-image-tiny-initramfs-srk-2
    3              -> core-image-tiny-initramfs-srk-3
    4              -> core-image-tiny-initramfs-srk-4-nocrypt
    5              -> core-image-tiny-initramfs-srk-5
    6              -> core-image-tiny-initramfs-srk-6
    7              -> core-image-tiny-initramfs-srk-7-sizeopt
    8              -> core-image-tiny-initramfs-srk-8-nonet
    9              -> core-image-tiny-initramfs-srk-9-nobusybox (BusyBox removed)
    10             -> core-image-tiny-initramfs-srk-10-selinux (SELinux enabled)
    11             -> core-image-tiny-initramfs-srk-11-bbb-examples (BBB hardware examples)
    <number>-<suffix> -> core-image-tiny-initramfs-srk-<number>-<suffix> (custom format)

Options:
    -m <machine>   Machine target (default: beaglebone-yocto)
                   Valid options: beaglebone-yocto, beaglebone-yocto-srk, beaglebone-yocto-srk-tiny
                   Short aliases: -srk (for beaglebone-yocto-srk), -tiny (for beaglebone-yocto-srk-tiny)
```

All requested features have been successfully implemented and tested!