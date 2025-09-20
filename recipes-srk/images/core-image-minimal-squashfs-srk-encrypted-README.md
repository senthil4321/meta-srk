# Core Image Minimal SquashFS SRK Encrypted

This recipe creates an encrypted container containing the SquashFS image from `core-image-minimal-squashfs-srk`.

## Architecture Overview

```mermaid
graph TB
    subgraph "Build Process Flow"
        subgraph "Base Components"
            PD[poky.conf]
            PD --> |"base config"| BC[Base Configuration]
            BC --> |"toolchain, providers"| BT[Build Tools]
        end
        
        subgraph "Main Image Build"
            MI[core-image-minimal-squashfs-srk]
            MI --> |"inherit"| PD
            MI --> |"build"| SQ[SquashFS Image]
            SQ --> |"output"| SF[core-image-minimal-squashfs-srk-beaglebone-yocto.squashfs]
        end
        
        subgraph "Encrypted Image Build"
            EI[core-image-minimal-squashfs-srk-encrypted]
            EI --> |"inherit"| MI
            EI --> |"post-process"| EP[do_encrypt_image]
            
            EP --> |"generate"| KF[keyfile]
            EP --> |"create"| EC[Encrypted Container]
            EP --> |"copy"| SF
            EC --> |"contains"| SF
            
            EC --> |"output"| EF[core-image-minimal-squashfs-srk-encrypted.img]
        end
        
        subgraph "Initramfs Build (Separate)"
            IR[initramfs Recipe]
            IR --> |"include"| CT[cryptsetup cryptsetup-plain]
            IR --> |"build"| IF[Initramfs Image]
        end
        
        subgraph "Boot Process"
            BP[Bootloader] --> |"load"| IF
            IF --> |"decrypt"| EC
            IF --> |"mount"| SF
            SF --> |"switch_root"| RT[Root Filesystem]
        end
    end
    
    subgraph "Encryption Details"
        ED1[AES-XTS-PLAIN64]
        ED2[256-bit Key]
        ED3[ext4 Filesystem]
        ED4[50MB Container]
        
        KF --> |"used by"| ED1
        ED1 --> |"encrypts"| EC
        EC --> |"formatted as"| ED3
        EC --> |"size"| ED4
    end
    
    %% Material Theme Colors
    style PD fill:#E3F2FD,stroke:#1976D2,stroke-width:3
    style BC fill:#E8EAF6,stroke:#3F51B5,stroke-width:2
    style BT fill:#F3E5F5,stroke:#9C27B0,stroke-width:2
    
    style MI fill:#E1F5FE,stroke:#0277BD,stroke-width:3
    style SQ fill:#E0F2F1,stroke:#00796B,stroke-width:2
    style SF fill:#E8F5E8,stroke:#388E3C,stroke-width:3,color:#FFFFFF
    
    style EI fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3
    style EP fill:#E8EAF6,stroke:#512DA8,stroke-width:2
    style EC fill:#4CAF50,stroke:#FFFFFF,stroke-width:3,color:#FFFFFF
    style EF fill:#2E7D32,stroke:#FFFFFF,stroke-width:3,color:#FFFFFF
    
    style IR fill:#FFF3E0,stroke:#F57C00,stroke-width:3
    style CT fill:#FFEBEE,stroke:#D32F2F,stroke-width:2
    style IF fill:#E8F5E8,stroke:#689F38,stroke-width:2
    
    style BP fill:#E3F2FD,stroke:#1565C0,stroke-width:2
    style RT fill:#FCE4EC,stroke:#AD1457,stroke-width:2
    
    style KF fill:#795548,stroke:#FFFFFF,stroke-width:3,color:#FFFFFF
    style ED1 fill:#FF5722,stroke:#FFFFFF,stroke-width:2,color:#FFFFFF
    style ED2 fill:#FF9800,stroke:#FFFFFF,stroke-width:2,color:#FFFFFF
    style ED3 fill:#4CAF50,stroke:#FFFFFF,stroke-width:2,color:#FFFFFF
    style ED4 fill:#2196F3,stroke:#FFFFFF,stroke-width:2,color:#FFFFFF
```

## Key Features

- **Base Image**: Inherits from `core-image-minimal-squashfs-srk`
- **Encryption**: Creates AES-XTS encrypted container using cryptsetup
- **Post-Processing**: Runs after main image build completes
- **Optional**: Can be enabled/disabled via configuration
- **Post-Processing**: Runs after main image build completes
- **Optional**: Can be enabled/disabled via configuration

## Usage

### Enable Encryption

Add to your `local.conf`:

```bash
# Enable encrypted image creation
ENCRYPT_IMAGE = "1"

# Optional: Set custom container size (default: 50MB)
ENCRYPTED_CONTAINER_SIZE = "100"
```

### Build the Encrypted Image

```bash
bitbake core-image-minimal-squashfs-srk-encrypted
```

## Output

The build will create:

1. **Encrypted Container**: `core-image-minimal-squashfs-srk-encrypted-beaglebone-yocto-encrypted.img`
2. **Keyfile**: `keyfile` in the build directory (if not exists)
3. **Original SquashFS**: `core-image-minimal-squashfs-srk-beaglebone-yocto.squashfs`

## Encryption Details

- **Cipher**: AES-XTS-PLAIN64
- **Key Size**: 256 bits
- **Container Size**: 50MB (configurable)
- **Filesystem**: ext4 inside encrypted container

## Security Notes

- **Keyfile**: Automatically generated if not present
- **Permissions**: Keyfile has 600 permissions
- **Storage**: Keep keyfile secure for decryption

## Dependencies

- `cryptsetup-native` for host tools
- Base image: `core-image-minimal-squashfs-srk`

## Integration with Initramfs

This recipe creates the encrypted container. The initramfs (built separately) should include:

```bitbake
# In your initramfs recipe
IMAGE_INSTALL:append = " cryptsetup cryptsetup-plain"
```

This ensures the initramfs has the necessary tools to decrypt and mount the container during boot.

## Troubleshooting

### Common Issues

1. **Loop device not found**: Ensure you have sufficient loop devices available
2. **Permission denied**: Run build with appropriate privileges
3. **Keyfile missing**: Check `${TOPDIR}/keyfile` exists and has correct permissions

### Debug Commands

```bash
# Check available loop devices
sudo losetup -a

# Verify encrypted container
sudo cryptsetup luksDump /path/to/encrypted.img

# Mount for inspection
sudo losetup -f /path/to/encrypted.img
sudo cryptsetup open /dev/loopX encrypted_container
sudo mount /dev/mapper/encrypted_container /mnt/test
```
