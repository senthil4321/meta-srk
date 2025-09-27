#!/bin/bash

# Script to create disable-peripherals.patch
# This script modifies the BeagleBone Black DTS files to disable unused peripherals
# and generates a patch from the changes.

set -e

# Define paths
KERNEL_SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/work-shared/beaglebone-yocto/kernel-source"
PATCH_DIR="/home/srk2cob/project/poky/meta-srk/recipes-kernel/linux/linux-yocto-srk-tiny/patches"
PATCH_FILE="$PATCH_DIR/disable-peripherals.patch"

echo "Creating disable-peripherals.patch..."

# Reset the DTS files to original state
cd "$KERNEL_SOURCE_DIR"
git checkout arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi
git checkout arch/arm/boot/dts/ti/omap/am335x-boneblack-common.dtsi

# Modify am335x-bone-common.dtsi to disable peripherals
# Enable UART0 (change status from disabled to okay)
sed -i '/&uart0 {/,/};/ { s/status = "disabled";/status = "okay";/ }' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable USB0
# sed -i '/&usb0 {/a\\tstatus = "disabled";' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable USB1
# sed -i '/&usb1 {/a\\tstatus = "disabled";' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable I2C0
sed -i '/&i2c0 {/,/};/ { s/status = "okay";/status = "disabled";/ }' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable I2C2
sed -i '/&i2c2 {/,/};/ { s/status = "okay";/status = "disabled";/ }' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable CPSW_PORT1
sed -i '/&cpsw_port1 {/a\\tstatus = "disabled";' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable MAC_SW (change status from okay to disabled)
# sed -i 's/status = "okay";/status = "disabled";/' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable DAVINCI_MDIO_SW
sed -i '/&davinci_mdio_sw {/a\\tstatus = "disabled";' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable AES
sed -i '/&aes {/,/};/ { s/status = "okay";/status = "disabled";/ }' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable SHAM
sed -i '/&sham {/,/};/ { s/status = "okay";/status = "disabled";/ }' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable RTC
sed -i '/&rtc {/,/};/ { s/status = "okay";/status = "disabled";/ }' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Disable PRUSS_TM
sed -i '/&pruss_tm {/,/};/ { s/status = "okay";/status = "disabled";/ }' arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi

# Modify am335x-boneblack-common.dtsi to disable MMC
# Disable MMC1
# sed -i '/&mmc1 {/a\\tstatus = "disabled";' arch/arm/boot/dts/ti/omap/am335x-boneblack-common.dtsi

# Disable MMC2
# sed -i '/&mmc2 {/a\\tstatus = "disabled";' arch/arm/boot/dts/ti/omap/am335x-boneblack-common.dtsi

# Validate DTS syntax after modifications
echo "Validating DTS syntax..."
echo "Note: DTS validation skipped due to include dependencies"
# if command -v dtc >/dev/null 2>&1; then
#     if ! dtc -I dts -O dtb arch/arm/boot/dts/ti/omap/am335x-bone.dts >/dev/null 2>&1; then
#         echo "Error: DTS syntax error detected after modifications"
#         echo "Check the sed commands for malformed output"
#         exit 1
#     fi
# else
#     echo "Warning: dtc not found, skipping DTS validation"
# fi

# Generate the patch
git diff arch/arm/boot/dts/ti/omap/am335x-bone-common.dtsi arch/arm/boot/dts/ti/omap/am335x-boneblack-common.dtsi > "$PATCH_FILE.tmp"

# Validate patch content
if ! grep -q "diff --git" "$PATCH_FILE.tmp"; then
    echo "Error: Generated patch appears malformed"
    echo "Check sed commands and git diff output"
    exit 1
fi

# Add Upstream-Status header
echo "Upstream-Status: Inappropriate [disable unused peripherals for faster boot]" > "$PATCH_FILE"
echo "" >> "$PATCH_FILE"
cat "$PATCH_FILE.tmp" >> "$PATCH_FILE"
rm "$PATCH_FILE.tmp"

echo "Patch created successfully: $PATCH_FILE"