DESCRIPTION = "BBB LED Blink application without libc - uses direct system calls"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://bbb-led-blink-nolibc.c \
           file://Makefile \
"
S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

# Disable security features for nolibc
SECURITY_CFLAGS = ""
SECURITY_LDFLAGS = ""

# Use direct assembly compilation without standard libraries
do_compile() {
    oe_runmake
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 bbb-03-led-blink-nolibc ${D}${bindir}/
}