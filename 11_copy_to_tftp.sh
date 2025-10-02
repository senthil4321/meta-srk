#!/bin/bash

# Copy files to TFTP server on Raspberry Pi
# Useful for deploying kernel images, device trees, and other boot files

VERSION="1.0.0"
SCRIPT_NAME="$(basename "$0")"
TFTP_DIR="/tmp/"

print_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [options] <file1> [file2] [...]

Copy files to TFTP server directory on Raspberry Pi for network booting.

Options:
    -d DIR         Target directory on TFTP server (default: $TFTP_DIR)
    -n NAME        Rename file on target (only works with single file)
    -c             Create target directory if it doesn't exist
    -v             Verbose output
    -l             List current TFTP directory contents
    -h             This help

Examples:
    $SCRIPT_NAME zImage                    # Copy zImage to TFTP root
    $SCRIPT_NAME -n zImage-debug zImage    # Copy and rename to zImage-debug
    $SCRIPT_NAME -d /srv/tftp/bbb *.dtb    # Copy device trees to subdirectory
    $SCRIPT_NAME -c -d /srv/tftp/test file # Create directory and copy
    $SCRIPT_NAME -l                       # List TFTP contents

Common Files to Deploy:
    - zImage (kernel image)
    - *.dtb (device tree blobs)
    - uImage (U-Boot kernel image)
    - initramfs files
    - configuration files

TFTP Server: Raspberry Pi (ssh p)
Target Directory: $TFTP_DIR

Version: $VERSION
EOF
}

# Default values
TARGET_DIR="$TFTP_DIR"
NEW_NAME=""
CREATE_DIR=false
VERBOSE=false
LIST_ONLY=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d) TARGET_DIR="$2"; shift ;;
        -n) NEW_NAME="$2"; shift ;;
        -c) CREATE_DIR=true ;;
        -v) VERBOSE=true ;;
        -l) LIST_ONLY=true ;;
        -h)
            print_help
            exit 0
            ;;
        -*) echo "Unknown option: $1"; print_help; exit 1 ;;
        *) break ;; # Start of file arguments
    esac
    shift
done

# Verbose output function
verbose_echo() {
    if [ "$VERBOSE" = true ]; then
        echo "$@"
    fi
}

# Function to check SSH connection
check_ssh_connection() {
    verbose_echo "🔌 Checking SSH connection to Raspberry Pi..."
    if ! ssh -o ConnectTimeout=5 p "echo 'SSH connection OK'" >/dev/null 2>&1; then
        echo "❌ Error: Cannot connect to Raspberry Pi via 'ssh p'"
        echo "   Please ensure SSH alias 'p' is configured and accessible"
        exit 1
    fi
    verbose_echo "✅ SSH connection to Raspberry Pi OK"
}

# Function to list TFTP directory
list_tftp_contents() {
    echo "📂 TFTP Directory Contents ($TARGET_DIR):"
    echo "========================================="
    
    if ssh p "test -d '$TARGET_DIR'"; then
        ssh p "ls -la '$TARGET_DIR'" || {
            echo "❌ Error: Cannot list TFTP directory"
            exit 1
        }
        
        echo ""
        echo "📊 Directory Summary:"
        echo "===================="
        
        # Count files and show sizes
        FILE_COUNT=$(ssh p "find '$TARGET_DIR' -type f | wc -l")
        TOTAL_SIZE=$(ssh p "du -sh '$TARGET_DIR' 2>/dev/null | cut -f1" || echo "unknown")
        
        echo "📁 Total files: $FILE_COUNT"
        echo "💾 Total size: $TOTAL_SIZE"
        
        # Show recent files
        echo ""
        echo "🕒 Recently modified files:"
        ssh p "find '$TARGET_DIR' -type f -mtime -1 -ls 2>/dev/null | head -5" || echo "   (none found)"
        
    else
        echo "❌ Error: TFTP directory '$TARGET_DIR' does not exist"
        echo "   Use -c option to create it automatically"
        exit 1
    fi
}

