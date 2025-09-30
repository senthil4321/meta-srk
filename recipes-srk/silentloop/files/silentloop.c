#include <unistd.h>
#include <sys/wait.h>

// Silent init for kernel debugging
// This init does absolutely nothing except wait - no serial output
int main(void) {
    // Infinite loop doing nothing - perfect for debugging
    // No printf, no output, just a quiet init process
    while (1) {
        // Just sleep - no logging, no output
        sleep(3600); // Sleep for 1 hour at a time
        
        // Reap any zombie children (good practice for init)
        while (waitpid(-1, NULL, WNOHANG) > 0);
    }
    return 0;
}