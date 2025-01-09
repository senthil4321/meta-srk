#!/bin/bash

# Check if the password argument is provided or set as an environment variable
if [ -z "$1" ] && [ -z "$SCP_PASSWORD" ]; then
    echo "Usage: $0 -p <scp_password> [-m y|n] or set SCP_PASSWORD environment variable"
    exit 1
fi

# Parse arguments
MODULES_FLAG="n"
while getopts ":p:m:" opt; do
  case $opt in
    p)
      PASSWORD=$OPTARG
      ;;
    m)
      MODULES_FLAG=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# Define the input filenames and destination
INPUT_FILENAME="zImage"
MODULES_FILENAME="modules-beaglebone-yocto.tgz"
SOURCE_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$INPUT_FILENAME"
MODULES_FILE="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto/$MODULES_FILENAME"
DESTINATION="pi@srk.local:/tmp/"
PASSWORD=${PASSWORD:-$SCP_PASSWORD}

# Copy the zImage file using scp
echo "1. Copying $INPUT_FILENAME to $DESTINATION"
sshpass -p $PASSWORD scp $SOURCE_FILE $DESTINATION

# Check if the zImage copy was successful
if [ $? -eq 0 ];  then
    echo "2. $INPUT_FILENAME copied successfully to $DESTINATION"
    # Move the zImage file to the TFTP folder
    sshpass -p $PASSWORD ssh pi@srk.local "sudo mv /tmp/$INPUT_FILENAME /srv/tftp/"
    if [ $? -eq 0 ]; then
        echo "3. $INPUT_FILENAME moved successfully to /srv/tftp/"
    else
        echo "3. Failed to move $INPUT_FILENAME to /srv/tftp/"
    fi
else
    echo "2. Failed to copy $INPUT_FILENAME to $DESTINATION"
fi

# Copy the modules file using scp only if the -m y argument is passed
if [ "$MODULES_FLAG" == "y" ]; then
    echo "4. Copying $MODULES_FILENAME to $DESTINATION"
    sshpass -p $PASSWORD scp $MODULES_FILE $DESTINATION

    # Check if the modules copy was successful
    if [ $? -eq 0 ];  then
        echo "5. $MODULES_FILENAME copied successfully to $DESTINATION"
        # Extract the modules file to the appropriate directory
        sshpass -p $PASSWORD ssh pi@srk.local "sudo tar -xzf /tmp/$MODULES_FILENAME -C /srv/nfs/"
        if [ $? -eq 0 ]; then
            echo "6. $MODULES_FILENAME extracted successfully to /srv/nfs/"
        else
            echo "6. Failed to extract $MODULES_FILENAME to /srv/nfs/"
        fi
    else
        echo "5. Failed to copy $MODULES_FILENAME to $DESTINATION"
    fi
fi