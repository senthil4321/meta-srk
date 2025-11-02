SUMMARY = "Trust M RSA Example Programs"
DESCRIPTION = "Example programs for RSA key generation, signing, and verification using OpenSSL and optionally Trust M"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "\
    file://trustm-rsa-keygen.c \
    file://trustm-rsa-sign.c \
    file://trustm-rsa-verify.c \
    file://Makefile \
"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

DEPENDS = "openssl"
RDEPENDS:${PN} = "libssl libcrypto"

EXTRA_OEMAKE = "CC='${CC}' CFLAGS='${CFLAGS}' LDFLAGS='${LDFLAGS}'"

do_compile() {
    oe_runmake
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/trustm-rsa-keygen ${D}${bindir}/
    install -m 0755 ${S}/trustm-rsa-sign ${D}${bindir}/
    install -m 0755 ${S}/trustm-rsa-verify ${D}${bindir}/
}

FILES:${PN} = "${bindir}/*"