# Function to create target directory
create_target_directory() {
    if [ "$CREATE_DIR" = true ]; then
        verbose_echo "📁 Creating target directory: $TARGET_DIR"
        ssh p "mkdir -p '$TARGET_DIR'" || {
            echo "❌ Error: Cannot create directory '$TARGET_DIR'"
            exit 1
        }
        verbose_echo "✅ Directory created successfully"
    fi
}

# Function to copy single file
copy_file() {
    local local_file="$1"
    local remote_name="$2"
    
    if [ ! -f "$local_file" ]; then
        echo "❌ Error: Local file '$local_file' not found"
        return 1
    fi
    
    local file_size=$(stat -c%s "$local_file" 2>/dev/null || echo "unknown")
    local file_name=$(basename "$local_file")
    
    if [ -n "$remote_name" ]; then
        file_name="$remote_name"
    fi
    
    verbose_echo "📤 Copying: $local_file -> $TARGET_DIR/$file_name"
    verbose_echo "📏 Size: $file_size bytes"
    
    # Copy file
    if scp "$local_file" "p:$TARGET_DIR/$file_name"; then
        echo "✅ Copied: $file_name ($file_size bytes)"
        
        # Verify copy
        if ssh p "test -f '$TARGET_DIR/$file_name'"; then
            remote_size=$(ssh p "stat -c%s '$TARGET_DIR/$file_name'")
            if [ "$file_size" = "$remote_size" ]; then
                verbose_echo "✅ Verification: Size matches ($remote_size bytes)"
            else
                echo "⚠️  Warning: Size mismatch (local: $file_size, remote: $remote_size)"
            fi
        else
            echo "❌ Error: File not found on remote after copy"
            return 1
        fi
    else
        echo "❌ Error: Failed to copy $local_file"
        return 1
    fi
    
    return 0
}

# Main execution
main() {
    echo "📡 TFTP File Copy Utility"
    echo "========================"
    echo "Version: $VERSION"
    echo ""
    
    # Check SSH connection
    check_ssh_connection
    
    # Handle list-only mode
    if [ "$LIST_ONLY" = true ]; then
        list_tftp_contents
        exit 0
    fi
    
    # Check if files were provided
    if [ "$#" -eq 0 ]; then
        echo "❌ Error: No files specified"
        echo "   Use -h for help or -l to list TFTP contents"
        exit 1
    fi
    
    # Check for rename with multiple files
    if [ -n "$NEW_NAME" ] && [ "$#" -gt 1 ]; then
        echo "❌ Error: Cannot rename multiple files"
        echo "   Use -n option only with single file"
        exit 1
    fi
    
    # Check if target directory exists
    if ! ssh p "test -d '$TARGET_DIR'"; then
        if [ "$CREATE_DIR" = true ]; then
            create_target_directory
        else
            echo "❌ Error: Target directory '$TARGET_DIR' does not exist"
            echo "   Use -c option to create it automatically"
            exit 1
        fi
    fi
    
    echo "🎯 Target: ssh p:$TARGET_DIR"
    echo ""
    
    # Copy files
    SUCCESS_COUNT=0
    TOTAL_COUNT="$#"
    
    for file in "$@"; do
        if copy_file "$file" "$NEW_NAME"; then
            ((SUCCESS_COUNT++))
        fi
        echo ""
    done
    
    # Summary
    echo "📋 Copy Summary:"
    echo "==============="
    echo "✅ Successful: $SUCCESS_COUNT/$TOTAL_COUNT files"
    
    if [ "$SUCCESS_COUNT" -lt "$TOTAL_COUNT" ]; then
        echo "❌ Failed: $((TOTAL_COUNT - SUCCESS_COUNT)) files"
        exit 1
    fi
    
    echo ""
    echo "🔗 Files available via TFTP at: tftp://p$TARGET_DIR/"
}

# Execute main function
main "$@"