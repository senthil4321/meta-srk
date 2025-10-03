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
    // Rough calibration for ~1 second on ARM Cortex-A8
    // This is approximate and may need tuning based on CPU speed
    volatile unsigned long long iterations_per_second = 25000000ULL; // Tune this value
    
    for (int s = 0; s < seconds; s++) {
        for (count = 0; count < iterations_per_second; count++) {
            // Empty loop for busy waiting
            __asm__ volatile ("nop");
        }
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
    int num_leds = 4;
    char on = '1';
    char off = '0';

    write(1, "Starting LED blink loop...\n", 27);

    while (1) {
        write(1, "Opening LEDs...\n", 16);
        // Open all LEDs
        int fds[4];
        for (int i = 0; i < num_leds; i++) {
            fds[i] = open(led_paths[i], 1); // O_WRONLY = 1
            if (fds[i] < 0) {
                char err_msg[] = "Failed to open LED X\n";
                err_msg[18] = '0' + i;
                write(1, err_msg, sizeof(err_msg) - 1);
            } else {
                char ok_msg[] = "LED X opened\n";
                ok_msg[4] = '0' + i;
                write(1, ok_msg, 11);
            }
        }

        write(1, "LEDs ON for 5s\n", 15);
        // On for 2 seconds
        for (int i = 0; i < num_leds; i++) {
            if (fds[i] >= 0) {
                write(fds[i], &on, 1);
            }
        }
        delay_seconds(5);

        write(1, "LEDs OFF for 2s\n", 16);
        // Off for 1 second
        for (int i = 0; i < num_leds; i++) {
            if (fds[i] >= 0) {
                write(fds[i], &off, 1);
            }
        }
        delay_seconds(2);

        write(1, "Double blink (1s each)...\n", 26);
        // Blink twice (on 0.5s off 0.5s twice)
        for (int blink = 0; blink < 2; blink++) {
            for (int i = 0; i < num_leds; i++) {
                if (fds[i] >= 0) {
                    write(fds[i], &on, 1);
                }
            }
            delay_seconds(1);
            for (int i = 0; i < num_leds; i++) {
                if (fds[i] >= 0) {
                    write(fds[i], &off, 1);
                }
            }
            delay_seconds(1);
        }

        write(1, "Closing LEDs...\n", 16);
        // Close all LEDs
        for (int i = 0; i < num_leds; i++) {
            if (fds[i] >= 0) {
                close(fds[i]);
            }
        }
        write(1, "Loop complete\n", 14);
    }
}