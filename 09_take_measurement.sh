#!/bin/bash

BACKUP_DIR_SHORT=~/project/linux/beaglebone/backup

show_menu() {
    echo "Select an option:"
    echo "1. Take measurement"
    echo "2. Git add"
    echo "3. Git commit"
    echo "4. Git push"
    echo "5. Git add, commit, and push"
    echo "6. Git status"
    echo "7. Git pull"
    echo "8. Exit"
}

take_measurement() {
    # Check if FOLDER_NAME is provided as a parameter
    if [ -z "$1" ]; then
        echo "Usage: $0 <FOLDER_NAME>"
        exit 1
    fi

    # Define variables for the paths
    FOLDER_NAME=$1

    BACKUP_DIR=${BACKUP_DIR_SHORT}/${FOLDER_NAME}/
    BUILD_DIR=~/project/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/linux-yocto/6.6.21+git/linux-beaglebone_yocto-standard-build
    KSIZE_OUTPUT=${BACKUP_DIR}${FOLDER_NAME}_ksize.txt
    ZIMAGE_SIZE_LOG=${BACKUP_DIR_SHORT}/zImageSize.txt

    # Print progress
    echo "Creating backup directory: ${BACKUP_DIR}"
    mkdir -p ${BACKUP_DIR}

    # Print progress
    echo "Running ksize.py and saving output to ${KSIZE_OUTPUT}"
    cd ${BUILD_DIR}
    ksize.py > ${KSIZE_OUTPUT}

    # Print progress
    echo "Copying .config file to ${BACKUP_DIR}"
    cp .config ${BACKUP_DIR}

    # Add date to the zImageSize log file
    echo "Adding date to ${ZIMAGE_SIZE_LOG}"
    echo $FOLDER_NAME >> ${ZIMAGE_SIZE_LOG}
    date >> ${ZIMAGE_SIZE_LOG}

    INPUT_FILENAME="zImage"
    SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
    ls -lahL $SOURCE_FILE >> ${ZIMAGE_SIZE_LOG}
    ls -laL $SOURCE_FILE >> ${ZIMAGE_SIZE_LOG}
    ls -la $SOURCE_FILE >> ${ZIMAGE_SIZE_LOG}

    # Print completion message
    echo "Measurement and backup completed successfully."

    cat ${ZIMAGE_SIZE_LOG}
}

git_add() {
    cd ${BACKUP_DIR_SHORT}
    git add .
    echo "Files added to git."
}

git_commit() {
    cd ${BACKUP_DIR_SHORT}
    git commit -m "new measurement added"
    echo "Changes committed to git with message 'new measurement added'."
}

git_push() {
    cd ${BACKUP_DIR_SHORT}
    git push
    echo "Changes pushed to remote repository."
}

git_add_commit_push() {
    cd ${BACKUP_DIR_SHORT}
    git add .
    echo "Files added to git."
    git commit -m "new measurement added"
    echo "Changes committed to git with message 'new measurement added'."
    git push
    echo "Changes pushed to remote repository."
}

git_status() {
    cd ${BACKUP_DIR_SHORT}
    git status
}

git_pull() {
    cd ${BACKUP_DIR_SHORT}
    git pull
}

if [ -z "$1" ]; then
    show_menu
    read -p "Enter your choice: " choice
    case $choice in
        1)
            read -p "Enter folder name: " folder_name
            take_measurement $folder_name
            ;;
        2)
            git_add
            ;;
        3)
            git_commit
            ;;
        4)
            git_push
            ;;
        5)
            git_add_commit_push
            ;;
        6)
            git_status
            ;;
        7)
            git_pull
            ;;
        8)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
else
    take_measurement $1
fi