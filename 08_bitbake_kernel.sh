#!/bin/bash

VERSION="1.0.0"

show_menu() {
    echo "Select an option:"
    echo "0. bitbake virtual/kernel "
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
    echo "12. Show help"
    echo "13. Exit"
    echo "14. bitbake -c clean virtual/kernel"
    echo "15. bitbake -c devshell linux-yocto"
    echo "16. Print version"
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
            show_help
            ;;
        13)
            echo "Exiting..."
            exit 0
            ;;
        14)
            bitbake -c clean virtual/kernel
            ;;
        15)
            bitbake -c devshell linux-yocto
            ;;
        16)
            echo "Version: $VERSION"
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
}

show_help() {
    echo "Help:"
    echo "0. Build kernel: Builds the kernel using bitbake."
    echo "1. kernel_configme: Configures the kernel."
    echo "2. menuconfig: Opens the kernel menu configuration."
    echo "3. diffconfig: Shows the differences in the kernel configuration."
    echo "4. kernel_configcheck: Checks the kernel configuration."
    echo "5. Save defconfig: Saves the current kernel configuration."
    echo "6. Print .config file path: Prints the path to the .config file."
    echo "7. Print defconfig file path meta-srk: Prints the path to the defconfig file in meta-srk."
    echo "8. Print defconfig file path: Prints the path to the defconfig file."
    echo "9. Print fragment.cfg file path: Prints the path to the fragment.cfg file."
    echo "10. Print fragment.cfg file contents: Prints the contents of the fragment.cfg file."
    echo "11. Print fragment workflow: Prints the workflow for using fragment.cfg."
    echo "12. Show help: Displays this help message."
    echo "13. Exit: Exits the script."
    echo "14. Clean kernel: Cleans the kernel build using bitbake."
    echo "15. Open devshell: Opens the development shell for linux-yocto."
    echo "16. Print version: Prints the version of the script."
}

if [ -z "$1" ]; then
    show_menu
    read -p "Enter your choice: " choice
    execute_option $choice
else
    execute_option $1
fi