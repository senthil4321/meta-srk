# Fix glibc compilation issue with --gc-sections on ARM
# The issue is that --gc-sections is being used inappropriately during libc_pic.os creation

# Remove the problematic --gc-sections flag from LDFLAGS for glibc compilation
TARGET_LDFLAGS:remove = "-Wl,--gc-sections"

# Alternative: Override the LDFLAGS specifically for the problematic linker command
do_compile:prepend() {
    # Remove --gc-sections from LDFLAGS for glibc compilation
    export LDFLAGS="${@d.getVar('TARGET_LDFLAGS').replace('-Wl,--gc-sections', '')}"
}
#}