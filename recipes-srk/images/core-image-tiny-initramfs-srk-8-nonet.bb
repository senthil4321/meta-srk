SUMMARY = "srk-8-nonet: BusyBox-only initramfs with networking applets removed"
DESCRIPTION = "Trial 13: Based on srk-7-sizeopt (size flags + lz4) but removes BusyBox networking utilities via additional config fragment."
LICENSE = "MIT"

IMAGE_FSTYPES = "cpio.gz cpio.xz cpio.lz4"

inherit core-image

IMAGE_INSTALL = "busybox"
IMAGE_FEATURES = ""
SPDX_CREATE = "0"

BAD_RECOMMENDATIONS += "shadow shadow-base shadow-securetty"
IMAGE_LINGUAS = ""
GLIBC_GENERATE_LOCALES = ""
ENABLE_LOCALE_GENERATION = "0"

DISTRO_FEATURES:remove = " \
    x11 wayland opengl vulkan bluetooth wifi usbhost usbgadget pcmcia pci 3g nfc zeroconf pulseaudio alsa ptest gobject-introspection-data debuginfod nfs \
    "

COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

ROOTFS_POSTPROCESS_COMMAND += "create_minimal_passwd_shadow; create_simple_init; "

PASSWD_HASH_ROOT = ""
PASSWD_HASH_SRK  = ""

python create_minimal_passwd_shadow () {
    import os
    rootfs = d.getVar('IMAGE_ROOTFS')
    etc = os.path.join(rootfs, 'etc')
    os.makedirs(etc, exist_ok=True)
    passwd_content = "root:x:0:0:root:/root:/bin/sh\nsrk:x:1000:1000:srk:/home/srk:/bin/sh\n"
    shadow_content = f"root:{d.getVar('PASSWD_HASH_ROOT')}:19647:0:99999:7:::\nsrk:{d.getVar('PASSWD_HASH_SRK')}:19647:0:99999:7:::\n"
    for name, data in [('passwd', passwd_content), ('shadow', shadow_content), ('group', 'root:x:0:\nsrk:x:1000:\n'), ('gshadow', 'root:::\nsrk:::\n')]:
        with open(os.path.join(etc, name), 'w') as f:
            f.write(data)
    home = os.path.join(rootfs, 'home', 'srk')
    os.makedirs(home, exist_ok=True)
    os.chmod(home, 0o755)
}

python create_simple_init () {
    import os, stat
    rootfs = d.getVar('IMAGE_ROOTFS')
    init_path = os.path.join(rootfs, 'init')
    script = "#!/bin/sh\n\nmount -t proc proc /proc 2>/dev/null || true\nmount -t sysfs sysfs /sys 2>/dev/null || true\necho 'Initramfs (srk-8-nonet) shell. Networking applets removed. Press Ctrl-D to reboot.'\nexec /bin/sh\n"
    with open(init_path, 'w') as f:
        f.write(script)
    os.chmod(init_path, 0o755)
}

VIRTUAL-RUNTIME_init_manager = "busybox"
