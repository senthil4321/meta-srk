#!/usr/bin/env python3
"""
Serial Test Script for SRK Target Device over Remote SSH
Connects to remote host and accesses serial device using socat

Version: 1.3.0
Author: SRK Development Team
Copyright (c) 2025 SRK. All rights reserved.
License: MIT
"""

__version__ = "1.3.0"
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
from test_report import TestReportGenerator

# Suppress deprecation warnings from Paramiko
warnings.filterwarnings("ignore", category=DeprecationWarning)

def assert_in(expected, buffer):
    if expected not in buffer:
        raise AssertionError(f"Expected '{expected}' not found in:\n{buffer[-200:]}")
    return True

def assert_prompt(tester, timeout=10):
    buf = tester.read_until("beaglebone-yocto:~$", timeout=timeout)
    if "beaglebone-yocto:~$" not in buf:
        raise AssertionError("Shell prompt not detected")
    return True

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
        # Define test steps
        steps = [
            ("Check U-Boot logs", lambda t: assert_in("U-Boot", t.get_buffer())),
            ("Check kernel logs", lambda t: assert_in("Linux version", t.get_buffer())),
            ("Check initramfs logs", lambda t: assert_in("initramfs", t.get_buffer())),
            ("Wait for initial prompt", lambda t: (result := t.wait_for_initial_prompt(), setattr(t, 'already_logged_in', result[1]), result[0] or result[1])[2]),
            ("Perform login", lambda t: t.perform_login() if not getattr(t, 'already_logged_in', False) else True),
            ("Check hello exists", lambda t: (t.send_command("which hello"), assert_in("hello", t.read_until("beaglebone-yocto:~$", 10)))[1]),
            ("Run and verify hello", lambda t: (t.send_command("hello"), output := t.read_until("beaglebone-yocto:~$", 10), all(assert_in(line, output) for line in [
                "Hello, World! from meta-srk layer and recipes-srk V2!!!",
                "Hello, World! 20SEP2025 07:28 !!!",
                "Hello, World! 20SEP2025 23:50 !!!"
            ]))[2]),
            ("Check build version", lambda t: (t.send_command("uname -a"), assert_in("Linux", t.read_until("beaglebone-yocto:~$", 10)))[1]),
            ("Check build time", lambda t: (t.send_command("uname -v"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("#", output))[1]),
            ("Check system timestamp", lambda t: (t.send_command("cat /etc/timestamp 2>/dev/null || date -r /etc/issue"), output := t.read_until("beaglebone-yocto:~$", 10), len(output.strip()) > 0)[1]),
            ("Check system uptime", lambda t: (t.send_command("uptime"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("up", output))[1]),
            ("Check BusyBox version", lambda t: (t.send_command("busybox"), assert_in("BusyBox", t.read_until("beaglebone-yocto:~$", 10)))[1]),
        ]

        non_blocking = ["Check U-Boot logs", "Check kernel logs", "Check initramfs logs"]
        results = []

        for name, func in steps:
            print(f"\n➡️ Step: {name}")
            try:
                result = func(self.tester)
                results.append((name, True, "OK"))
                print(f"✅ PASS: {name}")
            except Exception as e:
                results.append((name, False, str(e)))
                print(f"❌ FAIL: {name} - {e}")
                if name not in non_blocking:
                    break  # stop on failure for strict ordering, except for non-blocking tests

        # Generate and print report
        report_generator = TestReportGenerator()
        report_generator.print_report(results, non_blocking)

        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SRK Serial Test Script")
    parser.add_argument("--save-report", type=str, help="Save test report to specified file")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    tester = TestSerialHello()
    tester.setUp()
    try:
        results = tester.run_all_tests()
        if args.save_report:
            report_generator = TestReportGenerator()
            report_generator.save_report_to_file(results, args.save_report, ["Check U-Boot logs", "Check kernel logs", "Check initramfs logs"])
    finally:
        tester.tearDown()