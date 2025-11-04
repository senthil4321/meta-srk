require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

# Add defconfig
SRC_URI += "file://defconfig"

# Add OMAP hardware crypto configuration fragment
SRC_URI += "file://omap-hwcrypto.cfg"

# Add LED support for BeagleBone user LEDs
SRC_URI += "file://leds.cfg"

# Add kernel printk timestamps
SRC_URI += "file://printk_time.cfg"

# Add AM33xx PM support for suspend-to-RAM - DISABLED
# SRC_URI += "file://pm33xx.cfg"

# Add Trust M Crypto Co-Processor support
SRC_URI += "file://trustm.cfg"

# Add PRU (Programmable Real-time Unit) support
SRC_URI += "file://pru.cfg"

KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto|beaglebone-yocto-srk"

# Depend on PM firmware for building it into kernel - DISABLED
# DEPENDS += "am335x-pm-firmware"

# Copy PM firmware to kernel source for CONFIG_EXTRA_FIRMWARE
do_configure:prepend() {
    # Create firmware directory in kernel source
    mkdir -p ${S}/firmware
    
    # Copy PM firmware from staging
    if [ -f "${STAGING_DIR_HOST}${base_libdir}/firmware/am335x-pm-firmware.elf" ]; then
        cp ${STAGING_DIR_HOST}${base_libdir}/firmware/am335x-pm-firmware.elf ${S}/firmware/
        echo "Copied PM firmware to kernel source"
    else
        bbwarn "PM firmware not found in staging, firmware may not load"
    fi
}

# Force enable PM drivers that may not be enabled by fragment merging
do_configure:append() {
    # Force enable WKUP_M3_IPC and AMX3_PM in .config
    sed -i 's/# CONFIG_WKUP_M3_IPC is not set/CONFIG_WKUP_M3_IPC=y/' ${B}/.config
    sed -i 's/# CONFIG_AMX3_PM is not set/CONFIG_AMX3_PM=y/' ${B}/.config
    
    # Add them if they don't exist at all
    grep -q "CONFIG_WKUP_M3_IPC" ${B}/.config || echo "CONFIG_WKUP_M3_IPC=y" >> ${B}/.config
    grep -q "CONFIG_AMX3_PM" ${B}/.config || echo "CONFIG_AMX3_PM=y" >> ${B}/.config
    
    # Re-run oldconfig to validate
    oe_runmake -C ${S} O=${B} olddefconfig
    
    # Verify the configs are set
    echo "Verifying PM configs..."
    grep "CONFIG_WKUP_M3_IPC" ${B}/.config || echo "WARNING: CONFIG_WKUP_M3_IPC not found"
    grep "CONFIG_AMX3_PM" ${B}/.config || echo "WARNING: CONFIG_AMX3_PM not found"
}
