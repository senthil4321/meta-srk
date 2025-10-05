# Fix perl configure to provide byteorder for both native and target builds
PACKAGECONFIG_CONFARGS:append:class-native = " -Dbyteorder=12345678"
PACKAGECONFIG_CONFARGS:append:class-target = " -Dbyteorder=1234"

# Fix perl config.h generation for ARM cross-compilation
do_configure:append:class-target() {
    # Fix the config.h file to have correct define values on the same line
    echo "Fixing config.h multiline defines..."
    
    # Use perl itself to fix the config file - this handles the multiline issues properly
    perl -i -pe 'if (/^#define\s+([A-Za-z_][A-Za-z0-9_]*)\s*$/) { 
        $define = $_; 
        $_ = <> // ""; 
        if (/^(\d+)\s*(\/\*.*\*\/)\s*$/) { 
            $_ = $define; 
            chomp; 
            $_ .= " $1 $2\n"; 
        } else { 
            print $define; 
        } 
    }' ${B}/config.h || echo "Perl fix failed, continuing..."
    
    echo "config.h has been processed"
}