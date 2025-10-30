#!/bin/bash

# AES Hardware Accelerator Benchmark Script
# Compares performance of AES operations with and without hardware acceleration

echo "=========================================="
echo "AES Hardware Accelerator Benchmark"
echo "BeagleBone Black (TI AM335x)"
echo "=========================================="
echo ""

BBB_IP="192.168.1.200"
TIMEOUT=30
TEST_SIZE_MB=10

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

print_test() {
    echo -e "${YELLOW}TEST:${NC} $1"
}

print_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
}

# Check if device is reachable
print_info "Checking if BeagleBone Black is reachable at ${BBB_IP}..."
if ! ping -c 2 -W 2 ${BBB_IP} > /dev/null 2>&1; then
    print_fail "Device is not reachable. Please ensure BBB is booted."
    exit 1
fi
print_pass "Device is reachable"
echo ""

# System Information
print_info "System Information:"
echo "=========================================="
CPU_INFO=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "grep -E 'model name|BogoMIPS|Features' /proc/cpuinfo | head -5" 2>/dev/null)
if [ -n "$CPU_INFO" ]; then
    echo "$CPU_INFO"
fi

MEMINFO=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "grep -E 'MemTotal|MemFree|MemAvailable' /proc/meminfo" 2>/dev/null)
if [ -n "$MEMINFO" ]; then
    echo "$MEMINFO"
fi
echo ""

# Check OpenSSL availability
print_info "Checking OpenSSL availability..."
OPENSSL_VERSION=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "openssl version 2>/dev/null" 2>/dev/null)
if [ -n "$OPENSSL_VERSION" ]; then
    print_pass "OpenSSL found: $OPENSSL_VERSION"
else
    print_fail "OpenSSL not found - required for benchmarking"
    echo ""
    echo "Please add 'openssl' and 'openssl-bin' to your image recipe:"
    echo "  IMAGE_INSTALL += \"openssl openssl-bin\""
    exit 1
fi
echo ""

# Display available crypto algorithms
print_info "Available Crypto Algorithms:"
echo "=========================================="
CRYPTO_LIST=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "cat /proc/crypto 2>/dev/null" 2>/dev/null)
if [ -n "$CRYPTO_LIST" ]; then
    # Show AES algorithms
    echo ""
    echo -e "${BLUE}AES Cipher Algorithms:${NC}"
    AES_ALGOS=$(echo "$CRYPTO_LIST" | awk '/^name.*aes/{name=$3} /^driver/{driver=$3} /^module/{module=$3; if(name!="") print "  Name: "name", Driver: "driver", Module: "module; name=""; driver=""; module=""}')
    echo "$AES_ALGOS"
    
    # Check for hardware acceleration
    HW_ACCEL=$(echo "$CRYPTO_LIST" | grep -i "omap")
    if [ -n "$HW_ACCEL" ]; then
        echo ""
        print_pass "Hardware acceleration detected (OMAP):"
        echo "$HW_ACCEL" | grep -E "name|driver|module" | head -10
    else
        echo ""
        print_info "No OMAP hardware accelerator detected - using software implementation"
    fi
    
    # Count total algorithms
    TOTAL_ALGOS=$(echo "$CRYPTO_LIST" | grep -c "^name")
    echo ""
    print_info "Total crypto algorithms available: $TOTAL_ALGOS"
else
    print_fail "Could not retrieve crypto information"
fi
echo ""

# Check loaded kernel modules
print_info "Loaded Crypto Kernel Modules:"
echo "=========================================="
LSMOD_OUTPUT=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "lsmod 2>/dev/null | grep -E 'aes|crypto|omap' || cat /proc/modules 2>/dev/null | grep -E 'aes|crypto|omap' || echo 'Built into kernel'" 2>/dev/null)
echo "$LSMOD_OUTPUT"
echo ""

echo "=========================================="
echo "Part 1: OpenSSL Speed Benchmark"
echo "=========================================="
echo ""

# OpenSSL speed test for different AES modes
print_test "Running OpenSSL speed test for AES-128-CBC..."
AES128_RESULT=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "openssl speed -elapsed -evp aes-128-cbc 2>&1" 2>/dev/null)
if [ -n "$AES128_RESULT" ]; then
    echo "$AES128_RESULT" | grep -E "aes-128 cbc|type|16 bytes|64 bytes|256 bytes|1024 bytes|8192 bytes|16384 bytes"
    
    # Extract key metrics
    THROUGHPUT=$(echo "$AES128_RESULT" | grep "aes-128 cbc" | awk '{print $NF}')
    if [ -n "$THROUGHPUT" ]; then
        print_pass "AES-128-CBC max throughput: ${THROUGHPUT}"
    fi
