# Core Image Minimal SquashFS SRK

A minimal, systemd-based squashfs image for embedded systems with optimized compression and security features.

## Overview

The `core-image-minimal-squashfs-srk` is a lightweight, compressed filesystem image designed for embedded devices that require:

- **Minimal footprint**: Only essential packages included
- **Systemd init system**: Modern service management
- **SquashFS compression**: Space-efficient read-only filesystem
- **Security features**: Custom user accounts and seccomp support
- **Bootloader-free**: Focused on rootfs without kernel/bootloader artifacts

## Image Components

```mermaid
graph TB
    subgraph "SRK Minimal SquashFS System"
        subgraph "Base Layer"
            PD[poky.conf]
            PD --> |"inherit base configs"| BD[Base Distro Features]
            BD --> |"toolchain, providers"| BC[Base Components]
        end
        
        subgraph "Distro Layer"
            D[srk-minimal-squashfs-distro.conf]
            PD --> |"require conf/distro/poky.conf"| D
            D --> DF[DISTRO_FEATURES]
            D --> VR[VIRTUAL-RUNTIME]
            D --> ED[EXTRA_IMAGEDEPENDS]
            
            DF --> |"append: systemd usrmerge"| SF[System Features]
            DF --> |"remove: sysvinit package-management"| RF[Removed Features]
            VR --> |"systemd"| IM[Init Manager]
            ED --> |"remove: bootloader qemu"| BDR[Build Dependencies Removed]
        end
        
        subgraph "Image Recipe"
            IR[core-image-minimal-squashfs-srk.bb]
            D --> |"DISTRO reference"| IR
            IR --> II[IMAGE_INSTALL]
            IR --> IF[IMAGE_FSTYPES]
            IR --> EU[EXTRA_USERS]
            IR --> IC[inherit core-image]
            
            II --> |"systemd busybox shadow"| CP[Core Packages]
            II --> |"squashfs-tools srk-seccomp"| SP[Security Packages]
            II --> |"hello systemd-serialgetty"| AP[Additional Packages]
            II --> |"remove: kernel u-boot"| RP[Removed Packages]
            
            IF --> |"squashfs"| FS[Filesystem Type]
            EU --> |"root, srk users"| UA[User Accounts]
        end
        
        subgraph "Core Components"
            CP --> SYS[systemd]
            CP --> BB[busybox]
            CP --> SH[shadow]
            
            SP --> ST[squashfs-tools]
            SP --> SC[srk-seccomp]
            
            AP --> HE[hello]
            AP --> SG[systemd-serialgetty]
        end
        
        subgraph "Security Layer"
            UA --> RU[Root User]
            UA --> SU[SRK User]
            SC --> SEC[SecComp Filtering]
            EU --> |"extrausers"| PWD[Password Hashing]
        end
        
        subgraph "Filesystem Output"
            FS --> |"compressed"| SQFS[SquashFS Image]
            SQFS --> |"read-only rootfs"| RO[Read-Only Root]
            SQFS --> |"8192KB size"| SZ[Image Size]
        end
        
        subgraph "Future Enhancements"
            FE1[XZ Compression<br/>EXTRA_IMAGECMD]
            FE2[Reduced Size<br/>6144KB]
            FE3[Read-Only Features<br/>IMAGE_FEATURES]
            
            style FE1 fill:#E8F5E8,stroke:#4CAF50,stroke-width:2,stroke-dasharray: 5 5
            style FE2 fill:#E8F5E8,stroke:#4CAF50,stroke-width:2,stroke-dasharray: 5 5
            style FE3 fill:#E8F5E8,stroke:#4CAF50,stroke-width:2,stroke-dasharray: 5 5
        end
    end
    
    %% Material Theme Colors
    style PD fill:#E3F2FD,stroke:#1976D2,stroke-width:3
    style BD fill:#E8EAF6,stroke:#3F51B5,stroke-width:2
    style BC fill:#F3E5F5,stroke:#9C27B0,stroke-width:2
    
    style D fill:#E1F5FE,stroke:#0277BD,stroke-width:3
    style DF fill:#E0F2F1,stroke:#00796B,stroke-width:2
    style VR fill:#E8F5E8,stroke:#388E3C,stroke-width:2
    style ED fill:#FFF3E0,stroke:#F57C00,stroke-width:2
    
    style IR fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3
    style II fill:#E8EAF6,stroke:#512DA8,stroke-width:2
    style IF fill:#E0F2F1,stroke:#00695C,stroke-width:2
    style EU fill:#FFF8E1,stroke:#FF8F00,stroke-width:2
    
    style SYS fill:#FFEBEE,stroke:#C62828,stroke-width:2
    style BB fill:#E8F5E8,stroke:#2E7D32,stroke-width:2
    style SH fill:#E3F2FD,stroke:#1565C0,stroke-width:2
    style ST fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2
    style SC fill:#FFF3E0,stroke:#EF6C00,stroke-width:2
    style HE fill:#E0F2F1,stroke:#00838F,stroke-width:2
    style SG fill:#FCE4EC,stroke:#AD1457,stroke-width:2
    
    style UA fill:#FFF8E1,stroke:#F9A825,stroke-width:2
    style RU fill:#FFEBEE,stroke:#D32F2F,stroke-width:2
    style SU fill:#E8F5E8,stroke:#689F38,stroke-width:2
    style SEC fill:#FF5722,stroke:#FFFFFF,stroke-width:3,color:#FFFFFF
    style PWD fill:#795548,stroke:#FFFFFF,stroke-width:2,color:#FFFFFF
    
    style SQFS fill:#4CAF50,stroke:#FFFFFF,stroke-width:3,color:#FFFFFF
    style RO fill:#8BC34A,stroke:#FFFFFF,stroke-width:2,color:#FFFFFF
    style SZ fill:#CDDC39,stroke:#333333,stroke-width:2
```

