SUMMARY = "Tiny image without cryptsetup (testing size impact)"
DESCRIPTION = "Variant of core-image-tiny-initramfs-srk-3 dropping cryptsetup and util-linux-mount to rely solely on BusyBox."

LICENSE = "MIT"

IMAGE_FSTYPES = "cpio.gz cpio.xz"

inherit core-image

# Drop cryptsetup + util-linux-mount compared to -3
IMAGE_INSTALL = "busybox srk-init"
IMAGE_INSTALL:append = " srk-init"

IMAGE_FEATURES = ""
SPDX_CREATE = "0"

BAD_RECOMMENDATIONS += "shadow shadow-base shadow-securetty"
IMAGE_LINGUAS = ""
GLIBC_GENERATE_LOCALES = ""
ENABLE_LOCALE_GENERATION = "0"

DISTRO_FEATURES:remove = " \
    x11 \
    wayland \
    opengl \
    vulkan \
    bluetooth \
    wifi \
    usbhost \
    usbgadget \
    pcmcia \
    pci \
    3g \
    nfc \
    zeroconf \
    pulseaudio \
    alsa \
    ptest \
    gobject-introspection-data \
    debuginfod \
    nfs \
    "

COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

ROOTFS_POSTPROCESS_COMMAND += "create_minimal_passwd_shadow; "

## Password hashes intentionally blank for passwordless login in initramfs (NOT for production use)
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

# NOTE: BusyBox mount must provide required flags; if missing, re-add util-linux-mount.
