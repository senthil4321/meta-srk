SUMMARY = "Decrypt and mount an encrypted image"
DESCRIPTION = "This recipe decrypts an encrypted image and mounts it to a specified directory."
LICENSE = "MIT"

# Ensure necessary tools are included
DEPENDS = "cryptsetup util-linux"

do_install() {
    # Create necessary directories
    install -d ${D}/mnt/encrypted

    # Decrypt the image
    cryptsetup luksOpen /path/to/encrypted.img decrypted_image

    # Mount the decrypted image
    mount /dev/mapper/decrypted_image ${D}/mnt/encrypted
}

# Specify the files and directories to be included in the package
FILES_${PN} += "/mnt/encrypted"