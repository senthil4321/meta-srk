#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

// BBB EEPROM structure (simplified)
struct bbb_eeprom {
    uint8_t header[4];      // "AA5533EE"
    uint8_t board_name[8];  // "A335BNLT"
    uint8_t version[4];     // Version
    uint8_t serial[12];     // Serial number
    uint8_t pin_options[6]; // Pin options
    uint8_t dc_spec[2];     // DC specification
    uint8_t mac_addr1[6];   // MAC address 1
    uint8_t mac_addr2[6];   // MAC address 2
    uint8_t mac_addr3[6];   // MAC address 3
    uint8_t mac_addr4[6];   // MAC address 4
    uint8_t crc[2];         // CRC
} __attribute__((packed));

void print_mac(uint8_t *mac, const char *label) {
    printf("%s: %02X:%02X:%02X:%02X:%02X:%02X\n",
           label, mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

void print_serial(uint8_t *serial) {
    printf("Serial Number: ");
    for (int i = 0; i < 12; i++) {
        printf("%c", serial[i]);
    }
    printf("\n");
}

void print_board_name(uint8_t *name) {
    printf("Board Name: ");
    for (int i = 0; i < 8; i++) {
        if (name[i] != 0xFF && name[i] != 0x00) {
            printf("%c", name[i]);
        }
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    int fd;
    struct bbb_eeprom eeprom;
    const char *eeprom_path = "/sys/bus/i2c/devices/0-0050/eeprom";

    printf("BBB EEPROM Reader\n");
    printf("=================\n\n");

    // Open EEPROM device
    fd = open(eeprom_path, O_RDONLY);
    if (fd < 0) {
        perror("Failed to open EEPROM device");
        printf("Make sure the EEPROM device is available at %s\n", eeprom_path);
        printf("You may need to run: modprobe at24\n");
        return 1;
    }

    // Read EEPROM data
    if (read(fd, &eeprom, sizeof(eeprom)) != sizeof(eeprom)) {
        perror("Failed to read EEPROM data");
        close(fd);
        return 1;
    }

    close(fd);

    // Check header
    if (eeprom.header[0] != 0xAA || eeprom.header[1] != 0x55 ||
        eeprom.header[2] != 0x33 || eeprom.header[3] != 0xEE) {
        printf("Invalid EEPROM header. This may not be a BBB EEPROM.\n");
        return 1;
    }

    // Display information
    print_board_name(eeprom.board_name);
    print_serial(eeprom.serial);

    printf("Version: %d.%d\n",
           eeprom.version[2], eeprom.version[3]);

    print_mac(eeprom.mac_addr1, "MAC Address 1");
    print_mac(eeprom.mac_addr2, "MAC Address 2");
    print_mac(eeprom.mac_addr3, "MAC Address 3");
    print_mac(eeprom.mac_addr4, "MAC Address 4");

    printf("\nEEPROM read successfully!\n");

    return 0;
}