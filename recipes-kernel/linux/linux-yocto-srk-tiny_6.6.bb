require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

# Add build timestamp to kernel version
def get_build_timestamp(d):
    import time
    import os
    # Set timezone to CET (handles DST automatically - becomes CEST when applicable)
    os.environ['TZ'] = 'CET'
    time.tzset()
    return time.strftime("%d%b%y-%H%M%S", time.localtime()).upper().upper()

KERNEL_LOCALVERSION = "-srk-tiny-${@get_build_timestamp(d)}"

# Exclude SCSI features for truly minimal kernel
KERNEL_FEATURES:remove = "features/scsi/scsi.scc features/scsi/scsi-debug.scc"
#file://disable-printk.cfg 
#file://disable-serial-tty.cfg 

SRC_URI += "file://defconfig \
            file://disable-scsi-debug.cfg \
            file://minimal-config.cfg \
            file://disable-rng.cfg \
            file://ultra-minimal.cfg \
            file://disable-ti-sysc.cfg \
            file://optimization_02_sound_multimedia.cfg \
            file://optimization_01_filesystem_optimization.cfg \
            file://optimization_03_wireless_bluetooth.cfg \
            file://optimization_04_graphics_display.cfg \
            file://optimization_05_crypto_security.cfg \
            file://optimization_06_kernel_debugging.cfg \
            file://optimization_07_power_management.cfg \
            file://optimization_08_profiling_tracing.cfg \
            file://optimization_09_memory_features.cfg \
            file://optimization_10_final_cleanup.cfg \
            file://optimization_11_driver_optimization.cfg \
            file://am335x-yocto-srk-tiny.dts;subdir=git/arch/arm/boot/dts/ti/omap"

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
    sed -i '/CONFIG_SCSI_MOD/d' ${B}/.config
    sed -i '/CONFIG_BLK_DEV_BSG/d' ${B}/.config
    sed -i '/CONFIG_HW_RANDOM/d' ${B}/.config
    sed -i '/CONFIG_HW_RANDOM_OMAP/d' ${B}/.config
    sed -i '/CONFIG_MODULES/d' ${B}/.config
    sed -i '/CONFIG_DEBUG_KERNEL/d' ${B}/.config
    sed -i '/CONFIG_PM/d' ${B}/.config
    sed -i '/CONFIG_INPUT/d' ${B}/.config
    sed -i '/CONFIG_VT/d' ${B}/.config
    sed -i '/CONFIG_USB_SUPPORT/d' ${B}/.config
    sed -i '/CONFIG_USB_DWC3_OMAP/d' ${B}/.config
    sed -i '/CONFIG_USB_MUSB_OMAP2PLUS/d' ${B}/.config
    sed -i '/CONFIG_OMAP_USB2/d' ${B}/.config
    sed -i '/CONFIG_OMAP_USB3/d' ${B}/.config
    sed -i '/CONFIG_OMAP_CONTROL_PHY/d' ${B}/.config
    sed -i '/CONFIG_HWMON/d' ${B}/.config
    sed -i '/CONFIG_THERMAL/d' ${B}/.config
    sed -i '/CONFIG_WATCHDOG/d' ${B}/.config
    sed -i '/CONFIG_RTC/d' ${B}/.config
    sed -i '/CONFIG_PWM/d' ${B}/.config
    sed -i '/CONFIG_LEDS/d' ${B}/.config
    sed -i '/CONFIG_SENSORS/d' ${B}/.config
    sed -i '/CONFIG_SOUND/d' ${B}/.config
    sed -i '/CONFIG_VIDEO/d' ${B}/.config
    sed -i '/CONFIG_DRM/d' ${B}/.config
    sed -i '/CONFIG_FB/d' ${B}/.config
    sed -i '/CONFIG_BACKLIGHT/d' ${B}/.config
    sed -i '/CONFIG_I2C/d' ${B}/.config
    sed -i '/CONFIG_REGULATOR/d' ${B}/.config
    sed -i '/CONFIG_MFD/d' ${B}/.config
    sed -i '/CONFIG_PCI/d' ${B}/.config
    sed -i '/CONFIG_PM_GENERIC_DOMAINS/d' ${B}/.config
    sed -i '/CONFIG_MEMORY/d' ${B}/.config
    sed -i '/CONFIG_CHAR/d' ${B}/.config
    sed -i '/CONFIG_PINCTRL/d' ${B}/.config
    sed -i '/CONFIG_RESET/d' ${B}/.config
    sed -i '/CONFIG_IRQCHIP/d' ${B}/.config
    sed -i '/CONFIG_RTC_CLASS/d' ${B}/.config
    sed -i '/CONFIG_BUS/d' ${B}/.config
    sed -i '/CONFIG_CLOCKSOURCE/d' ${B}/.config
    sed -i '/CONFIG_JFFS2/d' ${B}/.config
    sed -i '/CONFIG_UBIFS/d' ${B}/.config
    sed -i '/CONFIG_SQUASHFS/d' ${B}/.config
    sed -i '/CONFIG_CRAMFS/d' ${B}/.config
    sed -i '/CONFIG_MINIX/d' ${B}/.config
    sed -i '/CONFIG_ROMFS/d' ${B}/.config
    sed -i '/CONFIG_FAT_FS/d' ${B}/.config
    sed -i '/CONFIG_VFAT_FS/d' ${B}/.config
    sed -i '/CONFIG_MSDOS_FS/d' ${B}/.config
    sed -i '/CONFIG_CONFIGFS_FS/d' ${B}/.config
    sed -i '/CONFIG_NLS/d' ${B}/.config
    sed -i '/CONFIG_DEVPTS_FS/d' ${B}/.config
    sed -i '/CONFIG_EXPORTFS/d' ${B}/.config
    sed -i '/CONFIG_RAMFS/d' ${B}/.config
    sed -i '/CONFIG_CRYPTO/d' ${B}/.config
    sed -i '/CONFIG_ZSTD/d' ${B}/.config
    sed -i '/CONFIG_XZ/d' ${B}/.config
    sed -i '/CONFIG_LZ4/d' ${B}/.config
    sed -i '/CONFIG_LZO/d' ${B}/.config
    
    # Force disable configurations
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
    echo "# CONFIG_SCSI_MOD is not set" >> ${B}/.config
    echo "# CONFIG_BLK_DEV_BSG is not set" >> ${B}/.config
    echo "# CONFIG_HW_RANDOM is not set" >> ${B}/.config
    echo "# CONFIG_HW_RANDOM_OMAP is not set" >> ${B}/.config
    
    # Ultra-minimal optimizations for fastest boot (KEEP PRINTK for boot messages)
    echo "# CONFIG_MODULES is not set" >> ${B}/.config
    echo "# CONFIG_DEBUG_KERNEL is not set" >> ${B}/.config
    echo "# CONFIG_PM is not set" >> ${B}/.config
    echo "# CONFIG_INPUT is not set" >> ${B}/.config
    echo "# CONFIG_VT is not set" >> ${B}/.config
    echo "# CONFIG_USB_SUPPORT is not set" >> ${B}/.config
    echo "# CONFIG_USB_DWC3_OMAP is not set" >> ${B}/.config
    echo "# CONFIG_USB_MUSB_OMAP2PLUS is not set" >> ${B}/.config
    echo "# CONFIG_OMAP_USB2 is not set" >> ${B}/.config
    echo "# CONFIG_OMAP_USB3 is not set" >> ${B}/.config
    echo "# CONFIG_OMAP_CONTROL_PHY is not set" >> ${B}/.config
    echo "# CONFIG_HWMON is not set" >> ${B}/.config
    echo "# CONFIG_THERMAL is not set" >> ${B}/.config
    echo "# CONFIG_WATCHDOG is not set" >> ${B}/.config
    echo "# CONFIG_RTC is not set" >> ${B}/.config
    echo "# CONFIG_PWM is not set" >> ${B}/.config
    echo "# CONFIG_LEDS is not set" >> ${B}/.config
    echo "# CONFIG_SENSORS is not set" >> ${B}/.config
    echo "# CONFIG_SOUND is not set" >> ${B}/.config
    echo "# CONFIG_VIDEO is not set" >> ${B}/.config
    echo "# CONFIG_DRM is not set" >> ${B}/.config
    echo "# CONFIG_FB is not set" >> ${B}/.config
    echo "# CONFIG_BACKLIGHT is not set" >> ${B}/.config
    echo "# CONFIG_I2C is not set" >> ${B}/.config
    echo "# CONFIG_REGULATOR is not set" >> ${B}/.config
    echo "# CONFIG_MFD_SYSCON is not set" >> ${B}/.config
    echo "# CONFIG_PCI is not set" >> ${B}/.config
    echo "# CONFIG_PM_GENERIC_DOMAINS is not set" >> ${B}/.config
    echo "# CONFIG_MEMORY is not set" >> ${B}/.config
    echo "# CONFIG_CHAR is not set" >> ${B}/.config
    echo "# CONFIG_PINCTRL is not set" >> ${B}/.config
    echo "# CONFIG_RESET is not set" >> ${B}/.config
    echo "# CONFIG_IRQCHIP is not set" >> ${B}/.config
    echo "# CONFIG_RTC_CLASS is not set" >> ${B}/.config
    echo "# CONFIG_BUS is not set" >> ${B}/.config
    echo "# CONFIG_CLOCKSOURCE is not set" >> ${B}/.config
    echo "# CONFIG_JFFS2 is not set" >> ${B}/.config
    echo "# CONFIG_UBIFS is not set" >> ${B}/.config
    echo "# CONFIG_SQUASHFS is not set" >> ${B}/.config
    echo "# CONFIG_CRAMFS is not set" >> ${B}/.config
    echo "# CONFIG_MINIX is not set" >> ${B}/.config
    echo "# CONFIG_ROMFS is not set" >> ${B}/.config
    echo "# CONFIG_FAT_FS is not set" >> ${B}/.config
    echo "# CONFIG_VFAT_FS is not set" >> ${B}/.config
    echo "# CONFIG_MSDOS_FS is not set" >> ${B}/.config
    echo "# CONFIG_CONFIGFS_FS is not set" >> ${B}/.config
    echo "# CONFIG_NLS is not set" >> ${B}/.config
    echo "# CONFIG_DEVPTS_FS is not set" >> ${B}/.config
    echo "# CONFIG_EXPORTFS is not set" >> ${B}/.config
    echo "# CONFIG_RAMFS is not set" >> ${B}/.config
    echo "# CONFIG_CRYPTO is not set" >> ${B}/.config
    echo "# CONFIG_ZSTD is not set" >> ${B}/.config
    echo "# CONFIG_XZ is not set" >> ${B}/.config
    echo "# CONFIG_LZ4 is not set" >> ${B}/.config
    echo "# CONFIG_LZO is not set" >> ${B}/.config
    
    # Force enable serial console
    echo "CONFIG_SERIAL_8250=y" >> ${B}/.config
    echo "CONFIG_SERIAL_8250_CONSOLE=y" >> ${B}/.config
    
    # Rebuild config with dependencies resolved
    oe_runmake -C ${S} O=${B} olddefconfig
    
    # Force disable CONFIG_SCSI_MOD after olddefconfig (it defaults to y when SCSI=n)
    echo "# CONFIG_SCSI_MOD is not set" >> ${B}/.config
}
KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto-srk-tiny"

INITRAMFS_IMAGE = "core-image-tiny-initramfs-srk-9-nobusybox"
INITRAMFS_IMAGE_BUNDLE = "1"
INITRAMFS_IMAGE_NAME = "core-image-tiny-initramfs-srk-9-nobusybox-${MACHINE}.rootfs"

INSANE_SKIP:kernel-dev = "buildpaths"
KERNEL_IMAGETYPE ?= "zImage"

#How to build: change local.conf to use this kernel:
# PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-tiny"
# bitbake bitbake linux-yocto-srk-tiny
# bitbake core-image-tiny-initramfs-srk-9-nobusybox - not tested yet

