PN = "core-image-tiny-initramfs-srk-4-size-optimisation-trial"
SUMMARY = "Tiny image capable of booting a device."
DESCRIPTION = "Tiny image capable of booting a device."

LICENSE = "MIT"

# Specify the filesystem types for the initramfs (add xz for better compression)
IMAGE_FSTYPES = "cpio.gz cpio.xz"

inherit core-image

# Include only required tools (drop shadow to reduce size; use busybox passwd handling)
IMAGE_INSTALL = "busybox cryptsetup util-linux-mount srk-init"
# IMAGE_INSTALL:append = " srk-init-folder"
IMAGE_INSTALL:append = " srk-init"

# Do not include any additional features
IMAGE_FEATURES = ""

# Disable SPDX creation for minimal builds
SPDX_CREATE = "0"

# Exclude shadow packages even if recommended and strip locales
BAD_RECOMMENDATIONS += "shadow shadow-base shadow-securetty"
IMAGE_LINGUAS = ""
GLIBC_GENERATE_LOCALES = ""
ENABLE_LOCALE_GENERATION = "0"

# Remove unnecessary DISTRO_FEATURES for minimal initramfs
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

# Use the same restriction as initramfs-live-install
COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

# Custom minimal passwd/shadow (avoid pulling shadow package via extrausers)
ROOTFS_POSTPROCESS_COMMAND += "create_minimal_passwd_shadow; "

PASSWD_HASH_ROOT = "\$1\$WUwXnz3s\$dCRM7MUDP8/0wPAef1XfO1"
PASSWD_HASH_SRK  = "\$1\$V9izHbFg\$z8ZfBeREgRqdOP3AuHGn51"

python create_minimal_passwd_shadow () {
    import os
    rootfs = d.getVar('IMAGE_ROOTFS')
    etc = os.path.join(rootfs, 'etc')
    os.makedirs(etc, exist_ok=True)
    # passwd: root and srk with /bin/sh
    passwd_content = "root:x:0:0:root:/root:/bin/sh\nsrk:x:1000:1000:srk:/home/srk:/bin/sh\n"
    shadow_content = f"root:{d.getVar('PASSWD_HASH_ROOT')}:19647:0:99999:7:::\nsrk:{d.getVar('PASSWD_HASH_SRK')}:19647:0:99999:7:::\n"
    for name, data in [('passwd', passwd_content), ('shadow', shadow_content), ('group', 'root:x:0:\nsrk:x:1000:\n'), ('gshadow', 'root:::\nsrk:::\n')]:
        with open(os.path.join(etc, name), 'w') as f:
            f.write(data)
    # basic homedir
    home = os.path.join(rootfs, 'home', 'srk')
    os.makedirs(home, exist_ok=True)
    os.chmod(home, 0o755)
}

# Enable essential kernel modules
# DISTRO_FEATURES:remove = "systemd"
# DISTRO_FEATURES:append = " sysvinit"
# VIRTUAL-RUNTIME_init_manager = "busybox"
