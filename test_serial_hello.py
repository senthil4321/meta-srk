#!/usr/bin/env python3
"""
Serial Test Script for SRK Target Device over Remote SSH
Connects to remote host and accesses serial device using socat
"""

import time
import sys
import argparse
import paramiko
import threading
import queue
import warnings

# Suppress deprecation warnings from Paramiko
warnings.filterwarnings("ignore", category=DeprecationWarning)
import warnings

# Suppress deprecation warnings from Paramiko
warnings.filterwarnings("ignore", category=DeprecationWarning)

class RemoteSerialTester:
    def __init__(self, host, user, port='/dev/ttyUSB0', baudrate=115200, timeout=5):
        self.host = host
        self.user = user
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.client = None
        self.channel = None
        self.output_queue = queue.Queue()

    def connect(self):
        """Establish SSH connection and configure serial"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, username=self.user)  # uses default SSH keys (~/.ssh/id_rsa)

            # Open an interactive shell
            self.channel = self.client.invoke_shell()
            time.sleep(1)

            # Use socat for reliable bidirectional serial communication
            cmd = f"socat - /dev/ttyUSB0,b{self.baudrate},raw,echo=0"
            self.channel.send(cmd + "\n")

            # Start background reader
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
            self.channel.send(command + "\n")
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

                if not login_found and "beaglebone-yocto login:" in combined_buffer:
                    login_found = True
                    print("✓ Login prompt detected")
                    break

                if not already_logged_in and "beaglebone-yocto:~$" in combined_buffer:
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
        print("\n2. Sending username 'srk'...")
        if self.channel:
            self.channel.send("srk\n")
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
                        self.channel.send("\n")
                    password_sent = True
                if "beaglebone-yocto:~$" in buffer:
                    print("✓ Shell prompt detected")
                    break
            except queue.Empty:
                pass
        else:
            print("ERROR: Timeout waiting for shell prompt")
            return False

        if "beaglebone-yocto:" not in buffer:
            print("ERROR: Shell prompt not found")
            return False

        return True

    def check_hello_exists(self):
        """Check if hello command exists on the system"""
        print("\n4. Checking if hello command exists...")
        self.send_command("which hello")
        which_output = self.read_until("beaglebone-yocto:~$", timeout=10)
        if "hello" not in which_output:
            print("ERROR: hello command not found on target system")
            return False
        print("✓ hello command found")
        return True

    def run_and_verify_hello(self):
        """Run hello command and verify its output"""
        print("5. Running 'hello' command...")
        self.send_command("hello")

        print("6. Capturing hello command output...")
        output = ""
        for _ in range(10):
            try:
                data = self.output_queue.get(timeout=0.5)
                output += data
                print(f"Received: {data.strip()}")
            except queue.Empty:
                break

        # Also try to read until we get a shell prompt to make sure command completed
        remaining_output = self.read_until("beaglebone-yocto:~$", timeout=5)
        output += remaining_output

        expected_lines = [
            "Hello, World! from meta-srk layer and recipes-srk V2!!!",
            "Hello, World! 20SEP2025 07:28 !!!",
            "Hello, World! 20SEP2025 23:50 !!!"
        ]

        print("\n7. Verifying output...")
        success = True
        for line in expected_lines:
            if line in output:
                print(f"✓ Found: {line}")
            else:
                print(f"✗ Missing: {line}")
                success = False

        if success:
            return True
        else:
            print("\n❌ TEST FAILED: Some expected output missing")
            return False

import unittest

class TestSerialHello(unittest.TestCase):
    def setUp(self):
        self.tester = RemoteSerialTester(
            host='192.168.1.100',
            user='pi',
            port='/dev/ttyUSB0',
            baudrate=115200,
            timeout=5
        )
        self.assertTrue(self.tester.connect(), "Failed to establish SSH connection")

    def tearDown(self):
        self.tester.disconnect()

    def run_all_tests(self):
        tests = [
            ("check_uboot_logs", self.test_00_check_uboot_logs),
            ("check_kernel_logs", self.test_00_check_kernel_logs),
            ("check_initramfs_logs", self.test_00_check_initramfs_logs),
            ("wait_for_initial_prompt", self.test_01_wait_for_initial_prompt),
            ("perform_login", self.test_02_perform_login),
            ("check_hello_exists", self.test_03_check_hello_exists),
            ("run_and_verify_hello", self.test_04_run_and_verify_hello),
        ]
        non_blocking = ["check_uboot_logs", "check_kernel_logs", "check_initramfs_logs"]
        results = []
        for name, func in tests:
            print(f"\n➡️ Step: {name}")
            try:
                func()
                results.append((name, True, "OK"))
                print(f"✅ PASS: {name}")
            except unittest.SkipTest:
                results.append((name, True, "SKIPPED"))
                print(f"⏭️ SKIP: {name}")
            except Exception as e:
                results.append((name, False, str(e)))
                print(f"❌ FAIL: {name} - {e}")
                if name not in non_blocking:
                    break  # stop on failure for strict ordering, except for non-blocking tests

        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        # Define colored icons
        green_check = "\033[92m✅\033[0m"
        red_x = "\033[91m❌\033[0m"
        yellow_warn = "\033[93m⚠️\033[0m"
        blue_skip = "\033[94m⏭️\033[0m"
        
        # Table header
        print(f"{'#':<3} | {'Test Name':<30} | {'Status':<20} | {'Message':<40}")
        print("-" * 97)
        
        counter = 1
        for name, passed, msg in results:
            if msg == "SKIPPED":
                status = f"{blue_skip} SKIP"
            elif passed:
                status = f"{green_check} PASS"
            else:
                if name in non_blocking:
                    status = f"{yellow_warn} NON-BLOCK FAIL"
                else:
                    status = f"{red_x} FAIL"
            
            # Truncate name and msg if too long
            name_display = name[:28] + "..." if len(name) > 28 else name
            msg_display = msg[:38] + "..." if len(msg) > 38 else msg
            
            print(f"{counter:<3} | {name_display:<30} | {status:<20} | {msg_display:<40}")
            counter += 1
        
        print("-" * 97)
        
        total = len(results)
        passed_count = sum(1 for _, p, _ in results if p)
        failed_count = sum(1 for name, p, _ in results if not p and name not in non_blocking)
        warning_count = sum(1 for name, p, _ in results if not p and name in non_blocking)
        print(f"\nTotal: {total}, Passed: {passed_count}, Failed: {failed_count}, Warnings: {warning_count}")

    def test_00_check_uboot_logs(self):
        """Test for U-Boot logs in serial output"""
        buffer = self.tester.get_buffer()
        assert "U-Boot" in buffer, "U-Boot logs not found in serial output"

    def test_00_check_kernel_logs(self):
        """Test for kernel logs in serial output"""
        buffer = self.tester.get_buffer()
        assert "Linux version" in buffer, "Kernel logs not found in serial output"

    def test_00_check_initramfs_logs(self):
        """Test for initramfs logs in serial output"""
        buffer = self.tester.get_buffer()
        assert "initramfs" in buffer, "Initramfs logs not found in serial output"

    def test_01_wait_for_initial_prompt(self):
        """Test waiting for login or shell prompt"""
        login_found, already_logged_in = self.tester.wait_for_initial_prompt()
        assert login_found or already_logged_in, "Neither login prompt nor shell prompt detected"
        self.already_logged_in = already_logged_in

    def test_02_perform_login(self):
        """Test performing login if not already logged in"""
        if self.already_logged_in:
            raise unittest.SkipTest("System is already logged in, skipping login test")
        success = self.tester.perform_login()
        assert success, "Login process failed"

    def test_03_check_hello_exists(self):
        """Test checking if hello command exists"""
        success = self.tester.check_hello_exists()
        assert success, "Hello command not found on the system"

    def test_04_run_and_verify_hello(self):
        """Test running hello command and verifying output"""
        success = self.tester.run_and_verify_hello()
        assert success, "Hello command output verification failed"


if __name__ == "__main__":
    tester = TestSerialHello()
    tester.setUp()
    try:
        tester.run_all_tests()
    finally:
        tester.tearDown()