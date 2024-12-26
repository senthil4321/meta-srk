#!/bin/bash

# Define the source and destination directories
SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/"
cd "$SOURCE_DIR"
REMOTE_DEST_DIR="selinux@selinux1.local:/mnt/beaglebone/"
REMOTE_PASSWORD="selinux123"

sshpass -p "$REMOTE_PASSWORD" scp -r "$SOURCE_DIR"/MLO "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" scp -r "$SOURCE_DIR"/u-boot.img "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" scp -r "$SOURCE_DIR"/zImage "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" scp -r "$SOURCE_DIR"/am335x-boneblack.dtb "$REMOTE_DEST_DIR"
sshpass -p "$REMOTE_PASSWORD" scp -r "$SOURCE_DIR"/beaglebone-yocto-rootfs.tar.gz "$REMOTE_DEST_DIR"

echo "BeagleBone build output copied to $SOURCE_DIR and $REMOTE_DEST_DIR"
