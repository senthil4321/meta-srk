#!/bin/bash
"""
Quick Boot Monitor Script - Simple version for immediate use
"""

TIMEOUT=30
LOG_FILE="quick_boot_$(date +%Y%m%d_%H%M%S).log"

echo "🔧 Quick BeagleBone Black Boot Monitor"
echo "===================================="
echo "📄 Saving log to: $LOG_FILE"
echo "⏰ Timeout: ${TIMEOUT}s"
echo ""

# Start serial monitoring in background and save to file
ssh p "timeout ${TIMEOUT} socat - /dev/ttyUSB0,b115200,raw,echo=0,crnl" | tee "$LOG_FILE" &
MONITOR_PID=$!

# Wait a moment for monitoring to start
sleep 2

echo "🔄 Triggering reset..."
./13_remote_reset_bbb.sh

# Wait for monitoring to complete or timeout
wait $MONITOR_PID

echo ""
echo "📊 Quick Analysis:"
echo "=================="

# Extract key timings from log
if grep -q "U-Boot SPL" "$LOG_FILE"; then
    echo "✅ Boot detected"
else
    echo "❌ No boot detected"
fi

if grep -q "Hello World 1970-01-01 00:00:00" "$LOG_FILE"; then
    echo "✅ Application started"
else
    echo "❌ Application start not detected"
fi

# Count TI SYSC errors
SYSC_ERRORS=$(grep -c "ti-sysc: probe.*failed with error -16" "$LOG_FILE" 2>/dev/null || echo "0")
echo "⚠️  TI SYSC errors: $SYSC_ERRORS"

# Show memory info
MEMORY_LINE=$(grep "Memory:.*available" "$LOG_FILE" 2>/dev/null | head -1)
if [ -n "$MEMORY_LINE" ]; then
    echo "💾 $MEMORY_LINE"
fi

# Show init timing
INIT_TIME=$(grep -o "\[.*\] Run /init as init process" "$LOG_FILE" 2>/dev/null | grep -o "\[.*\]" | tr -d '[]' | awk '{print $1}')
if [ -n "$INIT_TIME" ]; then
    echo "🚀 Kernel to init: ${INIT_TIME}s"
fi

echo ""
echo "📄 Full log saved in: $LOG_FILE"
echo "🔍 Run: cat $LOG_FILE | grep -E '(U-Boot|Starting kernel|console.*enabled|Run /init|Hello World)'"