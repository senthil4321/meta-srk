SUMMARY = "PRU Blink Example"
DESCRIPTION = "Simple PRU program to test PRU cores by blinking an LED"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://pru-blink.c \
    file://pru-test.sh \
"

# PRU requires TI's PRU compiler (clpru) which is not in standard Yocto
# For now, we'll just install the test script
# The C code shows what a PRU program would look like

do_compile() {
    :
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/sources-unpack/pru-test.sh ${D}${bindir}/pru-test
    
    # Install PRU source as documentation
    install -d ${D}${docdir}/${PN}
    install -m 0644 ${WORKDIR}/sources-unpack/pru-blink.c ${D}${docdir}/${PN}/
}

INSANE_SKIP:${PN} += "installed-vs-shipped"

FILES:${PN} = "${bindir}/pru-test"
FILES:${PN}-doc = "${docdir}/${PN}"

RDEPENDS:${PN} = "bash"
