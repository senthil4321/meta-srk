# meta-srk

meta-srk

## bitbake tutorial

```bash
bitbake-layers create-layer ../meta-srk
bitbake-layers add-layer ../meta-srk
bitbake-layers show-layers
```

## Important Variables

```bash
PACKAGE_INSTALL
IMAGE_INSTALL
IMAGE_FSTYPES
IMAGE_FEATURES
```

### Package Group Recipe

A package group recipe bundles multiple packages together and then instead of having to explicitly specify each package in the IMAGE_INSTALL variable you can simply specify the package group name.

* https://lists.yoctoproject.org/g/yocto/message/20345

```bash
# How to list all package groups?
ls meta*/recipes*/packagegroups/*
ls meta*/recipes*/images/*
ls meta*/recipes-kernel/*
```

```bash
bitbake -c copy_rootfs_to_nfs rootfs-nfs-copy 
```