SUMMARY = "BBB EEPROM Reader Image with BusyBox - SRK Examples"
DESCRIPTION = "Minimal image with BusyBox init system and BBB EEPROM reader utility - Part of SRK examples series"
LICENSE = "MIT"

inherit core-image

# Include BusyBox, EEPROM reader app, and LED blink app
IMAGE_INSTALL = "busybox bbb-01-eeprom bbb-02-led-blink bbb-03-rtc"

# Minimal system packages
IMAGE_INSTALL += "base-files base-passwd"

# Networking & i2c tools (optional)
IMAGE_INSTALL += "netbase i2c-tools"

# No extra features
IMAGE_FEATURES = ""
IMAGE_LINGUAS = ""

# Debug helpers
EXTRA_IMAGE_FEATURES += "debug-tweaks"

# Remove unneeded distro features
DISTRO_FEATURES:remove = "x11 wayland opengl vulkan bluetooth wifi usbhost usbgadget \
                          pcmcia pci 3g nfc zeroconf pulseaudio alsa ptest \
                          gobject-introspection-data debuginfod nfs"

# Use BusyBox init system
VIRTUAL-RUNTIME_init_manager = "busybox"
VIRTUAL-RUNTIME_initscripts = "busybox"

# Rootfs size
IMAGE_ROOTFS_SIZE = "8192"

# Build cpio.gz initramfs
IMAGE_FSTYPES = "cpio.gz"

# Postprocess steps
ROOTFS_POSTPROCESS_COMMAND += "install_minimal_init; create_minimal_devnodes; "

python install_minimal_init () {
    bb.warn("Running install_minimal_init for BBB EEPROM image")
    import os
    rootfs = d.getVar('IMAGE_ROOTFS')

    busybox_path = os.path.join(rootfs, 'bin', 'busybox')
    init_path = os.path.join(rootfs, 'init')
    sbin_init = os.path.join(rootfs, 'sbin', 'init')

    if not os.path.exists(busybox_path):
        bb.error("busybox binary not found at %s" % busybox_path)
        return

    # /init -> bin/busybox
    if os.path.islink(init_path) or os.path.exists(init_path):
        try:
            os.remove(init_path)
        except OSError as e:
            bb.warn("Failed removing existing /init: %s" % e)
    os.symlink('bin/busybox', init_path)
    bb.warn("Created /init -> bin/busybox")

    # /sbin/init script
    sbin_dir = os.path.join(rootfs, 'sbin')
    if not os.path.exists(sbin_dir):
        os.makedirs(sbin_dir)

    init_script = """#!/bin/busybox sh
# Minimal init for BBB EEPROM testing

export PATH=/bin:/sbin:/usr/bin:/usr/sbin
export HOME=/root

# Mount essential filesystems
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev

echo "=== BBB EEPROM Minimal Image Booted ==="
echo "Running EEPROM reader..."
/bin/bbb-01-eeprom

echo "Dropping into root shell..."
exec /bin/sh </dev/ttyS0 >/dev/ttyS0 2>&1
"""

    with open(sbin_init, 'w') as f:
        f.write(init_script)
    os.chmod(sbin_init, 0o755)
    bb.warn("Created /sbin/init script")
}

python create_minimal_devnodes () {
    import os, stat
    rootfs = d.getVar('IMAGE_ROOTFS')
    devdir = os.path.join(rootfs, 'dev')
    if not os.path.isdir(devdir):
        os.makedirs(devdir)

    console = os.path.join(devdir, 'console')
    null = os.path.join(devdir, 'null')
    ttyS0 = os.path.join(devdir, 'ttyS0')

    def mknod(path, mode, dev):
        if not os.path.exists(path):
            os.mknod(path, mode | stat.S_IFCHR, dev)

    # Device nodes
    mknod(console, 0o600, os.makedev(5,1))
    mknod(null, 0o666, os.makedev(1,3))
    mknod(ttyS0, 0o620, os.makedev(4,64))  # ttyS0 major=4, minor=64
    bb.warn("Created minimal device nodes: console, null, ttyS0")
}
# Compatible Kernel Recipe
PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-bbb"