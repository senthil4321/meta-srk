# meta-srk

meta-srk

## bitbake tutorial

```bash
bitbake-layers create-layer ../meta-srk
bitbake-layers add-layer ../meta-srk
bitbake-layers show-layers
```

## Important Variables

```bash
PACKAGE_INSTALL
IMAGE_INSTALL
IMAGE_FSTYPES
IMAGE_FEATURES
```

### Package Group Recipe

A package group recipe bundles multiple packages together and then instead of having to explicitly specify each package in the IMAGE_INSTALL variable you can simply specify the package group name.

* https://lists.yoctoproject.org/g/yocto/message/20345

```bash
# How to list all package groups?
ls meta*/recipes*/packagegroups/*
ls meta*/recipes*/images/*
ls meta*/recipes-kernel/*
```

```bash
bitbake -c copy_rootfs_to_nfs rootfs-nfs-copy 
```

```bash
# Generate the dependency graph files
bitbake -g systemd

# Install Graphviz (if not already installed)
sudo apt-get install graphviz

# Convert the DOT file to a PNG image
dot -Tpng task-depends.dot -o systemd-dependency-tree.png

# Open the PNG image to view the dependency tree
xdg-open systemd-dependency-tree.png
```

goto rootfs

```bash
cd $(bitbake -e core-image-tiny-initramfs-srk-1 | grep "^IMAGE_ROOTFS=" | cut -d'=' -f2 | tr -d '"')

openssl passwd -1 1 | sed 's/\$/\\$/g'

echo '$1$V9izHbFg$z8ZfBeREgRqdOP3AuHGn51' | sed 's/\$/\\$/g'
echo \$1\$V9izHbFg\$z8ZfBeREgRqdOP3AuHGn51 | sed 's/\\//g'
```

## Mount sqashfs and switch root

```bash
zcat /proc/config.gz |grep "=y"|grep "CONFIG_SQUASHFS"

CONFIG_SQUASHFS=y
CONFIG_SQUASHFS_FILE_CACHE=y
CONFIG_SQUASHFS_DECOMP_SINGLE=y
CONFIG_SQUASHFS_COMPILE_DECOMP_SINGLE=y
CONFIG_SQUASHFS_XATTR=y
CONFIG_SQUASHFS_ZLIB=y
CONFIG_SQUASHFS_LZ4=y
CONFIG_SQUASHFS_LZO=y
CONFIG_SQUASHFS_XZ=y
CONFIG_SQUASHFS_ZSTD=y

modprobe loop
mount -t squashfs -o loop core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs /mnt/
switch_root /mnt /sbin/init
exec switch_root -c /dev/ttyS0 /mnt /sbin/init
```

```bash
bootargs 'console=ttyS0,115200n8 root=/dev/ram0 rw'

setenv bootargs  'console=ttyS0,115200n8 root=/dev/nfs ip=192.168.1.200 nfsroot=192.168.1.100:/srv/nfs,nfsvers=3,tcp rw'
setenv bootcmd 'tftp 0x81000000 zImage; sleep .2 ; tftp 0x84000000 am335x-boneblack.dtb; sleep .2 ; bootz 0x81000000 - 0x84000000'

setenv bootargs 'console=ttyS0,115200n8 root=/dev/ram0'
saveenv
boo
mount -t nfs 192.168.1.100:/srv/nfs /mnt/

```

## Workflow

1. Run bitbake `bitbake core-image-tiny-initramfs-srk-2` to compile initRamFS Image
2. Run bitbake `bitbake core-image-minimal-srk` to compile Kernel with initRamFS included
3. Copy `zImage` using script `04_copy_zImage.sh`
4. Deply squashfs based ROOTS to `nfs`

## Trial 3.1

Use `busybox` init_manager
Log : meta-srk/backup/01_busybox_init_srk-3/01_busybox_sysv_init_fileSize.txt

```bash
# 2. Remove Kernel and U-Boot from Image
IMAGE_INSTALL:remove = "virtual/kernel virtual/bootloader"
DISTRO_FEATURES:remove = "systemd"
DISTRO_FEATURES:append = " sysvinit"
VIRTUAL-RUNTIME_init_manager = "busybox"
```

## Trial 3.2

Use `mdev-busybox` init_manager

Log : meta-srk/backup/01_busybox_init_srk-3/02_busybox_mdev_init_fileSize

```bash
# 2. Remove Kernel and U-Boot from Image
IMAGE_INSTALL:remove = "virtual/kernel virtual/bootloader"
DISTRO_FEATURES:remove = "systemd"
DISTRO_FEATURES:remove = " sysvinit"
VIRTUAL-RUNTIME_init_manager = "mdev-busybox"
SERIAL_CONSOLES = ""
```

## Trial 3.3 - TODO

Change the library to `musl`

Log : meta-srk/backup/01_busybox_init_srk-3/

Result : Faulure

```bash
# 2. Remove Kernel and U-Boot from Image
IMAGE_INSTALL:remove = "virtual/kernel virtual/bootloader"
DISTRO_FEATURES:remove = "systemd"
DISTRO_FEATURES:append = " sysvinit"
VIRTUAL-RUNTIME_init_manager = "busybox"

PREFERRED_PROVIDER_virtual/libc = "musl"
PREFERRED_PROVIDER_virtual/libiconv = "glibc"

```

### Kernel Modules

```bash
sunrpc - Used by NFS
xfrm - used by IPSec
```

TODO 

~~~ ### add `LINUX_VERSION_EXTENSION += "-srk-trial20"`~~

To overwrite kernel version update the Yocot variable in custom `kernel recipe` or `local.conf`
# LINUX_VERSION_EXTENSION += "-srk-trial20"

### workflow rootfs encrypted build

```bash
bitbake core-image-minimal-srk
06_created_encrypted_image.sh 4
06_created_encrypted_image.sh 8
06_created_encrypted_image.sh 10
05_copy_squashfs.sh -i
```
