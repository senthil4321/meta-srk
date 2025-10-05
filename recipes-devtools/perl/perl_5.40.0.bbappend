# Fix byteorder detection issue for perl-native
PACKAGECONFIG_CONFARGS:append:class-native = " -Dbyteorder=12345678"