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

ROOTFS_POSTPROCESS_COMMAND += "install_minimal_init; "

python install_minimal_init () {
    import os, stat
    rootfs = d.getVar('IMAGE_ROOTFS')
    init_path = os.path.join(rootfs, 'init')
    # Link /init to /sbin/helloloop (installed by recipe)
    target = '/sbin/helloloop'
    with open(init_path, 'w') as f:
        f.write("#!/bin/sh\nexec {}\n".format(target))
    os.chmod(init_path, 0o755)
}

# No need for passwd/shadow; single binary environment
VIRTUAL-RUNTIME_init_manager = ""
