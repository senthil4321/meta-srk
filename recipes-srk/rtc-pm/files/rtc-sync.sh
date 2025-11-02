#!/bin/bash
#
# RTC Synchronization Script
# Syncs system time to RTC at startup and shutdown
#

set -e

RTC_DEVICE="/dev/rtc0"
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_NC='\033[0m' # No Color

log_info() {
    echo -e "${COLOR_BLUE}[INFO]${COLOR_NC} $1"
    logger -t rtc-sync "$1"
}

log_success() {
    echo -e "${COLOR_GREEN}[OK]${COLOR_NC} $1"
    logger -t rtc-sync "$1"
}

log_warning() {
    echo -e "${COLOR_YELLOW}[WARN]${COLOR_NC} $1"
    logger -t rtc-sync "WARNING: $1"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_NC} $1"
    logger -t rtc-sync "ERROR: $1"
}

# Check if RTC device exists
if [ ! -e "$RTC_DEVICE" ]; then
    log_error "RTC device $RTC_DEVICE not found"
    exit 1
fi

# Display current times
log_info "RTC Synchronization"
echo ""
echo -e "${COLOR_BLUE}System Time:${COLOR_NC} $(date)"

if hwclock -r &>/dev/null; then
    echo -e "${COLOR_BLUE}RTC Time:   ${COLOR_NC} $(hwclock -r)"
else
    log_error "Cannot read RTC time"
    exit 1
fi

echo ""

# Sync system time to RTC
log_info "Syncing system time to RTC..."

if hwclock -w; then
    log_success "RTC synchronized with system time"
    echo -e "${COLOR_GREEN}New RTC Time:${COLOR_NC} $(hwclock -r)"
else
    log_error "Failed to sync RTC"
    exit 1
fi

exit 0
