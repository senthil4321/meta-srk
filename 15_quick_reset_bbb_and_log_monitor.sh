#!/bin/bash
"""
Quick Boot Monitor Script - Simplified version
"""

VERSION="1.0.0"
TIMEOUT=30
SEARCH_PATTERN=""
STOP_ON_MATCH=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -g|--grep)
            SEARCH_PATTERN="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -s|--stop-on-match)
            STOP_ON_MATCH=true
            shift
            ;;
        --help)
            echo "Usage: $0 [-g PATTERN] [-t SECONDS] [-s] [--grep PATTERN] [--timeout SECONDS] [--stop-on-match]"
            echo "  -g, --grep PATTERN: Text pattern to search for in the log file (optional)"
            echo "  -t, --timeout SECONDS: Monitoring timeout in seconds (default: 30)"
            echo "  -s, --stop-on-match: Stop monitoring early when pattern is found"
            echo "  --help: Show this help message"
            echo "  --version: Show version information"
            exit 0
            ;;
        --version)
            echo "$0 version $VERSION"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage"
            exit 1
            ;;
    esac
done

# Use local temp directory in project folder for easy access
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="$SCRIPT_DIR/temp/bbb_boot_logs"
mkdir -p "$TEMP_DIR"

LOG_FILE="$TEMP_DIR/quick_boot_$(date +%Y%m%d_%H%M%S).log"

echo "🔧 Quick BeagleBone Black Boot Monitor"
echo "===================================="
echo "📄 Saving log to: $LOG_FILE"
echo "⏰ Timeout: ${TIMEOUT}s"
if [ -n "$SEARCH_PATTERN" ]; then
    echo "🔍 Search pattern: $SEARCH_PATTERN"
    if [ "$STOP_ON_MATCH" = "true" ]; then
        echo "🎯 Will stop early on match"
    fi
fi
echo ""

# Start serial monitoring in background and save to file
ssh p "timeout ${TIMEOUT} socat - /dev/ttyUSB0,b115200,raw,echo=0,crnl" | tee "$LOG_FILE" &
MONITOR_PID=$!

# Wait a moment for monitoring to start
sleep 2

echo "🔄 Triggering reset..."
./13_remote_reset_bbb.sh

# Monitor for early pattern match if enabled
if [ -n "$SEARCH_PATTERN" ] && [ "$STOP_ON_MATCH" = "true" ]; then
    while kill -0 $MONITOR_PID 2>/dev/null; do
        if grep -q "$SEARCH_PATTERN" "$LOG_FILE"; then
            echo "🎯 Pattern found early! Stopping monitoring..."
            kill $MONITOR_PID
            break
        fi
        sleep 2
    done
fi

# Wait for monitoring to complete or timeout
wait $MONITOR_PID

echo ""
echo "📄 Full log saved in: $LOG_FILE"

# Search for pattern if provided
if [ -n "$SEARCH_PATTERN" ]; then
    echo "🔍 Searching log for pattern: $SEARCH_PATTERN"
    if grep -q "$SEARCH_PATTERN" "$LOG_FILE"; then
        echo "✅ Pattern found"
        echo "Matching lines:"
        grep "$SEARCH_PATTERN" "$LOG_FILE"
    else
        echo "❌ Pattern not found"
    fi
fi