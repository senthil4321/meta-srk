SUMMARY = "IPsec kernel modules auto-loader"
DESCRIPTION = "Systemd service to load IPsec kernel modules at boot"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

inherit systemd

SRC_URI = "file://ipsec-modules.service"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

SYSTEMD_SERVICE:${PN} = "ipsec-modules.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/ipsec-modules.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} = "${systemd_system_unitdir}/ipsec-modules.service"
