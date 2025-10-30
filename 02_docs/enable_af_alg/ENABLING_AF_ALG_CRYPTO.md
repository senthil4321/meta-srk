# Enabling Hardware Crypto via AF_ALG Interface

## Current Status

### Kernel Side: ✅ COMPLETE
The kernel is already configured to support hardware crypto via AF_ALG socket interface:

```
CONFIG_CRYPTO_USER_API=y              # AF_ALG socket interface
CONFIG_CRYPTO_USER_API_HASH=y         # Hash algorithms via AF_ALG
CONFIG_CRYPTO_USER_API_SKCIPHER=y     # Symmetric ciphers via AF_ALG
CONFIG_CRYPTO_USER_API_AEAD=y         # Authenticated encryption via AF_ALG
CONFIG_CRYPTO_USER_API_RNG=y          # RNG via AF_ALG
```

Hardware drivers loaded and active:
- `omap-sha256` - SHA hardware accelerator
- `omap-aes` - AES hardware accelerator  
- `cbc-aes-omap`, `ecb-aes-omap`, `ctr-aes-omap` - AES modes

### User Space Side: 🔄 IN PROGRESS

**Problem**: OpenSSL 3.3.1 only uses software crypto (default provider)
- No hardware acceleration despite kernel support
- Performance gains modest (~1-3%)

**Solution**: Use libkcapi to access kernel crypto API

## What is libkcapi?

`libkcapi` is a user-space library that provides access to the Linux kernel crypto API via the AF_ALG socket interface.

### Features:
- Direct access to kernel crypto (including hardware accelerators)
- No need for /dev/crypto device
- No additional kernel modules needed
- Works with existing kernel CONFIG_CRYPTO_USER_API
- Provides drop-in replacement tools for OpenSSL commands

### Tools Included:
- `kcapi-hasher` - Hash files using kernel crypto (replaces sha256sum)
- `kcapi-enc` - Encrypt/decrypt using kernel crypto
- `kcapi-rng` - Random number generation
- `kcapi-speed` - Benchmark kernel crypto performance

## Changes Made

### 1. Added libkcapi to Image Recipe

**File**: `recipes-srk/images/core-image-tiny-initramfs-srk-2-bash-ssh-key-recipe.bb`

```bitbake
IMAGE_INSTALL = "\
    ...
    openssl \
    openssl-bin \
    libkcapi \        # Added: Kernel crypto API library
"
```

### 2. Enabled libkcapi Apps

**File**: `recipes-crypto/libkcapi/libkcapi_%.bbappend`

```bitbake
# Enable libkcapi apps and hasher for hardware crypto testing
# This enables kcapi-hasher, kcapi-speed, and other tools
PACKAGECONFIG:append = " apps"
```

This enables:
- `kcapi-hasher` - SHA hashing tool
- `kcapi-speed` - Performance benchmarking
- `kcapi-enc` - Encryption/decryption tool
- `kcapi-rng` - Random number generation

## How AF_ALG Works

```
User Application
      ↓
  socket(AF_ALG, SOCK_SEQPACKET, 0)
      ↓
  bind() with algorithm name (e.g., "sha256")
      ↓
  Kernel Crypto API
      ↓
  Checks /proc/crypto for algorithm
      ↓
  Uses hardware driver if available (omap-sha256)
      ↓
  Falls back to software if hardware unavailable
      ↓
  Returns result to user space
```

## Testing After Deployment

### 1. Verify libkcapi Installation
```bash
kcapi-hasher --version
kcapi-speed --help
```

### 2. List Available Kernel Crypto Algorithms
```bash
cat /proc/crypto | grep -E "name|driver" | grep -A 1 sha256
```

Expected output:
```
name         : sha256
driver       : omap-sha256  # Hardware driver!
```

### 3. Test Hardware-Accelerated Hashing
```bash
# Create test file
dd if=/dev/zero of=/tmp/testfile bs=1M count=10

# Hash with libkcapi (uses kernel crypto)
time kcapi-hasher -n sha256 /tmp/testfile

# Compare with OpenSSL (uses software)
time sha256sum /tmp/testfile
```

