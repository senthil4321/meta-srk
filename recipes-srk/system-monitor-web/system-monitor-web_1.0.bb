SUMMARY = "Lightweight web server for system monitoring"
DESCRIPTION = "Python-based web server that displays CPU, RAM, and network metrics"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "\
    file://system-monitor.py \
    file://system-monitor.service \
"

S = "${WORKDIR}/sources-unpack"

RDEPENDS:${PN} = "\
    python3-core \
    python3-netserver \
    python3-json \
    python3-datetime \
    python3-math \
    python3-io \
"

inherit systemd

SYSTEMD_SERVICE:${PN} = "system-monitor.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    # Install the Python web server script
    install -d ${D}${bindir}
    install -m 0755 ${S}/system-monitor.py ${D}${bindir}/system-monitor
    
    # Install systemd service file
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/system-monitor.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += "\
    ${bindir}/system-monitor \
    ${systemd_system_unitdir}/system-monitor.service \
"
