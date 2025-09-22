# Initramfs Size Optimization Progress

This document records the iterative optimizations applied to `core-image-tiny-initramfs-srk-3` and their impact on the compressed and uncompressed initramfs sizes.

## Baseline Context

- MACHINE: `beaglebone-yocto`
- DISTRO: `poky`
- Initial image: minimal busybox + shadow + cryptsetup + util-linux-mount + srk-init
- Filesystem type: `cpio.gz` only (at start)
- Kernel/feature manipulations focused on reducing `DISTRO_FEATURES` and runtime packages.

## Size Timeline

Sizes captured from `tmp/deploy/images/beaglebone-yocto/`.
Uncompressed size measured via: `gunzip -c <file>.cpio.gz | wc -c` (and equivalent for xz).

| Step | Change Description | DISTRO_FEATURES notable removals (delta this step) | Compressed (gz) | Compressed (xz) | Uncompressed | Δ Uncompressed vs Previous | Notes |
|------|--------------------|-----------------------------------------------|----------------:|----------------:|-------------:|---------------------------:|-------|
| 0 | Baseline (ipv6 present) | — | 14M | — | 31,856,640 | — | Busybox + shadow + cryptsetup + util-linux-mount |
| 1 | Remove ipv6 (local.conf) | ipv6 | 14M | — | 31,856,640 | 0 | No packages depended on ipv6; no change |
| 2 | Remove extra features (ptest, introspection, debuginfod) | ptest gobject-introspection-data debuginfod | 14M | — | 31,856,640 | 0 | Features not pulling packages in this image |
| 3 | Add xz compression variant | (no feature change) | 14M | 7.4M | 31,856,640 | 0 | XZ ~47% of gzip size |
| 4 | Remove shadow from IMAGE_INSTALL (but still auto-added) | — | 14M | 7.4M | 31,856,640 | 0 | DNF added shadow due to user creation tooling |
| 5 | Add nfs to removals | nfs | 14M | 7.4M | 31,856,640 | 0 | nfs not contributing packages in this set |
| 6 | Exclude shadow (BAD_RECOMMENDATIONS) & strip locales (attempt) | — | (build failed) | — | — | — | DNF error: shadow explicitly required (extrausers) |
| 7 | Replace extrausers with custom passwd/shadow; exclude shadow; disable locales | shadow family, locales removed | 13M | 6.6M | 26,629,120 | -5,227,520 | Successful removal of shadow + locale data |

## Current Image State

- Packages: busybox(+udhcpc), cryptsetup, util-linux-mount, srk-init (custom), minimal passwd/group files.
- DISTRO_FEATURES (final observed): `acl ext2 ipv4 xattr vfat seccomp multiarch sysvinit ldconfig`
- Compression: both gzip (13M) and xz (6.6M) provided.

## Key Savings Sources

1. Shadow removal (binaries + libs) and locale elimination: ~5 MB uncompressed.
2. XZ compression: ~50% size of gzip variant (runtime trade-off: slower decompression).

## Ineffective Changes (No Size Impact)

- Removing ipv6, ptest, gobject-introspection-data, debuginfod, nfs in this minimal context.

## Methodology Notes

- Each change followed by `bitbake core-image-tiny-initramfs-srk-3` and artifact size capture.
- Uncompressed size used to isolate real content differences vs compression effects.
- Manifest inspected to validate package presence/absence.
- Rootfs logs (`log.do_rootfs`) checked when expected removals did not occur.

## Recommended Next Optimization Steps

Ordered by expected impact:

1. Switch glibc -> musl (`TCLIBC = "musl"` in `local.conf`): large libc footprint reduction.
2. Reassess need for `cryptsetup` in initramfs; if not needed at early boot, remove it (drops openssl+devmapper stack).
3. Replace `util-linux-mount` if busybox mount fully suffices; confirm needed options.
4. Provide a trimmed BusyBox config (disable unused applets) via bbappend or custom recipe.
5. Consider `cpio.lz4` (if supported by boot chain) for faster decompression vs xz.
6. Enable size optimization globally: `TUNE_FEATURES:append = " optimize-size"` or per-package CFLAGS `-Os -fdata-sections -ffunction-sections` with `INHIBIT_PACKAGE_STRIP = "0"` (strip already default, ensure not disabled).
7. Audit for any remaining locale or charset files (e.g., `/usr/lib/locale/`, `i18n` directories) and remove if safe.

## Risks / Considerations

- Removing cryptsetup changes boot encryption capabilities; ensure alternative path if needed.
- musl switch can affect ABI compatibility with prebuilt binaries (if any) and certain glibc-isms.
- BusyBox-only user management limits passwd feature set; ensure no runtime tools require full shadow utilities.
- XZ decompression cost vs boot time budget should be measured on target hardware.

## How to Reproduce Current Build

1. Ensure layer `meta-srk` is in `bblayers.conf`.
2. Build target:
   `bitbake core-image-tiny-initramfs-srk-3`
3. Artifacts: `tmp/deploy/images/beaglebone-yocto/core-image-tiny-initramfs-srk-3-beaglebone-yocto.rootfs-*.cpio.{gz,xz}`

## Appendix: Possible Config Snippets

- musl switch: `echo 'TCLIBC = "musl"' >> build/conf/local.conf`
- Drop cryptsetup: remove it from `IMAGE_INSTALL` in image recipe.
- Force size flags example:
  `TARGET_CFLAGS:append = " -Os -fdata-sections -ffunction-sections"`
  `EXTRA_OECONF:append = " --disable-nls"` (package-specific where supported)

---
Document generated automatically as part of optimization tracking.
