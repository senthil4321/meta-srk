DESCRIPTION = "Silent init program for kernel debugging - produces no output"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://silentloop.c \
           file://Makefile"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

do_configure[noexec] = "1"

do_compile() {
    oe_runmake
}

do_install() {
    install -d ${D}${base_sbindir}
    install -m 0755 silentloop ${D}${base_sbindir}/silentloop
}