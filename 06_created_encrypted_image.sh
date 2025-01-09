#!/bin/sh

# Create a file to use as the encrypted device
dd if=/dev/zero of=encrypted.img bs=1M count=50

# Set up the loop device
losetup /dev/loop0 encrypted.img

# Create the LUKS encrypted device
cryptsetup luksFormat /dev/loop0

# Open the encrypted device
cryptsetup luksOpen /dev/loop0 encrypted_device

# Create a filesystem on the encrypted device
mkfs.ext4 /dev/mapper/encrypted_device

# Mount the encrypted device
mkdir -p /mnt/encrypted
mount /dev/mapper/encrypted_device /mnt/encrypted

# Add some data to the encrypted device
echo "This is a test file" > /mnt/encrypted/testfile.txtcryptsetup luksFormat /dev/loop0

# Unmount and close the encrypted device
umount /mnt/encrypted
cryptsetup luksClose encrypted_device
losetup -d /dev/loop0