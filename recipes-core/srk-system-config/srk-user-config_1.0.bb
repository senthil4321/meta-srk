SUMMARY = "SRK user configuration files"
DESCRIPTION = "Provides home directory configuration for the srk user including bashrc and SSH keys."

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "\
    file://bashrc \
    file://authorized_keys \
"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

do_install() {
    # Install srk user's home directory files
    install -d ${D}/home/srk
    install -m 0644 ${S}/bashrc ${D}/home/srk/.bashrc
    
    # Install SSH authorized_keys for srk user
    install -d ${D}/home/srk/.ssh
    install -m 0600 ${S}/authorized_keys ${D}/home/srk/.ssh/authorized_keys
}

FILES:${PN} += "\
    /home/srk/.bashrc \
    /home/srk/.ssh/authorized_keys \
"

# Ensure proper ownership for srk user files (UID 1000, GID 1000)
USERADD_PACKAGES = "${PN}"
USERADD_PARAM:${PN} = "-u 1000 -d /home/srk -s /bin/bash srk"

pkg_postinst_ontarget:${PN}() {
    # Fix ownership of srk's home directory and files
    chown -R srk:srk /home/srk
}

RDEPENDS:${PN} = "srk-system-config"
