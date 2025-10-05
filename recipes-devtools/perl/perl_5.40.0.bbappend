# Fix byteorder detection issue for perl-native
PACKAGECONFIG_CONFARGS:append:class-native = " '-Dbyteorder=12345678'"

# Fix byteorder detection issue for target perl (ARM little-endian)
PACKAGECONFIG_CONFARGS:append:class-target = " '-Dbyteorder=1234'"