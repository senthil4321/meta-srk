# SHA and Random Number Generator Performance Results

**Date:** October 30, 2025  
**System:** BeagleBone Black (TI AM335x Cortex-A8)  
**Kernel:** Linux 6.6.75-yocto-standard  
**OpenSSL:** 3.3.1 (compiled with NEON optimizations)

---

## SHA Hash Performance

### OpenSSL Speed Test (Software Implementation)

Performance on different block sizes (in KB/s):

| Algorithm | 16 bytes | 64 bytes | 256 bytes | 1024 bytes | 8192 bytes | 16384 bytes |
|-----------|----------|----------|-----------|------------|------------|-------------|
| **SHA-1**   | 4,397 KB/s | 16,043 KB/s | 48,835 KB/s | 100,148 KB/s | **143,305 KB/s** | **147,904 KB/s** |
| **SHA-256** | 3,993 KB/s | 13,182 KB/s | 35,430 KB/s | 61,459 KB/s | **78,213 KB/s** | **80,199 KB/s** |
| **SHA-512** | 2,573 KB/s | 10,249 KB/s | 21,382 KB/s | 34,965 KB/s | **42,697 KB/s** | **43,412 KB/s** |

**Maximum Throughput:**
- **SHA-1:** ~144 MB/s (on 8KB blocks) - ~148 MB/s (on 16KB blocks)
- **SHA-256:** ~76 MB/s (on 8KB blocks) - ~78 MB/s (on 16KB blocks)
- **SHA-512:** ~42 MB/s (on 8KB blocks) - ~42 MB/s (on 16KB blocks)

### Real-World File Hashing Performance

#### Using OpenSSL dgst command:

| File Size | SHA-1 Time | SHA-1 Throughput | SHA-256 Time | SHA-256 Throughput | SHA-512 Time | SHA-512 Throughput |
|-----------|------------|------------------|--------------|---------------------|--------------|---------------------|
| 1 MB      | 0.058s     | ~17.2 MB/s       | 0.063s       | ~15.9 MB/s          | 0.074s       | ~13.5 MB/s          |
| 10 MB     | 0.159s     | ~62.9 MB/s       | 0.218s       | ~45.9 MB/s          | 0.330s       | ~30.3 MB/s          |
| 50 MB     | 0.638s     | ~78.4 MB/s       | 0.909s       | ~55.0 MB/s          | 1.476s       | ~33.9 MB/s          |

#### Using sha256sum command:

| File Size | Time   | Throughput  |
|-----------|--------|-------------|
| 1 MB      | 0.058s | ~17.2 MB/s  |
| 10 MB     | 0.415s | ~24.1 MB/s  |
| 50 MB     | 2.004s | ~25.0 MB/s  |

**Note:** sha256sum shows lower performance than OpenSSL dgst for large files.

---

## Random Number Generator Performance

### Hardware RNG Status
- **Device:** `/dev/hwrng` - **AVAILABLE**
- **Current RNG:** `48310000.rng` (OMAP RNG hardware accelerator)
- **Available RNGs:** `48310000.rng`

### /dev/urandom Performance (Non-blocking, Cryptographically Secure PRNG)

| Data Size | Time    | Throughput   |
|-----------|---------|--------------|
| 1 MB      | 0.065s  | ~15.4 MB/s   |
| 10 MB     | 0.348s  | ~28.7 MB/s   |
| 50 MB     | 2.816s  | ~17.8 MB/s   |

**Average Throughput:** ~20-29 MB/s

### /dev/hwrng Performance (Hardware RNG - True Random)

| Data Size | Time     | Throughput      |
|-----------|----------|-----------------|
| 1 MB      | 1.615s   | ~0.62 MB/s      |
| 5 MB      | 13.931s  | **~0.36 MB/s**  |

**Hardware RNG Throughput:** ~0.36 - 0.62 MB/s (~360-620 KB/s)

**Note:** Hardware RNG is significantly slower but provides true randomness from physical entropy sources. This is expected behavior - it's designed for generating cryptographic keys and seeds, not bulk random data generation.

