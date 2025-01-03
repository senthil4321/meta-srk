#!/bin/bash

# Define the source and destination directories
SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
cd "$SOURCE_DIR"
REMOTE_DEST_DIR="selinux@selinux1.local:/mnt/beaglebone/"
REMOTE_PASSWORD="selinux123"

# Copy files only if they have changed using rsync and sshpass
sshpass -p "$REMOTE_PASSWORD" rsync -avzu --progress "$SOURCE_DIR"/MLO "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" rsync -avzu --progress "$SOURCE_DIR"/u-boot.img "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" rsync -avzu --progress "$SOURCE_DIR"/zImage "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" rsync -avzu --progress "$SOURCE_DIR"/am335x-boneblack.dtb "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" rsync -avzu --progress "$SOURCE_DIR"/core-image-minimal-beaglebone-yocto.rootfs-*.tar.bz2 "$REMOTE_DEST_DIR"

echo "BeagleBone build output copied to $REMOTE_DEST_DIR if changed"
