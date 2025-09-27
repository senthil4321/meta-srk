#!/usr/bin/env python3
"""
Serial Test Script for SRK Target Device over Remote SSH
Connects to remote host and accesses serial device using socat
Tests include hello application, system info, LED control, EEPROM access, and RTC functionality

Version: 1.4.0
Author: SRK Development Team
Cop        elif test_type == "COMMAND_AND_EXTRACT":
            # Send command and extract specific information
            tester.send_command(command + "\r\n")
            timeout = kwargs.get('timeout', 10)
            output = tester.read_until(tester.prompt, timeout)
            try:
                if expected and assert_in(expected, output):
                    # Extract value based on pattern
                    extract_pattern = kwargs.get('extract_pattern', expected)
                    if extract_pattern in output:
                        # Simple extraction - can be made more sophisticated
                        parts = output.split(extract_pattern)
                        if len(parts) > 1:
                            value = parts[1].split()[0] if len(parts[1].split()) > 0 else "Unknown"
                            return (True, value)
                return (False, "Unknown")
            except AssertionError:
                return (False, "Unknown") SRK. All rights reserved.
License: MIT
"""

__version__ = "1.8.0"
__author__ = "SRK Development Team"
__copyright__ = "Copyright (c) 2025 SRK. All rights reserved."
__license__ = "MIT"

import time
import sys
import argparse
import paramiko
import threading
import queue
import warnings
import subprocess
from test_report import TestReportGenerator

# Suppress deprecation warnings from Paramiko
warnings.filterwarnings("ignore", category=DeprecationWarning)

def assert_in(expected, buffer):
    if expected not in buffer:
        raise AssertionError(f"Expected '{expected}' not found in:\r\n{buffer[-200:]}")
    return True

