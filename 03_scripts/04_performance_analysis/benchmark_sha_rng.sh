#!/bin/bash

echo "========================================="
echo "SHA and RNG Hardware vs Software Benchmark"
echo "BeagleBone Black (TI AM335x)"
echo "========================================="
echo "Date: $(date)"
echo "Kernel: $(uname -r)"
echo "========================================="
echo ""

# Results storage
declare -A RESULTS_SHA

# Part 0: Check Hardware Availability
echo "=== Part 0: Hardware Crypto Detection ==="
echo ""
echo "Checking for OMAP hardware crypto drivers..."
HW_SHA=$(cat /proc/crypto | grep -E '^(name|driver|priority)' | grep -B 2 -A 1 'omap.*sha')
if [ -n "$HW_SHA" ]; then
    echo "✓ OMAP hardware SHA accelerator detected:"
    echo "$HW_SHA"
    HW_AVAILABLE=true
else
    echo "ℹ No OMAP hardware SHA detected - using software only"
    HW_AVAILABLE=false
fi
echo ""

echo "Current SHA algorithm priorities:"
cat /proc/crypto | grep -E '^(name|driver|priority)' | grep -A 2 'name.*sha' | head -30
echo ""

# Part 1: SHA Performance Testing with OpenSSL
echo "=== Part 1: OpenSSL SHA Speed Tests (Hardware if available) ==="
echo ""
echo "Testing SHA-1, SHA-256, and SHA-512 algorithms..."
echo "Note: OpenSSL automatically uses highest priority algorithm"
echo ""

# SHA-1 performance
echo "--- SHA-1 Performance ---"
SHA1_RESULT=$(openssl speed -elapsed sha1 2>&1)
echo "$SHA1_RESULT" | grep -E 'type|sha1'
SHA1_SPEED=$(echo "$SHA1_RESULT" | grep '^sha1' | awk '{print $(NF-1)}')
if [ -n "$SHA1_SPEED" ]; then
    RESULTS_SHA["SHA1"]="$SHA1_SPEED"
    echo "SHA-1 throughput: ${SHA1_SPEED} KB/s"
fi
echo ""

# SHA-256 performance
echo "--- SHA-256 Performance ---"
SHA256_RESULT=$(openssl speed -elapsed sha256 2>&1)
echo "$SHA256_RESULT" | grep -E 'type|sha256'
SHA256_SPEED=$(echo "$SHA256_RESULT" | grep '^sha256' | awk '{print $(NF-1)}')
if [ -n "$SHA256_SPEED" ]; then
    RESULTS_SHA["SHA256"]="$SHA256_SPEED"
    echo "SHA-256 throughput: ${SHA256_SPEED} KB/s"
fi
echo ""

# SHA-512 performance
echo "--- SHA-512 Performance ---"
SHA512_RESULT=$(openssl speed -elapsed sha512 2>&1)
echo "$SHA512_RESULT" | grep -E 'type|sha512'
SHA512_SPEED=$(echo "$SHA512_RESULT" | grep '^sha512' | awk '{print $(NF-1)}')
if [ -n "$SHA512_SPEED" ]; then
    RESULTS_SHA["SHA512"]="$SHA512_SPEED"
    echo "SHA-512 throughput: ${SHA512_SPEED} KB/s"
fi
echo ""

# Part 2: Real-world SHA testing with file hashing
echo "=== Part 2: Real-world File Hashing Performance ==="
echo ""

# Create test files of different sizes
echo "Creating test files..."
dd if=/dev/urandom of=/tmp/test_1mb.bin bs=1M count=1 2>/dev/null
dd if=/dev/urandom of=/tmp/test_10mb.bin bs=1M count=10 2>/dev/null
dd if=/dev/urandom of=/tmp/test_50mb.bin bs=1M count=50 2>/dev/null
echo "Test files created: 1MB, 10MB, 50MB"
echo ""

# Test SHA-1 on different file sizes
echo "--- SHA-1 File Hashing Performance ---"
sizes="1 10 50"
for sz in $sizes; do
    file="/tmp/test_${sz}mb.bin"
    echo "Hashing ${sz}MB file with SHA-1..."
    start=$(date +%s.%N)
    sha1sum $file > /dev/null
    end=$(date +%s.%N)
    elapsed=$(echo "$end - $start" | bc)
    throughput=$(echo "scale=2; $sz / $elapsed" | bc)
    echo "  Time: ${elapsed}s, Throughput: ${throughput} MB/s"
    if [ "$sz" = "10" ]; then
        RESULTS_SHA["SHA1_FILE_10MB"]="$throughput"
    fi
done
echo ""

