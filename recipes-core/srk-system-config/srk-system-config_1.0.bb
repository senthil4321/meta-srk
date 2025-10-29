SUMMARY = "System configuration files for SRK embedded devices"
DESCRIPTION = "Provides system configuration files including bash profiles, network setup, \
SSH keys, and systemd service configurations for SRK embedded images."

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "\
    file://bashrc \
    file://10-eth0.network \
    file://authorized_keys \
    file://systemd-logind-override.conf \
    file://systemd-timesyncd-override.conf \
    file://systemd-resolved-override.conf \
    file://systemd-time-resolve.conf \
    file://systemd-logind-srk.conf \
"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

do_install() {
    # Note: We don't install /etc/profile, /etc/shells, or /etc/hostname here
    # to avoid conflicts with base-files. These will be modified via the image recipe.
    
    # Install root's bashrc
    install -d ${D}/root
    install -m 0644 ${S}/bashrc ${D}/root/.bashrc
    
    # Install network configuration
    install -d ${D}${sysconfdir}/systemd/network
    install -m 0644 ${S}/10-eth0.network ${D}${sysconfdir}/systemd/network/10-eth0.network
    
    # Install SSH authorized_keys for root
    install -d ${D}/root/.ssh
    install -m 0600 ${S}/authorized_keys ${D}/root/.ssh/authorized_keys
    
    # Install systemd service overrides
    install -d ${D}${sysconfdir}/systemd/system/systemd-logind.service.d
    install -m 0644 ${S}/systemd-logind-override.conf \
        ${D}${sysconfdir}/systemd/system/systemd-logind.service.d/override.conf
    
    install -d ${D}${sysconfdir}/systemd/system/systemd-timesyncd.service.d
    install -m 0644 ${S}/systemd-timesyncd-override.conf \
        ${D}${sysconfdir}/systemd/system/systemd-timesyncd.service.d/override.conf
    
    install -d ${D}${sysconfdir}/systemd/system/systemd-resolved.service.d
    install -m 0644 ${S}/systemd-resolved-override.conf \
        ${D}${sysconfdir}/systemd/system/systemd-resolved.service.d/override.conf
    
    # Install tmpfiles configurations
    install -d ${D}${nonarch_libdir}/tmpfiles.d
    install -m 0644 ${S}/systemd-time-resolve.conf \
        ${D}${nonarch_libdir}/tmpfiles.d/systemd-time-resolve.conf
    install -m 0644 ${S}/systemd-logind-srk.conf \
        ${D}${nonarch_libdir}/tmpfiles.d/systemd-logind-srk.conf
}

FILES:${PN} += "\
    ${sysconfdir}/systemd/network/10-eth0.network \
    ${sysconfdir}/systemd/system/systemd-logind.service.d/override.conf \
    ${sysconfdir}/systemd/system/systemd-timesyncd.service.d/override.conf \
    ${sysconfdir}/systemd/system/systemd-resolved.service.d/override.conf \
    ${nonarch_libdir}/tmpfiles.d/systemd-time-resolve.conf \
    ${nonarch_libdir}/tmpfiles.d/systemd-logind-srk.conf \
    /root/.bashrc \
    /root/.ssh/authorized_keys \
"

CONFFILES:${PN} += "\
    ${sysconfdir}/systemd/network/10-eth0.network \
"

# Fix permissions at runtime (SSH requires .ssh directory to be mode 700 and /root to be mode 700)
pkg_postinst_ontarget:${PN}() {
    chmod 700 /root
    chmod 700 /root/.ssh
    chmod 600 /root/.ssh/authorized_keys
    chown -R root:root /root/.ssh
}

# Runtime dependencies
RDEPENDS:${PN} = "bash systemd"
