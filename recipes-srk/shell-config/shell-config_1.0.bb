SUMMARY = "Shell configuration for proper terminal prompt"
DESCRIPTION = "Provides proper shell configuration files for busybox ash and bash compatibility"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://profile \
           file://bashrc \
           file://setup-shell.sh"

S = "${WORKDIR}/sources"

do_unpack[cleandirs] = "${S}"
do_unpack() {
    mkdir -p ${S}
}

do_install() {
    install -d ${D}${sysconfdir}
    install -d ${D}${sysconfdir}/skel
    install -d ${D}${sysconfdir}/init.d
    
    # Install system-wide profile
    install -m 0644 ${WORKDIR}/profile ${D}${sysconfdir}/profile
    
    # Install bashrc for root and skel
    install -m 0644 ${WORKDIR}/bashrc ${D}${sysconfdir}/skel/.bashrc
    install -d ${D}/root
    install -m 0644 ${WORKDIR}/bashrc ${D}/root/.bashrc
    
    # Install shell setup script
    install -m 0755 ${WORKDIR}/setup-shell.sh ${D}${sysconfdir}/init.d/setup-shell
}

FILES:${PN} = "${sysconfdir}/profile \
               ${sysconfdir}/skel/.bashrc \
               ${sysconfdir}/init.d/setup-shell \
               /root/.bashrc"

PACKAGES = "${PN}"