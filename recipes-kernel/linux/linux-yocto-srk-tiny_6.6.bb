require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}:"

SRC_URI += "file://defconfig \
            file://printk_time.cfg \
            file://disable_scsi_debug.cfg \
            file://patches/disable-audio.patch \
            file://am335x-yocto-srk-tiny.dts;subdir=git/arch/arm/boot/dts/ti/omap \
           "

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

