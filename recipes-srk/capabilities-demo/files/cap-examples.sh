#!/bin/bash
#
# Linux Capabilities Examples Script
# Demonstrates how to use setcap/getcap with the cap-demo program
#

PROGRAM="/usr/bin/cap-demo"

echo "=========================================="
echo "  Linux Capabilities Examples"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Note: Some examples require root privileges"
    echo "Run with: sudo $0"
    echo ""
fi

echo "1. Show current program capabilities:"
echo "   $ getcap $PROGRAM"
getcap $PROGRAM
echo ""

echo "2. Run cap-demo without special capabilities:"
echo "   $ cap-demo show"
$PROGRAM show
echo ""

echo "3. Run cap-demo and list effective capabilities:"
echo "   $ cap-demo list"
$PROGRAM list
echo ""

echo "4. Test network capabilities:"
echo "   $ cap-demo test-net"
$PROGRAM test-net
echo ""

echo "5. Test system time capability:"
echo "   $ cap-demo test-time"
$PROGRAM test-time
echo ""

if [ "$EUID" -eq 0 ]; then
    echo "=========================================="
    echo "  Root-only examples (setting capabilities)"
    echo "=========================================="
    echo ""
    
    # Remove any existing capabilities first
    echo "Removing existing capabilities..."
    setcap -r $PROGRAM 2>/dev/null
    
    echo "6. Grant network capabilities (CAP_NET_RAW, CAP_NET_ADMIN):"
    echo "   $ sudo setcap cap_net_raw,cap_net_admin=ep $PROGRAM"
    setcap cap_net_raw,cap_net_admin=ep $PROGRAM
    
    echo "   $ getcap $PROGRAM"
    getcap $PROGRAM
    
    echo "   $ cap-demo test-net"
    $PROGRAM test-net
    echo ""
    
    echo "7. Grant system time capability (CAP_SYS_TIME):"
    echo "   $ sudo setcap cap_sys_time=ep $PROGRAM"
    setcap cap_sys_time=ep $PROGRAM
    
    echo "   $ getcap $PROGRAM"
    getcap $PROGRAM
    
    echo "   $ cap-demo test-time"
    $PROGRAM test-time
    echo ""
    
    echo "8. Remove all capabilities:"
    echo "   $ sudo setcap -r $PROGRAM"
    setcap -r $PROGRAM
    
    echo "   $ getcap $PROGRAM"
    getcap $PROGRAM
    echo ""
else
    echo "=========================================="
    echo "  To set capabilities, run as root:"
    echo "=========================================="
    echo ""
    echo "sudo setcap cap_net_raw,cap_net_admin=ep $PROGRAM"
    echo "sudo setcap cap_sys_time=ep $PROGRAM"
    echo "sudo setcap -r $PROGRAM  # Remove capabilities"
    echo ""
fi

echo "=========================================="
echo "  Capability Format:"
echo "=========================================="
echo "  cap_name=set"
echo "  where set can be:"
echo "    e = effective"
echo "    p = permitted"
echo "    i = inheritable"
echo ""
echo "  Common capabilities:"
echo "    CAP_NET_RAW        - Raw sockets (ping, tcpdump)"
echo "    CAP_NET_ADMIN      - Network administration"
echo "    CAP_NET_BIND_SERVICE - Bind to ports < 1024"
echo "    CAP_SYS_TIME       - Set system time"
echo "    CAP_DAC_OVERRIDE   - Bypass file permissions"
echo "    CAP_CHOWN          - Change file ownership"
echo "    CAP_SETUID         - Set user ID"
echo "    CAP_SETGID         - Set group ID"
echo "=========================================="
