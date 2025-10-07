SUMMARY = "Static hello loop printing Hello World and date every second"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://helloloop.c \
           file://Makefile \
"

# Mirror structure of hello_1.0.bb
S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"
TARGET_CC_ARCH += "${LDFLAGS}"

do_compile() {
    oe_runmake
}

do_install() {
    install -d ${D}${base_sbindir}
    install -m 0755 helloloop ${D}${base_sbindir}/
}

FILES:${PN} = "${base_sbindir}/helloloop"
FILES:${PN}-dev = ""
FILES:${PN}-dbg = ""

# Ensure main package is created
PACKAGES = "${PN} ${PN}-dev ${PN}-dbg"

