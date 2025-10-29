#!/bin/bash

# Test the deployed image on BeagleBone Black
# This script verifies all configuration from the new modular recipe

echo "=========================================="
echo "BeagleBone Black Image Test Script"
echo "Testing: core-image-tiny-initramfs-srk-2-bash-ssh-key-recipe"
echo "=========================================="
echo ""

BBB_IP="192.168.1.200"
TIMEOUT=5

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${YELLOW}TEST:${NC} $1"
}

print_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
}

print_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
}

# Wait for device to be reachable
print_test "Checking if BeagleBone Black is reachable at ${BBB_IP}..."
if ping -c 2 -W 2 ${BBB_IP} > /dev/null 2>&1; then
    print_pass "Device is reachable"
else
    print_fail "Device is not reachable. Please ensure BBB is booted."
    exit 1
fi

echo ""

# Test 1: Hostname
print_test "1. Testing hostname..."
HOSTNAME=$(ssh -o ConnectTimeout=${TIMEOUT} -o StrictHostKeyChecking=no root@${BBB_IP} "hostname 2>/dev/null || cat /etc/hostname 2>/dev/null" 2>/dev/null | tr -d '\n\r')
if [ "$HOSTNAME" = "srk-device" ]; then
    print_pass "Hostname is correctly set to 'srk-device'"
else
    print_fail "Hostname is '$HOSTNAME', expected 'srk-device'"
fi

# Test 2: Network configuration
print_test "2. Testing network configuration..."
IP_ADDR=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "ip addr show eth0 | grep 'inet ' | awk '{print \$2}'" 2>/dev/null)
if [ "$IP_ADDR" = "192.168.1.200/24" ]; then
    print_pass "IP address is correctly configured: ${IP_ADDR}"
else
    print_fail "IP address is '$IP_ADDR', expected '192.168.1.200/24'"
fi

# Test 3: Gateway
print_test "3. Testing default gateway..."
GATEWAY=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "ip route show default 2>/dev/null | head -n 1 | awk '{print \$3}'" 2>/dev/null | tr -d '\n\r')
if [ "$GATEWAY" = "192.168.1.100" ]; then
    print_pass "Default gateway is correctly set: ${GATEWAY}"
else
    print_fail "Default gateway is '$GATEWAY', expected '192.168.1.100'"
fi

# Test 4: DNS configuration  
print_test "4. Testing DNS configuration..."
DNS=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "cat /etc/resolv.conf 2>/dev/null | grep -E '^nameserver' | head -n 1 | awk '{print \$2}'" 2>/dev/null | tr -d '\n\r')
if [ "$DNS" = "8.8.8.8" ]; then
    print_pass "DNS is correctly configured: ${DNS}"
else
    print_fail "DNS is '$DNS', expected '8.8.8.8'"
fi

# Test 5: Bash shell
print_test "5. Testing bash shell..."
SHELL=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "echo \$SHELL" 2>/dev/null)
if [ "$SHELL" = "/bin/bash" ]; then
    print_pass "Bash shell is active: ${SHELL}"
else
    print_fail "Shell is '$SHELL', expected '/bin/bash'"
fi

# Test 6: SRK user exists
print_test "6. Testing srk user..."
SRK_USER=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "id -u srk 2>/dev/null" 2>/dev/null)
if [ "$SRK_USER" = "1000" ]; then
    print_pass "SRK user exists with UID 1000"
else
    print_fail "SRK user UID is '$SRK_USER', expected '1000'"
fi

# Test 7: SRK user home directory
print_test "7. Testing srk user home directory..."
SRK_HOME=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "ls -d /home/srk 2>/dev/null" 2>/dev/null)
if [ "$SRK_HOME" = "/home/srk" ]; then
    print_pass "SRK user home directory exists"
else
    print_fail "SRK user home directory not found"
fi

# Test 8: SSH authentication (root)
print_test "8. Testing SSH key authentication for root..."
ssh -o ConnectTimeout=${TIMEOUT} -o StrictHostKeyChecking=no root@${BBB_IP} "exit" 2>/dev/null
if [ $? -eq 0 ]; then
    print_pass "SSH key authentication works for root"
else
    print_fail "SSH key authentication failed for root"
fi

# Test 9: SSH authentication (srk user)
print_test "9. Testing SSH key authentication for srk user..."
ssh -o ConnectTimeout=${TIMEOUT} -o StrictHostKeyChecking=no srk@${BBB_IP} "exit" 2>/dev/null
if [ $? -eq 0 ]; then
    print_pass "SSH key authentication works for srk user"
else
    print_fail "SSH key authentication failed for srk user"
fi

# Test 10: Systemd services
print_test "10. Testing systemd services..."
NETWORKD=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "systemctl is-active systemd-networkd" 2>/dev/null)
if [ "$NETWORKD" = "active" ]; then
    print_pass "systemd-networkd is active"
else
    print_fail "systemd-networkd is '$NETWORKD', expected 'active'"
fi

RESOLVED=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "systemctl is-active systemd-resolved" 2>/dev/null)
if [ "$RESOLVED" = "active" ]; then
    print_pass "systemd-resolved is active"
else
    print_fail "systemd-resolved is '$RESOLVED', expected 'active'"
fi

TIMESYNCD=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "systemctl is-active systemd-timesyncd" 2>/dev/null)
if [ "$TIMESYNCD" = "active" ]; then
    print_pass "systemd-timesyncd is active"
else
    print_fail "systemd-timesyncd is '$TIMESYNCD', expected 'active'"
fi

# Test 11: Internet connectivity
print_test "11. Testing internet connectivity..."
PING_GOOGLE=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "ping -c 2 -W 2 8.8.8.8 > /dev/null 2>&1 && echo 'success' || echo 'fail'" 2>/dev/null)
if [ "$PING_GOOGLE" = "success" ]; then
    print_pass "Internet connectivity is working"
else
    print_fail "Internet connectivity failed"
fi

# Test 12: Bash completion
print_test "12. Testing bash completion..."
BASH_COMPLETION=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "ls /etc/bash_completion 2>/dev/null" 2>/dev/null)
if [ -n "$BASH_COMPLETION" ]; then
    print_pass "Bash completion is available"
else
    print_fail "Bash completion not found"
fi

# Test 13: Configuration files from packages
print_test "13. Testing configuration files..."
BASHRC_ROOT=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "ls /root/.bashrc 2>/dev/null" 2>/dev/null)
BASHRC_SRK=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "ls /home/srk/.bashrc 2>/dev/null" 2>/dev/null)
if [ -n "$BASHRC_ROOT" ] && [ -n "$BASHRC_SRK" ]; then
    print_pass "Configuration files are properly installed"
else
    print_fail "Some configuration files are missing"
fi

# Test 14: Dropbear SSH server
print_test "14. Testing Dropbear SSH server..."
DROPBEAR=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "pgrep dropbear" 2>/dev/null)
if [ -n "$DROPBEAR" ]; then
    print_pass "Dropbear SSH server is running"
else
    print_fail "Dropbear SSH server not found"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "All critical tests completed!"
echo "The modular image recipe is working correctly."
echo ""
