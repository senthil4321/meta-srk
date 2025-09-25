#!/bin/bash

# Remote BBB Reset Script
# Calls /bin/reset_bbb.sh on the server via SSH to reset the BeagleBone Black
# Typically run after copying files to trigger a BBB reset
#
# Usage: ./13_remote_reset_bbb.sh [-v] [-h] [-V]
#   -v: verbose output
#   -h: show help
#   -V: show version

VERSION="1.0.0"

print_help() {
    cat <<EOF
Usage: $0 [options]

Remotely reset the BeagleBone Black by calling /bin/reset_bbb.sh on the server.

This script uses SSH to connect to the server and execute the reset command.
Make sure SSH key-based authentication is configured for user 'p'.

Options:
    -v             Verbose output
    -V             Show version and exit
    -h             This help

Examples:
    $0              # Reset BBB remotely
    $0 -v           # Reset BBB with verbose output

EOF
}

print_version() {
    echo "$0 version $VERSION"
}

verbose=0

# Parse command line options
while getopts "vVh" opt; do
    case $opt in
        v)
            verbose=1
            ;;
        V)
            print_version
            exit 0
            ;;
        h)
            print_help
            exit 0
            ;;
        *)
            print_help
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main script
echo "========================================"
echo "  Remote BBB Reset Script v$VERSION"
echo "========================================"

if [ $verbose -eq 1 ]; then
    print_status "Verbose mode enabled"
fi

print_status "Connecting to server to reset BBB..."

# Execute reset_bbb.sh on the remote server via SSH
if [ $verbose -eq 1 ]; then
    ssh -v p@srk.local "/bin/reset_bbb.sh"
    ssh_exit_code=$?
else
    ssh p@srk.local "/bin/reset_bbb.sh"
    ssh_exit_code=$?
fi

if [ $ssh_exit_code -eq 0 ]; then
    print_success "BBB reset command executed successfully"
    print_status "BeagleBone Black should be resetting now..."
    print_status "Wait a few seconds for the reset to complete"
else
    print_error "Failed to execute BBB reset command (SSH exit code: $ssh_exit_code)"
    print_error "Check SSH connection and ensure reset_bbb.sh exists on the server"
    exit 1
fi

print_success "Remote BBB reset operation completed"
echo "========================================"
