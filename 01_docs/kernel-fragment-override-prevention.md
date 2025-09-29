# How to Prevent Kernel's Built-in Fragments from Overriding Custom Configurations

## Overview

When customizing kernel configurations in Yocto, built-in kernel fragments (like `configs/features/scsi/scsi-debug.cfg`) can override your custom settings during the config merge process. This document explains various methods to prevent this and ensure your configurations have the final say.

## Problem Description

### The Issue
Yocto's kernel config merging process follows this order:
1. Base defconfig
2. Custom fragments (.cfg files)
3. **Built-in kernel fragments** ← These can override your settings
4. Final configuration resolution

### Example Scenario
```
CONFIG_SCSI_DEBUG : y ## .config: 869 :
    configs//./defconfig (y) 
    configs//./disable-scsi-debug.cfg (n) ← Your setting
    configs//features/scsi/scsi-debug.cfg (m) ← Built-in override
```

Result: Your `disable-scsi-debug.cfg` gets overridden by the built-in fragment.

## Solution Methods

### Method 1: Task Override (Recommended)

This is the most reliable method that forces your configuration after all fragments are processed.

**Implementation:**
```bitbake
# Force disable configs after all fragments are processed
do_kernel_configme:append() {
    # Remove existing lines for configs we want to control
    sed -i '/CONFIG_SCSI_DEBUG/d' ${B}/.config
    sed -i '/CONFIG_NET=/d' ${B}/.config
    
    # Force disable configurations
    echo "# CONFIG_SCSI_DEBUG is not set" >> ${B}/.config
    echo "# CONFIG_NET is not set" >> ${B}/.config
    
    # Rebuild config with dependencies resolved
    oe_runmake -C ${S} O=${B} olddefconfig
}
```

**Advantages:**
- ✅ Always works - runs after all fragment processing
- ✅ Handles dependencies automatically via `olddefconfig`
- ✅ Can override multiple configurations at once
- ✅ Clear and maintainable

**Example in Recipe:**
```bitbake
# In linux-yocto-srk-tiny_6.6.bb
SRC_URI += "file://defconfig \
            file://minimal-config.cfg"

do_kernel_configme:append() {
    # Remove and force disable SCSI
    sed -i '/CONFIG_SCSI=/d' ${B}/.config
    echo "# CONFIG_SCSI is not set" >> ${B}/.config
    oe_runmake -C ${S} O=${B} olddefconfig
}
```

### Method 2: Direct File Replacement

Replace the built-in fragment file directly in the kernel source tree.

**Implementation:**
```bitbake
SRC_URI += "file://my-scsi-debug.cfg;subdir=git/configs/features/scsi;name=scsi-debug"
```

**Advantages:**
- ✅ Replaces the problematic file at source
- ✅ No additional task overrides needed

**Disadvantages:**
- ❌ May not work for all fragment types
- ❌ Requires knowing exact kernel source paths
- ❌ Less reliable than task override

### Method 3: KERNEL_FEATURES Exclusion

Remove specific kernel features from being applied.

**Implementation:**
```bitbake
KERNEL_FEATURES:remove = "features/scsi/scsi-debug.scc"
```

**Advantages:**
- ✅ Clean removal of specific features
- ✅ Uses Yocto's intended mechanism

**Disadvantages:**
- ❌ Only works if the feature is defined as a .scc file
- ❌ May not catch all fragment sources

### Method 4: Patch-based Removal

Create a patch that removes the problematic fragment file entirely.

**Implementation:**
```bitbake
SRC_URI += "file://remove-scsi-debug-fragment.patch"
```

**Patch content:**
```diff
--- a/configs/features/scsi/scsi-debug.cfg
+++ /dev/null
@@ -1,1 +0,0 @@
-CONFIG_SCSI_DEBUG=m
```

**Advantages:**
- ✅ Permanently removes the conflicting file
- ✅ Standard patch mechanism

**Disadvantages:**
- ❌ Maintenance overhead for patches
- ❌ Kernel version dependent

## Best Practices

### 1. Use Method 1 (Task Override) for Most Cases
```bitbake
do_kernel_configme:append() {
    # Template for forcing config options
    sed -i '/CONFIG_OPTION_NAME/d' ${B}/.config
    echo "# CONFIG_OPTION_NAME is not set" >> ${B}/.config
    oe_runmake -C ${S} O=${B} olddefconfig
}
```

### 2. Group Related Configurations
```bitbake
do_kernel_configme:append() {
    # Network-related disables
    for option in NET IP_PNP ROOT_NFS NFS_FS TI_CPSW MII; do
        sed -i "/CONFIG_${option}/d" ${B}/.config
        echo "# CONFIG_${option} is not set" >> ${B}/.config
    done
    
    # SCSI-related disables
    for option in SCSI SCSI_DEBUG BLK_DEV_BSG; do
        sed -i "/CONFIG_${option}=/d" ${B}/.config
        echo "# CONFIG_${option} is not set" >> ${B}/.config
    done
    
    # Force enable critical options
    echo "CONFIG_SERIAL_8250=y" >> ${B}/.config
    echo "CONFIG_SERIAL_8250_CONSOLE=y" >> ${B}/.config
    
    oe_runmake -C ${S} O=${B} olddefconfig
}
```

