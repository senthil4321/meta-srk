FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"
SRC_URI += "file://defconfig"
# https://docs.yoctoproject.org/kernel-dev/common.html#changing-the-configuration

KCONFIG_MODE = "alldefconfig"
