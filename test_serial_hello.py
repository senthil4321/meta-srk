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

    def test_login_and_hello(self):
        """Main test logic"""
        print("Starting remote serial test for SRK target device...")
        print("=" * 50)

        if not self.connect():
            return False

        try:
            # Step 1: Wait for login prompt
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
                print(f"Last received data: {combined_buffer[-500:]}")  # Show last 500 chars
                return False

            if already_logged_in:
                print("Skipping login steps as system is already logged in")
            else:
                # Step 2: Send username
                print("\n2. Sending username 'srk'...")
                if self.channel:
                    self.channel.send("srk\n")
                    print("Sent: srk")
                    time.sleep(1)

                # Step 3: Wait for shell prompt
                print("3. Waiting for shell prompt...")
                shell_prompt = self.read_until("beaglebone-yocto:~$", timeout=30)
                if "beaglebone-yocto:" not in shell_prompt:
                    print("ERROR: Shell prompt not found")
                    print(f"Received data: {shell_prompt}")
                    return False
                print("✓ Shell prompt detected")

            # Step 4: Check if hello command exists
            print("\n4. Checking if hello command exists...")
            self.send_command("which hello")
            which_output = self.read_until("beaglebone-yocto:~$", timeout=10)
            if "hello" not in which_output:
                print("ERROR: hello command not found on target system")
                print(f"which output: {which_output}")
                return False
            print("✓ hello command found")

            # Step 5: Run hello command
            print("5. Running 'hello' command...")
            self.send_command("hello")

            # Step 6: Capture and verify output
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
                print("\n🎉 TEST PASSED: All expected output found!")
                return True
            else:
                print("\n❌ TEST FAILED: Some expected output missing")
                print(f"\nFull output received:\n{output}")
                return False

        except Exception as e:
            print(f"ERROR during test: {e}")
            return False
        finally:
            self.disconnect()


def main():
    parser = argparse.ArgumentParser(description='Test SRK target device via remote SSH serial')
    parser.add_argument('--host', default='192.168.1.100', help='Remote host IP (default: 192.168.1.100)')
    parser.add_argument('--user', default='pi', help='SSH username (default: pi)')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port on remote host (default: /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--timeout', type=int, default=5, help='Serial timeout in seconds (default: 5)')

    args = parser.parse_args()

    tester = RemoteSerialTester(
        host=args.host,
        user=args.user,
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout
    )

    success = tester.test_login_and_hello()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()