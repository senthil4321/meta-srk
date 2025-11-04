SUMMARY = "AM335x Power Management Firmware"
DESCRIPTION = "Firmware for TI AM335x Cortex-M3 PM processor (wkup_m3) for suspend-to-RAM support"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/BSD-3-Clause;md5=550794465ba0ec5312d6919e203a55f9"

# Use TI's official firmware repository
SRCREV = "${AUTOREV}"
SRC_URI = "git://git.ti.com/git/processor-firmware/ti-amx3-cm3-pm-firmware.git;protocol=https;branch=master"

S = "${WORKDIR}/git"

# The firmware is pre-built, no compilation needed
do_compile[noexec] = "1"

do_install() {
    install -d ${D}${nonarch_base_libdir}/firmware
    install -m 0644 ${S}/bin/am335x-pm-firmware.elf ${D}${nonarch_base_libdir}/firmware/
}

FILES:${PN} = "${nonarch_base_libdir}/firmware/am335x-pm-firmware.elf"

PACKAGE_ARCH = "${MACHINE_ARCH}"
COMPATIBLE_MACHINE = "beaglebone.*"
