DESCRIPTION = "Hello World C program with seccomp example"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://srk-seccomp.c"

DEPENDS += "libseccomp"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o srk-seccomp srk-seccomp.c -lseccomp
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 srk-seccomp ${D}${bindir}
}

FILES_${PN} = "${bindir}/srk-seccomp"
