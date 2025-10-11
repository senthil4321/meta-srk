#!/bin/bash

# Copy initramfs image to target device
# Uses SSH alias 'p' configured in ~/.ssh/config for pi@srk.local
# Uses SSH key-based authentication (no password required)

VERSION="1.0.1"

print_help() {
    cat <<EOF
Usage: 
    $(basename "$0") <VERSION|ALIAS> [MACHINE]   Copy initramfs by version number or alias
    $(basename "$0") -m <MACHINE> <VERSION|ALIAS> Specify machine with -m option

Arguments:
    VERSION         Version number (1-11) or hyphenated format (e.g., 11-custom)
    ALIAS           Predefined alias for specific image variants (e.g., 2-bash)
    MACHINE         Target machine (default: beaglebone-yocto)

<version> can be one of:
    1              -> core-image-tiny-initramfs-srk-1
    2              -> core-image-tiny-initramfs-srk-2
    3              -> core-image-tiny-initramfs-srk-3
    4              -> core-image-tiny-initramfs-srk-4-nocrypt
    5              -> core-image-tiny-initramfs-srk-5
    6              -> core-image-tiny-initramfs-srk-6
    7              -> core-image-tiny-initramfs-srk-7-sizeopt
    8              -> core-image-tiny-initramfs-srk-8-nonet
    9              -> core-image-tiny-initramfs-srk-9-nobusybox (BusyBox removed)
    10             -> core-image-tiny-initramfs-srk-10-selinux (SELinux enabled)
    11             -> core-image-tiny-initramfs-srk-11-bbb-examples (BBB hardware examples)
    <number>-<suffix> -> core-image-tiny-initramfs-srk-<number>-<suffix> (custom format)

<alias> can be one of:
    2-bash         -> core-image-tiny-initramfs-srk-2-bash

Options:
    -m <machine>   Machine target (default: beaglebone-yocto)
                   Valid options: beaglebone-yocto, beaglebone-yocto-srk, beaglebone-yocto-srk-tiny
                   Short aliases: srk (for beaglebone-yocto-srk), tiny (for beaglebone-yocto-srk-tiny)
    -V             Show version and exit
    -h             This help

Examples:
    ./03_copy_initramfs.sh 2                                    # Uses default machine: beaglebone-yocto
    ./03_copy_initramfs.sh 2 beaglebone-yocto-srk               # Uses beaglebone-yocto-srk machine
    ./03_copy_initramfs.sh 3 srk                                # Uses beaglebone-yocto-srk with short alias
    ./03_copy_initramfs.sh 9 tiny                               # Uses tiny machine variant
    ./03_copy_initramfs.sh 2-bash beaglebone-yocto-srk          # Uses alias directly (no -a needed)
    ./03_copy_initramfs.sh 2-bash srk                           # Uses alias with machine short alias  
    ./03_copy_initramfs.sh -m srk 2                             # Alternative: -m option with version
    ./03_copy_initramfs.sh -m srk 2-bash                        # Alternative: -m option with alias

Notes:
    - Uses SSH alias 'p' configured in ~/.ssh/config
    - SSH key-based authentication is used (no password required)
    - Supports multiple machine targets: beaglebone-yocto (default), beaglebone-yocto-srk, beaglebone-yocto-srk-tiny
    - Short aliases: srk, tiny for common machine variants
    - Images are deployed to /srv/nfs/ on remote target

Version: $VERSION
EOF
}

# Default machine target (will be set later if not specified)
MACHINE_TARGET=""

# Parse command line arguments manually to handle flexible argument order
VERSION_ARG=""
SHOW_VERSION=false
SHOW_HELP=false