def reset_bbb():
    """Reset the BeagleBone Black using the remote reset script"""
    try:
        print("🔄 Resetting BBB before starting tests...")
        result = subprocess.run(['./13_remote_reset_bbb.sh'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ BBB reset successful")
            time.sleep(10)  # Wait for BBB to reboot
            return True
        else:
            print(f"❌ BBB reset failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ BBB reset timed out")
        return False
    except FileNotFoundError:
        print("❌ Reset script not found. Please ensure 13_remote_reset_bbb.sh exists")
        return False
    except Exception as e:
        print(f"❌ BBB reset error: {e}")
        return False

class RemoteSerialTester:
    def __init__(self, host, user, port='/dev/ttyUSB0', baudrate=115200, timeout=5, prompt='beaglebone-yocto:~$'):
        self.host = host
        self.user = user
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.prompt = prompt
        self.login_prompt = "beaglebone-yocto login:"
        self.client = None
        self.channel = None
        self.output_queue = queue.Queue()
        self.last_command = None
        self.running = False

    def connect(self):
        """Establish SSH connection and start socat over serial"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, username=self.user)  # SSH keys (~/.ssh/id_rsa)

            # Open an interactive shell (pseudo-terminal)
            self.channel = self.client.invoke_shell()
            time.sleep(1)

            # Launch socat with CRLF translation for proper Enter
            cmd = f"socat - {self.port},b{self.baudrate},raw,echo=0,crnl\n"
            self.channel.send(cmd)

            # Start background thread to read output
            threading.Thread(target=self._reader, daemon=True).start()

            print(f"Connected to {self.host}:{self.port} at {self.baudrate} baud over SSH using socat")
            return True
        except Exception as e:
            print(f"Failed to connect via SSH: {e}")
            return False

    def _reader(self):
        """Background thread to capture remote output"""
        buffer = ""
        while self.channel and not self.channel.closed:
            if self.channel.recv_ready():
                data = self.channel.recv(1024).decode("utf-8", errors="ignore")
                self.output_queue.put(data)
            time.sleep(0.1)

    def get_buffer(self):
        """Get all available data from the output queue"""
        buffer = ""
        while not self.output_queue.empty():
            try:
                data = self.output_queue.get_nowait()
                buffer += data
            except queue.Empty:
                break
        return buffer

    def disconnect(self):
        """Close SSH connection"""
        if self.channel:
            self.channel.close()
        if self.client:
            self.client.close()
        print("SSH connection closed")

    def read_until(self, expected_text, timeout=10):
        """Read from serial until expected text is found"""
        buffer = ""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data = self.output_queue.get(timeout=0.5)
                buffer += data
                print(f"Received: {data.strip()}")
                # Strip echoed command if present
                if self.last_command and buffer.strip().startswith(self.last_command):
                    cmd_end = buffer.find('\r\n', len(self.last_command))
                    if cmd_end != -1:
                        buffer = buffer[cmd_end + 1:]
                        self.last_command = None  # Clear after stripping
                if expected_text in buffer:
                    return buffer
            except queue.Empty:
                pass
        print(f"Timeout waiting for: {expected_text}")
        return buffer

    def send_command(self, command):
        """Send command to serial device through socat"""
        if self.channel:
            # With socat, we can send directly through the channel
            self.channel.send(command)
            self.last_command = command.strip()
            print(f"Sent: {command}")
            time.sleep(1)  # Give time for command to be processed

    def wait_for_initial_prompt(self):
        """Wait for login prompt or shell prompt if already logged in"""
        print("\n1. Waiting for login prompt...")
        login_found = False
        already_logged_in = False
        combined_buffer = ""
        start_time = time.time()
        last_data_time = start_time

        while time.time() - start_time < 90:  # 90 second timeout
            try:
                data = self.output_queue.get(timeout=1.0)
                combined_buffer += data
                print(f"Received: {data.strip()}")
                last_data_time = time.time()

                if not login_found and self.login_prompt in combined_buffer:
                    login_found = True
                    print("✓ Login prompt detected")
                    break

                if not already_logged_in and self.prompt in combined_buffer:
                    already_logged_in = True
                    print("✓ Already logged in, shell prompt detected")
                    break

            except queue.Empty:
                # If no data for 5 seconds, send enter to refresh prompt
                if time.time() - last_data_time > 5 and not login_found and not already_logged_in:
                    print("No activity detected, sending enter to refresh prompt...")
                    if self.channel:
                        self.channel.send("\n")
                    last_data_time = time.time()
                continue

        if not login_found and not already_logged_in:
            print("ERROR: Neither login prompt nor shell prompt found")
            return False, False

        return login_found, already_logged_in

    def perform_login(self):
        """Send username, handle password if needed, and wait for shell prompt"""
        print("\r\n2. Sending username 'srk'...")
        if self.channel:
            self.channel.send("srk\r\n")
            print("Sent: srk")
            time.sleep(1)

        print("3. Waiting for password prompt or shell prompt...")
        buffer = ""
        start_time = time.time()
        password_sent = False
        while time.time() - start_time < 30:
            try:
                data = self.output_queue.get(timeout=0.5)
                buffer += data
                print(f"Received: {data.strip()}")
                if "Password:" in buffer and not password_sent:
                    print("✓ Password prompt detected, sending empty password")
                    if self.channel:
                        self.channel.send("\r\n")
                    password_sent = True
                if self.prompt in buffer:
                    print("✓ Shell prompt detected")
                    break
            except queue.Empty:
                pass
        else:
            print("ERROR: Timeout waiting for shell prompt")
            return False

        if self.prompt not in buffer:
            print("ERROR: Shell prompt not found")
            return False

        return True

import unittest

def run_generic_test(tester, test_config):
    """
    Generic test runner that handles different test types
    test_config format: [test_type, command, expected_value, failure_message, **kwargs]
    Returns: (success: bool, message: str)
    """
    test_type = test_config[0]
    command = test_config[1] if len(test_config) > 1 else None
    expected = test_config[2] if len(test_config) > 2 else None
    failure_msg = test_config[3] if len(test_config) > 3 else "Test failed"
    kwargs = test_config[4] if len(test_config) > 4 else {}

    # Replace {PROMPT} placeholder with actual prompt
    if expected and isinstance(expected, str):
        expected = expected.replace("{PROMPT}", tester.prompt)
    if isinstance(expected, list):
        expected = [e.replace("{PROMPT}", tester.prompt) if isinstance(e, str) else e for e in expected]

    try:
        if test_type == "ASSERT_IN_BUFFER":
            # Check if expected string exists in current buffer
            try:
                assert_in(expected, tester.get_buffer())
                return (True, expected)
            except AssertionError:
                return (False, failure_msg)

        elif test_type == "SEND_COMMAND":
            # Send a command without expecting specific output
            tester.send_command(command + "\r\n")
            return (True, "Command sent")

        elif test_type == "COMMAND_AND_ASSERT":
            # Send command and check for expected string in response
            tester.send_command(command + "\r\n")
            timeout = kwargs.get('timeout', 10)
            output = tester.read_until(tester.prompt, timeout)
            try:
                assert_in(expected, output)
                return (True, "OK")
            except AssertionError:
                return (False, failure_msg)

        elif test_type == "COMMAND_AND_VERIFY_MULTIPLE":
            # Send command and verify multiple expected strings
            tester.send_command(command + "\r\n")
            timeout = kwargs.get('timeout', 10)
            output = tester.read_until(tester.prompt, timeout)
            expected_lines = expected if isinstance(expected, list) else [expected]
            try:
                for line in expected_lines:
                    assert_in(line, output)
                return (True, "OK")
            except AssertionError:
                return (False, failure_msg)

        elif test_type == "COMMAND_AND_EXTRACT":
            # Send command and extract specific information
            tester.send_command(command + "\r\n")
            timeout = kwargs.get('timeout', 10)
            output = tester.read_until(tester.prompt, timeout)
            if expected and assert_in(expected, output):
                # Extract value based on pattern
                extract_pattern = kwargs.get('extract_pattern', expected)
                if extract_pattern in output:
                    # Simple extraction - can be made more sophisticated
                    parts = output.split(extract_pattern)
                    if len(parts) > 1:
                        value = parts[1].split()[0] if len(parts[1].split()) > 0 else "Unknown"
                        return (True, value)
            return (False, "Unknown")

        elif test_type == "WAIT_FOR_CONDITION":
            # Wait for a specific condition
            timeout = kwargs.get('timeout', 30)
            start_time = time.time()
            while time.time() - start_time < timeout:
                if expected in tester.get_buffer():
                    return (True, "Condition met")
                time.sleep(0.5)
            return (False, failure_msg)

        elif test_type == "WAIT":
            # Wait for a specified duration
            wait_duration = kwargs.get('duration', 'short')
            if wait_duration == 'very_short':
                wait_time = 1
            elif wait_duration == 'short':
                wait_time = 5
            elif wait_duration == 'medium':
                wait_time = 10
            else:
                wait_time = 5  # default to short
            
            print(f"⏳ Waiting {wait_duration} ({wait_time}s)...")
            time.sleep(wait_time)
            return (True, f"Waited {wait_duration} ({wait_time}s)")

        elif test_type == "HARDWARE_CHECK":
            # Check hardware availability
            tester.send_command(command + "\r\n")
            timeout = kwargs.get('timeout', 10)
            output = tester.read_until(tester.prompt, timeout)
            if expected:
                try:
                    assert_in(expected, output)
                    return (True, "Hardware found")
                except AssertionError:
                    return (False, "Hardware not found")
            else:
                # If no expected pattern, just check if we got any output
                if len(output.strip()) > 0:
                    return (True, "Hardware found")
                else:
                    return (False, "Hardware not found")

        elif test_type == "HARDWARE_TEST":
            # Test hardware functionality
            if isinstance(command, list):
                # Multiple commands for hardware test
                for cmd in command:
                    tester.send_command(cmd + "\r\n")
                    if 'sleep' in kwargs:
                        time.sleep(kwargs['sleep'])
                timeout = kwargs.get('timeout', 10)
                output = tester.read_until(tester.prompt, timeout)
                if expected:
                    try:
                        assert_in(expected, output)
                        return (True, "Hardware test OK")
                    except AssertionError:
                        return (False, failure_msg)
                else:
                    return (True, "Hardware test completed")
            else:
                # Single command hardware test
                tester.send_command(command + "\r\n")
                timeout = kwargs.get('timeout', 10)
                output = tester.read_until(tester.prompt, timeout)
                if expected:
                    try:
                        assert_in(expected, output)
                        return (True, "Hardware test OK")
                    except AssertionError:
                        return (False, failure_msg)
                else:
                    return (True, "Hardware test completed")

        elif test_type == "RESET_TARGET":
            # Reset the target device
            if reset_bbb():
                return (True, "Target reset successful")
            return (False, failure_msg)

        else:
            return (False, f"Unknown test type: {test_type}")

    except Exception as e:
        return (False, f"Test error: {str(e)}")

# Define test suites with generic format
DEFAULT_TEST_SUITE = [
    # [test_type, command, expected_value, failure_message, kwargs]

    # Reset BBB before starting tests
    ["RESET_TARGET", None, None, "Target reset failed"],

    # Base system checks
    ["ASSERT_IN_BUFFER", None, "U-Boot", "U-Boot not found in logs"],
    ["ASSERT_IN_BUFFER", None, "Linux version", "Kernel logs not found"],
    ["ASSERT_IN_BUFFER", None, "initramfs", "Initramfs logs not found"],
    ["WAIT_FOR_CONDITION", None, "beaglebone-yocto login:|beaglebone-yocto{PROMPT}", "No login or shell prompt found", {"timeout": 90}],

    # Detailed login steps - simplified for generic format
    ["SEND_COMMAND", "srk", None, "Username sent"],
    ["SEND_COMMAND", "", None, "Password sent"],
    ["WAIT_FOR_CONDITION", None, "beaglebone-yocto{PROMPT}", "Shell prompt not found", {"timeout": 30}],
    ["ASSERT_IN_BUFFER", None, "beaglebone-yocto:", "Login verification failed"],

    # Application tests
    ["COMMAND_AND_ASSERT", "which hello", "hello", "Hello binary not found"],
    ["COMMAND_AND_VERIFY_MULTIPLE", "hello", [
        "Hello, World! from meta-srk layer and recipes-srk V2!!!",
        "Hello, World! 20SEP2025 07:28 !!!",
        "Hello, World! 20SEP2025 23:50 !!!"
    ], "Hello output verification failed"],

    # System information tests
    ["COMMAND_AND_EXTRACT", "uname -a", "Linux", "Build version check failed", {"extract_pattern": "Linux"}],
    ["COMMAND_AND_EXTRACT", "uname -v", "#", "Build time check failed", {"extract_pattern": "#"}],
    ["COMMAND_AND_EXTRACT", "cat /etc/timestamp 2>/dev/null || date -r /etc/issue", None, "Timestamp check failed"],
    ["COMMAND_AND_EXTRACT", "uptime", "up", "Uptime check failed", {"extract_pattern": "up"}],
    ["COMMAND_AND_EXTRACT", "busybox", "BusyBox", "BusyBox version check failed", {"extract_pattern": "BusyBox"}],

    # Init system check (default: expects systemd or init)
    ["COMMAND_AND_ASSERT", "ps -p 1", "systemd", "Init system check failed"],

    # Security tests
    ["COMMAND_AND_ASSERT", "which cryptsetup", "cryptsetup", "Encryption support check failed"],
]

IMAGE_11_TEST_SUITE = [
    # [test_type, command, expected_value, failure_message, kwargs]

    # Reset BBB before starting tests
    # ["RESET_TARGET", None, None, "Target reset failed"],
    # ["WAIT", None, None, None, {"duration": "medium"}],
    # Detailed login steps - simplified for generic format
    # ["WAIT_FOR_CONDITION", None, "{PROMPT}", "Shell prompt not found", {"timeout": 30}],

    # Hardware-specific tests
    ["COMMAND_AND_ASSERT", "which bbb-02-rtc", "bbb-02-rtc", "RTC binary not found"],
    ["COMMAND_AND_ASSERT", "bbb-02-rtc read", "RTC Time:", "RTC read test failed"],
    ["COMMAND_AND_ASSERT", "bbb-02-rtc info", "RTC Device:", "RTC info test failed"],

    # System information tests
    ["COMMAND_AND_EXTRACT", "uname -a", "Linux", "Build version check failed", {"extract_pattern": "Linux"}],
    ["COMMAND_AND_EXTRACT", "uname -v", "#", "Build time check failed", {"extract_pattern": "#"}],
    ["COMMAND_AND_EXTRACT", "cat /etc/timestamp 2>/dev/null || date -r /etc/issue", None, "Timestamp check failed"],
    ["COMMAND_AND_EXTRACT", "uptime", "up", "Uptime check failed", {"extract_pattern": "up"}],
    ["COMMAND_AND_EXTRACT", "busybox", "BusyBox", "BusyBox version check failed", {"extract_pattern": "BusyBox"}],
]

class TestSerialHello(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_type = None

    def setUp(self):
        # Determine prompt based on image type (passed via command line)
        prompt = "# " if self.image_type == "11" else "beaglebone-yocto:~$"

        self.tester = RemoteSerialTester(
            host='192.168.1.100',
            user='pi',
            port='/dev/ttyUSB0',
            baudrate=115200,
            timeout=5,
            prompt=prompt
        )
        self.assertTrue(self.tester.connect(), "Failed to establish SSH connection")

    def tearDown(self):
        self.tester.disconnect()

    def run_all_tests(self, image_type=None):
        # Select test suite based on image type
        if image_type == "11":
            steps = IMAGE_11_TEST_SUITE
            print("🧪 Running IMAGE_11_TEST_SUITE (includes hardware tests)")
        else:
            steps = DEFAULT_TEST_SUITE
            print("🧪 Running DEFAULT_TEST_SUITE (minimal test set)")

        non_blocking = ["ASSERT_IN_BUFFER", "HARDWARE_CHECK", "WAIT_FOR_CONDITION", "WAIT"]
        results = []

        for i, test_config in enumerate(steps):
            # Create a descriptive name for the test
            test_type = test_config[0]
            command = test_config[1] if len(test_config) > 1 and test_config[1] else "N/A"
            expected = test_config[2] if len(test_config) > 2 and test_config[2] else "N/A"

            # Generate human-readable test name
            if test_type == "ASSERT_IN_BUFFER":
                name = f"Check for '{expected}' in buffer"
            elif test_type == "SEND_COMMAND":
                name = f"Send command: {command}"
            elif test_type == "COMMAND_AND_ASSERT":
                name = f"Run '{command}' and check for '{expected}'"
            elif test_type == "COMMAND_AND_VERIFY_MULTIPLE":
                name = f"Run '{command}' and verify multiple patterns"
            elif test_type == "COMMAND_AND_EXTRACT":
                name = f"Run '{command}' and extract info"
            elif test_type == "WAIT_FOR_CONDITION":
                name = f"Wait for condition: {expected}"
            elif test_type == "CONDITIONAL_SEND":
                name = f"Conditionally send: {command}"
            elif test_type == "HARDWARE_CHECK":
                name = f"Hardware check: {command}"
            elif test_type == "HARDWARE_TEST":
                name = f"Hardware test: {command}"
            elif test_type == "RESET_TARGET":
                name = "Reset Target Device"
            elif test_type == "WAIT":
                duration = test_config[4].get('duration', 'short') if len(test_config) > 4 and test_config[4] else 'short'
                name = f"Wait {duration}"
            else:
                name = f"{test_type}: {command or 'N/A'}"

            print(f"\r\n➡️ Step {i+1}: {name}")
            success, message = run_generic_test(self.tester, test_config)
            results.append((name, success, message))
            if success:
                print(f"✅ PASS: {name} - {message}")
            else:
                print(f"❌ FAIL: {name} - {message}")
                if test_type not in ["ASSERT_IN_BUFFER", "HARDWARE_CHECK", "WAIT_FOR_CONDITION"]:
                    break  # stop on failure for strict ordering, except for non-blocking tests

        # Generate and print report
        report_generator = TestReportGenerator()
        non_blocking_names = [name for name, _, _ in results if any(nb in name for nb in ["Check for", "Hardware check", "Wait for", "Reset"])]
        report_generator.print_report(results, non_blocking_names)
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SRK Serial Test Script")
    parser.add_argument("--save-report", type=str, help="Save test report to specified file")
    parser.add_argument("--image-type", type=str, help="Image type (e.g., 11 for bbb-examples, affects test selection)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    tester = TestSerialHello()
    tester.image_type = args.image_type  # Set image type before setup
    tester.setUp()
    try:
        results = tester.run_all_tests(args.image_type)
        if args.save_report:
            report_generator = TestReportGenerator()
            report_generator.save_report_to_file(results, args.save_report, ["Check for", "Hardware check", "Wait for", "Wait"])
    finally:
        tester.tearDown()