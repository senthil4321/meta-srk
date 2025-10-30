#!/bin/sh

echo "========================================="
echo "SHA and RNG Performance Benchmark"
echo "========================================="
echo "Date: $(date)"
echo "Kernel: $(uname -r)"
echo "========================================="
echo ""

# Part 1: SHA Performance Testing with OpenSSL
echo "=== Part 1: OpenSSL SHA Performance Tests ==="
echo ""
echo "Testing SHA-1, SHA-256, and SHA-512 algorithms..."
echo ""

# SHA-1 performance
echo "--- SHA-1 Performance ---"
openssl speed sha1 2>&1 | grep -E 'type|sha1'
echo ""

# SHA-256 performance
echo "--- SHA-256 Performance ---"
openssl speed sha256 2>&1 | grep -E 'type|sha256'
echo ""

# SHA-512 performance
echo "--- SHA-512 Performance ---"
openssl speed sha512 2>&1 | grep -E 'type|sha512'
echo ""

# Part 2: Real-world SHA testing with file hashing
echo "=== Part 2: Real-world File Hashing Performance ==="
echo ""

# Create test files of different sizes
echo "Creating test files..."
dd if=/dev/zero of=/tmp/test_1mb.bin bs=1M count=1 2>/dev/null
dd if=/dev/zero of=/tmp/test_10mb.bin bs=1M count=10 2>/dev/null
dd if=/dev/zero of=/tmp/test_50mb.bin bs=1M count=50 2>/dev/null
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
    # Calculate elapsed time (end - start)
    elapsed=$(awk "BEGIN {printf \"%.3f\", $end - $start}")
    echo "  Time: ${elapsed}s"
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
    elapsed=$(awk "BEGIN {printf \"%.3f\", $end - $start}")
    echo "  Time: ${elapsed}s"
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
    elapsed=$(awk "BEGIN {printf \"%.3f\", $end - $start}")
    echo "  Time: ${elapsed}s"
done
echo ""

# Part 3: Random Number Generator Testing
echo "=== Part 3: Random Number Generator Performance ==="
echo ""

# Check hardware RNG availability
echo "--- Hardware RNG Status ---"
if [ -c /dev/hwrng ]; then
    echo "Hardware RNG device: AVAILABLE (/dev/hwrng)"
    ls -l /dev/hwrng
else
    echo "Hardware RNG device: NOT AVAILABLE"
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

# Test /dev/random performance
echo "--- /dev/random Performance (Blocking) ---"
echo "Generating 1MB of random data from /dev/random..."
start=$(date +%s.%N)
dd if=/dev/random of=/tmp/random_1mb.bin bs=1M count=1 2>&1 | grep -v records
end=$(date +%s.%N)
elapsed=$(awk "BEGIN {printf \"%.3f\", $end - $start}")
echo "Time: ${elapsed}s"
echo ""

# Test /dev/urandom performance
echo "--- /dev/urandom Performance (Non-blocking) ---"
for size in 1 10 50; do
    echo "Generating ${size}MB of random data from /dev/urandom..."
    start=$(date +%s.%N)
    dd if=/dev/urandom of=/tmp/urandom_${size}mb.bin bs=1M count=$size 2>&1 | grep -v records
    end=$(date +%s.%N)
    elapsed=$(awk "BEGIN {printf \"%.3f\", $end - $start}")
    echo "  Time: ${elapsed}s"
done
echo ""

# Test hardware RNG directly if available
if [ -c /dev/hwrng ]; then
    echo "--- /dev/hwrng Performance (Hardware RNG) ---"
    for size in 1 10; do
        echo "Generating ${size}MB of random data from /dev/hwrng..."
        start=$(date +%s.%N)
        dd if=/dev/hwrng of=/tmp/hwrng_${size}mb.bin bs=1M count=$size 2>&1 | grep -v records
        end=$(date +%s.%N)
        elapsed=$(awk "BEGIN {printf \"%.3f\", $end - $start}")
        echo "  Time: ${elapsed}s"
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
elapsed=$(awk "BEGIN {printf \"%.3f\", $end - $start}")
echo "Generated 10MB of random data using OpenSSL"
echo "Time: ${elapsed}s"
echo ""

# Part 5: System Information
echo "=== Part 5: System Information ==="
echo ""
echo "--- CPU Load ---"
uptime
echo ""
echo "--- Memory Usage ---"
free -m
echo ""
echo "--- Available Crypto Algorithms ---"
cat /proc/crypto | grep 'name' | head -n 30
echo ""

# Cleanup
echo "Cleaning up temporary files..."
rm -f /tmp/test_*.bin /tmp/random_*.bin /tmp/urandom_*.bin /tmp/hwrng_*.bin /tmp/openssl_random_*.bin
echo ""

echo "========================================="
echo "Benchmark Complete!"
echo "========================================="
