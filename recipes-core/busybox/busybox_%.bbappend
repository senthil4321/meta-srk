# Trim BusyBox applets for srk-5 minimal initramfs.
# Remove networking extras, editors, and other non-essential utilities.
# This example keeps: sh, mount/umount, ls, cat, dmesg, echo, cp, mv, rm, mkdir, modprobe/insmod/rmmod, ps, top, ifconfig, udhcpc, ip, ping (optional), login, init, switch_root (though not used), tar, gzip/xz/lz4 (if built-in), vi removed.

# Use a custom defconfig fragment approach. We start from default then disable.
# For stronger control you could supply a full defconfig via FILESEXTRAPATHS and SRC_URI, but here we just append a fragment.

FILESEXTRAPATHS:prepend := "${THISDIR}/busybox-config:" 

SRC_URI:append = " file://defconfig-fragment.cfg"

# For srk-8 (no networking) include additional fragment
SRC_URI:append:pn-busybox += " ${@' file://defconfig-fragment-nonet.cfg' if d.getVar('IMAGE_BASENAME') == 'core-image-tiny-initramfs-srk-8-nonet' else ''}"

do_configure:append() {
    if [ -f ${WORKDIR}/defconfig-fragment.cfg ]; then
        # Apply fragment: disable listed symbols
        while IFS= read -r line; do
            # line format: CONFIG_FOO is not set
            opt=$(echo "$line" | sed -n 's/^# \(CONFIG_[A-Z0-9_]*\) is not set/\1/p')
            if [ -n "$opt" ]; then
                sed -i "/^$opt=/d" .config || true
                echo "$line" >> .config
            fi
        done < ${WORKDIR}/defconfig-fragment.cfg
    fi

    # Apply non-network fragment if present
    if [ -f ${WORKDIR}/defconfig-fragment-nonet.cfg ]; then
        while IFS= read -r line; do
            opt=$(echo "$line" | sed -n 's/^# \(CONFIG_[A-Z0-9_]*\) is not set/\1/p')
            if [ -n "$opt" ]; then
                sed -i "/^$opt=/d" .config || true
                echo "$line" >> .config
            fi
        done < ${WORKDIR}/defconfig-fragment-nonet.cfg
    fi
}
