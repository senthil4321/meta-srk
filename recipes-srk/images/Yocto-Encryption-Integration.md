# Yocto Integration for Encrypted SquashFS Image Processing

## Overview

This document outlines how to integrate the encrypted image processing steps into the Yocto build system as post-processing tasks.

## Current Manual Process Analysis

### Step 4: Mount Encrypted Image

- **Function**: `mount_encrypted_image()`
- **Purpose**: Mounts existing encrypted container using cryptsetup
- **Dependencies**: `encrypted.img`, `keyfile`
- **Output**: Mounted encrypted filesystem at `/mnt/encrypted`

### Step 8: Copy SquashFS to Encrypted Drive

- **Function**: `copy_file_to_mounted_drive()`
- **Purpose**: Copies the built squashfs image to encrypted container
- **Dependencies**: Mounted encrypted drive, built squashfs image
- **Output**: SquashFS image stored in encrypted container

### Step 10: Cleanup Encrypted Image

- **Function**: `cleanup_encrypted_image()`
- **Purpose**: Properly unmounts and cleans up encrypted container
- **Dependencies**: Mounted encrypted drive
- **Output**: Clean system state

## Yocto Integration Options

### Option 1: Post-Processing Recipe (Recommended)

Create a new recipe that depends on your image and handles the encryption:

```bitbake
# recipes-srk/images/core-image-minimal-squashfs-srk-encrypted.bb

SUMMARY = "Encrypted SquashFS image with post-processing"
DESCRIPTION = "Creates an encrypted container containing the SquashFS image"

# Inherit from your main image
inherit core-image-minimal-squashfs-srk

# CRITICAL: Add encryption tools to the image since initramfs needs them
# to mount the encrypted container during boot
#IMAGE_INSTALL:append = " cryptsetup cryptsetup-plain"

# Post-processing task
do_encrypt_image() {
    bbnote "Creating encrypted container for SquashFS image..."

    # Generate keyfile if it doesn't exist
    if [ ! -f "${TOPDIR}/keyfile" ]; then
        dd if=/dev/urandom of="${TOPDIR}/keyfile" bs=64 count=1
        chmod 600 "${TOPDIR}/keyfile"
    fi

    # Create encrypted container
    dd if=/dev/zero of="${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}-encrypted.img" bs=1M count=50

    # Setup loop device and encryption
    LOOP_DEV=$(sudo losetup -f "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}-encrypted.img")
    sudo cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 \
        --key-file "${TOPDIR}/keyfile" "$LOOP_DEV" encrypted_container

    # Format and mount
    sudo mkfs.ext4 /dev/mapper/encrypted_container
    sudo mkdir -p /mnt/encrypted
    sudo mount /dev/mapper/encrypted_container /mnt/encrypted

    # Copy SquashFS image
    sudo cp "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}-${MACHINE}.squashfs" \
        "/mnt/encrypted/${IMAGE_NAME}-${MACHINE}.squashfs"

    # Cleanup
    sudo umount /mnt/encrypted
    sudo cryptsetup close encrypted_container
    sudo losetup -d "$LOOP_DEV"

    bbnote "Encrypted image created: ${IMAGE_NAME}-encrypted.img"
}

# Add to build tasks
addtask encrypt_image after do_image_complete before do_build

# Make encryption optional
ENCRYPT_IMAGE ?= "0"
do_encrypt_image[noexec] = "${@'1' if d.getVar('ENCRYPT_IMAGE') == '0' else '0'}"
```

**Important Note:** The `IMAGE_INSTALL:append = " cryptsetup cryptsetup-plain"` line is **NOT needed** because:

- Initramfs is created in a separate build process
- The separate initramfs build will include cryptsetup tools for decryption
- The main image doesn't need encryption tools since initramfs handles decryption
- This keeps the main image minimal and focused on its core functionality

### Option 2: Custom Class

Create a reusable class for encrypted image processing:

