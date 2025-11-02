SUMMARY = "ACL (Access Control Lists) demonstration"
DESCRIPTION = "Demonstrates the use of extended file permissions with ACLs"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://acl-demo.sh"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

RDEPENDS:${PN} = "acl bash"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/acl-demo.sh ${D}${bindir}/acl-demo
}

FILES:${PN} = "${bindir}/acl-demo"
