#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/rtc.h>
#include <time.h>
#include <sys/time.h>
#include <string.h>

#define RTC_DEVICE "/dev/rtc0"

void print_usage(const char *prog_name) {
    printf("BBB RTC Read/Write Utility\n");
    printf("Usage: %s [command] [options]\n\n", prog_name);
    printf("Commands:\n");
    printf("  read              Read current RTC time\n");
    printf("  write [time]      Write time to RTC (format: YYYY-MM-DD HH:MM:SS)\n");
    printf("  set-system        Set system time from RTC\n");
    printf("  set-rtc           Set RTC time from system time\n");
    printf("  info              Show RTC device information\n");
    printf("\nExamples:\n");
    printf("  %s read\n", prog_name);
    printf("  %s write \"2025-09-27 15:30:00\"\n", prog_name);
    printf("  %s set-system\n", prog_name);
    printf("  %s set-rtc\n", prog_name);
    printf("  %s info\n", prog_name);
}

int read_rtc_time(int fd) {
    struct rtc_time rtc_tm;
    int ret;

    ret = ioctl(fd, RTC_RD_TIME, &rtc_tm);
    if (ret < 0) {
        perror("RTC_RD_TIME ioctl");
        return -1;
    }

    printf("RTC Time: %04d-%02d-%02d %02d:%02d:%02d\n",
           rtc_tm.tm_year + 1900, rtc_tm.tm_mon + 1, rtc_tm.tm_mday,
           rtc_tm.tm_hour, rtc_tm.tm_min, rtc_tm.tm_sec);

    return 0;
}

int write_rtc_time(int fd, const char *time_str) {
    struct rtc_time rtc_tm;
    int ret;

    // Parse time string manually (format: YYYY-MM-DD HH:MM:SS)
    // Expected format: "2025-09-27 15:30:00"
    int year, month, day, hour, minute, second;

    if (sscanf(time_str, "%d-%d-%d %d:%d:%d",
               &year, &month, &day, &hour, &minute, &second) != 6) {
        fprintf(stderr, "Invalid time format. Use: YYYY-MM-DD HH:MM:SS\n");
        fprintf(stderr, "Example: 2025-09-27 15:30:00\n");
        return -1;
    }

    // Validate ranges
    if (year < 1900 || year > 2100 || month < 1 || month > 12 ||
        day < 1 || day > 31 || hour < 0 || hour > 23 ||
        minute < 0 || minute > 59 || second < 0 || second > 59) {
        fprintf(stderr, "Invalid time values\n");
        return -1;
    }

    // Convert to rtc_time structure
    rtc_tm.tm_year = year - 1900;
    rtc_tm.tm_mon = month - 1;
    rtc_tm.tm_mday = day;
    rtc_tm.tm_hour = hour;
    rtc_tm.tm_min = minute;
    rtc_tm.tm_sec = second;
    rtc_tm.tm_wday = 0; // Not used for setting
    rtc_tm.tm_yday = 0; // Not used for setting
    rtc_tm.tm_isdst = 0; // Not used for setting

    ret = ioctl(fd, RTC_SET_TIME, &rtc_tm);
    if (ret < 0) {
        perror("RTC_SET_TIME ioctl");
        return -1;
    }

    printf("RTC time set to: %04d-%02d-%02d %02d:%02d:%02d\n",
           rtc_tm.tm_year + 1900, rtc_tm.tm_mon + 1, rtc_tm.tm_mday,
           rtc_tm.tm_hour, rtc_tm.tm_min, rtc_tm.tm_sec);

    return 0;
}

