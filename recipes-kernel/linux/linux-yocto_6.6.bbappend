# Base kernel recipe path
# meta/recipes-kernel/linux/linux-yocto_6.6.bb
# meta-yocto-bsp/recipes-kernel/linux/linux-yocto_6.6.bbappend

# Readme
# https://docs.yoctoproject.org/kernel-dev/common.html#changing-the-configuration

FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"
SRC_URI += "file://defconfig"


KCONFIG_MODE = "alldefconfig"
SRC_URI += "file://localversion.cfg"
