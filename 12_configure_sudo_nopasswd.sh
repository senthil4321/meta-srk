#!/bin/bash

# Script to configure passwordless sudo for required commands
# This script adds NOPASSWD entries to /etc/sudoers for the current user

USER=$(whoami)
SUDOERS_FILE="/etc/sudoers"
BACKUP_FILE="/etc/sudoers.backup.$(date +%Y%m%d_%H%M%S)"

echo "Configuring passwordless sudo for user: $USER"
echo "This will require your current sudo password once."

# Backup sudoers file
sudo cp "$SUDOERS_FILE" "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# Commands that need NOPASSWD
COMMANDS=(
    "/bin/mount"
    "/bin/umount"
    "/sbin/losetup"
    "/sbin/cryptsetup"
    "/bin/dd"
    "/sbin/mkfs.ext4"
    "/bin/cp"
    "/bin/rm"
    "/bin/mkdir"
    "/bin/chmod"
    "/bin/chown"
)

# Add NOPASSWD entries
for CMD in "${COMMANDS[@]}"; do
    if ! sudo grep -q "$USER.*NOPASSWD.*$CMD" "$SUDOERS_FILE"; then
        echo "$USER ALL=(ALL) NOPASSWD: $CMD" | sudo tee -a "$SUDOERS_FILE" > /dev/null
        echo "Added NOPASSWD for: $CMD"
    else
        echo "NOPASSWD already configured for: $CMD"
    fi
done

echo "Configuration complete. You may need to restart your terminal session."
echo "Test with: sudo -n true"