```bitbake
# classes/encrypted-image.bbclass

# Variables for encryption
ENCRYPTED_IMAGE_SIZE ?= "50"
ENCRYPTION_CIPHER ?= "aes-xts-plain64"
ENCRYPTION_KEY_SIZE ?= "256"

# Function to create encrypted container
create_encrypted_container() {
    local image_name="$1"
    local keyfile="$2"
    local output_dir="$3"

    bbnote "Creating encrypted container for ${image_name}..."

    # Create container file
    dd if=/dev/zero of="${output_dir}/${image_name}-encrypted.img" \
        bs=1M count="${ENCRYPTED_IMAGE_SIZE}"

    # Setup encryption
    LOOP_DEV=$(losetup -f "${output_dir}/${image_name}-encrypted.img")
    cryptsetup open --type plain --cipher "${ENCRYPTION_CIPHER}" \
        --key-size "${ENCRYPTION_KEY_SIZE}" --key-file "$keyfile" \
        "$LOOP_DEV" encrypted_container

    # Format and mount
    mkfs.ext4 /dev/mapper/encrypted_container
    mkdir -p /mnt/encrypted
    mount /dev/mapper/encrypted_container /mnt/encrypted
}

# Function to copy image to encrypted container
copy_to_encrypted() {
    local src_image="$1"
    local dest_name="$2"

    cp "$src_image" "/mnt/encrypted/$dest_name"
}

# Function to cleanup encrypted container
cleanup_encrypted() {
    umount /mnt/encrypted
    cryptsetup close encrypted_container
    losetup -d "$LOOP_DEV"
}

# Task to create encrypted image
do_create_encrypted_image() {
    local keyfile="${TOPDIR}/keyfile"
    local image_name="${IMAGE_NAME}"
    local output_dir="${DEPLOY_DIR_IMAGE}"

    # Generate keyfile if needed
    if [ ! -f "$keyfile" ]; then
        dd if=/dev/urandom of="$keyfile" bs=64 count=1
        chmod 600 "$keyfile"
    fi

    # Create and populate encrypted container
    create_encrypted_container "$image_name" "$keyfile" "$output_dir"
    copy_to_encrypted "${output_dir}/${image_name}-${MACHINE}.squashfs" \
        "${image_name}-${MACHINE}.squashfs"
    cleanup_encrypted

    bbnote "Encrypted image created successfully"
}

# Add task to build process
EXPORT_FUNCTIONS do_create_encrypted_image
```

### Option 3: WIC Plugin (Advanced)

Create a WIC plugin for encrypted image creation:

```python
# wic/plugins/source/encrypted.py

import os
import subprocess
from wic.pluginbase import SourcePlugin
from wic.utils.oe.misc import exec_cmd

class EncryptedPlugin(SourcePlugin):
    name = 'encrypted'

    @classmethod
    def do_install_disk(cls, disk, disk_name, cr, workdir, oe_builddir,
                       bootimg_dir, kernel_dir, native_sysroot):
        """
        Called after all partitions have been prepared and assembled
        """

        # Create encrypted container
        image_path = os.path.join(cr.workdir, f"{disk_name}-encrypted.img")
        keyfile = os.path.join(oe_builddir, "keyfile")

        # Generate keyfile if needed
        if not os.path.exists(keyfile):
            exec_cmd(f"dd if=/dev/urandom of={keyfile} bs=64 count=1")
            os.chmod(keyfile, 0o600)

        # Create encrypted image using cryptsetup
        exec_cmd(f"dd if=/dev/zero of={image_path} bs=1M count=50")
        exec_cmd(f"losetup -f {image_path}", as_root=True)
        loop_dev = exec_cmd("losetup -a | grep encrypted.img | cut -d: -f1",
                          as_root=True).strip()

        exec_cmd(f"cryptsetup open --type plain --cipher aes-xts-plain64 "
                f"--key-size 256 --key-file {keyfile} {loop_dev} encrypted_container",
                as_root=True)

        # Format and copy SquashFS
        exec_cmd("mkfs.ext4 /dev/mapper/encrypted_container", as_root=True)
        exec_cmd("mkdir -p /mnt/encrypted", as_root=True)
        exec_cmd("mount /dev/mapper/encrypted_container /mnt/encrypted", as_root=True)

        # Copy the SquashFS image
        squashfs_path = os.path.join(cr.workdir, f"{disk_name}.squashfs")
        exec_cmd(f"cp {squashfs_path} /mnt/encrypted/", as_root=True)

        # Cleanup
        exec_cmd("umount /mnt/encrypted", as_root=True)
        exec_cmd("cryptsetup close encrypted_container", as_root=True)
        exec_cmd(f"losetup -d {loop_dev}", as_root=True)

        return 0

    @classmethod
    def do_configure_partition(cls, part, source_params, cr, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             native_sysroot):
        """
        Called before do_prepare_partition
        """
        # Configuration specific to encrypted partitions
        pass
```

