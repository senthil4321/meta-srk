# SUMMARY = "Custom Linux kernel for SRK"
# DESCRIPTION = "Custom Linux kernel for SRK"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-2.0-only;md5=751419260aa954499f7abaabaa882bbe"

# SRC_URI = "git://git.yoctoproject.org/linux-yocto.git;branch=yocto-5.10;protocol=https \
#            file://defconfig"

# FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

# do_configure:prepend() {
#     cp ${WORKDIR}/defconfig ${B}/.config
# }

# inherit kernel