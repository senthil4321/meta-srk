DESCRIPTION = "Copy rootfs to NFS share"
LICENSE = "MIT"
PR = "r0"


# Define the task to copy the initramfs using the script
do_copy_initramfs() {
    /home/srk2cob/project/poky/meta-srk/03_copy_initramfs.sh
}

# Add the tasks to the do_rootfs task
ROOTFS_POSTPROCESS_COMMAND += "do_copy_initramfs; "

addtask copy_initramfs after do_copy_rootfs_to_nfs before do_image_complete