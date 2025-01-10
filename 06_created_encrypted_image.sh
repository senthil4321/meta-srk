#!/bin/sh

FILE_NAME="core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"

create_luks_encrypted_image() {
    echo "1. Creating LUKS encrypted image..."
    dd if=/dev/zero of=encrypted.img bs=1M count=10
    sudo losetup -f encrypted.img
    LOOP_DEVICE=$(sudo losetup -a | grep encrypted.img | cut -d: -f1)
    if [ -z "$LOOP_DEVICE" ]; then
        echo "Error: Loop device for encrypted.img not found."
        exit 1
    fi
    sudo cryptsetup luksFormat --cipher aes-cbc-essiv:sha256 $LOOP_DEVICE
    sudo cryptsetup luksOpen $LOOP_DEVICE encrypted_device
    sudo mkfs.ext3 /dev/mapper/encrypted_device
    sudo mount /dev/mapper/encrypted_device /mnt/encrypted
    echo "This is a test file" | sudo tee /mnt/encrypted/testfile.txt
    sudo umount /mnt/encrypted
    sudo cryptsetup luksClose encrypted_device
    sudo losetup -d $LOOP_DEVICE
}

# create_luks_encrypted_image

generate_keyfile() {
    echo "2. Generating keyfile..."
    dd if=/dev/urandom of=keyfile bs=64 count=1
    chmod 600 keyfile
    echo -n "KkzPRSNodEhlTr9F7JB6Rrh3yGyfgl22r5aMmKBcBOJ5Kd3xslfshwYft+V1u5Ki" > keyfile
}

mount_encrypted_image() {
    echo "3. Mounting encrypted image..."
    local run_mkfs=$1
    if [ "$run_mkfs" = true ]; then
        dd if=/dev/zero of=encrypted.img bs=1M count=40
    fi    
    sudo losetup -fP encrypted.img
    LOOP_DEVICE=$(sudo losetup -a | grep encrypted.img | cut -d: -f1)
    if [ -z "$LOOP_DEVICE" ]; then
        echo "Error: Loop device for encrypted.img not found."
        exit 1
    fi
    echo $LOOP_DEVICE
    sudo cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 --key-file keyfile $LOOP_DEVICE en_device

    if [ "$run_mkfs" = true ]; then
        sudo mkfs.ext4 /dev/mapper/en_device
    fi

    if [ ! -d /mnt/encrypted ]; then
        sudo mkdir -p /mnt/encrypted
    fi

    sudo mount /dev/mapper/en_device /mnt/encrypted
}

write_sample_data() {
    echo "4. Writing sample data..."
    echo "Hello $(date)" | sudo tee -a /mnt/encrypted/hello.txt
}

read_encrypted_data() {
    echo "5. Reading encrypted data..."
    sudo cat /mnt/encrypted/hello.txt
}

# core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs
# home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto
copy_file_to_mounted_drive() {
    echo "6. Copying file to mounted drive..."
    local FILE_NAME="core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
    local src_path="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$FILE_NAME"
    local dest_path="/mnt/encrypted/$FILE_NAME"
    sudo cp $src_path $dest_path
}

verify_file_hash() {
    echo "7. Verifying file hash..."
    local FILE_NAME="core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
    local src_path="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$FILE_NAME"
    local dest_path="/mnt/encrypted/$FILE_NAME"
    local src_hash=$(sha256sum $src_path | cut -d ' ' -f 1)
    local dest_hash=$(sudo sha256sum $dest_path | cut -d ' ' -f 1)
    if [ "$src_hash" = "$dest_hash" ]; then
        echo "File hash verification successful."
    else
        echo "File hash verification failed."
        exit 1
    fi
}

cleanup_encrypted_image() {
    echo "8. Cleaning up encrypted image..."
    sudo umount /mnt/encrypted
    sudo cryptsetup close en_device
    sudo losetup -d $LOOP_DEVICE
}

# generate_keyfile
mount_encrypted_image true
write_sample_data
read_encrypted_data
copy_file_to_mounted_drive
verify_file_hash
cleanup_encrypted_image

