DESCRIPTION = "Linux Capabilities demonstration program for BeagleBone Black"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://cap-demo.c \
           file://Makefile \
           file://cap-examples.sh \
"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

# Depend on libcap for capability functions
DEPENDS = "libcap"
RDEPENDS:${PN} = "libcap libcap-bin bash"

TARGET_CC_ARCH += "${LDFLAGS}"

do_compile() {
    oe_runmake
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 cap-demo ${D}${bindir}/
    install -m 0755 cap-examples.sh ${D}${bindir}/
}

FILES:${PN} += "${bindir}/cap-demo ${bindir}/cap-examples.sh"
