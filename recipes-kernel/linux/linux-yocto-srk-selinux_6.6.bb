require recipes-kernel/linux/linux-yocto_6.6.bb

DESCRIPTION = "Custom Linux kernel (SELinux enabled) based on linux-yocto from srk"
FILESEXTRAPATHS:prepend := "${THISDIR}/linux-yocto-srk-selinux:"

# Reuse existing defconfig from baseline kernel
SRC_URI += "file://defconfig"
SRC_URI += "file://selinux.cfg"
SRC_URI += "file://localversion.cfg"

KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto"
