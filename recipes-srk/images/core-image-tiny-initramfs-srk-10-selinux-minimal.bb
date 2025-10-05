SUMMARY = "Minimal initramfs image with SELinux (no SDK)"
DESCRIPTION = "Ultra minimal initramfs image with basic SELinux support"

LICENSE = "MIT"

# Use most basic image inheritance
inherit image

# Minimal set of packages
IMAGE_INSTALL = "busybox base-files"

# Add hello application
IMAGE_INSTALL += "hello"

# Add SELinux libraries only if SELinux is enabled
IMAGE_INSTALL += "${@bb.utils.contains("DISTRO_FEATURES", "selinux", "libselinux libsepol", "", d)}"

# Set image type
IMAGE_FSTYPES = "cpio.gz"

# No features
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""

# Small size
IMAGE_ROOTFS_SIZE ?= "8192"

# Completely block SDK-related tasks
do_populate_sdk[noexec] = "1"
do_populate_sdk_ext[noexec] = "1"
do_testimage[noexec] = "1"
do_testsdk[noexec] = "1"

# No SDK dependencies
TOOLCHAIN_HOST_TASK = ""
TOOLCHAIN_TARGET_TASK = ""

# Make sure no SDK stuff gets pulled in
EXTRA_IMAGEDEPENDS = ""

COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"