# meta-srk

meta-srk

## bitbake tutorial

```bash
bitbake-layers create-layer ../meta-srk
bitbake-layers add-layer ../meta-srk
bitbake-layers show-layers
```

## Important Variables

```ba### Kernel Modules```
```

T```

TODO

```bash
### add `LINUX_VERSION_EXTENSION += "-srk-trial20"`
```

To overwrite kernel version update the Yocot variable in custom `kernel recipe` or `local.conf`
# LINUX_VERSION_EXTENSION += "-srk-trial20"bash
### add `LINUX_VERSION_EXTENSION += "-srk-trial20"`
```

To overwrite kernel version update the Yocot variable in custom `kernel recipe` or `local.conf`
# LINUX_VERSION_EXTENSION += "-srk-trial20"``bash
### add `LINUX_VERSION_EXTENSION += "-srk-trial20"`
```bash
sunrpc - Used by NFS
xfrm - used by IPSec
```

TODO

```bash
### add `LINUX_VERSION_EXTENSION += "-srk-trial20"`
```

To overwrite kernel version update the Yocot variable in custom `kernel recipe` or `local.conf`
# LINUX_VERSION_EXTENSION += "-srk-trial20"
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

### Workflow - initramfs

1. Run bitbake `bitbake core-image-tiny-initramfs-srk-3` to compile initRamFS Image with cryptsetup.
2. Run bitbake `bitbake core-image-minimal-squashfs-srk` to compile rootfs
3. Run `106_created_encrypted_image.sh 4`
4. Run `06_created_encrypted_image.sh 8`
5. Run `06_created_encrypted_image.sh 10`
6. Run `03_copy_initramfs.sh 3`
7. Run `05_copy_squashfs.sh -i -k` -> note order is important, as command 6 deletes entire nfs in the server.
8. Copy `zImage` using script `04_copy_zImage.sh`
`

## Initramfs Image Recipes

The meta-srk layer provides several initramfs image recipes optimized for different use cases:

### core-image-tiny-initramfs-srk-2 (systemd-based)

* **Init System**: systemd
* **Core Packages**: systemd, busybox, shadow, nfs-utils
* **Features**: systemd-serialgetty, kernel-modules
* **Use Case**: Traditional Linux initramfs with service management and NFS support
* **Size**: Larger footprint due to full systemd inclusion

### core-image-tiny-initramfs-srk-3 (busybox-based)

* **Init System**: busybox (sysvinit)
* **Core Packages**: busybox, shadow, cryptsetup, util-linux-mount, srk-init
* **Features**: Encryption support via cryptsetup, custom srk-init for encrypted boot
* **Use Case**: Minimal initramfs for encrypted SquashFS root filesystem booting
* **Size**: Smaller footprint, optimized for embedded systems

### Key Differences

| Feature | srk-2 (systemd) | srk-3 (busybox) |
|---------|----------------|-----------------|
| **Init Manager** | systemd | busybox sysvinit |
| **Encryption** | ❌ None | ✅ cryptsetup |
| **SRK Integration** | ❌ None | ✅ srk-init |
| **NFS Support** | ✅ Built-in | ❌ None |
| **Services** | systemd services | Minimal busybox |
| **Footprint** | Larger | Smaller |

### Recommendation

* **Use srk-2**: For general initramfs testing, NFS booting, or traditional Linux workflows
* **Use srk-3**: For encrypted root filesystem workflows with SquashFS images

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
### TODO 
~### add `LINUX_VERSION_EXTENSION += "-srk-trial20"`~
To overwrite kernel version update the Yocot variable in custom `kernel recipe` or `local.conf`

```text
# LINUX_VERSION_EXTENSION += "-srk-trial20"
```

### workflow rootfs encrypted build

```bash
bitbake core-image-minimal-srk
06_created_encrypted_image.sh 4
06_created_encrypted_image.sh 8
06_created_encrypted_image.sh 10
05_copy_squashfs.sh -i
```

## SRK Serial Test Script

A Python-based test automation script for SRK target devices that connects via SSH and performs serial communication testing.

### Version
1.6.0

### Features

- **Remote Serial Testing**: Connects to target device via SSH and socat for reliable serial communication
- **Automated Test Suite**: Runs comprehensive tests including login, command execution, and output verification
- **Colored Report Generation**: Generates formatted test reports with color-coded status indicators
- **Detailed Output**: Shows actual system information (versions, timestamps, uptime) in test results
- **Modular Design**: Separated report generation into a reusable module
- **Command-line Interface**: Supports saving reports to files and version display
- **Initramfs Analysis**: Separated checks for init system type and encryption support

### Usage

#### Basic Usage
```bash
python3 test_serial_hello.py
```

#### Save Report to File
```bash
python3 test_serial_hello.py --save-report test_results.txt
```

#### Show Version
```bash
python3 test_serial_hello.py --version
```

## Important

### Yocto Best Practices

- Flexibility: Images can override distro defaults when needed
- Layered Configuration: Distro → Image → Machine → Local overrides
- Common Pattern: Many Yocto projects do this (e.g., initramfs with busybox, rootfs with systemd)

### Test Steps

The script performs the following test steps:

1. **Check U-Boot logs** - Verifies U-Boot boot logs (non-blocking)
2. **Check kernel logs** - Verifies Linux kernel boot logs (non-blocking)
3. **Check initramfs logs** - Verifies initramfs boot logs (non-blocking)
4. **Wait for initial prompt** - Waits for login or shell prompt
5. **Perform login** - Logs into the system if not already logged in
6. **Check hello exists** - Verifies hello command is available
7. **Run and verify hello** - Executes hello command and verifies output
8. **Check build version** - Verifies system build information
9. **Check build time** - Displays kernel build timestamp from `uname -v`
10. **Check system timestamp** - Shows system build time from `/etc/timestamp` or file modification dates
11. **Check system uptime** - Displays how long the system has been running since last boot
12. **Check BusyBox version** - Verifies BusyBox installation
13. **Check encryption support** - Verifies presence of encryption components (cryptsetup, srk-init)
14. **Check init system type** - Determines whether systemd or busybox init is running

### Build Time Information

The test script now includes comprehensive build time checking with **detailed output**:

- **Kernel Build Time**: Shows when the Linux kernel was compiled (e.g., "Tue Mar 19 16:42:51 UTC 2024")
- **System Timestamp**: Displays the build timestamp from system files
- **System Uptime**: Indicates how long the system has been running (e.g., "2 days, 3:45")
- **Build Version**: Shows complete system version information
- **BusyBox Version**: Displays the exact BusyBox version installed

This information is crucial for:
- Verifying the freshness of the build
- Troubleshooting timing-related issues
- Confirming the system is running the expected version
- Performance analysis and optimization

### Requirements

- Python 3.8+
- paramiko
- SSH access to target device
- socat installed on target device

### Copyright

Copyright (c) 2025 SRK. All rights reserved.

