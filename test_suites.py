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
    ["COMMAND_AND_ASSERT", "Check RTC binary", "which bbb-02-rtc", "bbb-02-rtc", "RTC binary not found"],
    ["COMMAND_AND_ASSERT", "Test RTC read", "bbb-02-rtc read", "RTC Time:", "RTC read test failed"],
    ["COMMAND_AND_ASSERT", "Test RTC info", "bbb-02-rtc info", "RTC Device:", "RTC info test failed"],

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