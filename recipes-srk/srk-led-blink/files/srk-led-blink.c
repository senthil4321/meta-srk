struct timespec {
    long tv_sec;
    long tv_nsec;
};

int open(const char *pathname, int flags) {
    int ret;
    __asm__ volatile (
        "mov r0, %1\n"
        "mov r1, %2\n"
        "mov r7, #5\n"
        "svc 0\n"
        "mov %0, r0\n"
        : "=r"(ret)
        : "r"(pathname), "r"(flags)
        : "r0", "r1", "r7"
    );
    return ret;
}

int write(int fd, const void *buf, int count) {
    int ret;
    __asm__ volatile (
        "mov r0, %1\n"
        "mov r1, %2\n"
        "mov r2, %3\n"
        "mov r7, #4\n"
        "svc 0\n"
        "mov %0, r0\n"
        : "=r"(ret)
        : "r"(fd), "r"(buf), "r"(count)
        : "r0", "r1", "r2", "r7"
    );
    return ret;
}

int read(int fd, void *buf, int count) {
    int ret;
    __asm__ volatile (
        "mov r0, %1\n"
        "mov r1, %2\n"
        "mov r2, %3\n"
        "mov r7, #3\n"
        "svc 0\n"
        "mov %0, r0\n"
        : "=r"(ret)
        : "r"(fd), "r"(buf), "r"(count)
        : "r0", "r1", "r2", "r7"
    );
    return ret;
}

int close(int fd) {
    int ret;
    __asm__ volatile (
        "mov r0, %1\n"
        "mov r7, #6\n"
        "svc 0\n"
        "mov %0, r0\n"
        : "=r"(ret)
        : "r"(fd)
        : "r0", "r7"
    );
    return ret;
}

int nanosleep(const struct timespec *req, struct timespec *rem) {
    int ret;
    __asm__ volatile (
        "mov r0, %1\n"
        "mov r1, %2\n"
        "mov r7, #162\n"
        "svc 0\n"
        "mov %0, r0\n"
        : "=r"(ret)
        : "r"(req), "r"(rem)
        : "r0", "r1", "r7"
    );
    return ret;
}

// Busy wait delay function (when nanosleep doesn't work in early boot)
void delay_seconds(int seconds) {
    volatile unsigned long long count = 0;
    // Much more conservative calibration for ARM Cortex-A8
    volatile unsigned long long iterations_per_second = 500000ULL; // Reduced significantly
    
    for (int s = 0; s < seconds; s++) {
        write(1, "Delaying 1 second...\n", 21);
        for (count = 0; count < iterations_per_second; count++) {
            // Empty loop for busy waiting
            __asm__ volatile ("nop");
        }
        write(1, "Delay complete\n", 15);
    }
}

int mount(const char *source, const char *target, const char *filesystemtype, unsigned long mountflags, const void *data) {
    int ret;
    __asm__ volatile (
        "mov r0, %1\n"
        "mov r1, %2\n"
        "mov r2, %3\n"
        "mov r3, %4\n"
        "mov r4, %5\n"
        "mov r7, #21\n"
        "svc 0\n"
        "mov %0, r0\n"
        : "=r"(ret)
        : "r"(source), "r"(target), "r"(filesystemtype), "r"(mountflags), "r"(data)
        : "r0", "r1", "r2", "r3", "r4", "r7"
    );
    return ret;
}

int mkdir(const char *pathname, int mode) {
    int ret;
    __asm__ volatile (
        "mov r0, %1\n"
        "mov r1, %2\n"
        "mov r7, #39\n"
        "svc 0\n"
        "mov %0, r0\n"
        : "=r"(ret)
        : "r"(pathname), "r"(mode)
        : "r0", "r1", "r7"
    );
    return ret;
}

