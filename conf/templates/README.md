# TEMPLATECONF - Reproducible Build Configurations

This directory contains template configurations for reproducible Yocto builds without manually editing `local.conf` every time.

## 🚀 Quick Start

### Using Templates

```bash
# From meta-srk directory
./template-config.sh list        # Show available templates
./template-config.sh nfs-dev     # Apply NFS development template
./template-config.sh production  # Apply production template
./template-config.sh current     # Show current template
```

### Building with Templates

```bash
# 1. Apply desired template
./template-config.sh nfs-dev

# 2. Enter build environment
cd build
source ../oe-init-build-env

# 3. Build your image
bitbake core-image-tiny-initramfs-srk-11-bbb-nfs
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

## 🔄 How It Works

1. **Template Storage**: Templates are stored in `meta-srk/conf/templates/`
2. **Automatic Backup**: Current configuration is backed up before switching
3. **Copy Operation**: Template files are copied to `build/conf/`
4. **Tracking**: Current template is tracked in `conf-summary.txt`

## 📁 Directory Structure

```
meta-srk/
├── .templateconf                    # Points to default template
├── template-config.sh               # Template management script
├── conf/templates/
│   ├── default/                     # Standard configuration
│   │   ├── local.conf.sample
│   │   ├── bblayers.conf.sample
│   │   └── conf-summary.txt
│   ├── nfs-dev/                     # NFS development
│   │   ├── local.conf.sample
│   │   ├── bblayers.conf.sample
│   │   └── conf-summary.txt
│   └── production/                  # Production configuration
│       ├── local.conf.sample
│       ├── bblayers.conf.sample
│       └── conf-summary.txt
└── backup/                          # Automatic configuration backups
    └── conf_YYYYMMDD_HHMMSS/        # Timestamped backups
```

## 🛠️ Creating Custom Templates

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
   ./template-config.sh my-template
   ```

## 💡 Benefits

- **Reproducible Builds**: Consistent configuration across different environments
- **No Manual Editing**: No need to modify `local.conf` manually
- **Quick Switching**: Easy switching between development and production configs
- **Automatic Backups**: Current configuration is always backed up
- **Version Control**: Templates can be versioned in git
- **Team Collaboration**: Shared configurations across team members

## 🔧 Advanced Usage

### Environment Variables
You can override template settings using environment variables:

```bash
# Override machine type
MACHINE=beaglebone-yocto ./template-config.sh nfs-dev

# Override download directory
DL_DIR=/path/to/downloads ./template-config.sh production
```

### Integration with CI/CD
Templates make CI/CD integration easier:

```bash
#!/bin/bash
# CI build script
cd meta-srk
./template-config.sh production
cd build
source ../oe-init-build-env
bitbake core-image-tiny-initramfs-srk-production
```

### Template Validation
The script validates templates before applying:
- Checks for required files
- Validates template directory structure
- Shows warnings for incomplete templates

## 📚 Migration from Manual Configuration

If you have existing `local.conf` customizations:

1. **Backup Current Config**:
   ```bash
   cp build/conf/local.conf meta-srk/backup/my-custom-local.conf
   ```

2. **Create Custom Template**:
   ```bash
   mkdir -p meta-srk/conf/templates/my-config
   cp build/conf/local.conf meta-srk/conf/templates/my-config/local.conf.sample
   cp build/conf/bblayers.conf meta-srk/conf/templates/my-config/bblayers.conf.sample
   echo "my-config" > meta-srk/conf/templates/my-config/conf-summary.txt
   ```

3. **Test Template**:
   ```bash
   ./template-config.sh my-config
   ```

This system eliminates the need to manually edit `local.conf` and provides a clean, reproducible way to manage different build configurations!