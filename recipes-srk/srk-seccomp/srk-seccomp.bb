DESCRIPTION = "Hello World C program with seccomp example"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835c6e3e3b5b5b5b5b5b5b5b5b5b5"

SRC_URI = "file://srk-seccomp.c"

DEPENDS = "libseccomp"

S = "${WORKDIR}"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o srk-seccomp srk-seccomp.c -lseccomp
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 srk-seccomp ${D}${bindir}
}

FILES_${PN} = "${bindir}/srk-seccomp"