## Implementation Recommendation

### Recommended Approach: Option 1 (Post-Processing Recipe)

**Pros:**

- ✅ Simple to implement
- ✅ Clear dependency chain
- ✅ Easy to enable/disable
- ✅ Reusable across images
- ✅ Standard Yocto patterns

**Usage:**

```bash
# Enable encryption in local.conf
ENCRYPT_IMAGE = "1"

# Build with encryption
bitbake core-image-minimal-squashfs-srk-encrypted
```

**Integration Steps:**

1. **Create the recipe** as shown in Option 1
2. **Add to your layer** in `recipes-srk/images/`
3. **Set dependencies** on your main image
4. **Configure via variables** for flexibility
5. **Test the build process**

### Alternative: Custom Tasks in Main Recipe

Add encryption tasks directly to your existing image recipe:

```bitbake
# In core-image-minimal-squashfs-srk.bb

# CRITICAL: Add encryption tools since initramfs needs them to mount encrypted container
IMAGE_INSTALL:append = " cryptsetup cryptsetup-plain"

# Encryption configuration
ENCRYPT_IMAGE ?= "0"
ENCRYPTED_CONTAINER_SIZE ?= "50"

do_encrypt_postprocess() {
    if [ "${ENCRYPT_IMAGE}" = "1" ]; then
        bbnote "Creating encrypted container..."

        # Your encryption logic here
        # (adapted from the shell script functions)
    fi
}

addtask encrypt_postprocess after do_image_complete before do_build
```

**Note:** The `IMAGE_INSTALL:append = " cryptsetup cryptsetup-plain"` is essential because the encrypted SquashFS image requires these tools to be present for initramfs to decrypt and mount the container during system boot.

## Benefits of Yocto Integration

1. **Automated**: No manual steps required
2. **Reproducible**: Same process every build
3. **Version Controlled**: Changes tracked in git
4. **Configurable**: Easy to enable/disable via variables
5. **Integrated**: Part of the standard build process
6. **Testable**: Can be tested as part of CI/CD

## Critical Requirements for Initramfs Mounting

### Why cryptsetup is NOT Required in Main Image

When using encrypted SquashFS images with separate initramfs builds:

1. **Separate Build Process**: Initramfs is built independently with its own configuration
2. **Initramfs Responsibility**: The initramfs build includes cryptsetup tools for decryption
3. **Clean Separation**: Main image remains minimal, initramfs handles specialized decryption tasks
4. **Build Efficiency**: Avoids including unnecessary tools in the main filesystem

### Initramfs Build Requirements

The initramfs build (separate recipe) should include:

```bitbake
# In initramfs recipe (separate build)
IMAGE_INSTALL:append = " cryptsetup cryptsetup-plain"
```

This approach provides:

- ✅ **Clean Architecture**: Separation of concerns between main image and initramfs
- ✅ **Minimal Main Image**: Main image stays focused on core functionality
- ✅ **Flexible Initramfs**: Initramfs can be customized independently
- ✅ **Build Optimization**: Only include decryption tools where needed

## Next Steps

1. Choose the integration approach that best fits your workflow
2. Implement the selected option
3. Test with your build environment
4. Document the new process
5. Consider adding verification steps

Would you like me to implement any of these approaches or help you choose between them?
