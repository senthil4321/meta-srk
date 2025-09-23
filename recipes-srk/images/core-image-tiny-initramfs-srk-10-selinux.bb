SUMMARY = "srk-10-selinux: BusyBox initramfs with SELinux support"
DESCRIPTION = "Trial 15: Derives from srk-8-nonet but adds SELinux kernel + userspace components for experimentation. Not size-optimized."
LICENSE = "MIT"

IMAGE_FSTYPES = "cpio.gz cpio.xz cpio.lz4"

inherit core-image

# Add SELinux feature (requires meta-selinux layer in bblayers.conf)
DISTRO_FEATURES:append = " selinux"

# Prefer the SELinux-enabled kernel for this image only
PREFERRED_PROVIDER_virtual/kernel = "linux-yocto-srk-selinux"

# Reference policy selection (common upstream naming – adjust if different in your layers)
PREFERRED_PROVIDER_virtual/refpolicy ?= "refpolicy-targeted"

IMAGE_INSTALL = "busybox \
                 libselinux \
                 libsepol \
                 libsemanage \
                 policycoreutils-loadpolicy \
                 policycoreutils-setfiles \
                 policycoreutils-sestatus \
                 policycoreutils-secon \
                 policycoreutils-semodule \
                 policycoreutils-setsebool \
                 refpolicy-targeted \
                 "

# Avoid pulling in shadow, keep tiny passwd model (optional)
BAD_RECOMMENDATIONS += "shadow shadow-base shadow-securetty"

IMAGE_FEATURES = ""
SPDX_CREATE = "0"

IMAGE_LINGUAS = ""
GLIBC_GENERATE_LOCALES = ""
ENABLE_LOCALE_GENERATION = "0"

DISTRO_FEATURES:remove = " x11 wayland opengl vulkan bluetooth wifi usbhost usbgadget pcmcia pci 3g nfc zeroconf pulseaudio alsa ptest gobject-introspection-data debuginfod nfs "

COMPATIBLE_HOST = "(i.86|x86_64|aarch64|arm).*-linux"

ROOTFS_POSTPROCESS_COMMAND += "create_minimal_passwd_shadow; create_selinux_init; "

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

python create_selinux_init () {
    import os
    rootfs = d.getVar('IMAGE_ROOTFS')
    init_path = os.path.join(rootfs, 'init')
    script = """#!/bin/sh
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
# Create basic /dev structure if needed
if [ ! -d /dev ]; then
    mkdir -p /dev
fi
# Mount devtmpfs to provide device nodes
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
# Create console device if it doesn't exist
if [ ! -c /dev/console ]; then
    mknod /dev/console c 5 1 2>/dev/null || true
fi
mount -t selinuxfs selinuxfs /sys/fs/selinux 2>/dev/null || echo 'WARN: selinuxfs mount failed'
echo 'Loading SELinux policy (if present)...'
if command -v load_policy >/dev/null 2>&1; then
    load_policy || echo 'WARN: load_policy failed'
fi
if command -v setenforce >/dev/null 2>&1; then
    setenforce 0 2>/dev/null || true
fi
echo 'SELinux trial environment (srk-10-selinux). Type exit or Ctrl-D to reboot.'
# Set up console for interactive shell
exec /bin/sh < /dev/console > /dev/console 2>&1
"""
    with open(init_path, 'w') as f:
        f.write(script)
    os.chmod(init_path, 0o755)
}

VIRTUAL-RUNTIME_init_manager = "busybox"

# Notes:
# 1. Ensure meta-selinux layer is added to bblayers.conf before building.
# 2. Kernel fragment selinux.cfg enables SELinux in kernel; adjust policies as needed.
# 3. Initial setenforce 0 (permissive) to avoid early denials while experimenting.