while [ $# -gt 0 ]; do
    case $1 in
        -V)
            SHOW_VERSION=true
            shift
            ;;
        -h)
            SHOW_HELP=true
            shift
            ;;
        -m)
            if [ -z "$2" ]; then
                echo "Option -m requires an argument" >&2
                exit 1
            fi
            case "$2" in
                beaglebone-yocto-srk|beaglebone-yocto|beaglebone-yocto-srk-tiny)
                    MACHINE_TARGET="$2"
                    ;;
                srk)
                    MACHINE_TARGET="beaglebone-yocto-srk"
                    ;;
                tiny)
                    MACHINE_TARGET="beaglebone-yocto-srk-tiny"
                    ;;
                *)
                    echo "Invalid machine '$2'. Valid options: beaglebone-yocto, beaglebone-yocto-srk, beaglebone-yocto-srk-tiny, srk, tiny" >&2
                    exit 1
                    ;;
            esac
            shift 2
            ;;
        -*)
            echo "Invalid option: $1" >&2
            print_help
            exit 1
            ;;
        *)
            if [ -z "$VERSION_ARG" ]; then
                VERSION_ARG="$1"
            elif [ -z "$MACHINE_TARGET" ]; then
                # Second positional argument is machine target
                case "$1" in
                    beaglebone-yocto-srk|beaglebone-yocto|beaglebone-yocto-srk-tiny)
                        MACHINE_TARGET="$1"
                        ;;
                    srk)
                        MACHINE_TARGET="beaglebone-yocto-srk"
                        ;;
                    tiny)
                        MACHINE_TARGET="beaglebone-yocto-srk-tiny"
                        ;;
                    *)
                        echo "Invalid machine '$1'. Valid options: beaglebone-yocto, beaglebone-yocto-srk, beaglebone-yocto-srk-tiny, srk, tiny" >&2
                        exit 1
                        ;;
                esac
            else
                echo "Unexpected argument: '$1'" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

# Handle help and version requests
if [ "$SHOW_VERSION" = true ]; then
    echo "$(basename "$0") version $VERSION"
    exit 0
fi

if [ "$SHOW_HELP" = true ]; then
    print_help
    exit 0
fi

# Check if version argument is provided
if [ -z "$VERSION_ARG" ]; then
    echo "Missing version argument or alias. See --help (-h) for options."
    exit 1
fi

# Set default machine if not specified
if [ -z "$MACHINE_TARGET" ]; then
    MACHINE_TARGET="beaglebone-yocto"
fi

# Function to map alias to image name
map_alias_to_image() {
    local alias="$1"
    case "$alias" in
        2-bash)
            echo "core-image-tiny-initramfs-srk-2-bash"
            ;;
        *)
            echo ""  # Invalid alias
            ;;
    esac
}

# Try to detect if VERSION_ARG is actually an alias
IMAGE_BASE=$(map_alias_to_image "$VERSION_ARG")
if [ -n "$IMAGE_BASE" ]; then
    # It's an alias
    INITRAMFS_VERSION="$VERSION_ARG"
else
    # It's a version number, process normally
    INITRAMFS_VERSION="$VERSION_ARG"
fi

# Function to map version numbers to specific image recipes
map_version_to_image() {
    local version="$1"
    case "$version" in
        1)
            echo "core-image-tiny-initramfs-srk-1"
            ;;
        2)
            echo "core-image-tiny-initramfs-srk-2"
            ;;
        3)
            echo "core-image-tiny-initramfs-srk-3"
            ;;
        4)
            echo "core-image-tiny-initramfs-srk-4-nocrypt"
            ;;
        5)
            echo "core-image-tiny-initramfs-srk-5"
            ;;
        6)
            echo "core-image-tiny-initramfs-srk-6"
            ;;
        7)
            echo "core-image-tiny-initramfs-srk-7-sizeopt"
            ;;
        8)
            echo "core-image-tiny-initramfs-srk-8-nonet"
            ;;
        9)
            echo "core-image-tiny-initramfs-srk-9-nobusybox"
            ;;
        10)
            echo "core-image-tiny-initramfs-srk-10-selinux"
            ;;
        11)
            echo "core-image-tiny-initramfs-srk-11-bbb-examples"
            ;;
        [0-9]*-*)
            # Handle hyphenated versions like "11-bbb-examples"
            echo "core-image-tiny-initramfs-srk-${version}"
            ;;
        [0-9]*)
            # Generic numeric versions not specifically mapped
            echo "core-image-tiny-initramfs-srk-${version}"
            ;;
        *)
            echo ""  # Invalid version
            ;;
    esac
}

# Get the image base name
if [ -z "$IMAGE_BASE" ]; then
    # Only map version if IMAGE_BASE is not already set by alias
    IMAGE_BASE=$(map_version_to_image "$INITRAMFS_VERSION")
fi