### OpenSSL Random Number Generation (PRNG)

| Data Size | Time    | Throughput   |
|-----------|---------|--------------|
| 1 MB      | 0.085s  | ~11.8 MB/s   |
| 10 MB     | 0.373s  | ~26.8 MB/s   |
| 50 MB     | 1.660s  | ~30.1 MB/s   |

**Average Throughput:** ~23-30 MB/s

---

## Summary and Analysis

### SHA Hashing Performance

1. **SHA-1 is fastest:** ~78-144 MB/s depending on file size
   - Best for non-cryptographic checksums
   - Not recommended for security applications (deprecated)

2. **SHA-256 is balanced:** ~45-76 MB/s
   - Most commonly used for security
   - Good balance of speed and security
   - Industry standard for digital signatures and certificates

3. **SHA-512 is slower:** ~30-42 MB/s
   - Provides highest security level
   - Better suited for 64-bit systems
   - Slower on 32-bit ARM Cortex-A8

### Random Number Generation

1. **Hardware RNG (`/dev/hwrng`):**
   - **Throughput:** ~0.36-0.62 MB/s
   - **Quality:** True randomness from hardware entropy
   - **Use case:** Generating cryptographic keys, seeds, initialization vectors
   - **Note:** Should be used to seed the system entropy pool, not for bulk data

2. **`/dev/urandom` (CSPRNG):**
   - **Throughput:** ~20-29 MB/s
   - **Quality:** Cryptographically secure pseudo-random
   - **Use case:** General-purpose secure random data
   - **Note:** Uses hardware RNG to seed the entropy pool

3. **OpenSSL RAND:**
   - **Throughput:** ~23-30 MB/s
   - **Quality:** Cryptographically secure pseudo-random
   - **Use case:** Application-level random data generation
   - **Similar performance to /dev/urandom**

### Hardware Acceleration Status

**Current Status:** Software-only implementations with NEON optimizations

**Hardware RNG:** ✅ Working (OMAP hardware RNG active)
- Device: `48310000.rng`
- Provides true random numbers at ~0.36-0.62 MB/s
- Used to seed the kernel entropy pool

**SHA Hardware Acceleration:** ❌ Not Active
- OMAP SHA accelerator drivers not loaded in kernel 6.6
- Using software implementation with ARMv7 NEON optimizations
- Still achieving good performance (78 MB/s for SHA-256)

### Recommendations

1. **For maximum SHA performance on BeagleBone Black:**
   - Use SHA-1 if cryptographic security is not required (~144 MB/s)
   - Use SHA-256 for secure hashing (~78 MB/s)
   - Avoid SHA-512 on 32-bit ARM unless specifically required

2. **For random number generation:**
   - Use `/dev/urandom` for general-purpose random data
   - Use `/dev/hwrng` or `openssl rand` for cryptographic key generation
   - The hardware RNG is already seeding the system entropy pool

3. **Future optimizations:**
   - Investigate enabling OMAP SHA hardware accelerator
   - Consider using ARMv7 NEON-optimized crypto (already partially active)
   - For kernel 6.6, `CONFIG_CRYPTO_AES_TI` might provide better AES performance

---

## System Configuration

- **CPU:** ARM Cortex-A8 (AM335x) @ 1 GHz
- **Compiler Flags:** `-mfpu=neon -mfloat-abi=hard -mcpu=cortex-a8`
- **OpenSSL Capabilities:** NEON optimizations enabled (`OPENSSL_armcap=0x1`)
- **Memory:** 512 MB RAM
- **Available Crypto Algorithms:**
  - Hash: SHA-1, SHA-256, SHA-384, SHA-512, SHA3 variants, Blake2b, MD5
  - Cipher: AES, DES, 3DES
  - RNG: jitterentropy_rng, stdrng (multiple instances), OMAP hardware RNG

---

## Test Environment

- All tests performed on BeagleBone Black booted via NFS
- System under minimal load (load average: 0.82, 0.42, 0.22)
- Memory usage: ~31 MB used / 496 MB total
- No other significant processes running during tests
