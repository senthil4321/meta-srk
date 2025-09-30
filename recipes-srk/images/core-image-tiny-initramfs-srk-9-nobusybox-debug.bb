SUMMARY = "srk-debug: Silent init for kernel debugging (no output)"
DESCRIPTION = "Debug version: Uses silent init that produces no serial output, perfect for KGDB debugging without interference."
LICENSE = "MIT"

IMAGE_FSTYPES = "cpio.gz cpio.xz cpio.lz4"

inherit core-image

# Use silent init instead of helloloop
IMAGE_INSTALL = "silentloop"
IMAGE_FEATURES = ""
SPDX_CREATE = "0"

BAD_RECOMMENDATIONS += "busybox shadow shadow-base shadow-securetty"
IMAGE_LINGUAS = ""
GLIBC_GENERATE_LOCALES = ""
ENABLE_LOCALE_GENERATION = "0"

DISTRO_FEATURES:remove = " x11 wayland opengl vulkan bluetooth wifi usbhost usbgadget pcmcia pci 3g nfc zeroconf pulseaudio alsa ptest gobject-introspection-data debuginfod nfs "

ROOTFS_POSTPROCESS_COMMAND += "install_silent_init; create_minimal_devnodes; "

python install_silent_init () {
    bb.warn("Running install_silent_init for debugging")
    import os
    rootfs = d.getVar('IMAGE_ROOTFS')
    target_rel = 'sbin/silentloop'
    silentloop_path = os.path.join(rootfs, target_rel)
    if not os.path.exists(silentloop_path):
        bb.error("silentloop binary not found at %s" % silentloop_path)
    
    # Copy silentloop to /init
    init_path = os.path.join(rootfs, 'init')
    if os.path.islink(init_path) or os.path.exists(init_path):
        try:
            os.remove(init_path)
        except OSError as e:
            bb.warn("Failed removing existing /init: %s" % e)
    import shutil
    shutil.copy2(silentloop_path, init_path)
    os.chmod(init_path, 0o755)
    bb.warn("Copied silentloop to /init - NO SERIAL OUTPUT for debugging")
    
    # Provide /sbin/init symlink too (kernel fallback search path)
    sbin_init = os.path.join(rootfs, 'sbin', 'init')
    if os.path.islink(sbin_init) or os.path.exists(sbin_init):
        try:
            os.remove(sbin_init)
        except OSError as e:
            bb.warn("Failed removing existing /sbin/init: %s" % e)
    os.symlink('silentloop', sbin_init)  # relative inside /sbin
    bb.warn("Created /sbin/init symlink - SILENT MODE for KGDB")
    
    # Create a debug info file
    debug_info = os.path.join(rootfs, 'DEBUG_INFO.txt')
    with open(debug_info, 'w') as f:
        f.write("DEBUG INITRAMFS - Silent Init\n")
        f.write("=============================\n")
        f.write("This initramfs uses a silent init program that produces NO output.\n")
        f.write("Perfect for kernel debugging with KGDB - no serial interference.\n")
        f.write("Init process: silentloop (completely quiet)\n")
        f.write("Created: $(date)\n")
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
    bb.warn("Created minimal device nodes for debug initramfs")
}

# No need for passwd/shadow; single binary environment
VIRTUAL-RUNTIME_init_manager = ""