DESCRIPTION = "Copy rootfs to NFS share"
LICENSE = "MIT"
PR = "r0"

# Define the task to copy the rootfs to the NFS share
do_copy_rootfs_to_nfs() {
    # # Ensure the NFS share is mounted
    # if ! mountpoint -q /mnt/nfs; then
    #     sudo mount -t nfs ${NFS_SERVER}:${NFS_SHARE} /mnt/nfs
    # fi

    # # Copy the rootfs to the NFS share
    # if mountpoint -q /mnt/nfs; then
    #     cp -r ${IMAGE_ROOTFS} /mnt/nfs/${IMAGE_BASENAME}
    #     echo "Rootfs copied to NFS share: /mnt/nfs/${IMAGE_BASENAME}"
    # else
    #     echo "Failed to mount NFS share. Rootfs not copied."
    # fi
    printf "do_copy_rootfs_to_nfs() executed\n"
}

# Add the task to the do_rootfs task
ROOTFS_POSTPROCESS_COMMAND += "do_copy_rootfs_to_nfs; "

# Ensure the task runs after the rootfs is created
addtask copy_rootfs_to_nfs after do_rootfs before do_image_complete