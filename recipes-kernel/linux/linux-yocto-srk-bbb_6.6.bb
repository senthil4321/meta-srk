require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel for BeagleBone Black based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://defconfig \
            file://bbb-eeprom.cfg \
            file://bbb-led.cfg"

KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto"