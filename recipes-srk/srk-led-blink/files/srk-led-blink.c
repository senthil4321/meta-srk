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

void _start() {
    struct timespec ts_on = {2, 0};      // 2 seconds
    struct timespec ts_off = {1, 0};     // 1 second
    struct timespec ts_blink = {0, 500000000}; // 0.5 seconds

    char *led_paths[] = {
        "/sys/class/leds/beaglebone:green:usr0/brightness",
        "/sys/class/leds/beaglebone:green:usr1/brightness",
        "/sys/class/leds/beaglebone:green:usr2/brightness",
        "/sys/class/leds/beaglebone:green:usr3/brightness"
    };
    int num_leds = 4;
    char on = '1';
    char off = '0';

    while (1) {
        // Open all LEDs
        int fds[4];
        for (int i = 0; i < num_leds; i++) {
            fds[i] = open(led_paths[i], 1); // O_WRONLY = 1
        }

        // On for 2 seconds
        for (int i = 0; i < num_leds; i++) {
            write(fds[i], &on, 1);
        }
        nanosleep(&ts_on, 0);

        // Off for 1 second
        for (int i = 0; i < num_leds; i++) {
            write(fds[i], &off, 1);
        }
        nanosleep(&ts_off, 0);

        // Blink twice (on 0.5s off 0.5s twice)
        for (int blink = 0; blink < 2; blink++) {
            for (int i = 0; i < num_leds; i++) {
                write(fds[i], &on, 1);
            }
            nanosleep(&ts_blink, 0);
            for (int i = 0; i < num_leds; i++) {
                write(fds[i], &off, 1);
            }
            nanosleep(&ts_blink, 0);
        }

        // Close all LEDs
        for (int i = 0; i < num_leds; i++) {
            close(fds[i]);
        }
    }
}