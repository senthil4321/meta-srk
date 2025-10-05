SUMMARY = "Hello World SELinux Policy Module"
DESCRIPTION = "SELinux policy module for the hello world application"
SECTION = "admin"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/GPL-2.0-only;md5=801f80980d171dd6425610833a22dbe6"

DEPENDS = "policycoreutils-native selinux-python-native"
RDEPENDS:${PN} = "policycoreutils selinux-python"

# We need refpolicy source
DEPENDS += "refpolicy"

SRC_URI = "file://hello.te \
           file://hello.fc \
           file://hello.if \
          "

S = "${WORKDIR}/sources"

do_unpack:append() {
    bb.utils.mkdirhier(d.getVar('S'))
    import shutil
    for f in ['hello.te', 'hello.fc', 'hello.if']:
        src = os.path.join(d.getVar('WORKDIR'), f)
        dst = os.path.join(d.getVar('S'), f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
}

POLICY_NAME = "hello"
POLICY_VERSION = "1.0.0"

# Use the cross-compilation tools
export CROSS_COMPILE = "${TARGET_PREFIX}"

do_compile() {
    # Create a temporary policy build directory
    mkdir -p ${WORKDIR}/policy-build
    cd ${WORKDIR}/policy-build
    
    # Copy policy files from source directory
    cp ${S}/hello.te .
    cp ${S}/hello.fc .
    cp ${S}/hello.if .
    
    # Find refpolicy files
    REFPOLICY_DIR="${STAGING_DATADIR}/selinux/refpolicy"
    
    if [ -d "${REFPOLICY_DIR}" ]; then
        # Use refpolicy build system
        echo "Using refpolicy build system from ${REFPOLICY_DIR}"
        
        # Create a simple Makefile for our module
        cat > Makefile << 'EOF'
# Makefile for hello SELinux policy module

# Policy module name
POLICY_NAME = hello

# Policy files
POLICY_TE = $(POLICY_NAME).te
POLICY_FC = $(POLICY_NAME).fc
POLICY_IF = $(POLICY_NAME).if

# Output files
POLICY_MOD = $(POLICY_NAME).mod
POLICY_PP = $(POLICY_NAME).pp

# Build the policy module
all: $(POLICY_PP)

$(POLICY_PP): $(POLICY_MOD)
	semodule_package -o $@ -m $<

$(POLICY_MOD): $(POLICY_TE)
	checkmodule -M -m -o $@ $<

install:
	mkdir -p $(DESTDIR)/usr/share/selinux/packages
	cp $(POLICY_PP) $(DESTDIR)/usr/share/selinux/packages/

clean:
	rm -f *.mod *.pp

.PHONY: all install clean
EOF
        
        # Build the policy module
        make DESTDIR=${D} all
        
    else
        # Fallback: manual compilation
        bberror "refpolicy not found, using manual compilation"
        
        # Compile the Type Enforcement file to a module
        checkmodule -M -m -o hello.mod hello.te
        
        # Package the module
        semodule_package -o hello.pp -m hello.mod
    fi
}

do_install() {
    # Create the package directory
    install -d ${D}${datadir}/selinux/packages
    
    # Install the compiled policy package
    if [ -f ${WORKDIR}/policy-build/hello.pp ]; then
        install -m 644 ${WORKDIR}/policy-build/hello.pp ${D}${datadir}/selinux/packages/
    else
        bbwarn "Policy package hello.pp not found"
    fi
    
    # Install source files for reference
    install -d ${D}${datadir}/selinux/hello
    install -m 644 ${S}/hello.te ${D}${datadir}/selinux/hello/
    install -m 644 ${S}/hello.fc ${D}${datadir}/selinux/hello/
    install -m 644 ${S}/hello.if ${D}${datadir}/selinux/hello/
}

FILES:${PN} = "${datadir}/selinux/packages/hello.pp \
               ${datadir}/selinux/hello/ \
              "

PACKAGES = "${PN}"

# This package is arch-independent
PACKAGE_ARCH = "all"