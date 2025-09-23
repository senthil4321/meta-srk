# SRK Documentation Index

This directory contains documentation for the SRK (Security Research Kernel) project.

## Documentation Files

### Core Documentation

- **[kernel_variants.md](./kernel_variants.md)**: Comprehensive documentation of all kernel variants including base kernel and SELinux-enabled kernel
- **[initramfs_size_optimization.md](./initramfs_size_optimization.md)**: Detailed optimization progress for initramfs size reduction

### Image Composition

- **[srk-3-image-composition.md](./srk-3-image-composition.md)**: Analysis of SRK-3 image composition and dependencies
- **[srk-3-image-composition.svg](./srk-3-image-composition.svg)**: Visual diagram of SRK-3 image composition

### Distribution Features

- **[distro_features_diagram.md](./distro_features_diagram.md)**: Documentation of distribution features and their impact
- **[destro_image_difference.md](./destro_image_difference.md)**: Analysis of distribution and image differences

### Historical

- **[chat_history_2025-09-22.md](./chat_history_2025-09-22.md)**: Development chat history from September 22, 2025

## Quick Start

### Building Kernels

```bash
# Base kernel
bitbake linux-yocto-srk

# SELinux kernel
bitbake linux-yocto-srk-selinux
```

### Building Images

```bash
# Minimal initramfs (no BusyBox)
bitbake core-image-tiny-initramfs-srk-9-nobusybox

# SELinux-enabled initramfs
bitbake core-image-tiny-initramfs-srk-10-selinux
```

### Deployment

```bash
# Copy initramfs
./03_copy_initramfs.sh 10

# Copy kernel
./04_copy_zImage.sh
```

## Key Features

- **Minimal Initramfs**: Reduced from 14MB to ~88B compressed through iterative optimization
- **SELinux Support**: Full SELinux integration with custom kernel and userspace
- **Security Research**: Tools and configurations for security experimentation
- **Yocto Integration**: Standard Yocto Project workflows and tooling

## Architecture

The SRK project provides:

1. **Custom Kernels**: Base and SELinux variants based on Linux 6.6 LTS
2. **Minimal Images**: Highly optimized initramfs images for different use cases
3. **Security Tools**: SELinux policy and management tools
4. **Deployment Scripts**: Automated deployment to target devices

For detailed information, see the individual documentation files linked above.