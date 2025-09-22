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
| 9 | Drop cryptsetup + util-linux-mount; passwordless | (no feature change) | 1.7M | 1.1M | 3,536,896 | -23,096,320 | Massive reduction: removal of cryptsetup, its deps (openssl, libdevmapper, argon2), mount util; BusyBox only |
| 10 | srk-5: Trim BusyBox (partial), no init pivot (lz4 removed for isolation) | (no feature change) | 1.7M | 1.1M | 3,405,312 | -131,584 | lz4 moved to Step 11 to isolate compression impact; minor uncompressed drop from trimming applets |
| 11 | srk-6: Reintroduce lz4 (same content as srk-5) | (no feature change) | 1.7M | 1.1M | 3,405,312 | 0 | Adds cpio.lz4 (1.9M); gz 1,698,462 B vs 1,698,467 B (srk-5), xz 1,089,252 B vs 1,089,188 B (insignificant variance) |

## Current Image State

- Libc: musl
- Latest minimal variant (srk-5): BusyBox only, passwordless root/srk, simple `/init` shell (no pivot / mount of real rootfs).
- Prior variants kept for comparison: srk-4-nocrypt (no cryptsetup) and srk-3 (with cryptsetup).
- DISTRO_FEATURES (observed minimal): `acl ext2 ipv4 xattr vfat seccomp multiarch sysvinit ldconfig`
- Compression (srk-5): gzip 1.7M, xz 1.1M. (lz4 measured separately in srk-6 ~1.9M expected; xz smallest, lz4 fastest expected runtime decompression.)
- Net savings dominated by dropping cryptsetup stack; BusyBox trimming yielded modest additional ~130 KB uncompressed.

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

1. Further BusyBox minimization: generate full custom defconfig (strip networking tools if not needed at early boot, consider removing shell history/editing entirely — editing already disabled).
2. Benchmark decompression time: compare gz vs xz vs lz4 on target to choose optimal boot trade-off.
3. Apply global size flags: `TARGET_CFLAGS:append = " -Os -fdata-sections -ffunction-sections"`, with `LDFLAGS:append = " -Wl,--gc-sections"`; validate no regressions.
4. Explore static BusyBox build vs dynamic (measure: potential removal of ld-musl + libc pieces vs larger monolithic binary) — only if net win.
5. Confirm absence of extraneous data: run `du -a` in `/usr/share` & `/lib/modules` (should be minimal) to detect accidental growth.
6. Optional: integrate initramfs signing or hash measurement (boot integrity) now that size is stable.

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
