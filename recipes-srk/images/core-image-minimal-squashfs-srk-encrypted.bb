# core-image-minimal-squashfs-srk-encrypted.bb
# Encrypted SquashFS image with post-processing
# Creates an encrypted container containing the SquashFS image

SUMMARY = "Encrypted SquashFS image with post-processing"
DESCRIPTION = "Creates an encrypted container containing the SquashFS image"

LICENSE = "MIT"

# No inheritance needed for post-processing recipe
# This recipe depends on core-image-minimal-squashfs-srk being built first

# NOTE: cryptsetup tools are NOT needed here since initramfs is built separately
# and will include the necessary decryption tools

# Use standard deploy task for post-processing
do_deploy() {
    bbnote "Creating encrypted container for SquashFS image..."

    # Generate keyfile if it doesn't exist
    if [ ! -f "${TOPDIR}/keyfile" ]; then
        bbnote "Generating new encryption keyfile..."
        dd if=/dev/urandom of="${TOPDIR}/keyfile" bs=64 count=1
        chmod 600 "${TOPDIR}/keyfile"
    fi

    # Create encrypted container
    ENCRYPTED_IMG="${DEPLOYDIR}/core-image-minimal-squashfs-srk-${MACHINE}-encrypted.img"
    bbnote "Creating encrypted container: ${ENCRYPTED_IMG}"

    # Create container file
    dd if=/dev/zero of="${ENCRYPTED_IMG}" bs=1M count=50

    # Setup loop device and encryption
    LOOP_DEV=$(losetup -f)
    losetup "${LOOP_DEV}" "${ENCRYPTED_IMG}"
    bbnote "Using loop device: ${LOOP_DEV}"

    # Create encrypted mapping
    cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 \
        --key-file "${TOPDIR}/keyfile" "${LOOP_DEV}" encrypted_container

    # Format and mount
    mkfs.ext4 /dev/mapper/encrypted_container
    mkdir -p /mnt/encrypted
    mount /dev/mapper/encrypted_container /mnt/encrypted

    # Copy SquashFS image
    SOURCE_IMG="${DEPLOY_DIR_IMAGE}/core-image-minimal-squashfs-srk-${MACHINE}.squashfs"
    DEST_IMG="/mnt/encrypted/core-image-minimal-squashfs-srk-${MACHINE}.squashfs"

    bbnote "Copying SquashFS image..."
    bbnote "From: ${SOURCE_IMG}"
    bbnote "To: ${DEST_IMG}"

    cp "${SOURCE_IMG}" "${DEST_IMG}"

    # Verify copy
    if cmp "${SOURCE_IMG}" "${DEST_IMG}"; then
        bbnote "File copy verification successful"
    else
        bbfatal "File copy verification failed"
    fi

    # Cleanup
    bbnote "Cleaning up..."
    umount /mnt/encrypted
    cryptsetup close encrypted_container
    losetup -d "${LOOP_DEV}"

    bbnote "Encrypted image created successfully: ${ENCRYPTED_IMG}"
    bbnote "Keyfile location: ${TOPDIR}/keyfile"
}

# Make encryption optional
ENCRYPT_IMAGE ?= "1"
do_deploy[noexec] = "${@'1' if d.getVar('ENCRYPT_IMAGE') == '0' else '0'}"

# Task flags
do_deploy[network] = "0"
do_deploy[umask] = "022"

# Dependencies
do_deploy[depends] += "cryptsetup-native:do_populate_sysroot"
do_deploy[depends] += "e2fsprogs-native:do_populate_sysroot"
do_deploy[depends] += "core-image-minimal-squashfs-srk:do_image_complete"