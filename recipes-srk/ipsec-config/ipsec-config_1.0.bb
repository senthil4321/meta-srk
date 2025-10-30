SUMMARY = "IPsec configuration files for BeagleBone Black"
DESCRIPTION = "Provides StrongSwan configuration for IPsec connection to Pi Gateway"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://swanctl.conf \
    file://ipsec.conf \
    file://ipsec.secrets \
"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

# Install to a temporary location first
do_install() {
    # Install our custom configs to /usr/share (not /etc to avoid conflicts)
    install -d ${D}${datadir}/${PN}
    install -m 0644 ${S}/swanctl.conf ${D}${datadir}/${PN}/swanctl.conf
    install -m 0644 ${S}/ipsec.conf ${D}${datadir}/${PN}/ipsec.conf
    install -m 0600 ${S}/ipsec.secrets ${D}${datadir}/${PN}/ipsec.secrets
}

# Post-install script to copy configs to /etc after strongswan is installed
pkg_postinst_ontarget:${PN}() {
    # Copy our custom configs to the actual locations
    cp ${datadir}/${PN}/swanctl.conf /etc/swanctl/swanctl.conf
    cp ${datadir}/${PN}/ipsec.conf /etc/ipsec.conf
    cp ${datadir}/${PN}/ipsec.secrets /etc/ipsec.secrets
    chmod 600 /etc/ipsec.secrets
    echo "IPsec configuration installed successfully"
}

FILES:${PN} = " \
    ${datadir}/${PN}/swanctl.conf \
    ${datadir}/${PN}/ipsec.conf \
    ${datadir}/${PN}/ipsec.secrets \
"

RDEPENDS:${PN} = "strongswan"
