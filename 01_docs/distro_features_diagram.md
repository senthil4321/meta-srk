# Poky Distro Features Flow

The diagram below shows how the final DISTRO_FEATURES for `core-image-tiny-initramfs-srk-3` are derived:

Steps:

1. Start from Poky base + Poky default extras.
2. Apply image-level removals in the image recipe (intended list below).
3. Observe the final effective feature set used to build the 14MB initramfs.

```mermaid
flowchart TD
    A[Base Poky Features] --> B[Image-Level Removals]
    B --> C[Final Features]

    A1["acl<br>alsa<br>bluetooth<br>debuginfod<br>ext2<br>ipv4<br>ipv6<br>pcmcia<br>usbgadget<br>usbhost<br>wifi<br>xattr<br>nfs<br>zeroconf<br>pci<br>3g<br>nfc<br>x11<br>vfat<br>seccomp<br>opengl<br>ptest<br>multiarch<br>wayland<br>vulkan<br>sysvinit<br>pulseaudio<br>gobject-introspection-data<br>ldconfig"] --> B

    B1["Removed in Image:<br>x11<br>wayland<br>opengl<br>vulkan<br>bluetooth<br>wifi<br>usbhost<br>usbgadget<br>pcmcia<br>pci<br>3g<br>nfc<br>zeroconf<br>pulseaudio<br>alsa"] --> C

    C1["acl<br>debuginfod<br>ext2<br>ipv4<br>ipv6<br>xattr<br>nfs<br>vfat<br>seccomp<br>ptest<br>multiarch<br>gobject-introspection-data<br>ldconfig"] --> D[Result: 14MB initramfs]

    style A fill:#e1f5fe,stroke:#0277bd
    style B fill:#fff3e0,stroke:#ef6c00
    style C fill:#e8f5e9,stroke:#2e7d32
    style D fill:#f3e5f5,stroke:#6a1b9a
```

Notes:

- The image-level `DISTRO_FEATURES:remove` was originally specified but due to later edits it was removed; this diagram reflects the intended removal list.
- Features like `ptest`, `multiarch`, `gobject-introspection-data`, `ldconfig` persist because they are injected by Poky defaults/backfill unless explicitly suppressed.
