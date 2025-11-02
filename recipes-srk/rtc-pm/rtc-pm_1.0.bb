SUMMARY = "RTC Power Management utilities for suspend/resume"
DESCRIPTION = "Utilities for RTC-based alarm wakeup and suspend to RAM"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "\
    file://rtc-suspend \
    file://rtc-wakeup \
    file://rtc-pm-test \
    file://rtc-pm.service \
    file://rtc-sync.sh \
    file://rtc-sync.service \
    file://README.md \
    file://QUICK-REFERENCE.md \
"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

RDEPENDS:${PN} = "bash util-linux"

do_install() {
    # Install scripts
    install -d ${D}${sbindir}
    install -m 0755 ${S}/rtc-suspend ${D}${sbindir}/
    install -m 0755 ${S}/rtc-wakeup ${D}${sbindir}/
    install -m 0755 ${S}/rtc-pm-test ${D}${sbindir}/
    install -m 0755 ${S}/rtc-sync.sh ${D}${sbindir}/
    
    # Install systemd services
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/rtc-pm.service ${D}${systemd_system_unitdir}/
    install -m 0644 ${S}/rtc-sync.service ${D}${systemd_system_unitdir}/
    
    # Install documentation
    install -d ${D}${docdir}/${PN}
    install -m 0644 ${S}/README.md ${D}${docdir}/${PN}/
    install -m 0644 ${S}/QUICK-REFERENCE.md ${D}${docdir}/${PN}/
}

FILES:${PN} += "\
    ${sbindir}/rtc-suspend \
    ${sbindir}/rtc-wakeup \
    ${sbindir}/rtc-pm-test \
    ${sbindir}/rtc-sync.sh \
    ${systemd_system_unitdir}/rtc-pm.service \
    ${systemd_system_unitdir}/rtc-sync.service \
    ${docdir}/${PN}/README.md \
    ${docdir}/${PN}/QUICK-REFERENCE.md \
"

inherit systemd
SYSTEMD_SERVICE:${PN} = "rtc-pm.service rtc-sync.service"
SYSTEMD_AUTO_ENABLE:${PN}:rtc-pm.service = "disable"
SYSTEMD_AUTO_ENABLE:${PN}:rtc-sync.service = "enable"
