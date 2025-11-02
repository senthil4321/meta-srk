SUMMARY = "Infineon OPTIGA Trust M Library and Tools"
DESCRIPTION = "Library and command-line tools for Infineon OPTIGA Trust M secure element"
HOMEPAGE = "https://github.com/Infineon/optiga-trust-m"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=9592eadf4026ab21a12671b78c4e83a3"

SRCREV = "b544b618f4ae8827f60080e5b4e5d0e60cf9b5fa"
SRC_URI = "git://github.com/Infineon/optiga-trust-m.git;protocol=https;branch=master"

S = "${WORKDIR}/git"

DEPENDS = "openssl"
RDEPENDS:${PN} = "libssl libcrypto i2c-tools"

inherit cmake

# Target the BeagleBone I2C configuration
EXTRA_OECMAKE = " \
    -DOPTIGA_TRUST_M_PORTING=linux \
    -DOPTIGA_TRUST_M_EXAMPLES=ON \
    -DI2C_DEVICE=/dev/i2c-2 \
"

do_install:append() {
    # Install library
    install -d ${D}${libdir}
    install -m 0755 ${B}/lib/liboptigatrustm.so ${D}${libdir}/ || true
    
    # Install header files
    install -d ${D}${includedir}/optiga
    install -m 0644 ${S}/include/*.h ${D}${includedir}/optiga/ || true
    
    # Install example binaries
    install -d ${D}${bindir}
    install -m 0755 ${B}/examples/* ${D}${bindir}/ 2>/dev/null || true
}

FILES:${PN} += "${libdir}/liboptigatrustm.so"
FILES:${PN} += "${bindir}/*"

COMPATIBLE_MACHINE = "beaglebone.*"
