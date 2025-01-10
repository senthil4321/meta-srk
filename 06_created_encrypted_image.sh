#!/bin/sh

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
        dd if=/dev/zero of=encrypted.img bs=1M count=10
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

cleanup_encrypted_image() {
    echo "6. Cleaning up encrypted image..."
    sudo umount /mnt/encrypted
    sudo cryptsetup close en_device
    sudo losetup -d $LOOP_DEVICE
}

# generate_keyfile
mount_encrypted_image true
write_sample_data
read_encrypted_data
cleanup_encrypted_image

