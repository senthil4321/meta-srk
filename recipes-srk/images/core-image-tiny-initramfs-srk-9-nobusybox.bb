SUMMARY = "srk-9-nobusybox: Minimal static helloloop only (no BusyBox)"
DESCRIPTION = "Trial 14: Removes BusyBox entirely; provides a static /init replacement (helloloop) printing Hello World + date every second."
LICENSE = "MIT"

IMAGE_FSTYPES = "cpio.gz cpio.xz cpio.lz4"

inherit core-image

# Do not pull in busybox
IMAGE_INSTALL = "helloloop"
IMAGE_FEATURES = ""
SPDX_CREATE = "0"

BAD_RECOMMENDATIONS += "busybox shadow shadow-base shadow-securetty"
IMAGE_LINGUAS = ""
GLIBC_GENERATE_LOCALES = ""
ENABLE_LOCALE_GENERATION = "0"

DISTRO_FEATURES:remove = " x11 wayland opengl vulkan bluetooth wifi usbhost usbgadget pcmcia pci 3g nfc zeroconf pulseaudio alsa ptest gobject-introspection-data debuginfod nfs "

ROOTFS_POSTPROCESS_COMMAND += "install_minimal_init; create_minimal_devnodes; "

python install_minimal_init () {
    bb.warn("Running install_minimal_init")
    import os
    rootfs = d.getVar('IMAGE_ROOTFS')
    target_rel = 'sbin/helloloop'
    helloloop_path = os.path.join(rootfs, target_rel)
    if not os.path.exists(helloloop_path):
        bb.error("helloloop binary not found at %s" % helloloop_path)
    # Copy helloloop to /init
    init_path = os.path.join(rootfs, 'init')
    if os.path.islink(init_path) or os.path.exists(init_path):
        try:
            os.remove(init_path)
        except OSError as e:
            bb.warn("Failed removing existing /init: %s" % e)
    import shutil
    shutil.copy2(helloloop_path, init_path)
    os.chmod(init_path, 0o755)
    bb.warn("Copied helloloop to /init")
    # Provide /sbin/init symlink too (kernel fallback search path)
    sbin_init = os.path.join(rootfs, 'sbin', 'init')
    if os.path.islink(sbin_init) or os.path.exists(sbin_init):
        try:
            os.remove(sbin_init)
        except OSError as e:
            bb.warn("Failed removing existing /sbin/init: %s" % e)
    os.symlink('helloloop', sbin_init)  # relative inside /sbin
    bb.warn("Created /sbin/init symlink")
}

python create_minimal_devnodes () {
    import os, stat
    rootfs = d.getVar('IMAGE_ROOTFS')
    devdir = os.path.join(rootfs, 'dev')
    if not os.path.isdir(devdir):
        os.makedirs(devdir)
    console = os.path.join(devdir, 'console')
    null = os.path.join(devdir, 'null')
    def mknod(path, mode, dev):
        if not os.path.exists(path):
            os.mknod(path, mode | stat.S_IFCHR, dev)
    import os as _os
    # c 5 1 console (0600)
    mknod(console, 0o600, os.makedev(5,1))
    # c 1 3 null (0666)
    mknod(null, 0o666, os.makedev(1,3))
}

# No need for passwd/shadow; single binary environment
VIRTUAL-RUNTIME_init_manager = ""
