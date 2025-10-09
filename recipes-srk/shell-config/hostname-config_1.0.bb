SUMMARY = "Hostname configuration for SRK device"
DESCRIPTION = "Sets the hostname for the SRK embedded device"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://hostname"

S = "${WORKDIR}/sources"

do_unpack[cleandirs] = "${S}"
do_unpack() {
    mkdir -p ${S}
}

do_install() {
    install -d ${D}${sysconfdir}
    install -m 0644 ${WORKDIR}/hostname ${D}${sysconfdir}/hostname
}

FILES:${PN} = "${sysconfdir}/hostname"