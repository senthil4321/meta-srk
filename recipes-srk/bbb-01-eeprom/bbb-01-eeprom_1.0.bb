SUMMARY = "BBB EEPROM Reader"
DESCRIPTION = "Program to read and display BeagleBone Black EEPROM contents including MAC addresses, serial number, and board information"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://bbb-01-eeprom.c \
           file://Makefile \
           file://README.md \
           file://setup-eeprom.sh"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

TARGET_CC_ARCH += "${LDFLAGS}"

do_compile() {
    oe_runmake
}

do_install() {
    oe_runmake install DESTDIR=${D}
    install -d ${D}/usr/bin
    install -m 0755 ${UNPACKDIR}/setup-eeprom.sh ${D}/usr/bin/setup-eeprom.sh
}

FILES:${PN} = "/usr/bin/bbb-01-eeprom /usr/bin/setup-eeprom.sh"