else
    print_fail "AES-128-CBC benchmark failed"
fi
echo ""

print_test "Running OpenSSL speed test for AES-256-CBC..."
AES256_RESULT=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "openssl speed -elapsed -evp aes-256-cbc 2>&1" 2>/dev/null)
if [ -n "$AES256_RESULT" ]; then
    echo "$AES256_RESULT" | grep -E "aes-256 cbc|type|16 bytes|64 bytes|256 bytes|1024 bytes|8192 bytes|16384 bytes"
    
    # Extract key metrics
    THROUGHPUT=$(echo "$AES256_RESULT" | grep "aes-256 cbc" | awk '{print $NF}')
    if [ -n "$THROUGHPUT" ]; then
        print_pass "AES-256-CBC max throughput: ${THROUGHPUT}"
    fi
else
    print_fail "AES-256-CBC benchmark failed"
fi
echo ""

echo "=========================================="
echo "Part 2: Real-World Encryption Benchmark"
echo "=========================================="
echo ""

# Real-world file encryption test
print_test "Creating ${TEST_SIZE_MB}MB test file..."
CREATE_RESULT=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "dd if=/dev/zero of=/tmp/plaintext.bin bs=1M count=${TEST_SIZE_MB} 2>&1 | tail -1" 2>/dev/null)
if [ -n "$CREATE_RESULT" ]; then
    print_pass "Test file created: ${TEST_SIZE_MB}MB"
    echo "  $CREATE_RESULT"
else
    print_fail "Failed to create test file"
    exit 1
fi
echo ""

# Test AES-128-CBC encryption
print_test "Testing AES-128-CBC encryption (${TEST_SIZE_MB}MB)..."
ENC_START=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "openssl enc -aes-128-cbc -salt -in /tmp/plaintext.bin -out /tmp/encrypted_128.bin -pass pass:testkey123" 2>/dev/null
ENC_END=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
if [ -n "$ENC_START" ] && [ -n "$ENC_END" ]; then
    ENC_TIME=$(echo "$ENC_END - $ENC_START" | bc)
    if [ -n "$ENC_TIME" ] && [ "$(echo "$ENC_TIME > 0" | bc)" -eq 1 ]; then
        THROUGHPUT=$(echo "scale=2; ${TEST_SIZE_MB} / ${ENC_TIME}" | bc)
        print_pass "Encryption time: ${ENC_TIME}s, Throughput: ${THROUGHPUT} MB/s"
    else
        print_fail "Encryption time measurement failed"
    fi
else
    print_fail "Encryption failed"
fi

print_test "Testing AES-128-CBC decryption (${TEST_SIZE_MB}MB)..."
DEC_START=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "openssl enc -d -aes-128-cbc -in /tmp/encrypted_128.bin -out /tmp/decrypted_128.bin -pass pass:testkey123" 2>/dev/null
DEC_END=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
if [ -n "$DEC_START" ] && [ -n "$DEC_END" ]; then
    DEC_TIME=$(echo "$DEC_END - $DEC_START" | bc)
    if [ -n "$DEC_TIME" ] && [ "$(echo "$DEC_TIME > 0" | bc)" -eq 1 ]; then
        THROUGHPUT=$(echo "scale=2; ${TEST_SIZE_MB} / ${DEC_TIME}" | bc)
        print_pass "Decryption time: ${DEC_TIME}s, Throughput: ${THROUGHPUT} MB/s"
    else
        print_fail "Decryption time measurement failed"
    fi
else
    print_fail "Decryption failed"
fi
echo ""

# Test AES-256-CBC encryption
print_test "Testing AES-256-CBC encryption (${TEST_SIZE_MB}MB)..."
ENC_START=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "openssl enc -aes-256-cbc -salt -in /tmp/plaintext.bin -out /tmp/encrypted_256.bin -pass pass:testkey123" 2>/dev/null
ENC_END=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
if [ -n "$ENC_START" ] && [ -n "$ENC_END" ]; then
    ENC_TIME=$(echo "$ENC_END - $ENC_START" | bc)
    if [ -n "$ENC_TIME" ] && [ "$(echo "$ENC_TIME > 0" | bc)" -eq 1 ]; then
        THROUGHPUT=$(echo "scale=2; ${TEST_SIZE_MB} / ${ENC_TIME}" | bc)
        print_pass "Encryption time: ${ENC_TIME}s, Throughput: ${THROUGHPUT} MB/s"
    else
        print_fail "Encryption time measurement failed"
    fi
