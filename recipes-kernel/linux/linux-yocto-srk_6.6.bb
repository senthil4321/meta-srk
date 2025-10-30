require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

# Add defconfig
SRC_URI += "file://defconfig"

# Add OMAP hardware crypto configuration fragment
SRC_URI += "file://omap-hwcrypto.cfg"

KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto|beaglebone-yocto-srk"
