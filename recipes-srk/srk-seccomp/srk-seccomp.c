#include <stdio.h>
#include <seccomp.h>
#include <errno.h>

int main() {
    // Initialize the seccomp filter
    scmp_filter_ctx ctx;
    ctx = seccomp_init(SCMP_ACT_KILL); // Default action: kill the process

    // Allow the write syscall
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);

    // Load the filter
    if (seccomp_load(ctx) < 0) {
        perror("seccomp_load");
        return 1;
    }

    // This will be allowed by seccomp
    printf("Hello, World!\n");

    // This will be killed by seccomp
    if (fork() == -1 && errno == EACCES) {
        perror("fork");
    }

    // Release the seccomp filter
    seccomp_release(ctx);

    return 0;
}
