DESCRIPTION = "BBB RTC Read/Write application - reads and writes to BeagleBone Black RTC"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://bbb-02-rtc.c \
           file://Makefile \
"
S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"
TARGET_CC_ARCH += "${LDFLAGS}"

do_compile() {
    oe_runmake
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 bbb-02-rtc ${D}${bindir}/
}