if [ -z "$IMAGE_BASE" ]; then
    echo "Invalid version or alias '$INITRAMFS_VERSION'." >&2
    echo "Supported versions:" >&2
    echo "  1  -> core-image-tiny-initramfs-srk-1" >&2
    echo "  2  -> core-image-tiny-initramfs-srk-2" >&2
    echo "  3  -> core-image-tiny-initramfs-srk-3" >&2
    echo "  4  -> core-image-tiny-initramfs-srk-4-nocrypt" >&2
    echo "  5  -> core-image-tiny-initramfs-srk-5" >&2
    echo "  6  -> core-image-tiny-initramfs-srk-6" >&2
    echo "  7  -> core-image-tiny-initramfs-srk-7-sizeopt" >&2
    echo "  8  -> core-image-tiny-initramfs-srk-8-nonet" >&2
    echo "  9  -> core-image-tiny-initramfs-srk-9-nobusybox" >&2
    echo "  10 -> core-image-tiny-initramfs-srk-10-selinux" >&2
    echo "  11 -> core-image-tiny-initramfs-srk-11-bbb-examples" >&2
    echo "Or use hyphenated format like '11-custom' for core-image-tiny-initramfs-srk-11-custom" >&2
    echo "Supported aliases:" >&2
    echo "  2-bash -> core-image-tiny-initramfs-srk-2-bash" >&2
    exit 1
fi

INPUT_FILENAME="${IMAGE_BASE}-${MACHINE_TARGET}.rootfs.cpio.gz"

# Define the source file and destination
SOURCE_DIR="/home/srk2cob/project/poky/build/tmp/deploy/images/${MACHINE_TARGET}/"
SOURCE_FILE="${SOURCE_DIR}${INPUT_FILENAME}"

# Check if the expected file exists, if not try to find a matching file with suffix
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Expected file $INPUT_FILENAME not found, looking for files with suffix..."
    
    # Extract the base pattern (e.g., "11" from "core-image-tiny-initramfs-srk-11")
    BASE_PATTERN=$(echo "$IMAGE_BASE" | sed 's/core-image-tiny-initramfs-srk-//')
    
    # Look for files matching the pattern with suffix
    CANDIDATE_FILES=$(find "$SOURCE_DIR" -name "core-image-tiny-initramfs-srk-${BASE_PATTERN}*-${MACHINE_TARGET}.rootfs.cpio.gz" -type l 2>/dev/null)
    
    if [ -n "$CANDIDATE_FILES" ]; then
        # Use the first candidate file found
        ACTUAL_FILE=$(echo "$CANDIDATE_FILES" | head -n1)
        INPUT_FILENAME=$(basename "$ACTUAL_FILE")
        SOURCE_FILE="$ACTUAL_FILE"
        echo "Found matching file: $INPUT_FILENAME"
    else
        echo "Error: No matching initramfs file found for pattern: core-image-tiny-initramfs-srk-${BASE_PATTERN}*-${MACHINE_TARGET}.rootfs.cpio.gz" >&2
        echo "Source directory: $SOURCE_DIR" >&2
        echo "Available files:" >&2
        ls -la "$SOURCE_DIR"core-image-tiny-initramfs-srk-${BASE_PATTERN}* 2>/dev/null || echo "No files found with pattern core-image-tiny-initramfs-srk-${BASE_PATTERN}*" >&2
        exit 1
    fi
fi

DESTINATION="p:/tmp/"

# Copy the file using scp
echo "1. Copying $INPUT_FILENAME to $DESTINATION (Machine: $MACHINE_TARGET)"
scp $SOURCE_FILE $DESTINATION

# Check if the copy was successful
if [ $? -eq 0 ];  then
    echo "2. $INPUT_FILENAME copied successfully to $DESTINATION"
    # Delete the content of the NFS folder before extraction
    ssh p "sudo rm -rf /srv/nfs/*"
    if [ $? -eq 0 ]; then
        echo "3. NFS folder content deleted successfully"
        echo "4. Extracting $INPUT_FILENAME to /srv/nfs/"
        # Extract the file in the remote folder /srv/nfs/
        ssh p "gunzip -c /tmp/$INPUT_FILENAME | sudo cpio -idmv -D /srv/nfs/"
        if [ $? -eq 0 ]; then
            echo "5. $INPUT_FILENAME extracted successfully to /srv/nfs/"
        else
            echo "5. Failed to extract $INPUT_FILENAME to /srv/nfs/"
        fi
    else
        echo "3. Failed to delete NFS folder content"
    fi
else
    echo "2. Failed to copy $INPUT_FILENAME to $DESTINATION"
fi