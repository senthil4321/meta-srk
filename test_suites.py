#!/usr/bin/env python3
"""
Test Suite Definitions for SRK Serial Test Script
Contains predefined test suites for different image types and configurations.
"""

__version__ = "1.0.0"
__author__ = "SRK Development Team"
__copyright__ = "Copyright (c) 2025 SRK. All rights reserved."
__license__ = "MIT"

# Define test suites with generic format
DEFAULT_TEST_SUITE = [
    # [test_type, description, command, expected_value, failure_message, kwargs]

    # Base system checks
    ["ASSERT_IN_BUFFER", "Check U-Boot logs", None, "U-Boot", "U-Boot not found in logs"],
    ["ASSERT_IN_BUFFER", "Check kernel logs", None, "Linux version", "Kernel logs not found"],
    ["ASSERT_IN_BUFFER", "Check initramfs logs", None, "initramfs", "Initramfs logs not found"],
    ["WAIT_FOR_CONDITION", "Wait for login prompt", None, "beaglebone-yocto login:|beaglebone-yocto{PROMPT}", "No login or shell prompt found", {"timeout": 90}],

    # Detailed login steps - simplified for generic format
    ["SEND_COMMAND", "Send username", "srk", None, "Username sent"],
    ["SEND_COMMAND", "Send password", "", None, "Password sent"],
    ["WAIT_FOR_CONDITION", "Wait for shell prompt", None, "beaglebone-yocto{PROMPT}", "Shell prompt not found", {"timeout": 30}],
    ["ASSERT_IN_BUFFER", "Verify login", None, "beaglebone-yocto:", "Login verification failed"],

    # Application tests
    ["COMMAND_AND_ASSERT", "Check hello binary", "which hello", "hello", "Hello binary not found"],
    ["COMMAND_AND_VERIFY_MULTIPLE", "Test hello output", "hello", [
        "Hello, World! from meta-srk layer and recipes-srk V2!!!",
        "Hello, World! 20SEP2025 07:28 !!!",
        "Hello, World! 20SEP2025 23:50 !!!"
    ], "Hello output verification failed"],

    # System information tests
    ["COMMAND_AND_EXTRACT", "Check kernel version", "uname -a", "Linux", "Build version check failed", {"extract_pattern": "Linux"}],
    ["COMMAND_AND_EXTRACT", "Check build time", "uname -v", "#", "Build time check failed", {"extract_pattern": "#"}],
    ["COMMAND_AND_EXTRACT", "Check timestamp", "cat /etc/timestamp 2>/dev/null || date -r /etc/issue", None, "Timestamp check failed"],
    ["COMMAND_AND_EXTRACT", "Check uptime", "uptime", "up", "Uptime check failed", {"extract_pattern": "up"}],
    ["COMMAND_AND_EXTRACT", "Check BusyBox", "busybox", "BusyBox", "BusyBox version check failed", {"extract_pattern": "BusyBox"}],

    # Init system check (default: expects systemd or init)
    ["COMMAND_AND_ASSERT", "Check init system", "ps -p 1", "systemd", "Init system check failed"],

    # Security tests
    ["COMMAND_AND_ASSERT", "Check encryption support", "which cryptsetup", "cryptsetup", "Encryption support check failed"],
]

IMAGE_11_TEST_SUITE = [
    # [test_type, description, command, expected_value, failure_message, kwargs]

    # Reset BBB before starting tests
    # ["RESET_TARGET", "Reset BBB", None, None, "Target reset failed"],
    # ["WAIT", "Wait after reset", None, None, None, {"duration": "medium"}],
    # Detailed login steps - simplified for generic format
    # ["WAIT_FOR_CONDITION", "Wait for shell prompt", None, "{PROMPT}", "Shell prompt not found", {"timeout": 30}],

    # Hardware-specific tests
    ["COMMAND_AND_ASSERT", "Check RTC binary", "which bbb-03-rtc", "bbb-03-rtc", "RTC binary not found"],
    ["COMMAND_AND_ASSERT", "Test RTC read", "bbb-03-rtc read", "RTC Time:", "RTC read test failed"],
    ["COMMAND_AND_ASSERT", "Test RTC info", "bbb-03-rtc info", "RTC Device:", "RTC info test failed"],

    # System information tests
    ["COMMAND_AND_EXTRACT", "Check kernel version", "uname -a", "Linux", "Build version check failed", {"extract_pattern": "Linux"}],
    ["COMMAND_AND_EXTRACT", "Check build time", "uname -v", "#", "Build time check failed", {"extract_pattern": "#"}],
    ["COMMAND_AND_EXTRACT", "Check timestamp", "cat /etc/timestamp 2>/dev/null || date -r /etc/issue", None, "Timestamp check failed"],
    ["COMMAND_AND_EXTRACT", "Check uptime", "uptime", "up", "Uptime check failed", {"extract_pattern": "up"}],
    ["COMMAND_AND_EXTRACT", "Check BusyBox", "busybox", "BusyBox", "BusyBox version check failed", {"extract_pattern": "BusyBox"}],
    # Reset and capture serial boot logs; ensure root shell message appears
    ["CAPTURE_LOG", "Capture boot serial logs", None, None, "Error Capturing Log", {
        "capture_name": "root-shell-boot",
        "reset_before": True
    }],
    ["CAPTURE_LOG_ASSERT", "Verify boot message", None, "Dropping into root shell...", "Message not found", {"capture_name": "root-shell-boot"}],

]

