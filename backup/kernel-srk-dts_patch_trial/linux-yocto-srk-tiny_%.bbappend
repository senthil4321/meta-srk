do_patch:append() {
    sed -i 's/#include "am335x-boneblack-hdmi.dtsi"/\/\/#include "am335x-boneblack-hdmi.dtsi"/' ${S}/arch/arm/boot/dts/ti/omap/am335x-boneblack.dts
}
