# TEMPLATECONF - Reproducible Build Configurations

This directory contains template configurations for reproducible Yocto builds without manually editing `local.conf` every time.

## 🚀 Quick Start

### Direct TEMPLATECONF (Recommended)

```bash
# From poky directory
cd /home/srk2cob/project/poky

# NFS Development build
TEMPLATECONF=meta-srk/conf/templates/nfs-dev source oe-init-build-env build-nfs-dev
bitbake core-image-tiny-initramfs-srk-11-bbb-nfs

# Production build  
TEMPLATECONF=meta-srk/conf/templates/production source oe-init-build-env build-production
bitbake core-image-tiny-initramfs-srk-3

# Default build
TEMPLATECONF=meta-srk/conf/templates/default source oe-init-build-env build-default
bitbake core-image-tiny-initramfs-srk-3
```

## 📋 Available Templates

### `default` - Standard Configuration
- **Purpose**: Standard BeagleBone Black tiny configuration
- **Machine**: `beaglebone-yocto-srk-tiny`
- **Features**: Basic embedded Linux setup
- **Use Case**: General development and testing

### `nfs-dev` - NFS Development
- **Purpose**: Rapid development with NFS root filesystem
- **Machine**: `beaglebone-yocto-srk-tiny`
- **Features**: 
  - Debugging tools (GDB, strace, ltrace, tcpdump)
  - SSH server enabled
  - Package management enabled
  - ext4 and tar.bz2 image formats
- **Use Case**: Active development with frequent code changes

### `production` - Production Build
- **Purpose**: Minimal, secure production deployment
- **Machine**: `beaglebone-yocto-srk-tiny`
- **Features**:
  - No debug tools or SSH
  - No package management
  - Minimal init system (mdev-busybox)
  - SquashFS image format
  - Security hardened
- **Use Case**: Final production deployments

## 🏗️ Template Structure

Each template directory contains:
```
templates/[template-name]/
├── local.conf.sample      # Main build configuration
├── bblayers.conf.sample   # Layer configuration
└── conf-summary.txt       # Template identifier
```

## � Benefits

- **Standard Yocto**: Uses official TEMPLATECONF mechanism
- **Reproducible Builds**: Consistent configuration across different environments  
- **No Manual Editing**: No need to modify `local.conf` manually
- **Fresh Environments**: Each build gets clean configuration
- **Parallel Builds**: Multiple build directories with different configs
- **Version Control**: Templates can be versioned in git
- **Team Collaboration**: Shared configurations across team members

## 🛠️ Advanced Usage

### Custom Build Directory Names
```bash
TEMPLATECONF=meta-srk/conf/templates/nfs-dev source oe-init-build-env my-custom-build
```

### Environment Variable Override
```bash
MACHINE=beaglebone-yocto TEMPLATECONF=meta-srk/conf/templates/nfs-dev source oe-init-build-env build-dev
```

### Multiple Parallel Builds
```bash
# Create separate environments for different purposes
TEMPLATECONF=meta-srk/conf/templates/nfs-dev source oe-init-build-env build-dev
TEMPLATECONF=meta-srk/conf/templates/production source oe-init-build-env build-prod
# Now you have two independent build environments!
```

### One-liner Build Commands
```bash
TEMPLATECONF=meta-srk/conf/templates/nfs-dev source oe-init-build-env build-nfs && bitbake core-image-tiny-initramfs-srk-11-bbb-nfs
```

## 🔧 Creating Custom Templates

1. **Create Template Directory**:
   ```bash
   mkdir -p meta-srk/conf/templates/my-template
   ```

2. **Add Configuration Files**:
   ```bash
   # Copy from existing template
   cp meta-srk/conf/templates/default/* meta-srk/conf/templates/my-template/
   
   # Edit configurations  
   nano meta-srk/conf/templates/my-template/local.conf.sample
   ```

3. **Update Description**:
   ```bash
   echo "meta-srk/conf/templates/my-template" > meta-srk/conf/templates/my-template/conf-summary.txt
   ```

4. **Use Your Template**:
   ```bash
   TEMPLATECONF=meta-srk/conf/templates/my-template source oe-init-build-env build-custom
   ```