else
    print_fail "Encryption failed"
fi

print_test "Testing AES-256-CBC decryption (${TEST_SIZE_MB}MB)..."
DEC_START=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "openssl enc -d -aes-256-cbc -in /tmp/encrypted_256.bin -out /tmp/decrypted_256.bin -pass pass:testkey123" 2>/dev/null
DEC_END=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "date +%s.%N" 2>/dev/null)
if [ -n "$DEC_START" ] && [ -n "$DEC_END" ]; then
    DEC_TIME=$(echo "$DEC_END - $DEC_START" | bc)
    if [ -n "$DEC_TIME" ] && [ "$(echo "$DEC_TIME > 0" | bc)" -eq 1 ]; then
        THROUGHPUT=$(echo "scale=2; ${TEST_SIZE_MB} / ${DEC_TIME}" | bc)
        print_pass "Decryption time: ${DEC_TIME}s, Throughput: ${THROUGHPUT} MB/s"
    else
        print_fail "Decryption time measurement failed"
    fi
else
    print_fail "Decryption failed"
fi
echo ""

# Verify data integrity
print_test "Verifying data integrity..."
VERIFY_128=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "cmp /tmp/plaintext.bin /tmp/decrypted_128.bin && echo 'OK' || echo 'FAIL'" 2>/dev/null)
VERIFY_256=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "cmp /tmp/plaintext.bin /tmp/decrypted_256.bin && echo 'OK' || echo 'FAIL'" 2>/dev/null)

if [ "$VERIFY_128" = "OK" ]; then
    print_pass "AES-128-CBC: Data integrity verified"
else
    print_fail "AES-128-CBC: Data integrity check failed"
fi

if [ "$VERIFY_256" = "OK" ]; then
    print_pass "AES-256-CBC: Data integrity verified"
else
    print_fail "AES-256-CBC: Data integrity check failed"
fi
echo ""

# System load during/after encryption
print_test "Checking system load..."
LOAD=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "cat /proc/loadavg" 2>/dev/null)
if [ -n "$LOAD" ]; then
    print_info "Load average: $LOAD"
fi

MEMINFO_AFTER=$(ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "grep -E 'MemFree|MemAvailable' /proc/meminfo" 2>/dev/null)
if [ -n "$MEMINFO_AFTER" ]; then
    print_info "Memory status after tests:"
    echo "$MEMINFO_AFTER"
fi
echo ""

# Cleanup
print_info "Cleaning up test files..."
ssh -o ConnectTimeout=${TIMEOUT} root@${BBB_IP} "rm -f /tmp/plaintext.bin /tmp/encrypted_*.bin /tmp/decrypted_*.bin" 2>/dev/null
print_pass "Cleanup complete"
echo ""

echo "=========================================="
echo "Summary & Analysis"
echo "=========================================="
echo ""
print_info "Hardware Crypto Acceleration Status:"
if echo "$CRYPTO_LIST" | grep -qi "omap.*aes"; then
    echo "  ✓ OMAP hardware AES accelerator is AVAILABLE"
    echo "  ✓ Should provide improved performance vs software-only"
else
    echo "  ℹ Using software AES implementation (aes-generic)"
    echo "  ℹ Hardware acceleration may not be enabled in kernel"
fi
echo ""

print_info "Performance Notes:"
echo "  - BeagleBone Black (AM335x) has hardware crypto acceleration"
echo "  - To enable hardware acceleration, kernel must be configured with:"
echo "    CONFIG_CRYPTO_DEV_OMAP_AES=y or =m"
echo "    CONFIG_CRYPTO_DEV_OMAP_SHAM=y or =m"
echo "  - Hardware accelerator offloads CPU for better performance"
echo "  - Software implementation (aes-generic) is portable but slower"
echo ""

print_info "Typical Performance Comparison:"
echo "  Software AES (aes-generic):"
echo "    - ~5-15 MB/s on ARM Cortex-A8"
echo "    - Higher CPU usage"
echo ""
echo "  Hardware AES (omap-aes):"
echo "    - ~20-40 MB/s on AM335x"
echo "    - Lower CPU usage"
echo "    - Better power efficiency"
echo ""


