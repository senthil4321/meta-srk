/*
 * Linux Capabilities Demo for BeagleBone Black
 * 
 * This program demonstrates various Linux capabilities:
 * - CAP_NET_RAW: Raw socket operations
 * - CAP_NET_ADMIN: Network administration
 * - CAP_SYS_TIME: Set system time
 * - CAP_DAC_OVERRIDE: Bypass file permission checks
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/capability.h>
#include <sys/prctl.h>
#include <errno.h>

void print_capabilities(const char *stage) {
    cap_t caps;
    char *cap_text;
    
    caps = cap_get_proc();
    if (caps == NULL) {
        perror("cap_get_proc");
        return;
    }
    
    cap_text = cap_to_text(caps, NULL);
    if (cap_text == NULL) {
        perror("cap_to_text");
        cap_free(caps);
        return;
    }
    
    printf("\n=== Capabilities at %s ===\n", stage);
    printf("%s\n", cap_text);
    
    cap_free(cap_text);
    cap_free(caps);
}

void show_effective_capabilities() {
    cap_t caps;
    cap_flag_value_t cap_val;
    
    caps = cap_get_proc();
    if (caps == NULL) {
        perror("cap_get_proc");
        return;
    }
    
    printf("\n=== Effective Capabilities Status ===\n");
    
    const char *cap_names[] = {
        "CAP_CHOWN", "CAP_DAC_OVERRIDE", "CAP_DAC_READ_SEARCH",
        "CAP_FOWNER", "CAP_FSETID", "CAP_KILL",
        "CAP_SETGID", "CAP_SETUID", "CAP_SETPCAP",
        "CAP_LINUX_IMMUTABLE", "CAP_NET_BIND_SERVICE", "CAP_NET_BROADCAST",
        "CAP_NET_ADMIN", "CAP_NET_RAW", "CAP_IPC_LOCK",
        "CAP_IPC_OWNER", "CAP_SYS_MODULE", "CAP_SYS_RAWIO",
        "CAP_SYS_CHROOT", "CAP_SYS_PTRACE", "CAP_SYS_PACCT",
        "CAP_SYS_ADMIN", "CAP_SYS_BOOT", "CAP_SYS_NICE",
        "CAP_SYS_RESOURCE", "CAP_SYS_TIME", "CAP_SYS_TTY_CONFIG",
        "CAP_MKNOD", "CAP_LEASE", "CAP_AUDIT_WRITE",
        "CAP_AUDIT_CONTROL", "CAP_SETFCAP"
    };
    
    int cap_values[] = {
        CAP_CHOWN, CAP_DAC_OVERRIDE, CAP_DAC_READ_SEARCH,
        CAP_FOWNER, CAP_FSETID, CAP_KILL,
        CAP_SETGID, CAP_SETUID, CAP_SETPCAP,
        CAP_LINUX_IMMUTABLE, CAP_NET_BIND_SERVICE, CAP_NET_BROADCAST,
        CAP_NET_ADMIN, CAP_NET_RAW, CAP_IPC_LOCK,
        CAP_IPC_OWNER, CAP_SYS_MODULE, CAP_SYS_RAWIO,
        CAP_SYS_CHROOT, CAP_SYS_PTRACE, CAP_SYS_PACCT,
        CAP_SYS_ADMIN, CAP_SYS_BOOT, CAP_SYS_NICE,
        CAP_SYS_RESOURCE, CAP_SYS_TIME, CAP_SYS_TTY_CONFIG,
        CAP_MKNOD, CAP_LEASE, CAP_AUDIT_WRITE,
        CAP_AUDIT_CONTROL, CAP_SETFCAP
    };
    
    int num_caps = sizeof(cap_values) / sizeof(cap_values[0]);
    
    for (int i = 0; i < num_caps; i++) {
        if (cap_get_flag(caps, cap_values[i], CAP_EFFECTIVE, &cap_val) == 0) {
            if (cap_val == CAP_SET) {
                printf("✓ %s\n", cap_names[i]);
            }
        }
    }
    
    cap_free(caps);
}

void test_net_raw_capability() {
    cap_t caps;
    cap_flag_value_t cap_val;
    
    printf("\n=== Testing CAP_NET_RAW ===\n");
    
    caps = cap_get_proc();
    if (caps == NULL) {
        perror("cap_get_proc");
        return;
    }
    
    if (cap_get_flag(caps, CAP_NET_RAW, CAP_EFFECTIVE, &cap_val) == 0) {
        if (cap_val == CAP_SET) {
            printf("✓ CAP_NET_RAW is SET - Can create raw sockets\n");
        } else {
            printf("✗ CAP_NET_RAW is NOT SET - Cannot create raw sockets\n");
        }
    }
    
    cap_free(caps);
}

void test_sys_time_capability() {
    cap_t caps;
    cap_flag_value_t cap_val;
    
    printf("\n=== Testing CAP_SYS_TIME ===\n");
    
    caps = cap_get_proc();
    if (caps == NULL) {
        perror("cap_get_proc");
        return;
    }
    
    if (cap_get_flag(caps, CAP_SYS_TIME, CAP_EFFECTIVE, &cap_val) == 0) {
        if (cap_val == CAP_SET) {
            printf("✓ CAP_SYS_TIME is SET - Can set system time\n");
        } else {
            printf("✗ CAP_SYS_TIME is NOT SET - Cannot set system time\n");
        }
    }
    
    cap_free(caps);
}

void test_net_admin_capability() {
    cap_t caps;
    cap_flag_value_t cap_val;
    
    printf("\n=== Testing CAP_NET_ADMIN ===\n");
    
    caps = cap_get_proc();
    if (caps == NULL) {
        perror("cap_get_proc");
        return;
    }
    
    if (cap_get_flag(caps, CAP_NET_ADMIN, CAP_EFFECTIVE, &cap_val) == 0) {
        if (cap_val == CAP_SET) {
            printf("✓ CAP_NET_ADMIN is SET - Can perform network administration\n");
        } else {
            printf("✗ CAP_NET_ADMIN is NOT SET - Cannot perform network administration\n");
        }
    }
    
    cap_free(caps);
}

void show_user_info() {
    printf("\n=== Process Information ===\n");
    printf("Real UID: %d\n", getuid());
    printf("Effective UID: %d\n", geteuid());
    printf("Real GID: %d\n", getgid());
    printf("Effective GID: %d\n", getegid());
    printf("PID: %d\n", getpid());
}

void print_usage(const char *progname) {
    printf("Linux Capabilities Demo\n");
    printf("Usage: %s [command]\n\n", progname);
    printf("Commands:\n");
    printf("  show         Show all current capabilities (default)\n");
    printf("  list         List all effective capabilities\n");
    printf("  test-net     Test network-related capabilities\n");
    printf("  test-time    Test CAP_SYS_TIME capability\n");
    printf("  info         Show process and user information\n");
    printf("  help         Show this help message\n\n");
    printf("Examples:\n");
    printf("  %s show\n", progname);
    printf("  %s list\n", progname);
    printf("  %s test-net\n", progname);
    printf("\nNote: Run with specific capabilities using:\n");
    printf("  sudo setcap cap_net_raw,cap_net_admin=ep %s\n", progname);
    printf("  sudo setcap cap_sys_time=ep %s\n", progname);
    printf("  getcap %s  # Show assigned capabilities\n", progname);
}

int main(int argc, char *argv[]) {
    const char *command = "show";
    
    if (argc > 1) {
        command = argv[1];
    }
    
    if (strcmp(command, "help") == 0 || strcmp(command, "-h") == 0 || 
        strcmp(command, "--help") == 0) {
        print_usage(argv[0]);
        return 0;
    }
    
    printf("===========================================\n");
    printf("  Linux Capabilities Demo - BeagleBone Black\n");
    printf("===========================================\n");
    
    show_user_info();
    
    if (strcmp(command, "show") == 0) {
        print_capabilities("startup");
    } else if (strcmp(command, "list") == 0) {
        show_effective_capabilities();
    } else if (strcmp(command, "test-net") == 0) {
        test_net_raw_capability();
        test_net_admin_capability();
    } else if (strcmp(command, "test-time") == 0) {
        test_sys_time_capability();
    } else if (strcmp(command, "info") == 0) {
        show_user_info();
    } else {
        printf("\nUnknown command: %s\n", command);
        print_usage(argv[0]);
        return 1;
    }
    
    printf("\n===========================================\n");
    
    return 0;
}
