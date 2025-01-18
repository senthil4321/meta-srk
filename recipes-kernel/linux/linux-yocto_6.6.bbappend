# Base kernel recipe path
# meta/recipes-kernel/linux/linux-yocto_6.6.bb
# meta-yocto-bsp/recipes-kernel/linux/linux-yocto_6.6.bbappend

# Readme
# https://docs.yoctoproject.org/kernel-dev/common.html#changing-the-configuration

FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"
SRC_URI += "file://defconfig"


KCONFIG_MODE = "alldefconfig"
SRC_URI += "file://localversion.cfg"

SRC_URI += "file://trail12_usb_sound.cfg"

# remove SMB file system
SRC_URI += "file://trial13_smb.cfg"

# remove BTRFS file system
SRC_URI += "file://trial14_btrf.cfg"

# add ktime support during boot
SRC_URI += "file://trial15_ktime.cfg"

# remove MTD file system and sound
SRC_URI += "file://trial16_sound_mtd.cfg"

# remove SCSI CD etc
SRC_URI += "file://trial17_scsi.cfg"

# add AES OMAP support
SRC_URI += "file://trial18_aes_omap.cfg"

# reove uwanted network driver
SRC_URI += "file://trial19_xfrm-ipsec.cfg"


