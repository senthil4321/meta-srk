DESCRIPTION = "BBB LED Blink application - blinks all 4 user LEDs in sequence"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://bbb-led-blink.c \
           file://Makefile \
"

S = "${WORKDIR}/sources-unpack"

TARGET_CC_ARCH += "${LDFLAGS}"

do_compile() {
    oe_runmake
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 bbb-02-led-blink ${D}${bindir}/
}