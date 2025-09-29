require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://defconfig \
            file://disable-scsi-debug.cfg \
            file://minimal-config.cfg \
            file://disable-rng.cfg \
            file://ultra-minimal.cfg \
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
    sed -i '/CONFIG_BLK_DEV_BSG/d' ${B}/.config
    sed -i '/CONFIG_HW_RANDOM/d' ${B}/.config
    sed -i '/CONFIG_HW_RANDOM_OMAP/d' ${B}/.config
    sed -i '/CONFIG_MODULES/d' ${B}/.config
    sed -i '/CONFIG_DEBUG_KERNEL/d' ${B}/.config
    sed -i '/CONFIG_PM/d' ${B}/.config
    sed -i '/CONFIG_INPUT/d' ${B}/.config
    sed -i '/CONFIG_VT/d' ${B}/.config
    sed -i '/CONFIG_USB_SUPPORT/d' ${B}/.config
    
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
    echo "CONFIG_INIT_STACK_NONE=y" >> ${B}/.config
    
    # Force enable serial console
    echo "CONFIG_SERIAL_8250=y" >> ${B}/.config
    echo "CONFIG_SERIAL_8250_CONSOLE=y" >> ${B}/.config
    
    # Rebuild config with dependencies resolved
    oe_runmake -C ${S} O=${B} olddefconfig
}
KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto-srk-tiny"

INITRAMFS_IMAGE = "core-image-tiny-initramfs-srk-9-nobusybox"
INITRAMFS_IMAGE_BUNDLE = "1"
INITRAMFS_IMAGE_NAME = "core-image-tiny-initramfs-srk-9-nobusybox-${MACHINE}.rootfs"

INSANE_SKIP:kernel-dev = "buildpaths"

#How to build: change local.conf to use this kernel:
# PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-tiny"
# bitbake bitbake linux-yocto-srk-tiny
# bitbake core-image-tiny-initramfs-srk-9-nobusybox - not tested yet

