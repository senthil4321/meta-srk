CC = $(CROSS_COMPILE)gcc
CFLAGS = -Wall -Wextra -O2 -static

silentloop: silentloop.c
	$(CC) $(CFLAGS) -o silentloop silentloop.c

clean:
	rm -f silentloop

.PHONY: clean