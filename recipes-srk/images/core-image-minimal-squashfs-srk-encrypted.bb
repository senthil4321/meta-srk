# core-image-minimal-squashfs-srk-encrypted.bb
# Encrypted SquashFS image with post-processing
# Creates an encrypted container containing the SquashFS image

SUMMARY = "Encrypted SquashFS image with post-processing"
DESCRIPTION = "Creates an encrypted container containing the SquashFS image"

# Inherit from your main image
inherit core-image-minimal-squashfs-srk

# NOTE: cryptsetup tools are NOT needed here since initramfs is built separately
# and will include the necessary decryption tools

# Post-processing task
do_encrypt_image() {
    bbnote "Creating encrypted container for SquashFS image..."

    # Generate keyfile if it doesn't exist
    if [ ! -f "${TOPDIR}/keyfile" ]; then
        bbnote "Generating new encryption keyfile..."
        dd if=/dev/urandom of="${TOPDIR}/keyfile" bs=64 count=1
        chmod 600 "${TOPDIR}/keyfile"
    fi

    # Create encrypted container
    ENCRYPTED_IMG="${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}-encrypted.img"
    bbnote "Creating encrypted container: ${ENCRYPTED_IMG}"

    dd if=/dev/zero of="${ENCRYPTED_IMG}" bs=1M count=50

    # Setup loop device and encryption
    LOOP_DEV=$(sudo losetup -f "${ENCRYPTED_IMG}")
    bbnote "Using loop device: ${LOOP_DEV}"

    sudo cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 \
        --key-file "${TOPDIR}/keyfile" "$LOOP_DEV" encrypted_container

    # Format and mount
    sudo mkfs.ext4 /dev/mapper/encrypted_container
    sudo mkdir -p /mnt/encrypted
    sudo mount /dev/mapper/encrypted_container /mnt/encrypted

    # Copy SquashFS image
    SOURCE_IMG="${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}-${MACHINE}.squashfs"
    DEST_IMG="/mnt/encrypted/${IMAGE_NAME}-${MACHINE}.squashfs"

    bbnote "Copying SquashFS image..."
    bbnote "From: ${SOURCE_IMG}"
    bbnote "To: ${DEST_IMG}"

    sudo cp "${SOURCE_IMG}" "${DEST_IMG}"

    # Verify copy
    if sudo cmp "${SOURCE_IMG}" "${DEST_IMG}"; then
        bbnote "File copy verification successful"
    else
        bbfatal "File copy verification failed"
    fi

    # Cleanup
    bbnote "Cleaning up..."
    sudo umount /mnt/encrypted
    sudo cryptsetup close encrypted_container
    sudo losetup -d "$LOOP_DEV"

    bbnote "Encrypted image created successfully: ${ENCRYPTED_IMG}"
    bbnote "Keyfile location: ${TOPDIR}/keyfile"
}

# Add to build tasks
addtask encrypt_image after do_image_complete before do_build

# Make encryption optional
ENCRYPT_IMAGE ?= "0"
do_encrypt_image[noexec] = "${@'1' if d.getVar('ENCRYPT_IMAGE') == '0' else '0'}"

# Dependencies
do_encrypt_image[depends] += "cryptsetup-native:do_populate_sysroot"