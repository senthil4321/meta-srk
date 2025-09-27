# BeagleBone Black Peripheral Disable Workflow

## Overview

This workflow provides automated scripts to disable unused peripherals in the BeagleBone Black device tree for faster boot times. The scripts generate, apply, and test patches that disable hardware components not needed for minimal embedded systems.

## What Gets Disabled

The current patch disables the following peripherals:

### USB

- `&usb0` (USB0 controller)
- `&usb1` (USB1 controller)

### Ethernet

- `&cpsw_port1` (Ethernet port 1)
- `&mac_sw` (Ethernet switch)
- `&davinci_mdio_sw` (MDIO switch)

### Storage

- `&mmc1` (SD card slot)
- `&mmc2` (eMMC on BeagleBone Black)

### I2C

- `&i2c0` (I2C bus 0)
- `&i2c2` (I2C bus 2)

### Serial

- `&uart0` (UART0)

### Cryptography

- `&aes` (AES encryption)
- `&sham` (SHA/MD5 hash)

### Real Time Clock

- `&rtc` (RTC)

### Power Management

- `charger` (Battery charger)
- `pwrbutton` (Power button)

### Other

- `&pruss_tm` (PRU subsystem timer)

## Prerequisites

1. **Yocto Build Environment**: Poky build system set up for BeagleBone Black
2. **Kernel Source**: Linux kernel source available at `/home/srk2cob/project/poky/build/tmp/work-shared/beaglebone-yocto/kernel-source`
3. **Bash**: Scripts require bash shell
4. **Git**: For patch generation and source control

## File Structure

```
meta-srk/
├── scripts/
│   ├── create_patch.sh          # Generates disable-peripherals.patch
│   ├── apply_patch.sh           # Applies the patch to kernel source
│   └── test_patch.sh           # Builds kernel to verify patch
├── recipes-kernel/linux/linux-yocto-srk-tiny/
│   └── patches/
│       └── disable-peripherals.patch  # Generated patch file
└── patch_instruction.md         # This file
```

## Usage

### 1. Generate Patch

```bash
cd /home/srk2cob/project/poky/meta-srk/scripts
./create_patch.sh
```

This script:

- Resets DTS files to original state
- Adds `status = "disabled";` to unused peripherals
- Generates `disable-peripherals.patch` using `git diff`

### 2. Apply Patch

```bash
cd /home/srk2cob/project/poky/meta-srk/scripts
./apply_patch.sh
```

This script applies the patch to the kernel source using `git apply`.

### 3. Test Build

```bash
cd /home/srk2cob/project/poky/meta-srk/scripts
./test_patch.sh
```

This script:

- Builds the kernel using bitbake
- Verifies the patch doesn't break compilation
- Reports success/failure

### 4. Full Workflow

```bash
cd /home/srk2cob/project/poky/meta-srk/scripts
./create_patch.sh && ./apply_patch.sh && ./test_patch.sh
```

## How It Works

### Patch Generation Process

1. **Reset to Clean State**: `git checkout` ensures clean DTS files
2. **Selective Disable**: Uses `sed` to insert `status = "disabled";` after section headers
3. **Patch Creation**: `git diff` generates patch from changes
4. **Header Addition**: Adds Yocto Upstream-Status header

### Sed Commands Used

The scripts use simple, reliable sed commands:

```bash
# Insert status disabled after section header
sed -i '/&peripheral {/a\\tstatus = "disabled";' file.dtsi

# Change existing status
sed -i 's/status = "okay";/status = "disabled";/' file.dtsi
```

## Adding New Peripherals

To disable additional peripherals:

1. **Identify the Section**: Find the peripheral node in the DTS files
2. **Add to Script**: Add a sed command in `create_patch.sh`
3. **Test**: Run the full workflow to verify

Example for disabling SPI:

```bash
# In create_patch.sh
sed -i '/&spi0 {/a\\tstatus = "disabled";' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi
```

## Troubleshooting

### Common Issues

1. **"Patch does not apply cleanly"**
   - Kernel source may be modified
   - Run: `cd /path/to/kernel/source && git reset --hard`

2. **"Syntax error in DTS"**
   - Check patch content for malformed lines
   - Verify sed commands produce correct output

3. **"Git status shows unexpected changes"**
   - Reset kernel source: `git reset --hard HEAD`
   - Clean untracked files: `git clean -fd`

4. **"Build fails with config warnings"**
   - Warnings about CONFIG_* mismatches are normal
   - Only errors indicate real problems

### Debug Commands

```bash
# Check current kernel source state
cd /home/srk2cob/project/poky/build/tmp/work-shared/beaglebone-yocto/kernel-source
git status

# Verify DTS syntax
dtc -I dts -O dtb arch/arm/boot/dts/ti/omap/am335x-bone.dts

# Check patch content
head -50 /home/srk2cob/project/poky/meta-srk/recipes-kernel/linux/linux-yocto-srk-tiny/patches/disable-peripherals.patch
```

## Performance Impact

Disabling these peripherals typically reduces:

- **Boot time**: 2-5 seconds faster
- **Memory usage**: Reduced device tree size
- **Power consumption**: Less hardware initialization
- **Kernel size**: Smaller image

## Integration with Yocto

The patch is automatically applied during kernel build via the recipe:

```
recipes-kernel/linux/linux-yocto-srk-tiny_6.6.bb
```

Contains:

```
SRC_URI += "file://disable-peripherals.patch"
```

## Extending the Workflow

### For Different Boards

1. Update DTS file paths in scripts
2. Identify board-specific peripherals to disable
3. Test on target hardware

### For Different Kernel Versions

1. Verify peripheral node names haven't changed
2. Update kernel source path if needed
3. Test patch application

## Best Practices

1. **Always test patches** before committing to recipes
2. **Keep patches minimal** - only disable truly unused peripherals
3. **Document changes** - update this README when adding peripherals
4. **Version control** - commit working patches to git
5. **Backup** - keep original DTS files before modification

## Files Modified

The patch modifies:

- `arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi`
- `arch/arm/boot/dts/ti/omap/am335x-boneblack-common.dtsi`

These are included by the main BeagleBone Black DTS file.