# Test SHA-256 on different file sizes
echo "--- SHA-256 File Hashing Performance ---"
for sz in $sizes; do
    file="/tmp/test_${sz}mb.bin"
    echo "Hashing ${sz}MB file with SHA-256..."
    start=$(date +%s.%N)
    sha256sum $file > /dev/null
    end=$(date +%s.%N)
    elapsed=$(echo "$end - $start" | bc)
    throughput=$(echo "scale=2; $sz / $elapsed" | bc)
    echo "  Time: ${elapsed}s, Throughput: ${throughput} MB/s"
    if [ "$sz" = "10" ]; then
        RESULTS_SHA["SHA256_FILE_10MB"]="$throughput"
    fi
done
echo ""

# Test SHA-512 on different file sizes
echo "--- SHA-512 File Hashing Performance ---"
for sz in $sizes; do
    file="/tmp/test_${sz}mb.bin"
    echo "Hashing ${sz}MB file with SHA-512..."
    start=$(date +%s.%N)
    sha512sum $file > /dev/null
    end=$(date +%s.%N)
    elapsed=$(echo "$end - $start" | bc)
    throughput=$(echo "scale=2; $sz / $elapsed" | bc)
    echo "  Time: ${elapsed}s, Throughput: ${throughput} MB/s"
    if [ "$sz" = "10" ]; then
        RESULTS_SHA["SHA512_FILE_10MB"]="$throughput"
    fi
done
echo ""

# Part 3: Random Number Generator Testing
echo "=== Part 3: Random Number Generator Performance ==="
echo ""

# Check hardware RNG availability
echo "--- Hardware RNG Status ---"
if [ -c /dev/hwrng ]; then
    echo "✓ Hardware RNG device: AVAILABLE (/dev/hwrng)"
    ls -l /dev/hwrng
    HW_RNG_AVAILABLE=true
else
    echo "ℹ Hardware RNG device: NOT AVAILABLE"
    HW_RNG_AVAILABLE=false
fi
echo ""

# Check which RNG is being used
echo "--- Active RNG Information ---"
if [ -f /sys/class/misc/hw_random/rng_available ]; then
    echo "Available RNG: $(cat /sys/class/misc/hw_random/rng_available)"
fi
if [ -f /sys/class/misc/hw_random/rng_current ]; then
    echo "Current RNG: $(cat /sys/class/misc/hw_random/rng_current)"
fi
echo ""

# Test /dev/urandom performance (uses software PRNG or hardware if available)
echo "--- /dev/urandom Performance ---"
for size in 1 10 50; do
    echo "Generating ${size}MB of random data from /dev/urandom..."
    start=$(date +%s.%N)
    dd if=/dev/urandom of=/tmp/urandom_${size}mb.bin bs=1M count=$size 2>&1 | grep -v records
    end=$(date +%s.%N)
    elapsed=$(echo "$end - $start" | bc)
    throughput=$(echo "scale=2; $size / $elapsed" | bc)
    echo "  Time: ${elapsed}s, Throughput: ${throughput} MB/s"
    if [ "$size" = "10" ]; then
        RESULTS_SHA["URANDOM_10MB"]="$throughput"
    fi
done
echo ""

# Test hardware RNG directly if available
if [ "$HW_RNG_AVAILABLE" = true ]; then
    echo "--- /dev/hwrng Performance (Hardware RNG) ---"
    for size in 1 10; do
        echo "Generating ${size}MB of random data from /dev/hwrng..."
        start=$(date +%s.%N)
        dd if=/dev/hwrng of=/tmp/hwrng_${size}mb.bin bs=1M count=$size 2>&1 | grep -v records
        end=$(date +%s.%N)
        elapsed=$(echo "$end - $start" | bc)
        throughput=$(echo "scale=2; $size / $elapsed" | bc)
        echo "  Time: ${elapsed}s, Throughput: ${throughput} MB/s"
        if [ "$size" = "10" ]; then
            RESULTS_SHA["HWRNG_10MB"]="$throughput"
        fi
    done
    echo ""
fi

# Part 4: OpenSSL Random Number Generation
echo "=== Part 4: OpenSSL Random Number Generation ==="
echo ""
echo "Testing OpenSSL pseudo-random number generation..."
start=$(date +%s.%N)
openssl rand -out /tmp/openssl_random_10mb.bin $((10*1024*1024)) 2>&1
end=$(date +%s.%N)
elapsed=$(echo "$end - $start" | bc)
throughput=$(echo "scale=2; 10 / $elapsed" | bc)
echo "Generated 10MB of random data using OpenSSL"
echo "Time: ${elapsed}s, Throughput: ${throughput} MB/s"
RESULTS_SHA["OPENSSL_RAND"]="$throughput"
echo ""

# Part 5: System Information and Performance Summary
echo "=== Part 5: Performance Summary ==="
echo ""

