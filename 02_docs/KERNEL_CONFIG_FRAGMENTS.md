# Kernel Configuration Fragments in Yocto - Problem and Solution

## Date: October 30, 2025

## Problem Statement

When attempting to enable TI OMAP hardware crypto accelerators (SHA and AES) in the BeagleBone Black kernel, the kernel configuration options were not being applied despite:

1. Creating a `.cfg` configuration fragment file (`omap-hwcrypto.cfg`)
2. Adding it to `SRC_URI` in the kernel recipe
3. Successfully building the kernel

The configuration options remained disabled in the final kernel `.config` file.

## Root Cause Analysis

### Investigation Steps

1. **Initial Attempt**: Added `omap-hwcrypto.cfg` directly to `SRC_URI`:
   ```bitbake
   SRC_URI += "file://defconfig \
               file://omap-hwcrypto.cfg \
               "
   ```

2. **Verification**: Checked the kernel configuration merge log:
   ```bash
   grep -i "omap" tmp/work/.../temp/log.do_kernel_configme
   ```
   Result: No matches - the fragment wasn't being processed

3. **Log Analysis**: Examined the kernel metadata processing log:
   ```bash
   tail -100 tmp/work/.../temp/log.do_kernel_configme
   ```
   
   Key finding in the log:
   ```
   NOTE: Fragments from SRC_URI:
   NOTE: KERNEL_FEATURES:  cfg/fs/vfat.scc features/netfilter/netfilter.scc ...
   NOTE: Final scc/cfg list: /path/to/defconfig  cfg/fs/vfat.scc ...
   ```
   
   **The "Fragments from SRC_URI" line was EMPTY!**

### Root Cause

**Yocto's linux-yocto kernel uses a specialized metadata system (kernel-tools) that requires configuration fragments to be wrapped in `.scc` (System Configuration Container) files.**

Simply adding `.cfg` files to `SRC_URI` does NOT automatically make them available to the kernel configuration merge process. The kernel-tools metadata scanner looks for:

1. `.scc` files that reference `.cfg` files
2. Entries in `KERNEL_FEATURES` variable
3. BSP-specific configuration from the machine definition

Raw `.cfg` files in `SRC_URI` are fetched but ignored by the kernel configuration system.

## Solution

### Step 1: Create an `.scc` Feature File

Create `omap-hwcrypto.scc` to wrap the configuration fragment:

```scc
# Enable TI OMAP hardware crypto accelerators (SHA, AES)
define KFEATURE_DESCRIPTION "Enable TI OMAP hardware crypto accelerators"

kconf hardware omap-hwcrypto.cfg
```

**File location**: `meta-srk/recipes-kernel/linux/linux-yocto-srk/omap-hwcrypto.scc`

### Step 2: Update the Kernel Recipe

Modify `linux-yocto-srk_6.6.bb`:

```bitbake
require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://defconfig \
            file://omap-hwcrypto.scc \
            file://omap-hwcrypto.cfg \
            "

# Add the .scc file to KERNEL_FEATURES with full path
KERNEL_FEATURES:append = " ${THISDIR}/${PN}/omap-hwcrypto.scc"

KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto|beaglebone-yocto-srk"
```

### Step 3: The Configuration Fragment

The actual kernel configuration options in `omap-hwcrypto.cfg`:

```kconfig
# Hardware crypto support
CONFIG_CRYPTO_HW=y
CONFIG_CRYPTO_ENGINE=y

# TI OMAP hardware crypto accelerators
CONFIG_CRYPTO_DEV_OMAP=y
CONFIG_CRYPTO_DEV_OMAP_SHAM=y
CONFIG_CRYPTO_DEV_OMAP_AES=y
CONFIG_CRYPTO_DEV_OMAP_DES=y
```

### Step 4: Rebuild

```bash
cd /path/to/poky/build
bitbake -c cleansstate virtual/kernel
bitbake virtual/kernel
```

## Key Learnings

### What Works

1. **`.scc` files are mandatory** for linux-yocto kernel customization
2. **Full path in KERNEL_FEATURES** ensures the metadata scanner can find the files:
   ```bitbake
   KERNEL_FEATURES:append = " ${THISDIR}/${PN}/feature.scc"
   ```
3. **Both files must be in SRC_URI**:
   - The `.scc` file (feature descriptor)
   - The `.cfg` file (actual configuration)

### What Doesn't Work

1. ❌ Adding only `.cfg` files to `SRC_URI`
2. ❌ Adding `.scc` filename without path to `KERNEL_FEATURES`:
   ```bitbake
   KERNEL_FEATURES:append = " omap-hwcrypto.scc"  # File not found!
   ```
3. ❌ Expecting raw `.cfg` files to be automatically processed

## Verification

After successful build, verify the configuration:

```bash
# Check in build directory
grep CONFIG_CRYPTO_DEV_OMAP \
  tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto-srk/*/linux-*-build/.config

# Check on deployed system
ssh root@beaglebone "zcat /proc/config.gz | grep CONFIG_CRYPTO_DEV_OMAP"
```

Expected output:
```
CONFIG_CRYPTO_DEV_OMAP=y
CONFIG_CRYPTO_DEV_OMAP_SHAM=y
CONFIG_CRYPTO_DEV_OMAP_AES=y
```

## References

- **Yocto Kernel Development Manual**: https://docs.yoctoproject.org/kernel-dev/
- **BSP Configuration Fragments**: https://docs.yoctoproject.org/kernel-dev/common.html#creating-config-fragments
- **linux-yocto Metadata**: https://docs.yoctoproject.org/kernel-dev/advanced.html#working-with-linux-yocto-advanced-metadata

## Related Files

- Recipe: `meta-srk/recipes-kernel/linux/linux-yocto-srk_6.6.bb`
- Feature file: `meta-srk/recipes-kernel/linux/linux-yocto-srk/omap-hwcrypto.scc`
- Config fragment: `meta-srk/recipes-kernel/linux/linux-yocto-srk/omap-hwcrypto.cfg`

## Impact

Enabling the OMAP hardware crypto accelerators should provide significant performance improvements for cryptographic operations on BeagleBone Black:

- **SHA-1/SHA-256 hardware acceleration** for disk encryption, file verification
- **AES hardware acceleration** for dm-crypt, ipsec
- Expected 2-5x performance improvement vs software crypto
- Lower CPU utilization for cryptographic operations
