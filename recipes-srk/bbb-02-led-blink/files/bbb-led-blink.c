#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#define LED_COUNT 4
#define LED_PATH "/sys/class/leds/beaglebone:green:usr%d"
#define TRIGGER_FILE "trigger"
#define BRIGHTNESS_FILE "brightness"

void set_led_trigger(int led_num, const char *trigger) {
    char path[256];
    sprintf(path, LED_PATH "/trigger", led_num);

    // Check if LED exists first
    char led_base_path[256];
    sprintf(led_base_path, LED_PATH, led_num);
    if (access(led_base_path, F_OK) != 0) {
        printf("LED %d not found at %s\n", led_num, led_base_path);
        return;
    }

    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        perror("Failed to open trigger file");
        return;
    }

    write(fd, trigger, strlen(trigger));
    close(fd);
}

void set_led_brightness(int led_num, int brightness) {
    char path[256];
    sprintf(path, LED_PATH "/brightness", led_num);

    // Check if LED exists first
    char led_base_path[256];
    sprintf(led_base_path, LED_PATH, led_num);
    if (access(led_base_path, F_OK) != 0) {
        printf("LED %d not found at %s\n", led_num, led_base_path);
        return;
    }

    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        perror("Failed to open brightness file");
        return;
    }

    char buf[2];
    sprintf(buf, "%d", brightness);
    write(fd, buf, strlen(buf));
    close(fd);
}

int main() {
    printf("BBB LED Blink Program\n");
    printf("Checking available LEDs...\n");

    int available_leds[LED_COUNT] = {0};
    int available_count = 0;

    // Check which LEDs are available
    for (int i = 0; i < LED_COUNT; i++) {
        char led_path[256];
        sprintf(led_path, LED_PATH, i);
        if (access(led_path, F_OK) == 0) {
            available_leds[i] = 1;
            available_count++;
            printf("Found LED %d at %s\n", i, led_path);
        } else {
            printf("LED %d not found at %s\n", i, led_path);
        }
    }

    if (available_count == 0) {
        printf("No LEDs found! Check kernel configuration and device tree.\n");
        return 1;
    }

    printf("Found %d out of %d LEDs\n", available_count, LED_COUNT);
    printf("Blinking available LEDs in sequence...\n");
    printf("Press Ctrl+C to stop\n\n");

    // Set all available LEDs to manual control (disable triggers)
    for (int i = 0; i < LED_COUNT; i++) {
        if (available_leds[i]) {
            set_led_trigger(i, "none");
            set_led_brightness(i, 0); // Start with all LEDs off
        }
    }

    // Main blink loop - only use available LEDs
    while (1) {
        for (int led = 0; led < LED_COUNT; led++) {
            if (available_leds[led]) {
                printf("Turning on LED %d\n", led);

                // Turn on current LED
                set_led_brightness(led, 1);

                // Wait 1 second
                sleep(1);

                // Turn off current LED
                set_led_brightness(led, 0);
            }
        }

        printf("Completed one cycle, starting again...\n");
    }

    return 0;
}