IMAGE_11_TEST_SUITE_TINY = [
    # [test_type, description, command, expected_value, failure_message, kwargs]

    # Reset BBB before starting tests
    # ["RESET_TARGET", "Reset BBB", None, None, "Target reset failed"],
    # ["WAIT", "Wait after reset", None, None, None, {"duration": "medium"}],
    # Detailed login steps - simplified for generic format
    # ["WAIT_FOR_CONDITION", "Wait for shell prompt", None, "{PROMPT}", "Shell prompt not found", {"timeout": 30}],


    ["CAPTURE_LOG", "Capture boot serial logs", None, None, "Error Capturing Log", {
        "capture_name": "root-shell-boot",
        "reset_before": True,
        "timeout": 5,
        "end_conditions": ["Hello World"]
    }],
    ["CAPTURE_LOG_ASSERT", "Verify boot message", None, "Hello World", "Message not found", {"capture_name": "root-shell-boot"}],

]

IMAGE_2_BASH_TEST_SUITE = [
    # [test_type, description, command, expected_value, failure_message, kwargs]

    # Base system checks with login
    ["ASSERT_IN_BUFFER", "Check U-Boot logs", None, "U-Boot", "U-Boot not found in logs"],
    ["ASSERT_IN_BUFFER", "Check kernel logs", None, "Linux version", "Kernel logs not found"],
    # ["WAIT_FOR_CONDITION", "Wait for login prompt", None, "srk-device login:|srk-device:~$", "No login or shell prompt found", {"timeout": 90}],

    # Login sequence for srk user
    # ["SEND_COMMAND", "Send username", "srk", None, "Username sent"],
    # ["WAIT_FOR_CONDITION", "Wait for password prompt", None, "Password:", "Password prompt not found", {"timeout": 10}],
    # ["SEND_COMMAND", "Send password", "newsrkpass", None, "Password sent"],
    # ["WAIT_FOR_CONDITION", "Wait for shell prompt", None, "srk@srk-device:", "Shell prompt not found", {"timeout": 30}],

    # Bash functionality tests
    # ["COMMAND_AND_ASSERT", "Test bash shell", "echo $0", "bash", "Bash shell not detected"],
    ["COMMAND_AND_ASSERT", "Test hostname", "hostname", "srk-device", "Hostname not set correctly"],
    ["COMMAND_AND_ASSERT", "Test prompt variable", "echo $PS1", "\\u@\\h:\\w\\$", "PS1 prompt not set correctly"],
    
    # User and environment tests
    ["COMMAND_AND_ASSERT", "Check current user", "whoami", "srk", "Current user verification failed"],
    ["COMMAND_AND_ASSERT", "Check home directory", "pwd", "/home/srk", "Home directory not correct"],
    ["COMMAND_AND_ASSERT", "Test PATH variable", "echo $PATH", "/bin:/sbin:/usr/bin:/usr/sbin", "PATH variable not set correctly"],

    # Bash completion tests
    ["COMMAND_AND_ASSERT", "Check bash completion", "type _completion_loader", "_completion_loader is a function", "Bash completion not available"],
    ["COMMAND_AND_ASSERT", "Test completion files", "ls /usr/share/bash-completion/", "bash_completion", "Bash completion files not found"],

    # BeagleBone LED program tests
    ["COMMAND_AND_ASSERT", "Check LED blink program 1", "which bbb-02-led-blink", "/usr/bin/bbb-02-led-blink", "bbb-02-led-blink not found"],
    ["COMMAND_AND_ASSERT", "Check LED blink program 2", "which bbb-03-led-blink-nolibc", "/usr/bin/bbb-03-led-blink-nolibc", "bbb-03-led-blink-nolibc not found"],

    # Systemd tests
    ["COMMAND_AND_ASSERT", "Check systemd status", "systemctl is-system-running", "running", "Systemd not running properly"],
    ["COMMAND_AND_ASSERT", "Check init process", "ps -p 1", "systemd", "Systemd not PID 1"],

    # File system tests
    ["COMMAND_AND_ASSERT", "Test file creation", "touch /tmp/test && ls /tmp/test", "/tmp/test", "File creation failed"],
    ["COMMAND_AND_ASSERT", "Test file removal", "rm /tmp/test && test ! -f /tmp/test && echo 'removed'", "removed", "File removal failed"],

    # Network utilities test (NFS)
    ["COMMAND_AND_ASSERT", "Check NFS utilities", "which mount.nfs", "/sbin/mount.nfs", "NFS utilities not found"],

    # System information
    ["COMMAND_AND_EXTRACT", "Check kernel version", "uname -r", "6.", "Kernel version check failed", {"extract_pattern": "6."}],
    ["COMMAND_AND_EXTRACT", "Check system uptime", "uptime", "up", "Uptime check failed", {"extract_pattern": "up"}],
    ["COMMAND_AND_EXTRACT", "Check memory info", "free -h", "Mem:", "Memory info check failed", {"extract_pattern": "Mem:"}],

    # Advanced bash features
    ["COMMAND_AND_ASSERT", "Test command history", "history | tail -1", "history", "Command history not working"],
    ["COMMAND_AND_ASSERT", "Test bash variables", "TEST_VAR=hello && echo $TEST_VAR", "hello", "Bash variables not working"],
    ["COMMAND_AND_ASSERT", "Test command substitution", "echo $(whoami)", "srk", "Command substitution not working"],

]