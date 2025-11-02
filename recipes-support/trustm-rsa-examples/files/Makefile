CC = $(CROSS_COMPILE)gcc
CFLAGS = -Wall -Wextra -O2
LDLIBS = -lssl -lcrypto

TARGETS = trustm-rsa-keygen trustm-rsa-sign trustm-rsa-verify

all: $(TARGETS)

trustm-rsa-keygen: trustm-rsa-keygen.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

trustm-rsa-sign: trustm-rsa-sign.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

trustm-rsa-verify: trustm-rsa-verify.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f $(TARGETS)

.PHONY: all clean
