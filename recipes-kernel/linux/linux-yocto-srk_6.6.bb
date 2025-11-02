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

# Add AM33xx PM support for suspend-to-RAM
SRC_URI += "file://pm33xx.cfg"

KCONFIG_MODE = "alldefconfig"

COMPATIBLE_MACHINE = "beaglebone-yocto|beaglebone-yocto-srk"
