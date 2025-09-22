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
| 8 | Switch libc glibc -> musl | (no feature change) | 13M | 6.6M | 26,633,216 | +4,096 | libc swap yielded negligible net change; further savings require dropping cryptsetup/devmapper stack |

## Current Image State

- Libc: musl
- Packages: busybox(+udhcpc), cryptsetup, util-linux-mount, srk-init (custom), minimal passwd/group files.
- DISTRO_FEATURES (observed): `acl ext2 ipv4 xattr vfat seccomp multiarch sysvinit ldconfig`
- Compression: both gzip (13M) and xz (6.6M) provided.
- Note: Musl did not reduce size materially while cryptsetup + its dependencies remain.

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

Ordered by expected impact (musl already applied in Step 8):

1. Reassess need for `cryptsetup` in initramfs; if not needed at early boot, remove it (drops openssl + devmapper + libargon2 stack).
2. Replace `util-linux-mount` if BusyBox mount covers required flags; confirm via runtime test.
3. Provide a trimmed BusyBox config (disable unused applets) via bbappend or custom recipe (expect tens to hundreds of KB savings compressed).
4. Consider `cpio.lz4` (if supported by boot chain) for faster decompression vs xz (trade size for boot time).
5. Enable additional size flags globally: `TARGET_CFLAGS:append = " -Os -fdata-sections -ffunction-sections"` and ensure `LDFLAGS:append = " -Wl,--gc-sections"` where safe.
6. Audit for any residual locale/charset or timezone data pulled indirectly (e.g., tzdata) and remove if not required.
7. Investigate static linking of a minimal init helper (if cryptsetup removed) to potentially drop dynamic loader + unused musl components (advanced; measure carefully).

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

- musl switch (completed): `echo 'TCLIBC = "musl"' >> build/conf/local.conf`
- Drop cryptsetup: remove it from `IMAGE_INSTALL` in image recipe.
- Force size flags example:
  `TARGET_CFLAGS:append = " -Os -fdata-sections -ffunction-sections"`
  `EXTRA_OECONF:append = " --disable-nls"` (package-specific where supported)

---
Document generated automatically as part of optimization tracking.
