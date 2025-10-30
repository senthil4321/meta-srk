SUMMARY = "Rootfs build information updater"
DESCRIPTION = "Updates /etc/build-info with rootfs image name and build time"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

S = "${WORKDIR}/sources-unpack"

inherit allarch

# This recipe depends on build-info being installed first
RDEPENDS:${PN} = "build-info"

do_compile() {
    # This will be populated by image-specific bbappend files
    # or by IMAGE_BASENAME variable
    ROOTFS_NAME="${IMAGE_BASENAME_ROOTFS}"
    
    if [ -z "$ROOTFS_NAME" ]; then
        ROOTFS_NAME="unknown"
    fi
    
    # Create a script to update build-info at rootfs time
    cat > ${WORKDIR}/update-build-info.sh << 'EOFSCRIPT'
#!/bin/sh
# Update rootfs information in /etc/build-info

if [ ! -f /etc/build-info ]; then
    echo "Error: /etc/build-info not found"
    exit 1
fi

# Get rootfs image name from environment or command line
ROOTFS_IMAGE="${ROOTFS_IMAGE:-unknown}"
ROOTFS_BUILD_TIME="$(date '+%Y-%m-%d %H:%M:%S %Z')"

# Update the build-info file
sed -i "s|^ROOTFS_IMAGE=.*|ROOTFS_IMAGE=\"${ROOTFS_IMAGE}\"|" /etc/build-info
sed -i "s|^ROOTFS_BUILD_TIME=.*|ROOTFS_BUILD_TIME=\"${ROOTFS_BUILD_TIME}\"|" /etc/build-info

# Also get kernel build time if available
if [ -f /proc/version ]; then
    # Extract kernel build timestamp from version string
    KERNEL_BUILD_INFO="$(cat /proc/version | sed -n 's/.*#[0-9]* \(.*\) (.*)/\1/p' | cut -d'(' -f1)"
    if [ -n "$KERNEL_BUILD_INFO" ]; then
        sed -i "s|^KERNEL_BUILD_TIME=.*|KERNEL_BUILD_TIME=\"${KERNEL_BUILD_INFO}\"|" /etc/build-info
    fi
fi
EOFSCRIPT
    chmod +x ${WORKDIR}/update-build-info.sh
}

do_install() {
    install -d ${D}${sbindir}
    install -m 0755 ${WORKDIR}/update-build-info.sh ${D}${sbindir}/update-build-info.sh
}

FILES:${PN} = "${sbindir}/update-build-info.sh"

PACKAGE_ARCH = "${MACHINE_ARCH}"
