#!/bin/bash

# Define the device and source directories
DEVICE="/dev/sda"  # Replace with the actual device identifier
BOOT_PART="${DEVICE}1"
ROOTFS_PART="${DEVICE}2"
SOURCE_DIR="/mnt/beaglebone/"

# Unmount the device if it is mounted
umount "${BOOT_PART}" 2>/dev/null
umount "${ROOTFS_PART}" 2>/dev/null

# Create partitions
parted -s "$DEVICE" mklabel msdos
parted -s "$DEVICE" mkpart primary fat32 1MiB 100MiB
parted -s "$DEVICE" mkpart primary ext4 100MiB 100%

# Format the partitions
mkfs.vfat -F 32 "$BOOT_PART"
mkfs.ext4 "$ROOTFS_PART"

# Mount the partitions
mkdir -p /mnt/beaglebone-boot
mkdir -p /mnt/beaglebone-rootfs
mount "$BOOT_PART" /mnt/beaglebone-boot
mount "$ROOTFS_PART" /mnt/beaglebone-rootfs

# Copy the boot files using rsync
rsync -avzu --progress "$SOURCE_DIR"/MLO /mnt/beaglebone-boot/
rsync -avzu --progress "$SOURCE_DIR"/u-boot.img /mnt/beaglebone-boot/
rsync -avzu --progress "$SOURCE_DIR"/zImage /mnt/beaglebone-boot/
rsync -avzu --progress "$SOURCE_DIR"/am335x-boneblack.dtb /mnt/beaglebone-boot/

# Copy the root filesystem
tar -xvf "$SOURCE_DIR"/core-image-minimal-beaglebone-yocto.rootfs-*.tar.bz2 -C /mnt/beaglebone-rootfs/

# Sync and unmount
sync
umount /mnt/beaglebone-boot
umount /mnt/beaglebone-rootfs

echo "BeagleBone Black SD card prepared successfully"
