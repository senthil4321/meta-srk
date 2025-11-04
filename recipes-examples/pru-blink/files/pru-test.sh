#!/bin/bash
# PRU Test Script
# Tests if PRU cores are available and can be loaded

echo "=== PRU Core Test ==="
echo ""

# Check if remoteproc is available
if [ ! -d /sys/class/remoteproc ]; then
    echo "ERROR: remoteproc not available"
    exit 1
fi

# Find PRU cores
echo "Available remoteproc cores:"
for rproc in /sys/class/remoteproc/remoteproc*; do
    if [ -d "$rproc" ]; then
        name=$(cat $rproc/name 2>/dev/null)
        state=$(cat $rproc/state 2>/dev/null)
        firmware=$(cat $rproc/firmware 2>/dev/null)
        echo "  $(basename $rproc): $name - State: $state - Firmware: $firmware"
    fi
done

echo ""
echo "PRU-ICSS information:"
if [ -d /sys/devices/platform/ocp/4a300000.pruss-soc-bus ]; then
    echo "  PRU-ICSS device found"
    ls -la /sys/devices/platform/ocp/4a300000.pruss-soc-bus/ 2>/dev/null | grep pru
else
    echo "  PRU-ICSS device not found"
fi

echo ""
echo "Firmware directory:"
ls -lh /lib/firmware/*pru* 2>/dev/null || echo "  No PRU firmware found"

echo ""
echo "=== End of PRU Test ==="
