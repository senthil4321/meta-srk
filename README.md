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

```bash
# Generate the dependency graph files
bitbake -g systemd

# Install Graphviz (if not already installed)
sudo apt-get install graphviz

# Convert the DOT file to a PNG image
dot -Tpng depends.dot -o systemd-dependency-tree.png

# Open the PNG image to view the dependency tree
xdg-open systemd-dependency-tree.png
```

goto rootfs

```bash
cd $(bitbake -e core-image-tiny-initramfs-srk-1 | grep "^IMAGE_ROOTFS=" | cut -d'=' -f2 | tr -d '"')

openssl passwd -1 1 | sed 's/\$/\\$/g'

echo '$1$V9izHbFg$z8ZfBeREgRqdOP3AuHGn51' | sed 's/\$/\\$/g'
echo \$1\$V9izHbFg\$z8ZfBeREgRqdOP3AuHGn51 | sed 's/\\//g'
```