## Architecture

### Distro Configuration (`srk-minimal-squashfs-distro.conf`)

- **Purpose**: System-wide feature configuration
- **Features**:
  - Enables systemd, usrmerge
  - Removes sysvinit, package-management
  - Sets systemd as init manager
  - Removes bootloader dependencies

### Image Recipe (`core-image-minimal-squashfs-srk.bb`)

- **Purpose**: Package selection and image-specific settings
- **Packages**:
  - **Core**: systemd, busybox, shadow
  - **Tools**: squashfs-tools, hello
  - **Security**: srk-seccomp
  - **Services**: systemd-serialgetty

## Package Details

| Component | Purpose | Size Impact |
|-----------|---------|-------------|
| `systemd` | Modern init system and service manager | Medium |
| `busybox` | Essential Unix utilities in single binary | Small |
| `shadow` | User account management utilities | Small |
| `squashfs-tools` | Tools for creating/managing squashfs | Small |
| `srk-seccomp` | Security filtering for system calls | Minimal |
| `hello` | Custom application package | Minimal |
| `systemd-serialgetty` | Serial console support | Minimal |

## Security Features

### User Accounts

- **Root User**: Full system access with hashed password
- **SRK User**: Limited user account for applications
- **Password Hashing**: MD5 crypt format for compatibility

### SecComp Integration

- System call filtering via `srk-seccomp`
- Restricts dangerous system calls
- Enhances security for embedded applications

## Build Instructions

### Prerequisites

```bash
# Ensure meta-srk layer is added
bitbake-layers add-layer ../meta-srk
bitbake-layers show-layers
```

### Building the Image

```bash
# Set the distro (if not set in image recipe)
echo 'DISTRO = "srk-minimal-squashfs-distro"' >> conf/local.conf

# Build the image
bitbake core-image-minimal-squashfs-srk
```

### Output Location

```bash
# Image will be created at:
tmp/deploy/images/${MACHINE}/core-image-minimal-squashfs-srk-${MACHINE}.squashfs
```

## Configuration Options

### Current Settings

- **Filesystem Type**: SquashFS
- **Init System**: systemd
- **Image Size**: 8192 KB
- **Features**: Minimal (no package management)

### Future Enhancements (TODO)

- **Compression**: XZ compression with 1MB blocks
- **Size Optimization**: Reduced to 6144 KB
- **Read-Only**: Enhanced read-only filesystem features

## Testing

### Boot Testing

```bash
# Mount the squashfs image (for testing)
sudo mkdir -p /mnt/test-squashfs
sudo mount -o loop core-image-minimal-squashfs-srk-${MACHINE}.squashfs /mnt/test-squashfs

# Verify contents
ls -la /mnt/test-squashfs/
```

### User Account Verification

```bash
# Check user accounts in the image
sudo chroot /mnt/test-squashfs /bin/bash
cat /etc/passwd | grep -E "(root|srk)"
```

## Troubleshooting

### Common Issues

1. **Build Failures**: Ensure all dependencies are available
2. **Size Issues**: Check `IMAGE_ROOTFS_SIZE` if image is too large
3. **Boot Issues**: Verify systemd configuration and services

### Debug Commands

```bash
# Show image contents
bitbake -e core-image-minimal-squashfs-srk | grep ^IMAGE_INSTALL=

# Show distro features
bitbake -e core-image-minimal-squashfs-srk | grep ^DISTRO_FEATURES=

# Generate dependency graph
bitbake -g core-image-minimal-squashfs-srk
```

## Related Files

- **Distro Config**: `conf/distro/srk-minimal-squashfs-distro.conf`
- **Image Recipe**: `recipes-srk/images/core-image-minimal-squashfs-srk.bb`
- **Security Component**: `recipes-srk/srk-seccomp/srk-seccomp.bb`
- **Hello Package**: `recipes-srk/hello/hello_1.0.bb`

## License

MIT License - See COPYING.MIT for details.
