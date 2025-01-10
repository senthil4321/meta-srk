#!/bin/sh

# Create a file to use as the encrypted device
dd if=/dev/zero of=encrypted.img bs=1M count=10

# Set up the loop device
sudo losetup -f encrypted.img

# Get the loop device for encrypted.img
LOOP_DEVICE=$(sudo losetup -a | grep encrypted.img | cut -d: -f1)
if [ -z "$LOOP_DEVICE" ]; then
    echo "Error: Loop device for encrypted.img not found."
    exit 1
fi

# Create the LUKS encrypted device
sudo cryptsetup luksFormat $LOOP_DEVICE

# Open the encrypted device
sudo cryptsetup luksOpen $LOOP_DEVICE encrypted_device

# Create a filesystem on the encrypted device
mkfs.ext3 /dev/mapper/encrypted_device

# Mount the encrypted device
mkdir -p /mnt/encrypted
mount /dev/mapper/encrypted_device /mnt/encrypted

# Add some data to the encrypted device
echo "This is a test file" > /mnt/encrypted/testfile.txt

# Unmount and close the encrypted device
umount /mnt/encrypted
cryptsetup luksClose encrypted_device
sudo losetup -d $LOOP_DEVICE



# Create the LUKS encrypted device with specific cipher
dd if=/dev/zero of=encrypted.img bs=1M count=10

# Set up the loop device
sudo losetup -f encrypted.img

# Get the loop device for encrypted.img
LOOP_DEVICE=$(sudo losetup -a | grep encrypted.img | cut -d: -f1)
if [ -z "$LOOP_DEVICE" ]; then
    echo "Error: Loop device for encrypted.img not found."
    exit 1
fi
sudo cryptsetup luksFormat --cipher aes-cbc-essiv:sha256 $LOOP_DEVICE
sudo cryptsetup luksOpen $LOOP_DEVICE encrypted_device
sudo mkfs.ext3 /dev/mapper/encrypted_device
sudo mount /dev/mapper/encrypted_device /mnt/encrypted
echo "This is a test file" > /mnt/encrypted/testfile.txt
sudo umount /mnt/encrypted
sudo cryptsetup luksClose encrypted_device
sudo losetup -d $LOOP_DEVICE


LOOP_DEVICE=$(sudo losetup -a | grep encrypted.img | cut -d: -f1)
if [ -z "$LOOP_DEVICE" ]; then
    echo "Error: Loop device for encrypted.img not found."
    exit 1
fi
sudo cryptsetup open --type plain $LOOP_DEVICE my_encrypted_device
sudo mkfs.ext3 /dev/mapper/my_encrypted_device
sudo mount /dev/mapper/my_encrypted_device /mnt
sudo umount /mnt
sudo cryptsetup close my_encrypted_device
sudo losetup -d $LOOP_DEVICE


sudo losetup -fP encrypted.img
if [ -z "$LOOP_DEVICE" ]; then
    echo "Error: Loop device for encrypted.img not found."
    exit 1
fi
sudo cryptsetup open --type plain $LOOP_DEVICE my_encrypted_device

dd if=/dev/zero of=encrypted.img bs=1M count=10
sudo losetup -fP encrypted.img
if [ -z "$LOOP_DEVICE" ]; then
    echo "Error: Loop device for encrypted.img not found."
    exit 1
fi

dd if=/dev/urandom of=keyfile bs=64 count=1
chmod 600 keyfile
echo -n "KkzPRSNodEhlTr9F7JB6Rrh3yGyfgl22r5aMmKBcBOJ5Kd3xslfshwYft+V1u5Ki" > keyfile

---

sudo losetup -fP encrypted.img
LOOP_DEVICE=$(sudo losetup -a | grep encrypted.img | cut -d: -f1)
echo $LOOP_DEVICE
sudo cryptsetup open --type plain --key-file keyfile $LOOP_DEVICE en_device
sudo cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 --key-file keyfile $LOOP_DEVICE en_device

sudo mkfs.ext4 /dev/mapper/en_device
sudo mount /dev/mapper/en_device /mnt/encrypted


sudo umount /mnt/encrypted
sudo cryptsetup close en_device
sudo losetup -d $LOOP_DEVICE

