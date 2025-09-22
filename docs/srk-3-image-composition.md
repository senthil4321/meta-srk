# core-image-tiny-initramfs-srk-3 Composition

This document visualizes what *Poky base* (via `core-image-tiny-initramfs.bb`) brings in and what the `srk-3` customization (as expressed in `local.conf`) removes or overrides for the `core-image-tiny-initramfs-srk-3` build.

> NOTE: There is currently no dedicated `.bb` image recipe named `core-image-tiny-initramfs-srk-3` in the layer. The customization is driven from `local.conf` (see the `# srk-3` section). If you later create a dedicated image recipe, you can migrate the deltas there.

## 1. Base Reference: `core-image-tiny-initramfs.bb`

Key variables (from Poky `meta/recipes-core/images/core-image-tiny-initramfs.bb`):

- `PACKAGE_INSTALL` pulls in:
  - `initramfs-live-boot-tiny`
  - `packagegroup-core-boot`
  - `dropbear`
  - `${VIRTUAL-RUNTIME_base-utils}` (usually BusyBox)
  - `${VIRTUAL-RUNTIME_dev_manager}` (defaults to `busybox-mdev`)
  - `base-passwd`
  - `${ROOTFS_BOOTSTRAP_INSTALL}`
- `VIRTUAL-RUNTIME_dev_manager = "busybox-mdev"`
- `IMAGE_FEATURES = ""` (kept minimal)
- `IMAGE_FSTYPES = "${INITRAMFS_FSTYPES}"` (produces initramfs artifacts, not a full disk image)

## 2. srk-3 Customization Goals

From `local.conf` (comment block `# srk-3`):

1. Remove kernel dependency:
   - `PREFERRED_PROVIDER_virtual/kernel = ""`
2. Remove bootloader (U-Boot) dependency:
   - `PREFERRED_PROVIDER_virtual/bootloader = ""`
3. (Commented / potential future tweaks):
   - Remove kernel & bootloader from final image: `# IMAGE_INSTALL:remove = "virtual/kernel virtual/bootloader"`
   - Switch away from systemd / sysvinit: `# DISTRO_FEATURES:remove = "systemd"`, `# DISTRO_FEATURES:remove = " sysvinit"`
   - Use busybox mdev init manager: `# VIRTUAL-RUNTIME_init_manager = "mdev-busybox"`
   - Adjust serial consoles, add `openssl`, etc.

## 3. High-Level Flow Diagram

```mermaid
graph TD
  A[Poky Base Layers<br/>meta + meta-poky + meta-oe] --> B[core-image-tiny-initramfs.bb]
  B -->|PACKAGE_INSTALL| C[Base Packages<br/>initramfs-live-boot-tiny<br/>packagegroup-core-boot<br/>dropbear<br/>busybox / mdev<br/>base-passwd]
  B --> D[Initramfs Artifacts<br/>INITRAMFS_FSTYPES]
  subgraph SRK-3 Overrides (local.conf)
    E[Unset virtual/kernel]
    F[Unset virtual/bootloader]
    G[Future (optional)<br/>remove kernel & bootloader in IMAGE_INSTALL]
  end
  C --> H[Effective Minimal Rootfs]
  E --> H
  F --> H
  G --> H
  H --> D
```

## 4. What Is Removed / Not Pulled In

| Aspect | Default (Poky tiny initramfs) | srk-3 Adjustment | Net Effect |
|--------|-------------------------------|------------------|------------|
| Kernel dependency | Provided by preferred provider (e.g. `virtual/kernel`) | `PREFERRED_PROVIDER_virtual/kernel = ""` | Build avoids selecting a kernel (must ensure external kernel or not needed) |
| Bootloader dependency | U-Boot (or other) via `virtual/bootloader` | `PREFERRED_PROVIDER_virtual/bootloader = ""` | Bootloader not built as dependency |
| Image features | Empty | unchanged | Minimal stays minimal |
| Device manager | `busybox-mdev` | unchanged (comment shows possible explicit) | No change |
| Init system | Not systemd (tiny initramfs) | Comments contemplate removing systemd/sysvinit in other variants | Currently no change |
| Extra packages (openssl, etc.) | Not included by default | (commented) | Not included |

## 5. Risks / Considerations

- Clearing `PREFERRED_PROVIDER_virtual/kernel` & `virtual/bootloader` means the build won’t produce a deployable boot stack; ensure you have an external kernel + boot artifacts (e.g., prebuilt kernel, bootloader in board flash, or combined artifact elsewhere).
- Some recipes might still assume kernel headers or modules; validate that no package pulls them in indirectly.
- If you later create a squashed rootfs or overlay, ensure the kernel’s expected initramfs format matches what you produce here.

## 6. Suggested Next Steps

1. Create a dedicated image recipe: `meta-srk/recipes-core/images/core-image-tiny-initramfs-srk-3.bb` that inherits `core-image` and sets the explicit removals instead of keeping them in `local.conf`.
2. Add a `.bbappend` for `core-image-tiny-initramfs.bb` only if you want to patch behavior without a new recipe.
3. Add automated dependency graph extraction: `bitbake -g core-image-tiny-initramfs` then render `pn-buildlist`, `task-depends.dot`.
4. Document external kernel expectations: required compression, initramfs linkage method (CONFIG_INITRAMFS_SOURCE vs separate cpio), etc.

## 7. Template for Future Dedicated Recipe (Example)

```bitbake
# meta-srk/recipes-core/images/core-image-tiny-initramfs-srk-3.bb
SUMMARY = "SRK variant of tiny initramfs without kernel/bootloader build"
LICENSE = "MIT"
require recipes-core/images/core-image-tiny-initramfs.bb

# Remove kernel / bootloader dependencies
PREFERRED_PROVIDER_virtual/kernel = ""
PREFERRED_PROVIDER_virtual/bootloader = ""
IMAGE_INSTALL:remove = "virtual/kernel virtual/bootloader"

# Optional: add custom tools
# IMAGE_INSTALL:append = " openssl"

# Optional: adjust init manager
# VIRTUAL-RUNTIME_init_manager = "mdev-busybox"
```

## 8. Updating This Diagram

If you add or remove packages:

1. Run: `bitbake -g core-image-tiny-initramfs` (or your new image name)
2. Inspect `pn-buildlist` and `task-depends.dot`
3. Update the PACKAGE_INSTALL breakdown above.

---

*Generated documentation to clarify how srk-3 customizations differ from Poky base tiny initramfs image.*
