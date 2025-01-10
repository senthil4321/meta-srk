mount -t proc proc /proc    
echo "1. Mounting encrypted image on the target..."
losetup -fP encrypted.img
LOOP_DEVICE=$(losetup -a | grep encrypted.img | cut -d: -f1)
echo $LOOP_DEVICE
cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 --key-file keyfile $LOOP_DEVICE en_device
if [ ! -d /mnt/encrypted ]; then
    mkdir -p /mnt/encrypted
fi
mount /dev/mapper/en_device /mnt/encrypted


cat /mnt/encrypted/hello.txt

mount -t squashfs -o loop /mnt/encrypted/core-image-minimal-srk-beaglebone-yocto.rootfs.squashfs /srk-mnt


new_root="/srk-mnt"
old_root="/boot"
mount --move /proc "$new_root/proc"
mount --move /sys "$new_root/sys"
mount --move /dev "$new_root/dev"


echo "Move: /proc, /dev -> $new_root Success"

mount --move /mnt/encrypted "$new_root/mnt/"

echo "Move: /proc, /dev, /mnt/encrypted -> $new_root Success"

pivot_root "$new_root" "$new_root/$old_root"
echo "pivot_root: $new_root -> $new_root/$old_root Success "
echo "Change the current directory to the new root"
cd /
echo "Message from new root"
umount -l "/$old_root"
echo "umount: /$old_root Sucess"

exec chroot . /bin/sh -c 'exec /sbin/init'