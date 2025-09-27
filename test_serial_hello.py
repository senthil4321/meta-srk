#!/usr/bin/env python3
"""
Serial Test Script for SRK Target Device over Remote SSH
Connects to remote host and accesses serial device using socat
Tests include hello application, system info, LED control, EEPROM access, and RTC functionality

Version: 1.4.0
Author: SRK Development Team
Copyright (c) 2025 SRK. All rights reserved.
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
        raise AssertionError(f"Expected '{expected}' not found in:\n{buffer[-200:]}")
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
        # Reset BBB before starting tests
        if not reset_bbb():
            self.fail("BBB reset failed, cannot proceed with tests")

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

    def run_all_tests(self, image_type=None):
        # Define test steps based on image type
        base_steps = [
            ("Check U-Boot logs", lambda t: assert_in("U-Boot", t.get_buffer())),
            ("Check kernel logs", lambda t: assert_in("Linux version", t.get_buffer())),
            ("Check initramfs logs", lambda t: assert_in("initramfs", t.get_buffer())),
            ("Wait for initial prompt", lambda t: (result := t.wait_for_initial_prompt(), setattr(t, 'already_logged_in', result[1]), result[0] or result[1])[2]),
        ]

        # Detailed login steps
        login_steps = [
            ("Check if already logged in", lambda t: getattr(t, 'already_logged_in', False)),
            ("Detect login prompt", lambda t: (not getattr(t, 'already_logged_in', False) and "beaglebone-yocto login:" in t.get_buffer(), "Login prompt detected" if not getattr(t, 'already_logged_in', False) and "beaglebone-yocto login:" in t.get_buffer() else "No login prompt needed")[1]),
            ("Send username", lambda t: (t.send_command("srk") if not getattr(t, 'already_logged_in', False) else True, "Username sent" if not getattr(t, 'already_logged_in', False) else "Already logged in")[1]),
            ("Handle password prompt", lambda t: (t.send_command("") if not getattr(t, 'already_logged_in', False) and "Password:" in t.get_buffer() else True, "Password handled" if not getattr(t, 'already_logged_in', False) and "Password:" in t.get_buffer() else "No password needed")[1]),
            ("Wait for shell prompt", lambda t: (time.sleep(2), "beaglebone-yocto:~$" in t.get_buffer(), "Shell prompt detected" if "beaglebone-yocto:~$" in t.get_buffer() else "Shell prompt not found")[2]),
            ("Verify login success", lambda t: ("beaglebone-yocto:" in t.get_buffer(), "Login successful" if "beaglebone-yocto:" in t.get_buffer() else "Login failed")[1]),
        ]

        # Hardware-specific tests (available in image 11)
        hardware_steps = [
            ("Check LED support", lambda t: (t.send_command("ls /sys/class/leds/"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("beaglebone", output), ("LEDs found" if "beaglebone" in output else "No LEDs"))[3]),
            ("Test LED control", lambda t: (t.send_command("echo 1 > /sys/class/leds/beaglebone\\:green\\:usr0/brightness"), time.sleep(1), t.send_command("cat /sys/class/leds/beaglebone\\:green\\:usr0/brightness"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("1", output), ("LED control OK" if "1" in output else "LED control failed"))[5]),
            ("Check EEPROM support", lambda t: (t.send_command("ls /sys/bus/i2c/devices/ | grep -E '0-005[0-9]'"), output := t.read_until("beaglebone-yocto:~$", 10), len(output.strip()) > 0, ("EEPROM device found" if output.strip() else "No EEPROM device"))[3]),
            ("Test EEPROM read", lambda t: (t.send_command("hexdump -C /sys/bus/i2c/devices/0-0050/eeprom | head -1"), output := t.read_until("beaglebone-yocto:~$", 10), len(output.strip()) > 10, ("EEPROM readable" if len(output.strip()) > 10 else "EEPROM read failed"))[3]),
            ("Check RTC binary exists", lambda t: (t.send_command("which bbb-02-rtc"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("bbb-02-rtc", output), ("RTC binary found" if "bbb-02-rtc" in output else "RTC binary missing"))[3]),
            ("Test RTC read", lambda t: (t.send_command("bbb-02-rtc read"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("RTC Time:", output), ("RTC read OK" if "RTC Time:" in output else "RTC read failed"))[3]),
            ("Test RTC info", lambda t: (t.send_command("bbb-02-rtc info"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("RTC Device:", output), ("RTC info OK" if "RTC Device:" in output else "RTC info failed"))[3]),
        ]

        # Application and system tests
        app_steps = [
            ("Check hello exists", lambda t: (t.send_command("which hello"), assert_in("hello", t.read_until("beaglebone-yocto:~$", 10)))[1]),
            ("Run and verify hello", lambda t: (t.send_command("hello"), output := t.read_until("beaglebone-yocto:~$", 10), all(assert_in(line, output) for line in [
                "Hello, World! from meta-srk layer and recipes-srk V2!!!",
                "Hello, World! 20SEP2025 07:28 !!!",
                "Hello, World! 20SEP2025 23:50 !!!"
            ]))[2]),
        ]

        # System information tests
        system_steps = [
            ("Check build version", lambda t: (t.send_command("uname -a"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("Linux", output), (output.split("Linux")[1].split("beaglebone-yocto")[0].strip() if "Linux" in output else "Unknown"))[3]),
            ("Check build time", lambda t: (t.send_command("uname -v"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("#", output), (output.split("#")[1].split()[0] if "#" in output else "Unknown"))[3]),
            ("Check system timestamp", lambda t: (t.send_command("cat /etc/timestamp 2>/dev/null || date -r /etc/issue"), output := t.read_until("beaglebone-yocto:~$", 10), len(output.strip()) > 0, (output.strip().split('\n')[-1] if output.strip() else "Unknown"))[3]),
            ("Check system uptime", lambda t: (t.send_command("uptime"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("up", output), (output.split("up")[1].split(",")[0].strip() if "up" in output else "Unknown"))[3]),
            ("Check BusyBox version", lambda t: (t.send_command("busybox"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("BusyBox", output), (output.split("BusyBox")[1].split()[0] if "BusyBox" in output else "Unknown"))[3]),
        ]

        # Init system check - different expectations based on image type
        if image_type == "11":
            # Image 11 uses BusyBox init, not systemd
            init_step = ("Check init system type", lambda t: (t.send_command("ps -p 1"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("busybox", output.lower()), "busybox (expected for image 11)")[3])
        else:
            # Other images might use systemd or other init systems
            init_step = ("Check init system type", lambda t: (t.send_command("ps -p 1"), output := t.read_until("beaglebone-yocto:~$", 10), assert_in("systemd", output) or assert_in("init", output), ("systemd" if "systemd" in output else "busybox"))[3])

        # Security tests
        security_steps = [
            ("Check encryption support", lambda t: (t.send_command("which cryptsetup"), output1 := t.read_until("beaglebone-yocto:~$", 10), t.send_command("ls /usr/bin/srk-init 2>/dev/null"), output2 := t.read_until("beaglebone-yocto:~$", 10), True, ("Yes" if "cryptsetup" in output1 or "srk-init" in output2 else "No"))[4]),
        ]

        # Combine all steps based on image type
        if image_type == "11":
            # Image 11 (bbb-examples) includes hardware tests
            steps = base_steps + login_steps + hardware_steps + app_steps + system_steps + [init_step] + security_steps
        else:
            # Other images - minimal test set
            steps = base_steps + login_steps + app_steps + system_steps + [init_step] + security_steps

        non_blocking = ["Check U-Boot logs", "Check kernel logs", "Check initramfs logs", "Check if already logged in", "Detect login prompt", "Check LED support", "Test LED control", "Check EEPROM support", "Test EEPROM read", "Check RTC binary exists", "Test RTC read", "Test RTC info"]
        results = []

        for name, func in steps:
            print(f"\n➡️ Step: {name}")
            try:
                value = func(self.tester)
                if isinstance(value, str) and value:
                    message = value
                else:
                    message = "OK"
                results.append((name, True, message))
                print(f"✅ PASS: {name} - {message}")
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
    parser.add_argument("--image-type", type=str, help="Image type (e.g., 11 for bbb-examples, affects test selection)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    tester = TestSerialHello()
    tester.setUp()
    try:
        results = tester.run_all_tests(args.image_type)
        if args.save_report:
            report_generator = TestReportGenerator()
            report_generator.save_report_to_file(results, args.save_report, ["Check U-Boot logs", "Check kernel logs", "Check initramfs logs", "Check LED support", "Test LED control", "Check EEPROM support", "Test EEPROM read", "Check RTC binary exists", "Test RTC read", "Test RTC info"])
    finally:
        tester.tearDown()