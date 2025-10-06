CC ?= gcc
CFLAGS = -nostdlib -static -nostartfiles -fno-stack-protector -D_FORTIFY_SOURCE=0 -O0
LDFLAGS = -nostdlib -static

all: bbb-03-led-blink-nolibc

bbb-03-led-blink-nolibc: bbb-led-blink-nolibc.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f bbb-03-led-blink-nolibc