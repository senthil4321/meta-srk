#!/bin/sh

# BBB EEPROM Setup Script
# Instantiate the BBB EEPROM device on I2C bus 0

echo "Setting up BBB EEPROM device..."

# Check if I2C bus exists
if [ ! -d /sys/bus/i2c/devices/i2c-0 ]; then
    echo "Error: I2C bus 0 not found"
    exit 1
fi

echo "I2C bus 0 found"

# Try to load AT24 module if not already loaded
if ! lsmod | grep -q at24; then
    echo "Loading AT24 EEPROM module..."
    modprobe at24 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Warning: Could not load at24 module"
    else
        echo "AT24 module loaded"
    fi
else
    echo "AT24 module already loaded"
fi

# Wait for I2C bus to be ready
sleep 1

# Check if EEPROM device already exists
if [ -e /sys/bus/i2c/devices/0-0050/eeprom ]; then
    echo "EEPROM device already exists at /sys/bus/i2c/devices/0-0050/eeprom"
    exit 0
fi

echo "Instantiating AT24 EEPROM at address 0x50 on I2C bus 0..."
# Instantiate AT24 EEPROM at address 0x50 on I2C bus 0
# Format: echo <driver> <address> > /sys/bus/i2c/devices/i2c-0/new_device
echo "at24 0x50" > /sys/bus/i2c/devices/i2c-0/new_device 2>/dev/null

if [ $? -eq 0 ]; then
    echo "BBB EEPROM device instantiation command succeeded"
    # Wait a moment for the device to be created
    sleep 1
    if [ -e /sys/bus/i2c/devices/0-0050/eeprom ]; then
        echo "EEPROM device successfully created at /sys/bus/i2c/devices/0-0050/eeprom"
    else
        echo "Warning: EEPROM device instantiation reported success but device file not found"
        echo "Checking what devices exist on I2C bus 0..."
        ls -la /sys/bus/i2c/devices/0-* 2>/dev/null || echo "No I2C devices found"
    fi
else
    echo "Failed to instantiate BBB EEPROM device"
    echo "I2C bus may not be available or AT24 module not loaded"
    echo "Checking I2C bus status..."
    ls -la /sys/bus/i2c/devices/i2c-0/ 2>/dev/null || echo "I2C bus 0 not accessible"
fi