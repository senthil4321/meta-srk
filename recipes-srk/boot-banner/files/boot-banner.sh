#!/bin/sh
### BEGIN INIT INFO
# Provides:          boot-banner
# Required-Start:    $local_fs
# Required-Stop:
# Default-Start:     S
# Default-Stop:
# Short-Description: Display boot banner with build information
### END INIT INFO

# Read build information
if [ -f /etc/build-info ]; then
    . /etc/build-info
fi

# Display boot banner
echo "================================================================================"
echo "  System Boot Information"
echo "================================================================================"
echo "  Kernel Recipe: ${KERNEL_RECIPE:-unknown}"
echo "  Rootfs Image:  ${ROOTFS_IMAGE:-unknown}"
echo "  Machine:       ${MACHINE:-unknown}"
echo "  Build Time:    ${BUILD_TIME:-unknown}"
echo "  Kernel:        $(uname -r)"
echo "  Distro:        ${DISTRO:-unknown} ${DISTRO_VERSION:-}"
echo "================================================================================"

# Also log to kernel log
if [ -w /dev/kmsg ]; then
    echo "Boot: Kernel=${KERNEL_RECIPE:-unknown} Rootfs=${ROOTFS_IMAGE:-unknown} Build=${BUILD_TIME:-unknown}" > /dev/kmsg
fi
