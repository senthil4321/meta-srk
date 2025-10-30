SUMMARY = "Systemd logging configuration for timestamps"
DESCRIPTION = "Configures systemd to show timestamps in boot logs"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://show-timestamps.conf \
           file://timestamps.conf"

S = "${WORKDIR}/sources-unpack"

inherit allarch

RDEPENDS:${PN} = "systemd"

do_install() {
    # Install journald configuration
    install -d ${D}${sysconfdir}/systemd/journald.conf.d
    install -m 0644 ${S}/show-timestamps.conf ${D}${sysconfdir}/systemd/journald.conf.d/
    
    # Install system configuration
    install -d ${D}${sysconfdir}/systemd/system.conf.d
    install -m 0644 ${S}/timestamps.conf ${D}${sysconfdir}/systemd/system.conf.d/
}

FILES:${PN} = "${sysconfdir}/systemd/journald.conf.d/show-timestamps.conf \
               ${sysconfdir}/systemd/system.conf.d/timestamps.conf"
