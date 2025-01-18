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

generate_keyfile() {
    echo "2. Generating keyfile..."
    dd if=/dev/urandom of=keyfile bs=64 count=1
    chmod 600 keyfile
    echo -n "KkzPRSNodEhlTr9F7JB6Rrh3yGyfgl22r5aMmKBcBOJ5Kd3xslfshwYft+V1u5Ki" > keyfile
}

create_and_mount_encrypted_image() {
    echo "3. Creating and mounting encrypted image..."
    local run_mkfs=$1
    if [ "$run_mkfs" = true ]; then
        dd if=/dev/zero of=encrypted1.img bs=1M count=40
    fi    
    sudo losetup -fP encrypted1.img
    LOOP_DEVICE=$(sudo losetup -a | grep encrypted1.img | cut -d: -f1)
    if [ -z "$LOOP_DEVICE" ]; then
        echo "Error: Loop device for encrypted1.img not found."
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

mount_encrypted_image() {
    echo "4. Mounting encrypted image..."
    losetup -fP encrypted.img
    LOOP_DEVICE=$(sudo losetup -a | grep encrypted1.img | cut -d: -f1)
    if [ -z "$LOOP_DEVICE" ]; then
        echo "Error: Loop device for encrypted1.img not found."
        exit 1
    fi
    echo $LOOP_DEVICE
    cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 --key-file keyfile $LOOP_DEVICE en_device

    if [ ! -d /mnt/encrypted ]; then
        mkdir -p /mnt/encrypted
    fi
    mount /dev/mapper/en_device /mnt/encrypted
}

mount_encrypted_imageTarget() {
    echo "5. Mounting encrypted image on the target..."
    mount -t proc proc /proc    
    losetup -fP encrypted.img
    LOOP_DEVICE=$(losetup -a | grep encrypted.img | cut -d: -f1)
    echo $LOOP_DEVICE
    cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 --key-file keyfile $LOOP_DEVICE en_device
    if [ ! -d /mnt/encrypted ]; then
        sudo mkdir -p /mnt/encrypted
    fi
    mount /dev/mapper/en_device /mnt/encrypted

    mount -t squashfs -o loop /mnt/encrypted/core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs /srk-mnt
    umount  /srk-mnt

    umount /mnt/encrypted
    cryptsetup close en_device
    losetup -d $LOOP_DEVICE
}

write_sample_data() {
    echo "6. Writing sample data..."
    echo "Hello $(date)" | sudo tee -a /mnt/encrypted/hello.txt
}

read_encrypted_data() {
    echo "7. Reading encrypted data..."
    sudo cat /mnt/encrypted/hello.txt
}

copy_file_to_mounted_drive() {
    echo "8. Copying file to mounted drive..."
    local FILE_NAME="core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs"
    local src_path="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$FILE_NAME"
    local dest_path="/mnt/encrypted/$FILE_NAME"
    sudo cp $src_path $dest_path
}

verify_file_hash() {
    echo "9. Verifying file hash..."
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
    echo "10. Cleaning up encrypted image..."
    LOOP_DEVICE=$(losetup -a | grep encrypted.img | cut -d: -f1)
    echo $LOOP_DEVICE
    sudo umount /mnt/encrypted
    sudo cryptsetup close en_device
    sudo losetup -d $LOOP_DEVICE
}

show_menu() {
    echo "Select an option:"
    echo "1. Create LUKS encrypted image"
    echo "2. Generate keyfile"
    echo "3. Create and mount encrypted image"
    echo "4. Mount encrypted image"
    echo "5. Mount encrypted image on the target"
    echo "6. Write sample data"
    echo "7. Read encrypted data"
    echo "8. Copy file to mounted drive"
    echo "9. Verify file hash"
    echo "10. Cleanup encrypted image"
    echo "11. Exit"
}

execute_option() {
    case $1 in
        1)
            create_luks_encrypted_image
            ;;
        2)
            generate_keyfile
            ;;
        3)
            create_and_mount_encrypted_image true
            ;;
        4)
            mount_encrypted_image
            ;;
        5)
            mount_encrypted_imageTarget
            ;;
        6)
            write_sample_data
            ;;
        7)
            read_encrypted_data
            ;;
        8)
            copy_file_to_mounted_drive
            ;;
        9)
            verify_file_hash
            ;;
        10)
            cleanup_encrypted_image
            ;;
        11)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
}

if [ -z "$1" ]; then
    while true; do
        show_menu
        read -p "Enter your choice: " choice
        execute_option $choice
    done
else
    execute_option $1
fi

