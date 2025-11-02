SUMMARY = "AM335x Power Management Firmware"
DESCRIPTION = "Firmware for TI AM335x Cortex-M3 PM processor (wkup_m3) for suspend-to-RAM support"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/BSD-3-Clause;md5=550794465ba0ec5312d6919e203a55f9"

# Download prebuilt firmware binary
SRC_URI = "https://git.beagleboard.org/beagleboard/BeagleBoard-DeviceTrees/-/raw/v4.14-ti/firmware/am335x-pm-firmware.elf;name=firmware"
SRC_URI[firmware.sha256sum] = "f6f8327c89807bd3745df1ed27296e083472175af89a681925397309e79e282e"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

inherit allarch

do_install() {
    install -d ${D}${nonarch_base_libdir}/firmware
    install -m 0644 ${S}/am335x-pm-firmware.elf ${D}${nonarch_base_libdir}/firmware/
}

FILES:${PN} = "${nonarch_base_libdir}/firmware/am335x-pm-firmware.elf"

PACKAGE_ARCH = "${MACHINE_ARCH}"
COMPATIBLE_MACHINE = "beaglebone.*"
