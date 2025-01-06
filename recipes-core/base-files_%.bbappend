do_install_append() {
    mkdir -p ${D}/proc
    mkdir -p ${D}/sys
    mkdir -p ${D}/dev
}
