/*
 * BBB LED Blink - No libc version
 * Uses direct system calls without standard library
 */

#define SYS_OPEN    5
#define SYS_CLOSE   6
#define SYS_WRITE   4
#define SYS_READ    3
#define SYS_NANOSLEEP 162
#define SYS_EXIT    1
#define SYS_FCNTL   55

#define O_WRONLY    1
#define O_RDONLY    0
#define O_NONBLOCK  2048

#define F_GETFL     3
#define F_SETFL     4

#define NULL ((void*)0)

#define LED_COUNT   4

// System call implementations using Linux nolibc style
// Based on Linux kernel nolibc examples

#define __ARCH_WANT_SYSCALL_NO_AT
#define __ARCH_WANT_SYSCALL_NO_FLAGS

long my_syscall0(long nr) {
    long ret;
    __asm__ __volatile__ (
        "mov r7, %1\n"
        "svc #0\n"
        "mov %0, r0"
        : "=r"(ret)
        : "r"(nr)
        : "r7", "r0", "memory"
    );
    return ret;
}

long my_syscall1(long nr, long arg1) {
    long ret;
    __asm__ __volatile__ (
        "mov r7, %1\n"
        "mov r0, %2\n"
        "svc #0\n"
        "mov %0, r0"
        : "=r"(ret)
        : "r"(nr), "r"(arg1)
        : "r7", "r0", "memory"
    );
    return ret;
}

long my_syscall2(long nr, long arg1, long arg2) {
    long ret;
    __asm__ __volatile__ (
        "mov r7, %1\n"
        "mov r0, %2\n"
        "mov r1, %3\n"
        "svc #0\n"
        "mov %0, r0"
        : "=r"(ret)
        : "r"(nr), "r"(arg1), "r"(arg2)
        : "r7", "r0", "r1", "memory"
    );
    return ret;
}

long my_syscall3(long nr, long arg1, long arg2, long arg3) {
    long ret;
    __asm__ __volatile__ (
        "mov r7, %1\n"
        "mov r0, %2\n"
        "mov r1, %3\n"
        "mov r2, %4\n"
        "svc #0\n"
        "mov %0, r0"
        : "=r"(ret)
        : "r"(nr), "r"(arg1), "r"(arg2), "r"(arg3)
        : "r7", "r0", "r1", "r2", "memory"
    );
    return ret;
}

// System call wrapper functions
// Define necessary structures for nolibc
struct timespec {
    long tv_sec;   // seconds
    long tv_nsec;  // nanoseconds
};

int sys_open(const char *pathname, int flags) {
    return my_syscall2(SYS_OPEN, (long)pathname, flags);
}

int sys_close(int fd) {
    return my_syscall1(SYS_CLOSE, fd);
}

int sys_fcntl(int fd, int cmd, long arg) {
    return my_syscall3(SYS_FCNTL, fd, cmd, arg);
}

int sys_write(int fd, const char *buf, int count) {
    return my_syscall3(SYS_WRITE, fd, (long)buf, count);
}

int sys_read(int fd, void *buf, int count) {
    return my_syscall3(SYS_READ, fd, (long)buf, count);
}

int sys_nanosleep(struct timespec *req, struct timespec *rem) {
    return my_syscall2(SYS_NANOSLEEP, (long)req, (long)rem);
}

void sys_exit(int status) {
    my_syscall1(SYS_EXIT, status);
}

// Simple string length
int strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return p - s;
}

// Simple logging function - writes to stdout
void log_msg(const char *msg) {
    sys_write(1, msg, strlen(msg));
    sys_write(1, "\n", 1);
}

// Check for 'c' key press (non-blocking)
int check_cancel() {
    char c;
    int result = sys_read(0, &c, 1);
    if (result > 0 && c == 'c') {
        return 1;
    }
    return 0;
}

// System call numbers for ARM
// File descriptors
#define AT_FDCWD -100

// LED paths and constants - try multiple possibilities
const char led_base_path1[] = "/sys/class/leds/beaglebone:green:usr";
const char led_base_path2[] = "/sys/class/leds/green:usr";
const char led_base_path3[] = "/sys/class/leds/usr";
const char* led_base_paths[] = {led_base_path1, led_base_path2, led_base_path3};
#define LED_PATH_COUNT 3
const char trigger_suffix[] = "/trigger";
const char brightness_suffix[] = "/brightness";
const char none_str[] = "none";
const char zero_str[] = "0";
const char one_str[] = "1";

struct timespec delay = {1, 0}; // 1 second

char* strcpy(char *dest, const char *src) {
    char *d = dest;
    while (*src) {
        *dest++ = *src++;
    }
    *dest = 0;
    return d;
}

// Simple string concatenation
char* strcat(char *dest, const char *src) {
    char *d = dest;
    while (*dest) dest++;
    while (*src) {
        *dest++ = *src++;
    }
    *dest = 0;
    return d;
}

// Convert int to string (only for 0-9)
void int_to_str(int num, char *str) {
    str[0] = '0' + num;
    str[1] = 0;
}

// Set LED brightness
void set_led_brightness(int led_num, int brightness) {
    char path[256];
    char num_str[2];
    char log_buf[64];
    int fd = -1;
    int path_idx;

    // Try different LED path possibilities
    for (path_idx = 0; path_idx < LED_PATH_COUNT && fd < 0; path_idx++) {
        // Build path: /sys/class/leds/[path]/usrX/brightness
        strcpy(path, led_base_paths[path_idx]);
        int_to_str(led_num, num_str);
        strcat(path, num_str);
        strcat(path, brightness_suffix);

        // Try to open brightness file
        fd = sys_open(path, O_WRONLY);
    }
    
    if (fd < 0) {
        strcpy(log_buf, "Failed to open LED ");
        strcat(log_buf, num_str);
        strcat(log_buf, " - check LED paths");
        log_msg(log_buf);
        return;
    }

    // Write brightness value
    if (brightness) {
        sys_write(fd, one_str, 1);
        strcpy(log_buf, "LED ");
        strcat(log_buf, num_str);
        strcat(log_buf, " ON");
        log_msg(log_buf);
    } else {
        sys_write(fd, zero_str, 1);
        strcpy(log_buf, "LED ");
        strcat(log_buf, num_str);
        strcat(log_buf, " OFF");
        log_msg(log_buf);
    }

    sys_close(fd);
}

void _start() {
    int led;
    int flags;

    log_msg("BBB LED Blink nolibc application started");
    log_msg("Blinking LEDs 0-3 in sequence");
    log_msg("Press 'c' to cancel");

    // Set stdin to non-blocking mode
    flags = sys_fcntl(0, F_GETFL, 0);
    sys_fcntl(0, F_SETFL, flags | O_NONBLOCK);

    // Infinite loop blinking LEDs
    while (1) {
        for (led = 0; led < LED_COUNT; led++) {
            // Check for cancellation
            if (check_cancel()) {
                log_msg("Cancelled by user");
                sys_exit(0);
            }

            // Turn LED on
            set_led_brightness(led, 1);

            // Sleep 1 second
            sys_nanosleep(&delay, NULL);

            // Check for cancellation again
            if (check_cancel()) {
                log_msg("Cancelled by user");
                sys_exit(0);
            }

            // Turn LED off
            set_led_brightness(led, 0);

            // Sleep 1 second
            sys_nanosleep(&delay, NULL);
        }
    }

    // This should never be reached
    sys_exit(0);
}