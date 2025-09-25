#!/bin/sh

# BBB EEPROM Setup Script
# Instantiate the BBB EEPROM device on I2C bus 0

echo "Setting up BBB EEPROM device..."

# Wait for I2C bus to be ready
sleep 1

# Instantiate AT24 EEPROM at address 0x50 on I2C bus 0
# Format: echo <driver> <address> > /sys/bus/i2c/devices/i2c-0/new_device
echo "at24 0x50" > /sys/bus/i2c/devices/i2c-0/new_device 2>/dev/null

if [ $? -eq 0 ]; then
    echo "BBB EEPROM device instantiated successfully"
    # Wait a moment for the device to be created
    sleep 1
    if [ -e /sys/bus/i2c/devices/0-0050/eeprom ]; then
        echo "EEPROM device available at /sys/bus/i2c/devices/0-0050/eeprom"
    else
        echo "Warning: EEPROM device file not found after instantiation"
    fi
else
    echo "Failed to instantiate BBB EEPROM device"
    echo "I2C bus may not be available or AT24 module not loaded"
fi