int set_system_from_rtc(int fd) {
    struct rtc_time rtc_tm;
    struct tm sys_tm;
    struct timeval tv;
    int ret;

    ret = ioctl(fd, RTC_RD_TIME, &rtc_tm);
    if (ret < 0) {
        perror("RTC_RD_TIME ioctl");
        return -1;
    }

    // Convert rtc_time to struct tm
    sys_tm.tm_year = rtc_tm.tm_year;
    sys_tm.tm_mon = rtc_tm.tm_mon;
    sys_tm.tm_mday = rtc_tm.tm_mday;
    sys_tm.tm_hour = rtc_tm.tm_hour;
    sys_tm.tm_min = rtc_tm.tm_min;
    sys_tm.tm_sec = rtc_tm.tm_sec;
    sys_tm.tm_wday = rtc_tm.tm_wday;
    sys_tm.tm_yday = rtc_tm.tm_yday;
    sys_tm.tm_isdst = rtc_tm.tm_isdst;

    // Convert to time_t
    time_t time_val = mktime(&sys_tm);
    if (time_val == -1) {
        perror("mktime");
        return -1;
    }

    // Set system time using settimeofday
    tv.tv_sec = time_val;
    tv.tv_usec = 0;

    ret = settimeofday(&tv, NULL);
    if (ret < 0) {
        perror("settimeofday");
        return -1;
    }

    printf("System time set from RTC: %04d-%02d-%02d %02d:%02d:%02d\n",
           rtc_tm.tm_year + 1900, rtc_tm.tm_mon + 1, rtc_tm.tm_mday,
           rtc_tm.tm_hour, rtc_tm.tm_min, rtc_tm.tm_sec);

    return 0;
}

int set_rtc_from_system(int fd) {
    struct rtc_time rtc_tm;
    time_t now;
    struct tm *tm_now;
    int ret;

    now = time(NULL);
    tm_now = localtime(&now);

    // Convert struct tm to rtc_time
    rtc_tm.tm_year = tm_now->tm_year;
    rtc_tm.tm_mon = tm_now->tm_mon;
    rtc_tm.tm_mday = tm_now->tm_mday;
    rtc_tm.tm_hour = tm_now->tm_hour;
    rtc_tm.tm_min = tm_now->tm_min;
    rtc_tm.tm_sec = tm_now->tm_sec;
    rtc_tm.tm_wday = tm_now->tm_wday;
    rtc_tm.tm_yday = tm_now->tm_yday;
    rtc_tm.tm_isdst = tm_now->tm_isdst;

    ret = ioctl(fd, RTC_SET_TIME, &rtc_tm);
    if (ret < 0) {
        perror("RTC_SET_TIME ioctl");
        return -1;
    }

    printf("RTC time set from system: %04d-%02d-%02d %02d:%02d:%02d\n",
           rtc_tm.tm_year + 1900, rtc_tm.tm_mon + 1, rtc_tm.tm_mday,
           rtc_tm.tm_hour, rtc_tm.tm_min, rtc_tm.tm_sec);

    return 0;
}

int show_rtc_info(int fd) {
    int ret;

    // Try to get RTC capabilities by testing different ioctl calls
    ret = ioctl(fd, RTC_UIE_ON, 0);
    if (ret >= 0) {
        ioctl(fd, RTC_UIE_OFF, 0); // Turn it off immediately
        printf("RTC supports: Update interrupts\n");
    }

    ret = ioctl(fd, RTC_AIE_ON, 0);
    if (ret >= 0) {
        ioctl(fd, RTC_AIE_OFF, 0); // Turn it off immediately
        printf("RTC supports: Alarm interrupts\n");
    }

    ret = ioctl(fd, RTC_PIE_ON, 0);
    if (ret >= 0) {
        ioctl(fd, RTC_PIE_OFF, 0); // Turn it off immediately
        printf("RTC supports: Periodic interrupts\n");
    }

    printf("RTC Device: %s\n", RTC_DEVICE);
    return 0;
}

int main(int argc, char *argv[]) {
    int fd;
    int ret = 0;

    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    // Open RTC device
    fd = open(RTC_DEVICE, O_RDONLY);
    if (fd < 0) {
        perror("Failed to open RTC device");
        fprintf(stderr, "Make sure RTC device %s exists and is accessible\n", RTC_DEVICE);
        return 1;
    }

    const char *command = argv[1];

    if (strcmp(command, "read") == 0) {
        ret = read_rtc_time(fd);
    } else if (strcmp(command, "write") == 0) {
        if (argc < 3) {
            fprintf(stderr, "Error: write command requires time argument\n");
            print_usage(argv[0]);
            ret = 1;
        } else {
            ret = write_rtc_time(fd, argv[2]);
        }
    } else if (strcmp(command, "set-system") == 0) {
        ret = set_system_from_rtc(fd);
    } else if (strcmp(command, "set-rtc") == 0) {
        ret = set_rtc_from_system(fd);
    } else if (strcmp(command, "info") == 0) {
        ret = show_rtc_info(fd);
    } else {
        fprintf(stderr, "Unknown command: %s\n", command);
        print_usage(argv[0]);
        ret = 1;
    }

    close(fd);
    return ret;
}