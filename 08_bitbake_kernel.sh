#!/bin/bash

show_menu() {
    echo "Select an option:"
    echo "1. bitbake linux-yocto -c kernel_configme -f"
    echo "2. bitbake linux-yocto -c menuconfig"
    echo "3. bitbake linux-yocto -c diffconfig"
    echo "4. bitbake linux-yocto -c kernel_configcheck -f"
    echo "5. Open .config file"
    echo "6. Open defconfig file"
    echo "7. Exit"
}

execute_option() {
    case $1 in
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
            echo ~/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto/6.6.21+git/linux-beaglebone_yocto-standard-build/.config
            ;;
        6)
            echo /home/srk2cob/project/poky/meta-srk/recipes-kernel/linux/linux-yocto/defconfig
            ;;
        7)
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
