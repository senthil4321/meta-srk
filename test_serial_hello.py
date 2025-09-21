#!/usr/bin/env python3
"""
Serial Test Script for SRK Target Device over Remote SSH
Connects to remote host an            # Step 3: Wait for password             # Step 3: Wait for password prompt or shell prompt
            print("3. Waiting for password prompt or shell prompt...")
            password_or_shell = self.read_until("Password:", timeout=5)
            if "Password:" in password_or_shell:
                print("✓ Password prompt detected")
                self.send_command("")  # Empty password for srk
                # Wait for shell prompt after password
                shell_prompt = self.read_until("#", timeout=10)
                if "#" not in shell_prompt and "$" not in shell_prompt:
                    print("ERROR: Shell prompt not found after password")
                    return False
            elif "#" in password_or_shell or "$" in password_or_shell:
                print("✓ Shell prompt detected (no password required)")
            else:
                print("Note: No password prompt found, continuing...")
                # Try to wait for shell prompt anyway
                shell_prompt = self.read_until("#", timeout=10)
                if "#" not in shell_prompt and "$" not in shell_prompt:
                    print("ERROR: Shell prompt not found")
                    return Falseprom                  print("\n8. Verifying output...")
            success = True
            for line in expected_lines:
                if line in output:
                    print(f"✓ Found: {line}")
                else:
                    print(f"✗ Missing: {line}")
                    success = Falseint("\n7. Verifying output...")
            success = True
            for line in expected_lines:
                if line in output:
                    print(f"✓ Found: {line}")
                else:
                    print(f"✗ Missing: {line}")
                    success = False       print("3. Waiting for password prompt or shell prompt...")
            password_or_shell = self.read_until("Password:", timeout=5)
            if "Password:" in password_or_shell:
                print("✓ Password prompt detected")
                self.send_command("")  # Empty password for root
                # Wait for shell prompt after password
                shell_prompt = self.read_until("#", timeout=10)
                if "#" not in shell_prompt and "$" not in shell_prompt:
                    print("ERROR: Shell prompt not found after password")
                    return False
            elif "#" in password_or_shell or "$" in password_or_shell:
                print("✓ Shell prompt detected (no password required)")
            else:
                print("Note: No password prompt found, continuing...")
                # Try to wait for shell prompt anyway
                shell_prompt = self.read_until("#", timeout=10)
                if "#" not in shell_prompt and "$" not in shell_prompt:
                    print("ERROR: Shell prompt not found")
                    return Falsel device /dev/ttyUSB0
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

            # Open an interactive shell with cat for serial
            self.channel = self.client.invoke_shell()
            time.sleep(1)

            # Configure serial device
            cmd = f"stty -F {self.port} {self.baudrate} raw -echo && cat {self.port}"
            self.channel.send(cmd + "\n")

            # Start background reader
            threading.Thread(target=self._reader, daemon=True).start()

            print(f"Connected to {self.host}:{self.port} at {self.baudrate} baud over SSH")
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
        """Send command to serial device"""
        if self.channel:
            # Send raw command directly to serial device
            self.channel.send(command + "\n")
            print(f"Sent: {command}")
            time.sleep(2)  # Increased delay to give command more time to execute

    def test_login_and_hello(self):
        """Main test logic (same as your original, adapted)"""
        print("Starting remote serial test for SRK target device...")
        print("=" * 50)

        if not self.connect():
            return False

        try:
            # Step 1: Wait for system to fully boot and login prompt
            print("\n1. Waiting for system to boot and login prompt...")
            boot_found = False
            login_found = False
            combined_buffer = ""
            start_time = time.time()

            while time.time() - start_time < 90:  # 90 second timeout
                try:
                    data = self.output_queue.get(timeout=1.0)
                    combined_buffer += data
                    print(f"Received: {data.strip()}")

                    if not boot_found and "SRK Minimal SquashFS Distro 1.0 beaglebone-yocto ttyS0" in combined_buffer:
                        boot_found = True
                        print("✓ System boot detected")

                    if not login_found and "beaglebone-yocto login:" in combined_buffer:
                        login_found = True
                        print("✓ Login prompt detected")
                        break

                except queue.Empty:
                    continue

            if not boot_found:
                print("ERROR: System boot text not found")
                return False

            if not login_found:
                print("ERROR: Login prompt not found")
                print(f"Last received data: {combined_buffer[-500:]}")  # Show last 500 chars
                return False

            # Step 2: Send username
            print("\n2. Sending username 'srk'...")
            self.send_command("srk")

            # Step 3: Send Enter to complete login (no password required)
            print("3. Sending Enter to complete login...")
            self.send_command("")  # Send just Enter

            # Step 4: Wait for shell prompt
            print("4. Waiting for shell prompt...")
            shell_prompt = self.read_until("beaglebone-yocto:~$", timeout=30)  # Look for user prompt
            if "beaglebone-yocto:~$" not in shell_prompt:
                print("ERROR: Shell prompt not found")
                print(f"Received data: {shell_prompt}")
                return False
            print("✓ Shell prompt detected")

            # Step 5: Check if hello command exists
            print("\n5. Checking if hello command exists...")
            self.send_command("which hello")
            which_output = self.read_until("#", timeout=10)
            if "hello" not in which_output:
                print("ERROR: hello command not found on target system")
                print(f"which output: {which_output}")
                return False
            print("✓ hello command found")

            # Step 6: Run hello command
            print("6. Running 'hello' command...")
            self.send_command("hello")

            # Step 7: Capture and verify output
            print("7. Capturing hello command output...")
            # Wait a bit for command to execute and collect output
            time.sleep(2)
            output = ""
            # Collect output for a few seconds
            for _ in range(10):
                try:
                    data = self.output_queue.get(timeout=0.5)
                    output += data
                    print(f"Received: {data.strip()}")
                except queue.Empty:
                    break

            # Also try to read until we get a shell prompt to make sure command completed
            remaining_output = self.read_until("#", timeout=5)
            output += remaining_output

            expected_lines = [
                "Hello, World! from meta-srk layer and recipes-srk V2!!!",
                "Hello, World! 20SEP2025 07:28 !!!",
                "Hello, World! 20SEP2025 23:50 !!!"
            ]

            print("\n8. Verifying output...")
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
