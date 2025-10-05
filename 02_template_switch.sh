#!/bin/bash
# filepath: /home/srk2cob/project/poky/meta-srk/02_template_switch.sh

set -e

# Script directory and poky root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POKY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$POKY_ROOT/build"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Available templates
declare -A TEMPLATES=(
    ["default"]="meta-srk/conf/templates/default"
    ["nfs-dev"]="meta-srk/conf/templates/nfs-dev"
    ["production"]="meta-srk/conf/templates/production"
    ["conf-srk-tiny"]="meta-srk/conf/templates/conf-srk-tiny"
    ["dev"]="meta-srk/conf/templates/nfs-dev"  # Alias
    ["prod"]="meta-srk/conf/templates/production"  # Alias
    ["tiny"]="meta-srk/conf/templates/conf-srk-tiny"  # Alias
)

# Function to show usage
show_usage() {
    echo -e "${BLUE}Template Switch Script${NC}"
    echo "Usage: source $0 <template>  (or . $0 <template>)"
    echo ""
    echo "Available templates:"
    echo "  default        - Standard BeagleBone Black configuration"
    echo "  nfs-dev        - NFS development with debugging tools"
    echo "  dev            - Alias for nfs-dev"
    echo "  production     - Minimal, secure production build"
    echo "  prod           - Alias for production"
    echo "  conf-srk-tiny  - Tiny initramfs configuration"
    echo "  tiny           - Alias for conf-srk-tiny"
    echo ""
    echo "Examples:"
    echo "  source $0 dev            # Switch to NFS development template"
    echo "  source $0 production     # Switch to production template"
    echo "  source $0 conf-srk-tiny  # Switch to tiny initramfs template"
    echo "  source $0 tiny           # Switch to tiny initramfs template"
    echo ""
    echo "Note: This script must be sourced to set up the build environment in your shell."
}

# Function to backup existing config
backup_config() {
    if [ -f "$BUILD_DIR/conf/local.conf" ]; then
        local backup_dir="$SCRIPT_DIR/backup/conf_$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}📦 Backing up existing configuration...${NC}"
        mkdir -p "$backup_dir"
        cp "$BUILD_DIR/conf/local.conf" "$backup_dir/" 2>/dev/null || true
        cp "$BUILD_DIR/conf/bblayers.conf" "$backup_dir/" 2>/dev/null || true
        echo -e "${GREEN}✅ Configuration backed up to: $backup_dir${NC}"
    fi
}

# Function to delete old configuration
delete_old_config() {
    echo -e "${YELLOW}🗑️  Deleting old configuration files...${NC}"
    
    if [ -f "$BUILD_DIR/conf/local.conf" ]; then
        rm -f "$BUILD_DIR/conf/local.conf"
        echo -e "${GREEN}✅ Deleted old local.conf${NC}"
    else
        echo -e "${BLUE}ℹ️  No existing local.conf found${NC}"
    fi
    
    if [ -f "$BUILD_DIR/conf/bblayers.conf" ]; then
        rm -f "$BUILD_DIR/conf/bblayers.conf"
        echo -e "${GREEN}✅ Deleted old bblayers.conf${NC}"
    else
        echo -e "${BLUE}ℹ️  No existing bblayers.conf found${NC}"
    fi
}

# Function to apply new template
apply_template() {
    local template_path="$1"
    local template_name="$2"
    
    echo -e "${BLUE}🔄 Applying template: $template_name${NC}"
    echo -e "${YELLOW}📍 Template path: $template_path${NC}"
    
    # Change to poky root directory
    cd "$POKY_ROOT"
    
    # Set TEMPLATECONF and source oe-init-build-env
    echo -e "${BLUE}🚀 Initializing build environment...${NC}"
    export TEMPLATECONF="$template_path"
    
    # Source the build environment (this will create new conf files from templates)
    cd ~/project/poky/
    source oe-init-build-env build || {
        echo -e "${RED}❌ Failed to initialize build environment${NC}"
        [ "$0" = "$BASH_SOURCE" ] && exit 1 || return 1
    }
    cd ~/project/poky/meta-srk || {
        echo -e "${RED}❌ Failed to change directory to meta-srk${NC}"
        [ "$0" = "$BASH_SOURCE" ] && exit 1 || return 1
    }
    cat ~/project/poky/build/conf/local.conf | head -n 2

    echo -e "${GREEN}✅ Template applied successfully!${NC}"
    echo -e "${BLUE}Bitbake location: $(which bitbake)${NC}"
}

