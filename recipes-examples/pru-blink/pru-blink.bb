SUMMARY = "PRU Blink Example"
DESCRIPTION = "Simple PRU program to test PRU cores by blinking an LED"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://pru-blink.c \
    file://pru-test.sh \
    file://pru-load.sh \
    file://pru-compile \
    file://generate-pru-firmware.py \
"

# PRU requires TI's PRU compiler (clpru) which is not in standard Yocto
# For now, we'll just install the test script
# The C code shows what a PRU program would look like

RDEPENDS:${PN} = "bash python3-core"

do_compile() {
    # Generate PRU firmware files
    cd ${WORKDIR}/sources-unpack
    python3 generate-pru-firmware.py
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/sources-unpack/pru-test.sh ${D}${bindir}/pru-test
    install -m 0755 ${WORKDIR}/sources-unpack/pru-load.sh ${D}${bindir}/pru-load
    install -m 0755 ${WORKDIR}/sources-unpack/pru-compile ${D}${bindir}/pru-compile
    
    # Install firmware generator
    install -m 0755 ${WORKDIR}/sources-unpack/generate-pru-firmware.py ${D}${bindir}/pru-firmware-gen
    
    # Install generated firmware files
    install -d ${D}${nonarch_base_libdir}/firmware
    install -m 0644 ${WORKDIR}/sources-unpack/am335x-pru0-fw ${D}${nonarch_base_libdir}/firmware/
    install -m 0644 ${WORKDIR}/sources-unpack/am335x-pru1-fw ${D}${nonarch_base_libdir}/firmware/
    
    # Install PRU source as documentation
    install -d ${D}${docdir}/${PN}
    install -m 0644 ${WORKDIR}/sources-unpack/pru-blink.c ${D}${docdir}/${PN}/
}

INSANE_SKIP:${PN} += "installed-vs-shipped arch"

FILES:${PN} = "${bindir}/pru-test ${bindir}/pru-load ${bindir}/pru-compile ${bindir}/pru-firmware-gen ${nonarch_base_libdir}/firmware/am335x-pru*-fw"
FILES:${PN}-doc = "${docdir}/${PN}"

RDEPENDS:${PN} = "bash python3-core"
