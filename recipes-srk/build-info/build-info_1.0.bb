SUMMARY = "Build information file"
DESCRIPTION = "Creates /etc/build-info with kernel, rootfs, and machine information"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

S = "${WORKDIR}/sources-unpack"

inherit allarch

do_compile() {
    # Get current timestamp for kernel build time
    KERNEL_BUILD_TIME="$(date '+%Y-%m-%d %H:%M:%S %Z')"
    
    # Get kernel recipe name
    KERNEL_RECIPE="${PREFERRED_PROVIDER_virtual/kernel}"
    
    # Create the build-info file (without quotes around values to avoid double quoting)
    cat > ${WORKDIR}/build-info << EOF
# Build Information - Generated at build time
# This file is created by the build-info recipe

# System identification
MACHINE=${MACHINE}
DISTRO=${DISTRO}
DISTRO_VERSION=${DISTRO_VERSION}

# Kernel information
KERNEL_RECIPE=${KERNEL_RECIPE}
KERNEL_VERSION=${PREFERRED_VERSION_linux-yocto-srk}
KERNEL_BUILD_TIME=${KERNEL_BUILD_TIME}

# Rootfs information (updated by image recipe)
ROOTFS_IMAGE=unknown
ROOTFS_BUILD_TIME=unknown

# Architecture
TARGET_ARCH=${TARGET_ARCH}
BUILD_ARCH=${BUILD_ARCH}
EOF
}

do_install() {
    install -d ${D}${sysconfdir}
    install -m 0644 ${WORKDIR}/build-info ${D}${sysconfdir}/build-info
}

FILES:${PN} = "${sysconfdir}/build-info"

# This package should be machine-specific
PACKAGE_ARCH = "${MACHINE_ARCH}"
