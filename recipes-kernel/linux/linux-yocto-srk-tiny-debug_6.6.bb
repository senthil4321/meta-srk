require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Debuggable Linux kernel based on linux-yocto from srk with debugging enabled"
FILESEXTRAPATHS:prepend := "${THISDIR}/linux-yocto-srk-tiny:"

# Use same config fragments but exclude debugging optimization and add debug config
SRC_URI += "file://defconfig \
            file://disable-scsi-debug.cfg \
            file://minimal-config.cfg \
            file://disable-rng.cfg \
            file://disable-ti-sysc.cfg \
            file://optimization_01_filesystem_optimization.cfg \
            file://optimization_02_sound_multimedia.cfg \
            file://optimization_03_wireless_bluetooth.cfg \
            file://optimization_04_graphics_display.cfg \
            file://optimization_05_crypto_security.cfg \
            file://optimization_07_power_management.cfg \
            file://optimization_08_profiling_tracing.cfg \
            file://optimization_09_memory_features.cfg \
            file://optimization_10_final_cleanup.cfg \
            file://debug-config.cfg \
            file://am335x-yocto-srk-tiny.dts;subdir=git/arch/arm/boot/dts/ti/omap"

# Note: Deliberately excluding optimization_06_kernel_debugging.cfg to keep debug features

# Force disable multiple configs after all fragments are processed
do_kernel_configme:append() {
    # Remove existing lines for configs we want to control
    sed -i '/CONFIG_SCSI_DEBUG/d' ${B}/.config
    sed -i '/CONFIG_IP_PNP/d' ${B}/.config
    sed -i '/CONFIG_ROOT_NFS/d' ${B}/.config
    sed -i '/CONFIG_NFS_FS/d' ${B}/.config
    sed -i '/CONFIG_NET=/d' ${B}/.config
    sed -i '/CONFIG_TI_CPSW/d' ${B}/.config
    sed -i '/CONFIG_MII/d' ${B}/.config
    sed -i '/CONFIG_CFG80211/d' ${B}/.config
    sed -i '/CONFIG_MAC80211/d' ${B}/.config
    sed -i '/CONFIG_BT=/d' ${B}/.config
    sed -i '/CONFIG_SCSI=/d' ${B}/.config
    sed -i '/CONFIG_BLK_DEV_BSG/d' ${B}/.config
    sed -i '/CONFIG_HW_RANDOM/d' ${B}/.config
    sed -i '/CONFIG_HW_RANDOM_OMAP/d' ${B}/.config
    sed -i '/CONFIG_MODULES/d' ${B}/.config
    sed -i '/CONFIG_PM/d' ${B}/.config
    sed -i '/CONFIG_INPUT/d' ${B}/.config
    sed -i '/CONFIG_VT/d' ${B}/.config
    sed -i '/CONFIG_USB_SUPPORT/d' ${B}/.config
    sed -i '/CONFIG_USB_DWC3_OMAP/d' ${B}/.config
    sed -i '/CONFIG_USB_MUSB_OMAP2PLUS/d' ${B}/.config
    sed -i '/CONFIG_OMAP_USB2/d' ${B}/.config
    sed -i '/CONFIG_OMAP_USB3/d' ${B}/.config
    sed -i '/CONFIG_OMAP_CONTROL_PHY/d' ${B}/.config
    
    # Force disable most optimizations (but keep debug features)
    echo "# CONFIG_SCSI_DEBUG is not set" >> ${B}/.config
    echo "# CONFIG_IP_PNP is not set" >> ${B}/.config
    echo "# CONFIG_ROOT_NFS is not set" >> ${B}/.config
    echo "# CONFIG_NFS_FS is not set" >> ${B}/.config
    echo "# CONFIG_NET is not set" >> ${B}/.config
    echo "# CONFIG_TI_CPSW is not set" >> ${B}/.config
    echo "# CONFIG_MII is not set" >> ${B}/.config
    echo "# CONFIG_CFG80211 is not set" >> ${B}/.config
    echo "# CONFIG_MAC80211 is not set" >> ${B}/.config
    echo "# CONFIG_BT is not set" >> ${B}/.config
    echo "# CONFIG_SCSI is not set" >> ${B}/.config
    echo "# CONFIG_BLK_DEV_BSG is not set" >> ${B}/.config
    echo "# CONFIG_HW_RANDOM is not set" >> ${B}/.config
    echo "# CONFIG_HW_RANDOM_OMAP is not set" >> ${B}/.config
    
    # Keep minimal optimizations but enable debugging
    echo "# CONFIG_MODULES is not set" >> ${B}/.config
    echo "# CONFIG_PM is not set" >> ${B}/.config
    echo "# CONFIG_INPUT is not set" >> ${B}/.config
    echo "# CONFIG_VT is not set" >> ${B}/.config
    echo "# CONFIG_USB_SUPPORT is not set" >> ${B}/.config
    echo "# CONFIG_USB_DWC3_OMAP is not set" >> ${B}/.config
    echo "# CONFIG_USB_MUSB_OMAP2PLUS is not set" >> ${B}/.config
    echo "# CONFIG_OMAP_USB2 is not set" >> ${B}/.config
    echo "# CONFIG_OMAP_USB3 is not set" >> ${B}/.config
    echo "# CONFIG_OMAP_CONTROL_PHY is not set" >> ${B}/.config
    
    # ENABLE debugging features (opposite of optimization_06)
    echo "CONFIG_DEBUG_INFO=y" >> ${B}/.config
    echo "CONFIG_DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT=y" >> ${B}/.config
    echo "CONFIG_DEBUG_FS=y" >> ${B}/.config
    echo "CONFIG_MAGIC_SYSRQ=y" >> ${B}/.config
    
    # Additional debugging features
    echo "CONFIG_DEBUG_KERNEL=y" >> ${B}/.config
    echo "CONFIG_KALLSYMS=y" >> ${B}/.config
    echo "CONFIG_KALLSYMS_ALL=y" >> ${B}/.config
    echo "CONFIG_FRAME_POINTER=y" >> ${B}/.config
    echo "CONFIG_FUNCTION_TRACER=y" >> ${B}/.config
    echo "CONFIG_DYNAMIC_DEBUG=y" >> ${B}/.config
    echo "CONFIG_EARLY_PRINTK=y" >> ${B}/.config
    echo "CONFIG_DEBUG_BUGVERBOSE=y" >> ${B}/.config
    
    # Force enable serial console
    echo "CONFIG_SERIAL_8250=y" >> ${B}/.config
    echo "CONFIG_SERIAL_8250_CONSOLE=y" >> ${B}/.config
    
    # Enable GDB stub for kernel debugging (if available)
    echo "CONFIG_KGDB=y" >> ${B}/.config
    echo "CONFIG_KGDB_SERIAL_CONSOLE=y" >> ${B}/.config
    
    # Rebuild config with dependencies resolved
    oe_runmake -C ${S} O=${B} olddefconfig
}

KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto-srk-tiny"

# Use same initramfs for consistency
INITRAMFS_IMAGE = "core-image-tiny-initramfs-srk-9-nobusybox"
INITRAMFS_IMAGE_BUNDLE = "1"
INITRAMFS_IMAGE_NAME = "core-image-tiny-initramfs-srk-9-nobusybox-${MACHINE}.rootfs"

INSANE_SKIP:kernel-dev = "buildpaths"

# Enable debug symbols in the kernel package
DEBUG_BUILD = "1"
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"

#How to build: change local.conf to use this kernel:
# PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-tiny-debug"
# bitbake linux-yocto-srk-tiny-debug
# bitbake core-image-tiny-initramfs-srk-9-nobusybox