SUMMARY = "Custom init script for SRK"
DESCRIPTION = "Custom init script for SRK"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://srk-init.sh"
S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"
do_install() {
    install -d ${D}/sbin
    install -m 0755 ${S}/srk-init.sh ${D}/sbin/init
}

FILES:${PN} = "/sbin/init"
