#!/bin/bash
# PRU Firmware Loader
# Loads firmware to PRU cores and starts them

set -e

echo "=== PRU Firmware Loader ==="

# Check if firmware files exist
if [ ! -f /lib/firmware/am335x-pru0-fw ]; then
    echo "ERROR: PRU0 firmware not found at /lib/firmware/am335x-pru0-fw"
    exit 1
fi

if [ ! -f /lib/firmware/am335x-pru1-fw ]; then
    echo "ERROR: PRU1 firmware not found at /lib/firmware/am335x-pru1-fw"
    exit 1
fi

echo "Firmware files found:"
ls -lh /lib/firmware/am335x-pru*-fw

echo ""
echo "Current PRU states:"
for rproc in /sys/class/remoteproc/remoteproc*; do
    if [ -d "$rproc" ]; then
        name=$(cat $rproc/name)
        state=$(cat $rproc/state)
        firmware=$(cat $rproc/firmware)
        echo "  $(basename $rproc): $name - $state (firmware: $firmware)"
    fi
done

echo ""
echo "Starting PRU cores..."

# Start PRU0
if [ -w /sys/class/remoteproc/remoteproc0/state ]; then
    echo "Starting PRU0..."
    echo "start" > /sys/class/remoteproc/remoteproc0/state
    sleep 1
    state=$(cat /sys/class/remoteproc/remoteproc0/state)
    echo "  PRU0 state: $state"
else
    echo "  Cannot start PRU0 (state file not writable)"
    echo "  Trying alternative method..."
    
    # Check if firmware loading succeeded in dmesg
    dmesg | tail -20 | grep -i pru || echo "  No recent PRU messages in dmesg"
fi

echo ""
# Start PRU1
if [ -w /sys/class/remoteproc/remoteproc1/state ]; then
    echo "Starting PRU1..."
    echo "start" > /sys/class/remoteproc/remoteproc1/state
    sleep 1
    state=$(cat /sys/class/remoteproc/remoteproc1/state)
    echo "  PRU1 state: $state"
else
    echo "  Cannot start PRU1 (state file not writable)"
fi

echo ""
echo "Final PRU states:"
for rproc in /sys/class/remoteproc/remoteproc*; do
    if [ -d "$rproc" ]; then
        name=$(cat $rproc/name)
        state=$(cat $rproc/state)
        echo "  $(basename $rproc): $name - $state"
    fi
done

echo ""
echo "Checking kernel messages for PRU:"
dmesg | grep -i "pru\|remoteproc" | tail -10 || echo "No PRU messages found"

echo ""
echo "=== PRU Firmware Load Complete ==="