echo "========================================="
echo "SHA Algorithm Performance (OpenSSL speed)"
echo "========================================="
if [ -n "${RESULTS_SHA[SHA1]}" ]; then
    SHA1_KBPS="${RESULTS_SHA[SHA1]}"
    # Remove the 'k' suffix if present
    SHA1_NUM=$(echo "$SHA1_KBPS" | sed 's/k$//')
    SHA1_MBS=$(echo "scale=2; $SHA1_NUM / 1024" | bc)
    echo "SHA-1:   ${SHA1_KBPS} KB/s (~${SHA1_MBS} MB/s)"
fi
if [ -n "${RESULTS_SHA[SHA256]}" ]; then
    SHA256_KBPS="${RESULTS_SHA[SHA256]}"
    SHA256_NUM=$(echo "$SHA256_KBPS" | sed 's/k$//')
    SHA256_MBS=$(echo "scale=2; $SHA256_NUM / 1024" | bc)
    echo "SHA-256: ${SHA256_KBPS} KB/s (~${SHA256_MBS} MB/s)"
fi
if [ -n "${RESULTS_SHA[SHA512]}" ]; then
    SHA512_KBPS="${RESULTS_SHA[SHA512]}"
    SHA512_NUM=$(echo "$SHA512_KBPS" | sed 's/k$//')
    SHA512_MBS=$(echo "scale=2; $SHA512_NUM / 1024" | bc)
    echo "SHA-512: ${SHA512_KBPS} KB/s (~${SHA512_MBS} MB/s)"
fi
echo ""

echo "========================================="
echo "Real-World File Hashing (10MB files)"
echo "========================================="
if [ -n "${RESULTS_SHA[SHA1_FILE_10MB]}" ]; then
    echo "SHA-1:   ${RESULTS_SHA[SHA1_FILE_10MB]} MB/s"
fi
if [ -n "${RESULTS_SHA[SHA256_FILE_10MB]}" ]; then
    echo "SHA-256: ${RESULTS_SHA[SHA256_FILE_10MB]} MB/s"
fi
if [ -n "${RESULTS_SHA[SHA512_FILE_10MB]}" ]; then
    echo "SHA-512: ${RESULTS_SHA[SHA512_FILE_10MB]} MB/s"
fi
echo ""

echo "========================================="
echo "Random Number Generation (10MB)"
echo "========================================="
if [ -n "${RESULTS_SHA[URANDOM_10MB]}" ]; then
    echo "/dev/urandom:  ${RESULTS_SHA[URANDOM_10MB]} MB/s"
fi
if [ -n "${RESULTS_SHA[HWRNG_10MB]}" ]; then
    echo "/dev/hwrng:    ${RESULTS_SHA[HWRNG_10MB]} MB/s (hardware)"
fi
if [ -n "${RESULTS_SHA[OPENSSL_RAND]}" ]; then
    echo "OpenSSL rand:  ${RESULTS_SHA[OPENSSL_RAND]} MB/s"
fi
echo ""

echo "========================================="
echo "Hardware Acceleration Status"
echo "========================================="
if [ "$HW_AVAILABLE" = true ]; then
    echo "✓ OMAP hardware SHA accelerator is ACTIVE"
    echo "  Priority: 400 (hardware) vs 100 (software)"
    echo "  Drivers: omap-sha1, omap-sha256, omap-sha224, omap-md5"
else
    echo "ℹ Using software SHA implementation only"
    echo "  To enable: CONFIG_CRYPTO_DEV_OMAP_SHAM=y"
fi
echo ""

if [ "$HW_RNG_AVAILABLE" = true ]; then
    echo "✓ Hardware RNG (TRNG) is ACTIVE"
    echo "  Device: /dev/hwrng"
    echo "  Driver: omap_rng"
else
    echo "ℹ No hardware RNG detected"
    echo "  Using software PRNG only"
fi
echo ""

echo "========================================="
echo "System Information"
echo "========================================="
echo ""
echo "--- CPU Load ---"
cat /proc/loadavg
echo ""
echo "--- Memory Usage ---"
free -m
echo ""
echo "--- Top Crypto Algorithms (by priority) ---"
cat /proc/crypto | grep -E '^(name|driver|priority)' | grep -B 1 -A 1 'priority' | grep -E 'name|priority' | paste - - | sort -t: -k2 -rn | head -15
echo ""

# Cleanup
echo "Cleaning up temporary files..."
rm -f /tmp/test_*.bin /tmp/random_*.bin /tmp/urandom_*.bin /tmp/hwrng_*.bin /tmp/openssl_random_*.bin
echo ""

echo "========================================="
echo "Benchmark Complete!"
echo "========================================="
