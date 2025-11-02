SUMMARY = "RTC Power Management utilities for suspend/resume"
DESCRIPTION = "Utilities for RTC-based alarm wakeup and suspend to RAM"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "\
    file://rtc-suspend \
    file://rtc-wakeup \
    file://rtc-pm-test \
    file://rtc-pm.service \
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
    
    # Install systemd service
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/rtc-pm.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += "\
    ${sbindir}/rtc-suspend \
    ${sbindir}/rtc-wakeup \
    ${sbindir}/rtc-pm-test \
    ${systemd_system_unitdir}/rtc-pm.service \
"

inherit systemd
SYSTEMD_SERVICE:${PN} = "rtc-pm.service"
SYSTEMD_AUTO_ENABLE = "disable"
