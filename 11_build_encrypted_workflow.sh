#!/bin/bash

# build_encrypted_workflow.sh
# Automated workflow for building encrypted SquashFS images
# Version: 1.0.0
# Author: senthil4321

# Source Yocto environment
if [[ -f "/home/srk2cob/project/poky/oe-init-build-env" ]]; then
    source /home/srk2cob/project/poky/oe-init-build-env /home/srk2cob/project/poky/build
else
    echo "Error: Yocto environment script not found at /home/srk2cob/project/poky/oe-init-build-env"
    exit 1
fi

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BUILD_DIR="/home/srk2cob/project/poky/build"
META_DIR="/home/srk2cob/project/poky/meta-srk"
IMAGE_NAME="core-image-minimal-squashfs-srk"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Error handling function
handle_error() {
    local step=$1
    local error_code=$2
    log_error "Step '$step' failed with exit code $error_code"
    echo -e "${RED}Workflow failed at step: $step${NC}"
    echo -e "${YELLOW}You can resume from this step after fixing the issue.${NC}"
    exit $error_code
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Pre-flight checks
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Check if we're in the right environment
    if [[ ! -d "$BUILD_DIR" ]]; then
        log_error "Build directory not found: $BUILD_DIR"
        exit 1
    fi

    if [[ ! -d "$META_DIR" ]]; then
        log_error "Meta directory not found: $META_DIR"
        exit 1
    fi

    # Check for required commands
    local required_commands=("bitbake" "losetup" "cryptsetup" "rsync" "ssh")
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            log_error "Required command not found: $cmd"
            exit 1
        fi
    done

    # Check for SSH key authentication
    if [[ ! -f "$HOME/.ssh/id_rsa" ]]; then
        log_warning "SSH key not found. Make sure SSH key authentication is set up."
    fi

    log_success "Pre-flight checks passed"
}

# Step 1: Build the base image
step_build_image() {
    log_step "Building base image: $IMAGE_NAME"
    log_info "Changing to build directory: $BUILD_DIR"

    cd "$BUILD_DIR" || handle_error "Change to build directory" $?

    log_info "Starting BitBake build..."
    local start_time=$(date +%s)

    if bitbake "$IMAGE_NAME"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_success "Image build completed successfully in ${duration}s"
        return 0
    else
        handle_error "BitBake build" $?
    fi
}

# Step 2: Create encrypted image
step_create_encrypted() {
    log_step "Creating encrypted image"
    log_info "Changing to meta directory: $META_DIR"

    cd "$META_DIR" || handle_error "Change to meta directory" $?

    log_info "Running: ./06_created_encrypted_image.sh 2.5"
    if ./06_created_encrypted_image.sh 2.5; then
        log_success "Encrypted image created successfully"
        return 0
    else
        handle_error "Create encrypted image" $?
    fi
}

# Step 3: Mount encrypted image
step_mount_encrypted() {
    log_step "Mounting encrypted image"
    log_info "Changing to meta directory: $META_DIR"

    cd "$META_DIR" || handle_error "Change to meta directory" $?

    log_info "Running: ./06_created_encrypted_image.sh 4"
    if ./06_created_encrypted_image.sh 4; then
        log_success "Encrypted image mounted successfully"
        return 0
    else
        handle_error "Mount encrypted image" $?
    fi
}

# Step 3: Copy SquashFS to encrypted container
step_copy_squashfs() {
    log_step "Copying SquashFS to encrypted container"
    log_info "Running: ./06_created_encrypted_image.sh 8"

    if ./06_created_encrypted_image.sh 8; then
        log_success "SquashFS copied to encrypted container successfully"
        return 0
    else
        handle_error "Copy SquashFS to encrypted container" $?
    fi
}

# Step 4: Cleanup encrypted image
step_cleanup_encrypted() {
    log_step "Cleaning up encrypted image"
    log_info "Running: ./06_created_encrypted_image.sh 10"

    if ./06_created_encrypted_image.sh 10; then
        log_success "Encrypted image cleanup completed successfully"
        return 0
    else
        handle_error "Cleanup encrypted image" $?
    fi
}

# Step 5: Copy SquashFS to remote server
step_copy_to_remote() {
    log_step "Copying SquashFS to remote server"
    log_info "Running: ./05_copy_squashfs.sh -i"

    if ./05_copy_squashfs.sh -i; then
        log_success "SquashFS copied to remote server successfully"
        return 0
    else
        handle_error "Copy to remote server" $?
    fi
}

# Main workflow
main() {
    local start_time=$(date +%s)

    echo "=================================================="
    echo "🔐 Encrypted SquashFS Build Workflow"
    echo "=================================================="
    log_info "Starting workflow at $(date)"
    echo

    # Run pre-flight checks
    preflight_checks
    echo

    # Execute workflow steps
    step_build_image
    echo

    step_create_encrypted
    echo

    step_mount_encrypted
    echo

    step_copy_squashfs
    echo

    step_cleanup_encrypted
    echo

    step_copy_to_remote
    echo

    # Calculate total duration
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))

    echo "=================================================="
    log_success "Workflow completed successfully!"
    log_info "Total execution time: ${total_duration}s"
    echo "=================================================="

    # Summary
    echo
    echo "📋 Workflow Summary:"
    echo "  ✅ Base image built"
    echo "  ✅ Encrypted container created"
    echo "  ✅ Encrypted container mounted"
    echo "  ✅ SquashFS copied to encrypted container"
    echo "  ✅ Encrypted container cleaned up"
    echo "  ✅ Files copied to remote server"
    echo
    echo "🎉 Encrypted rootfs build workflow completed!"
}

# Trap for cleanup on script exit
trap 'echo -e "\n${YELLOW}Workflow interrupted${NC}"' INT TERM

# Run main function
main "$@"