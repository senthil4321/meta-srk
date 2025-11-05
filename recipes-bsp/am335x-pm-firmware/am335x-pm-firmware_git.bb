SUMMARY = "AM335x Power Management Firmware"
DESCRIPTION = "Firmware for TI AM335x Cortex-M3 PM processor (wkup_m3) for suspend-to-RAM support"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/BSD-3-Clause;md5=550794465ba0ec5312d6919e203a55f9"

# Use local firmware file (latest from TI, not stripped - keep resource table for kernel 6.x)
# Source: git://git.ti.com/git/processor-firmware/ti-amx3-cm3-pm-firmware.git
SRC_URI = "file://am335x-pm-firmware-latest.elf"

# Disable default unpack since we're providing a pre-built binary
do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
    install -d ${D}${nonarch_base_libdir}/firmware
    # File is unpacked to sources-unpack directory by BitBake
    install -m 0644 ${WORKDIR}/sources-unpack/am335x-pm-firmware-latest.elf ${D}${nonarch_base_libdir}/firmware/am335x-pm-firmware.elf
}

FILES:${PN} = "${nonarch_base_libdir}/firmware/am335x-pm-firmware.elf"

PACKAGE_ARCH = "${MACHINE_ARCH}"
COMPATIBLE_MACHINE = "beaglebone.*"
