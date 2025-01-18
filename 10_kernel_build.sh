#!/bin/bash

show_menu() {
    echo "Select an option:"
    echo "1. Build kernel"
    echo "2. Clean kernel"
    echo "3. Mrproper kernel"
    echo "4. Xconfig kernel"
    echo "5. Menuconfig kernel"
    echo "6. Exit"
}

execute_option() {
    case $1 in
        1)
            echo "Building the kernel..."
            make -j$(nproc)
            echo "Kernel build completed."
            ;;
        2)
            echo "Cleaning the kernel..."
            make clean
            echo "Kernel clean completed."
            ;;
        3)
            echo "Running mrproper on the kernel..."
            make mrproper
            echo "Kernel mrproper completed."
            ;;
        4)
            echo "Running xconfig on the kernel..."
            make xconfig
            echo "Kernel xconfig completed."
            ;;
        5)
            echo "Running menuconfig on the kernel..."
            make menuconfig
            echo "Kernel menuconfig completed."
            ;;
        6)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
}

if [ -z "$1" ]; then
    show_menu
    read -p "Enter your choice: " choice
    execute_option $choice
else
    execute_option $1
fi
