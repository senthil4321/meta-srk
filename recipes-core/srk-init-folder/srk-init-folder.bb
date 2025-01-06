SUMMARY = "Create SRK initialization folder in the root directory"
DESCRIPTION = "This recipe creates a folder named '/srk' in the root directory for system initialization or other purposes."
LICENSE = "MIT"


# Define the directory to create
PROC_DIR = "/proc"
SYS_DIR = "/sys"
DEV_DIR = "/dev"


do_install() {
    # Create the SRK directory in the root filesystem
    install -d ${D}${PROC_DIR}
    install -d ${D}${SYS_DIR}
    install -d ${D}${DEV_DIR}
}

# Specify which files or directories to package
FILES:${PN} = "${PROC_DIR}"
FILES:${PN} += "${SYS_DIR}"
FILES:${PN} += "${DEV_DIR}"

# Define where to deploy the package
RDEPENDS:${PN} = ""

# Package installation is automatic during image creation
