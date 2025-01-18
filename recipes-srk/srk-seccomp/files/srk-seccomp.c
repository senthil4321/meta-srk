#include <stdio.h>
#include <seccomp.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>

#define VERSION "1.0.0"

int main(int argc, char *argv[]) {
    // Print version
    printf("Version: %s\n", VERSION);

    int skip_fork_seccomp = 0;
    int skip_print_seccomp = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-s") == 0) {
            skip_fork_seccomp = 1;
        } else if (strcmp(argv[i], "-p") == 0) {
            skip_print_seccomp = 1;
        }
    }

    // Initialize the seccomp filter
    printf("Hello, World! init \n");
    scmp_filter_ctx ctx;
    ctx = seccomp_init(SCMP_ACT_KILL); // Default action: kill the process
    printf("Hello, World! seccomp context init  ! \n");
    // Allow the write and usleep syscalls
    if (!skip_print_seccomp) {
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
        printf("SCMP_SYS(write) added  ! \n");
    }
    
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(nanosleep), 0);
    printf("SCMP_SYS(nanosleep) added  ! \n");

    if (!skip_fork_seccomp) {
        // Allow the fork syscall
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(fork), 0);
        printf("SCMP_SYS(fork) added  ! \n");
    }
    printf("Loading the filter \n");
    // Load the filter
    if (seccomp_load(ctx) < 0) {
        perror("seccomp_load");
        return 1;
    }
    printf("System seccomp protection activated \n");
    // This will be allowed by seccomp
    for (int i = 0; i < 5; i++) {
        printf("Hello, World! %d\n", i); // Print loop count
        usleep(1000000); // Sleep for 1 second (1000000 microseconds)
    }

    // This will be killed by seccomp
    if (fork() == -1 && errno == EACCES) {
        perror("fork");
    }

    // Release the seccomp filter
    seccomp_release(ctx);

    return 0;
}