void _start() {
    char debug_msg[] = "LED Blink Init Starting...\n";
    write(1, debug_msg, sizeof(debug_msg) - 1);

    // Create /sys directory if it doesn't exist
    int mkdir_ret = mkdir("/sys", 0755);
    if (mkdir_ret == 0) {
        write(1, "Created /sys directory\n", 23);
    } else {
        write(1, "mkdir /sys failed or already exists\n", 35);
    }

    // Try to mount sysfs if not already mounted
    int mount_ret = mount("sysfs", "/sys", "sysfs", 0, 0);
    if (mount_ret == 0) {
        write(1, "Sysfs mounted successfully\n", 28);
    } else {
        write(1, "Sysfs mount failed\n", 20);
    }

    char *led_paths[] = {
        "/sys/class/leds/beaglebone:green:usr0/brightness",
        "/sys/class/leds/beaglebone:green:usr1/brightness",
        "/sys/class/leds/beaglebone:green:usr2/brightness",
        "/sys/class/leds/beaglebone:green:usr3/brightness"
    };
    
    char *alt_led_paths[] = {
        "/sys/class/leds/usr0/brightness",
        "/sys/class/leds/usr1/brightness",
        "/sys/class/leds/usr2/brightness",
        "/sys/class/leds/usr3/brightness"
    };
    
    char *trigger_paths[] = {
        "/sys/class/leds/beaglebone:green:usr0/trigger",
        "/sys/class/leds/beaglebone:green:usr1/trigger",
        "/sys/class/leds/beaglebone:green:usr2/trigger",
        "/sys/class/leds/beaglebone:green:usr3/trigger"
    };
    
    char *alt_trigger_paths[] = {
        "/sys/class/leds/usr0/trigger",
        "/sys/class/leds/usr1/trigger",
        "/sys/class/leds/usr2/trigger",
        "/sys/class/leds/usr3/trigger"
    };
    
    int num_leds = 4;
    char on = '1';
    char off = '0';
    char none_trigger[] = "none";

    write(1, "Setting LED triggers to none...\n", 32);
    
    // Try to detect which LED paths work
    int use_alt_paths = 0;
    
    // Test if primary paths work
    int test_fd = open(led_paths[0], 1);
    if (test_fd < 0) {
        // Try alternative paths
        test_fd = open(alt_led_paths[0], 1);
        if (test_fd >= 0) {
            use_alt_paths = 1;
            write(1, "Using alternative LED paths\n", 28);
            close(test_fd);
        } else {
            write(1, "Warning: No LED paths accessible\n", 33);
        }
    } else {
        write(1, "Using primary LED paths\n", 24);
        close(test_fd);
    }
    
    char **current_led_paths = use_alt_paths ? alt_led_paths : led_paths;
    char **current_trigger_paths = use_alt_paths ? alt_trigger_paths : trigger_paths;
    
    // Set all LED triggers to "none" to take manual control
    for (int i = 0; i < num_leds; i++) {
        int trigger_fd = open(current_trigger_paths[i], 1); // O_WRONLY = 1
        if (trigger_fd >= 0) {
            int write_ret = write(trigger_fd, none_trigger, 4); // "none" is 4 chars
            if (write_ret == 4) {
                char msg[] = "Set trigger for LED X to none\n";
                msg[20] = '0' + i;
                write(1, msg, 27);
            } else {
                char msg[] = "Failed to write trigger for LED X\n";
                msg[32] = '0' + i;
                write(1, msg, 34);
            }
            close(trigger_fd);
        } else {
            char msg[] = "Failed to open trigger for LED X\n";
            msg[33] = '0' + i;
            write(1, msg, 35);
        }
    }

    write(1, "Starting interactive LED control...\n", 35);
    write(1, "Press 't' to toggle all LEDs, 'q' to quit\n", 43);

    char led_states[4] = {0, 0, 0, 0}; // Track current state of each LED
    char input_buf[1];

    while (1) {
        write(1, "Opening LEDs...\n", 16);
        // Open all LEDs
        int fds[4];
        for (int i = 0; i < num_leds; i++) {
            fds[i] = open(current_led_paths[i], 1); // O_WRONLY = 1
            if (fds[i] >= 0) {
                // Set initial state
                char state = led_states[i] ? on : off;
                int write_ret = write(fds[i], &state, 1);
                if (write_ret == 1) {
                    char ok_msg[] = "LED X opened and set to ";
                    ok_msg[4] = '0' + i;
                    write(1, ok_msg, 21);
                    write(1, led_states[i] ? "ON\n" : "OFF\n", 4);
                } else {
                    char err_msg[] = "Failed to write to LED X\n";
                    err_msg[22] = '0' + i;
                    write(1, err_msg, 24);
                }
            } else {
                char err_msg[] = "Failed to open LED X\n";
                err_msg[18] = '0' + i;
                write(1, err_msg, sizeof(err_msg) - 1);
            }
        }

        write(1, "Waiting for input (t=toggle, q=quit)...\n", 42);
        
        // Read one character from stdin
        int bytes_read = read(0, input_buf, 1);
        if (bytes_read > 0) {
            char cmd = input_buf[0];
            write(1, "Received: ", 10);
            write(1, &cmd, 1);
            write(1, "\n", 1);
            
            if (cmd == 't' || cmd == 'T') {
                // Toggle all LEDs
                write(1, "Toggling all LEDs\n", 18);
                for (int i = 0; i < num_leds; i++) {
                    if (fds[i] >= 0) {
                        led_states[i] = !led_states[i]; // Toggle state
                        char state = led_states[i] ? on : off;
                        int write_ret = write(fds[i], &state, 1);
                        if (write_ret == 1) {
                            char msg[] = "LED X now ";
                            msg[4] = '0' + i;
                            write(1, msg, 9);
                            write(1, led_states[i] ? "ON\n" : "OFF\n", 4);
                        } else {
                            char msg[] = "Failed to toggle LED X\n";
                            msg[21] = '0' + i;
                            write(1, msg, 23);
                        }
                    } else {
                        char msg[] = "LED X not accessible for toggle\n";
                        msg[4] = '0' + i;
                        write(1, msg, 31);
                    }
                }
            } else if (cmd == 'q' || cmd == 'Q') {
                write(1, "Quitting...\n", 12);
                // Close LEDs and exit
                for (int i = 0; i < num_leds; i++) {
                    if (fds[i] >= 0) {
                        close(fds[i]);
                    }
                }
                break;
            } else {
                write(1, "Unknown command. Use 't' to toggle or 'q' to quit\n", 52);
            }
        } else {
            write(1, "Read failed or no input\n", 25);
        }

        write(1, "Closing LEDs...\n", 16);
        // Close all LEDs
        for (int i = 0; i < num_leds; i++) {
            if (fds[i] >= 0) {
                close(fds[i]);
            }
        }
        write(1, "Ready for next command\n", 24);
    }
}