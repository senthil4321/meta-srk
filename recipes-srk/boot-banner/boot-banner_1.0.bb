SUMMARY = "Boot banner showing build information"
DESCRIPTION = "Display kernel, rootfs, and build information at boot time"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://boot-banner.sh \
           file://boot-banner.service"

S = "${WORKDIR}/sources-unpack"

inherit systemd

SYSTEMD_SERVICE:${PN} = "boot-banner.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/boot-banner.sh ${D}${bindir}/boot-banner.sh
    
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/boot-banner.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} = "${bindir}/boot-banner.sh \
               ${systemd_system_unitdir}/boot-banner.service"

RDEPENDS:${PN} = "bash"
