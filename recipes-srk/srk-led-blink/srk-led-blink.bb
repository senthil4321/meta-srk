SUMMARY = "BBB LED blinker using direct syscalls"
DESCRIPTION = "Minimal program that blinks BBB LEDs without libc"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://srk-led-blink.c;subdir=${BP}"

do_compile() {
    ${CC} -nostdlib -static -fno-stack-protector srk-led-blink.c -o srk-led-blink
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 srk-led-blink ${D}${bindir}
}

FILES:${PN} = "${bindir}/srk-led-blink"