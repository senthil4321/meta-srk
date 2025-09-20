# SquashFS Filename Inconsistency Issue

## Problem
There is an inconsistency in SquashFS filenames across different scripts in the meta-srk layer:

**Current state:**
- Build produces: `core-image-minimal-squashfs-srk-beaglebone-yocto.rootfs.squashfs`
- Init script expects: `core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs`

## Affected Files
1. `06_created_encrypted_image.sh` - ✅ Fixed (uses correct filename)
2. `05_copy_squashfs.sh` - ✅ Fixed (uses correct filename)  
3. `07_target_changeRoot.sh` - ✅ Fixed (uses correct filename)
4. `recipes-srk/srk-init/files/srk-init.sh` - ❌ Still uses old filename

## Impact
- Init script on target device will fail to mount SquashFS during boot
- Target system won't be able to switch to the correct root filesystem
- Deployment appears successful but runtime fails

## Root Cause
The image name `core-image-minimal-squashfs-srk` contains 'squashfs' in the name, but the init script was written expecting just `core-image-minimal-srk`.

## Solution
Update `srk-init.sh` to use the correct filename:
```bash
# Change from:
mount -t squashfs -o loop /mnt/encrypted/core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs /srk-mnt

# Change to:
mount -t squashfs -o loop /mnt/encrypted/core-image-minimal-squashfs-srk-beaglebone-yocto.rootfs.squashfs /srk-mnt
```

## Priority
High - Affects target device boot process

## Labels
bug, deployment, critical, target-system