# Function to show template info
show_template_info() {
    local template="$1"
    
    echo -e "${BLUE}📋 Template Information:${NC}"
    case "$template" in
        "nfs-dev"|"dev")
            echo -e "${GREEN}🔧 NFS Development Template${NC}"
            echo "  • NFS root filesystem support"
            echo "  • GDB cross-debugging tools"
            echo "  • Network debugging (tcpdump, netcat)"
            echo "  • Hardware debugging (i2c-tools, devmem2)"
            echo "  • SSH server for remote development"
            echo "  • Development packages and tools"
            ;;
        "production"|"prod")
            echo -e "${GREEN}🏭 Production Template${NC}"
            echo "  • Minimal footprint"
            echo "  • Security hardening"
            echo "  • No development tools"
            echo "  • Optimized for deployment"
            ;;
        "default")
            echo -e "${GREEN}📦 Default Template${NC}"
            echo "  • Standard BeagleBone Black configuration"
            echo "  • Balanced feature set"
            echo "  • Good starting point"
            ;;
        "conf-srk-tiny"|"tiny")
            echo -e "${GREEN}🔸 Tiny Initramfs Template${NC}"
            echo "  • Minimal initramfs configuration"
            echo "  • Optimized for small footprint"
            echo "  • Fast boot times"
            echo "  • Suitable for embedded systems"
            ;;
    esac
}

# Function to show next steps
show_next_steps() {
    local template="$1"
    
    echo -e "${BLUE}🎯 Next Steps:${NC}"
    case "$template" in
        "nfs-dev"|"dev")
            echo "  bitbake core-image-tiny-initramfs-srk-11-bbb-examples"
            echo "  bitbake linux-yocto-srk-bbb"
            echo "  ../meta-srk/05_deploy_nfs_rootfs.sh"
            ;;
        "production"|"prod")
            echo "  bitbake core-image-tiny-initramfs-srk-3"
            echo "  ../meta-srk/04_copy_zImage.sh -i -tiny"
            ;;
        "default")
            echo "  bitbake core-image-tiny-initramfs-srk-3"
            echo "  ../meta-srk/04_copy_zImage.sh"
            ;;
        "conf-srk-tiny"|"tiny")
            echo "  bitbake core-image-tiny-initramfs-srk-9-nobusybox"
            echo "  bitbake linux-yocto-srk-tiny #builds kernel with embedded initramfs"
            echo "  ../meta-srk/04_copy_zImage.sh -i -tiny"
            ;;
    esac
}

# Main script logic
main() {
    # Check if template argument provided
    if [ $# -eq 0 ]; then
        show_usage
        [ "$0" = "$BASH_SOURCE" ] && exit 1 || return 1
    fi
    
    local template="$1"
    
    # Show help
    if [ "$template" = "help" ] || [ "$template" = "-h" ] || [ "$template" = "--help" ]; then
        show_usage
        [ "$0" = "$BASH_SOURCE" ] && exit 0 || return 0
    fi
    
    # Validate template exists
    if [ -z "${TEMPLATES[$template]}" ]; then
        echo -e "${RED}❌ Error: Template '$template' not found${NC}"
        echo ""
        show_usage
        [ "$0" = "$BASH_SOURCE" ] && exit 1 || return 1
    fi
    
    local template_path="${TEMPLATES[$template]}"
    
    # Verify template directory exists
    if [ ! -d "$POKY_ROOT/$template_path" ]; then
        echo -e "${RED}❌ Error: Template directory not found: $POKY_ROOT/$template_path${NC}"
        [ "$0" = "$BASH_SOURCE" ] && exit 1 || return 1
    fi
    
    echo -e "${BLUE}🔄 Template Switch Script${NC}"
    echo -e "${BLUE}========================${NC}"
    
    # Show template info
    show_template_info "$template"
    echo ""
    
    # Step 1: Backup existing configuration
    #backup_config
    #echo ""
    
    # Step 2: Delete old configuration files
    delete_old_config
    echo ""
    
    # Step 3: Apply new template
    apply_template "$template_path" "$template"
    echo ""
    
    # Show next steps
    show_next_steps "$template"
    echo ""
    
    echo -e "${GREEN}🎉 Template switch completed successfully!${NC}"
    echo -e "${BLUE}💡 You are now in the build environment with the '$template' template applied.${NC}"
}

# Run main function
main "$@"