#!/bin/bash
"""
Serial Command Monitor Script
Sends a command to serial console and monitors response
"""

VERSION="2.0.0"
TIMEOUT=30
COMMAND=""
EXPECTED_RESPONSE=""
STOP_ON_RESPONSE=false

# Cleanup function to kill background processes
cleanup() {
    if [ ! -z "$MONITOR_PID" ] && kill -0 $MONITOR_PID 2>/dev/null; then
        kill $MONITOR_PID 2>/dev/null
        wait $MONITOR_PID 2>/dev/null
    fi
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--command)
            COMMAND="$2"
            shift 2
            ;;
        -e|--expect)
            EXPECTED_RESPONSE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -s|--stop-on-response)
            STOP_ON_RESPONSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 -c COMMAND [-e RESPONSE] [-t SECONDS] [-s]"
            echo "  -c, --command COMMAND: Command to send to serial console"
            echo "  -e, --expect RESPONSE: Expected response pattern to check for (optional)"
            echo "  -t, --timeout SECONDS: Monitoring timeout in seconds (default: 30)"
            echo "  -s, --stop-on-response: Stop monitoring early when expected response is found"
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

# Validate required parameters
if [ -z "$COMMAND" ]; then
    echo "Error: Command is required. Use -c or --command"
    exit 1
fi

# Use local temp directory in project folder for easy access
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="$SCRIPT_DIR/temp/serial_command_logs"
mkdir -p "$TEMP_DIR"

LOG_FILE="$TEMP_DIR/serial_command_$(date +%Y%m%d_%H%M%S).log"

echo "🔧 Serial Command Monitor"
echo "========================="
echo "📄 Saving log to: $LOG_FILE"
echo "⏰ Timeout: ${TIMEOUT}s"
echo "💬 Command: $COMMAND"
if [ -n "$EXPECTED_RESPONSE" ]; then
    echo "🎯 Expected response: $EXPECTED_RESPONSE"
    if [ "$STOP_ON_RESPONSE" = "true" ]; then
        echo "🛑 Will stop early on response"
    fi
fi
echo ""

# Start serial monitoring in background and save to file
# Add overall timeout to prevent hanging
timeout $((TIMEOUT + 2)) ssh p "timeout ${TIMEOUT} socat - /dev/ttyUSB0,b115200,raw,echo=0" | tee "$LOG_FILE" &
MONITOR_PID=$!

# Wait a moment for monitoring to start
sleep 2

echo "📤 Sending command to serial console..."
# Send command to serial console with timeout protection
timeout 2 echo "$COMMAND" | timeout 2 ssh p "socat - /dev/ttyUSB0,b115200,raw,echo=0"

# Monitor for expected response if enabled
if [ -n "$EXPECTED_RESPONSE" ] && [ "$STOP_ON_RESPONSE" = "true" ]; then
    START_TIME=$(date +%s)
    while kill -0 $MONITOR_PID 2>/dev/null; do
        # Check for timeout to prevent infinite loop
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        if [ $ELAPSED -gt $((TIMEOUT + 2)) ]; then
            echo "⏰ Monitoring timeout reached, stopping..."
            kill $MONITOR_PID 2>/dev/null
            break
        fi

        if grep -q "$EXPECTED_RESPONSE" "$LOG_FILE"; then
            echo "🎯 Expected response found early! Stopping monitoring..."
            kill $MONITOR_PID
            break
        fi
        sleep 1
    done
fi

# Wait for monitoring to complete or timeout with safety timeout
START_WAIT=$(date +%s)
while kill -0 $MONITOR_PID 2>/dev/null; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_WAIT))
    if [ $ELAPSED -gt $((TIMEOUT + 15)) ]; then
        echo "⏰ Wait timeout reached, forcing exit..."
        kill $MONITOR_PID 2>/dev/null
        break
    fi
    sleep 1
done
wait $MONITOR_PID 2>/dev/null

echo ""
echo "📄 Full log saved in: $LOG_FILE"

# Check for expected response if provided
if [ -n "$EXPECTED_RESPONSE" ]; then
    echo "🔍 Checking for expected response: $EXPECTED_RESPONSE"
    if grep -q "$EXPECTED_RESPONSE" "$LOG_FILE"; then
        echo "✅ Expected response found"
        echo "Matching lines:"
        grep "$EXPECTED_RESPONSE" "$LOG_FILE"
    else
        echo "❌ Expected response not found"
    fi
fi