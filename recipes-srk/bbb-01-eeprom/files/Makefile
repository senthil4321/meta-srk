CC ?= gcc
CFLAGS ?= -Wall -Wextra -O2
LDFLAGS ?= 
TARGET = bbb-01-eeprom

all: $(TARGET)

$(TARGET): bbb-01-eeprom.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)

install: $(TARGET)
	install -d $(DESTDIR)/usr/bin
	install -m 0755 $(TARGET) $(DESTDIR)/usr/bin/

.PHONY: all clean install