### 3. Document Your Overrides
```bitbake
# Force minimal kernel configuration
# Prevents built-in fragments from enabling unwanted features
do_kernel_configme:append() {
    # Disable networking (prevents NFS, ethernet, wifi dependencies)
    sed -i '/CONFIG_NET=/d' ${B}/.config
    echo "# CONFIG_NET is not set" >> ${B}/.config
    
    # Disable SCSI subsystem (reduces kernel size)
    sed -i '/CONFIG_SCSI=/d' ${B}/.config
    echo "# CONFIG_SCSI is not set" >> ${B}/.config
    
    oe_runmake -C ${S} O=${B} olddefconfig
}
```

## Verification

### Check Configuration Application
```bash
# Build and check config
bitbake linux-yocto-srk-tiny -c cleansstate
bitbake linux-yocto-srk-tiny -c kernel_configcheck

# Verify final config
grep "CONFIG_SCSI_DEBUG" build/tmp/work/*/linux-yocto-srk-tiny/*/linux-*-build/.config
```

### Expected Results
```
# Before fix:
CONFIG_SCSI_DEBUG=m

# After fix:
# CONFIG_SCSI_DEBUG is not set
```

### Config Check Output Analysis
```
[INFO]: CONFIG_SCSI_DEBUG : n ## .config: 869 :
    configs//./defconfig (y) 
    configs//./minimal-config.cfg (n) 
    configs//features/scsi/scsi-debug.cfg (m) ← Built-in fragment
```

Final result should show `n` (disabled) despite built-in fragment trying to enable it.

## Troubleshooting

### Common Issues

1. **Configuration still enabled after override**
   - Check if `olddefconfig` is called after modifications
   - Verify sed patterns match exactly (watch for `=` vs no `=`)
   - Ensure task override is actually executing

2. **Dependency conflicts**
   - Use `olddefconfig` to resolve dependencies automatically
   - Check for conflicting enable/disable in same override

3. **Build failures after config changes**
   - Some options may be required by other kernel features
   - Test with `bitbake linux-yocto-srk-tiny -c kernel_configcheck` first

### Debug Commands
```bash
# Check if task override is executing
bitbake linux-yocto-srk-tiny -c kernel_configme -v

# View final merged config
bitbake linux-yocto-srk-tiny -c kernel_configcheck

# Check config file directly
find build/tmp/work -name ".config" -path "*linux-yocto-srk-tiny*"
```

## Real-World Example

**Recipe: `linux-yocto-srk-tiny_6.6.bb`**
```bitbake
require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Minimal kernel for BeagleBone with forced config overrides"
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://defconfig \
            file://minimal-config.cfg \
            file://am335x-yocto-srk-tiny.dts;subdir=git/arch/arm/boot/dts/ti/omap"

KCONFIG_MODE = "alldefconfig"
COMPATIBLE_MACHINE = "beaglebone-yocto-srk-tiny"

# Force minimal configuration - prevents built-in fragments from overriding
do_kernel_configme:append() {
    # Remove existing config lines we want to control
    sed -i '/CONFIG_SCSI_DEBUG/d' ${B}/.config
    sed -i '/CONFIG_NET=/d' ${B}/.config
    sed -i '/CONFIG_SCSI=/d' ${B}/.config
    
    # Force disable unwanted features
    echo "# CONFIG_SCSI_DEBUG is not set" >> ${B}/.config
    echo "# CONFIG_NET is not set" >> ${B}/.config
    echo "# CONFIG_SCSI is not set" >> ${B}/.config
    
    # Force enable required features
    echo "CONFIG_SERIAL_8250=y" >> ${B}/.config
    echo "CONFIG_SERIAL_8250_CONSOLE=y" >> ${B}/.config
    
    # Resolve dependencies and conflicts
    oe_runmake -C ${S} O=${B} olddefconfig
}
```

**Fragment: `minimal-config.cfg`**
```cfg
# Minimal kernel configuration fragment
# These settings may be overridden by built-in fragments
# The task override in the recipe ensures final application

# Disable networking
# CONFIG_NET is not set
# CONFIG_IP_PNP is not set
# CONFIG_ROOT_NFS is not set

# Disable SCSI
# CONFIG_SCSI is not set
# CONFIG_SCSI_DEBUG is not set

# Enable serial console
CONFIG_SERIAL_8250=y
CONFIG_SERIAL_8250_CONSOLE=y
```

## Summary

The **task override method** (`do_kernel_configme:append()`) is the most reliable approach for preventing built-in kernel fragments from overriding your custom configurations. It ensures your settings are applied after all fragment processing and automatically resolves configuration dependencies.

This method is essential for creating truly minimal kernel configurations where you need absolute control over which features are enabled or disabled.