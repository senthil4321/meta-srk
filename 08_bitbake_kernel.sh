#!/bin/bash

VERSION="1.1.0"

# Default values
USE_TINY=false
KERNEL_NAME="linux-yocto"
MACHINE_SUFFIX=""
BUILD_SUFFIX="-standard-build"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -tiny)
            USE_TINY=true
            KERNEL_NAME="linux-yocto-srk-tiny"
            MACHINE_SUFFIX="_srk_tiny"
            BUILD_SUFFIX="-standard-build"
            shift
            ;;
        *)
            break
            ;;
    esac
done

# Set up machine suffix and detect kernel version based on kernel type
if [ "$USE_TINY" = true ]; then
    MACHINE_SUFFIX="_srk_tiny"
    KERNEL_BASE_DIR="/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto${MACHINE_SUFFIX}-poky-linux-gnueabi/${KERNEL_NAME}"
    if [ -d "$KERNEL_BASE_DIR" ] && [ "$(ls -A "$KERNEL_BASE_DIR" 2>/dev/null)" ]; then
        KERNEL_VERSION=$(ls "$KERNEL_BASE_DIR" | head -1)
    else
        KERNEL_VERSION="6.6+git"  # fallback
    fi
else
    MACHINE_SUFFIX=""
    KERNEL_BASE_DIR="/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto"
    if [ -d "$KERNEL_BASE_DIR" ] && [ "$(ls -A "$KERNEL_BASE_DIR" 2>/dev/null)" ]; then
        KERNEL_VERSION=$(ls "$KERNEL_BASE_DIR" | head -1)
    else
        KERNEL_VERSION="6.6.21+git"  # fallback
    fi
fi

show_menu() {
    if [ "$USE_TINY" = true ]; then
        echo "=== TINY KERNEL MODE (-tiny) ==="
    else
        echo "=== STANDARD KERNEL MODE ==="
    fi
    echo "Work Flow 2, 3, 10 --- Run 2. menuconfig.  3. diffconfig and 10. Print fragment.cfg file contents ---"
    echo "Select an option:"
    echo "0. bitbake virtual/kernel "
    echo "1. bitbake $KERNEL_NAME -c kernel_configme -f"
    echo "2. bitbake $KERNEL_NAME -c menuconfig"
    echo "3. bitbake $KERNEL_NAME -c diffconfig"
    echo "4. bitbake $KERNEL_NAME -c kernel_configcheck -f"
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
    echo "15. bitbake -c devshell $KERNEL_NAME"
    echo "16. Print version"
}

execute_option() {
    case $1 in
        0)
            bitbake virtual/kernel
            ;;
        1)
            bitbake $KERNEL_NAME -c kernel_configme -f
            ;;
        2)
            bitbake $KERNEL_NAME -c menuconfig
            ;;
        3)
            bitbake $KERNEL_NAME -c diffconfig
            ;;
        4)
            bitbake $KERNEL_NAME -c kernel_configcheck -f
            ;;
        5)
            bitbake $KERNEL_NAME -c savedefconfig
            ;;
        6)
            echo "~/project/poky/build/tmp/work/beaglebone_yocto${MACHINE_SUFFIX}-poky-linux-gnueabi/${KERNEL_NAME}/${KERNEL_VERSION}/linux-beaglebone_yocto${MACHINE_SUFFIX}-standard-build/.config"
            ;;
        7)
            if [ "$USE_TINY" = true ]; then
                echo "/home/srk2cob/project/poky/meta-srk/recipes-kernel/linux/linux-yocto-srk-tiny/defconfig"
            else
                echo "/home/srk2cob/project/poky/meta-srk/recipes-kernel/linux/linux-yocto/defconfig"
            fi
            ;;
        8)
            echo "/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto${MACHINE_SUFFIX}-poky-linux-gnueabi/${KERNEL_NAME}/${KERNEL_VERSION}/linux-beaglebone_yocto${MACHINE_SUFFIX}-standard-build/defconfig"
            ;;
        9)
            echo "/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto${MACHINE_SUFFIX}-poky-linux-gnueabi/${KERNEL_NAME}/${KERNEL_VERSION}/fragment.cfg"
            ;;
        10)
            FRAGMENT_FILE="/home/srk2cob/project/poky/build/tmp/work/beaglebone_yocto${MACHINE_SUFFIX}-poky-linux-gnueabi/${KERNEL_NAME}/${KERNEL_VERSION}/fragment.cfg"
            if [ -f "$FRAGMENT_FILE" ]; then
                cat "$FRAGMENT_FILE"
            else
                echo "Fragment file does not exist: $FRAGMENT_FILE"
                echo "Run menuconfig (option 2) and diffconfig (option 3) first to create the fragment.cfg file."
            fi
            ;;
        11)
            echo "Run 2. menuconfig.  3. diffconfig and 10. Print fragment.cfg file contents"
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
            bitbake -c devshell $KERNEL_NAME
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
    echo "Usage: $0 [-tiny] [option]"
    echo ""
    echo "Options:"
    echo "  -tiny    Use tiny kernel (linux-yocto-srk-tiny) instead of standard kernel"
    echo ""
    echo "Menu Options:"
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
    echo "15. Open devshell: Opens the development shell for the current kernel."
    echo "16. Print version: Prints the version of the script."
    echo ""
    if [ "$USE_TINY" = true ]; then
        echo "Current mode: TINY KERNEL (linux-yocto-srk-tiny)"
    else
        echo "Current mode: STANDARD KERNEL (linux-yocto)"
    fi
}

if [ $# -eq 0 ] || ([ $# -eq 1 ] && [ "$1" = "-tiny" ]); then
    show_menu
    read -p "Enter your choice: " choice
    execute_option $choice
else
    # Remove the -tiny parameter if it was used, and execute the remaining argument
    if [ "$1" = "-tiny" ]; then
        execute_option $2
    else
        execute_option $1
    fi
fi