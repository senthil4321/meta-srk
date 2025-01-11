#!/bin/bash

show_menu() {
    echo "Select an option:"
    echo "0. Build kernel"
    echo "1. bitbake linux-yocto -c kernel_configme -f"
    echo "2. bitbake linux-yocto -c menuconfig"
    echo "3. bitbake linux-yocto -c diffconfig"
    echo "4. bitbake linux-yocto -c kernel_configcheck -f"
    echo "5. Save defconfig"
    echo "6. Print .config file path"
    echo "7. Print defconfig file path meta-srk"
    echo "8. Print defconfig file path"
    echo "9. Print fragment.cfg file path"
    echo "10. Print fragment.cfg file contents"
    echo "11. Print fragment workflow"
    echo "12. Exit"
}

execute_option() {
    case $1 in
        0)
            bitbake virtual/kernel
            ;;
        1)
            bitbake linux-yocto -c kernel_configme -f
            ;;
        2)
            bitbake linux-yocto -c menuconfig
            ;;
        3)
            bitbake linux-yocto -c diffconfig
            ;;
        4)
            bitbake linux-yocto -c kernel_configcheck -f
            ;;
        5)
            bitbake linux-yocto -c savedefconfig
            ;;
        6)
            echo "~/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto/6.6.21+git/linux-beaglebone_yocto-standard-build/.config"
            ;;
        7)
            echo "/home/srk2cob/project/poky/meta-srk/recipes-kernel/linux/linux-yocto/defconfig"
            ;;
        8)
            echo "/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto/6.6.21+git/linux-beaglebone_yocto-standard-build/defconfig"
            ;;
        9)
            echo "/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto/6.6.21+git/fragment.cfg"
            ;;
        10)
            cat "/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto/6.6.21+git/fragment.cfg"
            ;;
        11)
            echo "Run 2. menuconfig.  3. diffconfig and view the fragment.cfg file using 10. Print fragment.cfg file contents"
            ;;
        12)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
}

while true; do
    show_menu
    read -p "Enter your choice: " choice
    execute_option $choice
done