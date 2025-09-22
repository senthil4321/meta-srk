#include <stdio.h>
#include <time.h>
#include <unistd.h>

int main(void) {
    while (1) {
        time_t now = time(NULL);
        struct tm *tm = localtime(&now);
        if (tm) {
            char buf[64];
            if (strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", tm)) {
                printf("Hello World %s\n", buf);
                fflush(stdout);
            }
        }
        sleep(1);
    }
    return 0;
}
