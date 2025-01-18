#include <stdio.h>
#include <seccomp.h>
#include <errno.h>
#include <unistd.h>

int main() {
    // Initialize the seccomp filter
    printf("Hello, World! init \n");
    scmp_filter_ctx ctx;
    ctx = seccomp_init(SCMP_ACT_KILL); // Default action: kill the process

    // Allow the write and usleep syscalls
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(nanosleep), 0);

    // Load the filter
    if (seccomp_load(ctx) < 0) {
        perror("seccomp_load");
        return 1;
    }

    // This will be allowed by seccomp
    for (int i = 0; i < 5; i++) {
        printf("Hello, World!\n");
        usleep(500000); // Sleep for 500 ms
    }

    // This will be killed by seccomp
    if (fork() == -1 && errno == EACCES) {
        perror("fork");
    }

    // Release the seccomp filter
    seccomp_release(ctx);

    return 0;
}