### 4. Benchmark Performance
```bash
# Benchmark kernel crypto performance
kcapi-speed -c sha256

# Compare with OpenSSL
openssl speed sha256
```

### 5. Test Different Algorithms
```bash
# SHA-1
kcapi-hasher -n sha1 /tmp/testfile

# SHA-512  
kcapi-hasher -n sha512 /tmp/testfile

# AES encryption
echo "test data" | kcapi-enc -e -c "cbc(aes)" -k "0123456789abcdef0123456789abcdef" -i "0123456789abcdef"
```

## Expected Performance Improvement

With hardware acceleration via AF_ALG:

**SHA Performance** (estimated):
- SHA-256: 150-300 MB/s (2-4x improvement over software 78 MB/s)
- SHA-1: 200-400 MB/s (2-3x improvement over software 148 MB/s)

**AES Performance** (estimated):
- AES-128: 100-200 MB/s (hardware accelerated)
- AES-256: 80-150 MB/s (hardware accelerated)

Actual performance depends on:
- Block size (larger blocks = better throughput)
- CPU load
- DMA transfer overhead
- Hardware vs software crossover point

## Comparison: cryptodev vs AF_ALG

### cryptodev-linux (NOT USED)
- ❌ Requires out-of-tree kernel module
- ❌ Provides /dev/crypto device
- ❌ Additional complexity
- ✅ Works with older OpenSSL versions
- ✅ Well-established

### AF_ALG (USING THIS)
- ✅ Built into mainline kernel
- ✅ No additional kernel modules
- ✅ Already enabled in our kernel
- ✅ Direct socket interface
- ✅ Modern approach
- ⚠️  Requires user-space library (libkcapi)

## Integration with OpenSSL

### Option 1: Use libkcapi Tools Directly
```bash
# Instead of: sha256sum file
kcapi-hasher -n sha256 file

# Instead of: openssl enc -aes-256-cbc
kcapi-enc -e -c "cbc(aes)"
```

### Option 2: OpenSSL AF_ALG Engine (Future)
For OpenSSL to automatically use AF_ALG, need:
- OpenSSL AF_ALG engine/provider
- Not currently available in standard OpenSSL 3.x
- Would require custom provider development

### Option 3: Application-Level Integration
Applications can use libkcapi API directly:
```c
#include <kcapi.h>

struct kcapi_handle *handle;
kcapi_md_init(&handle, "sha256", 0);
kcapi_md_update(handle, data, datalen);
kcapi_md_final(handle, digest, digestlen);
kcapi_md_destroy(handle);
```

## Build and Deploy

### 1. Build the Image
```bash
cd /home/srk2cob/project/poky/build
bitbake core-image-tiny-initramfs-srk-2-bash-ssh-key-recipe
```

### 2. Deploy via TFTP
```bash
cd /home/srk2cob/project/poky/meta-srk
./04_copy_zImage.sh -srk -i -v
```

### 3. Test on Device
```bash
ssh root@192.168.1.200
kcapi-hasher --version
kcapi-speed -c sha256
```

## Files Modified

1. **recipes-srk/images/core-image-tiny-initramfs-srk-2-bash-ssh-key-recipe.bb**
   - Added `libkcapi` to IMAGE_INSTALL

2. **recipes-crypto/libkcapi/libkcapi_%.bbappend** (NEW)
   - Enabled apps PACKAGECONFIG

## Documentation References

- **libkcapi Homepage**: https://www.chronox.de/libkcapi/index.html
- **Kernel Crypto API**: Documentation/crypto/userspace-if.rst
- **AF_ALG Interface**: include/linux/if_alg.h

## Summary

This approach enables hardware crypto acceleration by:
1. ✅ Using existing kernel AF_ALG interface (already configured)
2. ✅ Adding libkcapi library (no kernel changes needed)
3. ✅ Providing tools for testing and benchmarking
4. ✅ Keeping system simple (no out-of-tree modules)

Next steps after deployment:
- Test and benchmark with kcapi tools
- Compare performance: software OpenSSL vs hardware AF_ALG
- Document actual performance improvements
- Consider integrating into application code

---
*Configuration: October 30, 2025*
