#!/usr/bin/env python3
"""
Serial Test Script for SRK Target Device over Remote SSH
Connects to remote host and accesses serial device using socat
Tests include hello application, system info, LED control, EEPROM access, and RTC functionality

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
import copy
import json
from test_suites import DEFAULT_TEST_SUITE, IMAGE_11_TEST_SUITE

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
        self.capture_sessions = {}
        self.active_captures = set()
        self.capture_lock = threading.Lock()

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
                self._record_capture(data)
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

    def start_capture(self, name="default", metadata=None):
        """Begin capturing all incoming serial data under a named session."""
        with self.capture_lock:
            self.capture_sessions[name] = {
                "data": "",
                "chunks": [],
                "start_time": time.time(),
                "end_time": None,
                "metadata": metadata or {}
            }
            self.active_captures.add(name)
        print(f"🎙️ Started capture '{name}'")

    def stop_capture(self, name=None):
        """Stop capturing data for the specified session (or all active sessions)."""
        with self.capture_lock:
            targets = [name] if name else list(self.active_captures)
            for capture_name in targets:
                session = self.capture_sessions.get(capture_name)
                if session:
                    session["end_time"] = time.time()
                self.active_captures.discard(capture_name)
        if name:
            print(f"🛑 Stopped capture '{name}'")
        elif targets:
            print("🛑 Stopped all active captures")

    def get_capture_data(self, name="default"):
        """Return all captured data for the named session."""
        with self.capture_lock:
            session = self.capture_sessions.get(name)
            if session:
                return session["data"]
        return None

    def get_capture_session(self, name="default"):
        """Return a copy of the capture session details."""
        with self.capture_lock:
            session = self.capture_sessions.get(name)
            if session:
                return copy.deepcopy(session)
        return None

    def get_capture_event_time(self, name, pattern, default=None):
        """Return the timestamp when a pattern first appeared in the capture."""
        session = self.get_capture_session(name)
        if not session:
            return None
        if pattern is None:
            return session.get("start_time", default)
        for timestamp, chunk in session.get("chunks", []):
            if pattern in chunk:
                return timestamp
        return default

    def _record_capture(self, data):
        if not data:
            return
        timestamp = time.time()
        with self.capture_lock:
            for name in list(self.active_captures):
                session = self.capture_sessions.get(name)
                if not session:
                    continue
                session["data"] += data
                session.setdefault("chunks", []).append((timestamp, data))
                session["end_time"] = timestamp

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
    test_config format: [test_type, description, command, expected_value, failure_message, **kwargs]
    Returns: (success: bool, message: str)
    """
    test_type = test_config[0] if len(test_config) > 0 else None
    description = test_config[1] if len(test_config) > 1 else "Unknown test"
    command = test_config[2] if len(test_config) > 2 else None
    expected = test_config[3] if len(test_config) > 3 else None
    failure_msg = test_config[4] if len(test_config) > 4 else "Test failed"
    kwargs = test_config[5] if len(test_config) > 5 else {}

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
            try:
                if expected:
                    if assert_in(expected, output):
                        # Extract value based on pattern
                        extract_pattern = kwargs.get('extract_pattern', expected)
                        if extract_pattern in output:
                            # Simple extraction - can be made more sophisticated
                            parts = output.split(extract_pattern)
                            if len(parts) > 1:
                                value = parts[1].split()[0] if len(parts[1].split()) > 0 else "Unknown"
                                return (True, value)
                    return (False, "Unknown")
                else:
                    # If no expected pattern, just check if command produced output
                    if len(output.strip()) > 0:
                        return (True, "Command executed successfully")
                    return (False, "No output from command")
            except AssertionError:
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

        elif test_type == "CAPTURE_LOG":
            capture_name = kwargs.get("capture_name") or description.replace(" ", "_").lower()
            end_conditions = []
            if expected:
                end_conditions = expected if isinstance(expected, list) else [expected]
            if "end_condition" in kwargs:
                cond = kwargs["end_condition"]
                end_conditions.extend(cond if isinstance(cond, list) else [cond])
            if "end_conditions" in kwargs:
                conds = kwargs["end_conditions"]
                end_conditions.extend(conds if isinstance(conds, list) else [conds])
            # remove duplicates
            end_conditions = list(dict.fromkeys(end_conditions))

            timeout = kwargs.get('timeout', 120)
            wait_for_all = kwargs.get('wait_for_all', True)
            capture_duration = kwargs.get('capture_duration')
            reset_before = kwargs.get('reset_before', False)
            metadata = kwargs.get('metadata')

            tester.start_capture(capture_name, metadata=metadata)

            preload_output = kwargs.get('preload_output')
            if preload_output and hasattr(tester, "enqueue_output"):
                for item in preload_output:
                    tester.enqueue_output(item)

            try:
                if reset_before:
                    if not reset_bbb():
                        tester.stop_capture(capture_name)
                        return (False, failure_msg)

                if command:
                    tester.send_command(command + "\r\n")

                if capture_duration is None and not end_conditions:
                    capture_duration = timeout

                success = False
                if end_conditions:
                    start_time = time.time()
                    while time.time() - start_time < timeout:
                        captured = tester.get_capture_data(capture_name) or ""
                        matches = [cond for cond in end_conditions if cond and cond in captured]
                        if (wait_for_all and len(matches) == len(end_conditions)) or (not wait_for_all and matches):
                            success = True
                            break
                        time.sleep(0.5)
                else:
                    time.sleep(capture_duration)
                    success = True

                tester.stop_capture(capture_name)
                captured_data = tester.get_capture_data(capture_name) or ""

                if success:
                    info = f"Captured '{capture_name}' ({len(captured_data)} bytes)"
                    if end_conditions:
                        info += " with end condition(s) satisfied"
                    return (True, info)
                else:
                    return (False, failure_msg)
            except Exception as exc:
                tester.stop_capture(capture_name)
                return (False, f"Capture error: {exc}")

        elif test_type == "CAPTURE_LOG_ASSERT":
            capture_name = kwargs.get('capture_name', 'default')
            capture_data = tester.get_capture_data(capture_name)
            if capture_data is None:
                return (False, f"Capture '{capture_name}' not found")

            patterns = expected if expected is not None else kwargs.get('patterns')
            if patterns is None:
                return (False, "No patterns provided for capture assertion")
            if isinstance(patterns, str):
                patterns = [patterns]

            missing = [pattern for pattern in patterns if pattern not in capture_data]
            if missing:
                return (False, f"{failure_msg}: missing {missing}")

            return (True, "Capture assertion passed")

        elif test_type == "CAPTURE_CHECK_DURATION":
            capture_name = kwargs.get('capture_name', 'default')
            session = tester.get_capture_session(capture_name)
            if not session:
                return (False, f"Capture '{capture_name}' not found")

            start_pattern = kwargs.get('start_pattern')
            end_pattern = expected or kwargs.get('end_pattern')
            if not end_pattern:
                return (False, "No end pattern provided for duration check")

            start_time = tester.get_capture_event_time(capture_name, start_pattern, default=session.get('start_time'))
            end_time = tester.get_capture_event_time(capture_name, end_pattern)

            if end_time is None or start_time is None:
                return (False, failure_msg)

            duration = end_time - start_time
            if duration < 0:
                return (False, f"{failure_msg}: invalid duration computed")

            max_seconds = kwargs.get('max_seconds')
            min_seconds = kwargs.get('min_seconds', 0)

            if max_seconds is not None and duration > max_seconds:
                return (False, f"{failure_msg}: {duration:.2f}s exceeds {max_seconds}s")
            if duration < min_seconds:
                return (False, f"{failure_msg}: {duration:.2f}s below {min_seconds}s")

            return (True, f"Duration {duration:.2f}s within limits")

        elif test_type == "RESET_TARGET":
            # Reset the target device
            print("🔄 Resetting target device...")
            if reset_bbb():
                print("✅ Target reset completed, waiting for system to reboot...")
                # After reset, we need to wait for the system to come back up
                # The serial connection might be lost, so we'll wait a bit longer
                time.sleep(15)  # Additional wait beyond the 10s in reset_bbb
                return (True, "Target reset successful")
            return (False, failure_msg)

        else:
            return (False, f"Unknown test type: {test_type}")

    except Exception as e:
        return (False, f"Test error: {str(e)}")

# Define test suites with generic format


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

    def run_all_tests(self, image_type=None, test_suite_file=None):
        # Select test suite based on image type or file
        if test_suite_file:
            try:
                with open(test_suite_file, 'r') as f:
                    steps = json.load(f)
                print(f"🧪 Loading test suite from file: {test_suite_file}")
            except Exception as e:
                print(f"❌ Error loading test suite from {test_suite_file}: {e}")
                return []
        elif image_type == "11":
            steps = IMAGE_11_TEST_SUITE
            print("🧪 Running IMAGE_11_TEST_SUITE (includes hardware tests)")
        else:
            steps = DEFAULT_TEST_SUITE
            print("🧪 Running DEFAULT_TEST_SUITE (minimal test set)")


        non_blocking = ["ASSERT_IN_BUFFER", "HARDWARE_CHECK", "WAIT_FOR_CONDITION", "WAIT"]
        results = []

        for i, test_config in enumerate(steps):
            # Get description from test config (now at index 1)
            description = test_config[1] if len(test_config) > 1 else "Unknown test"
            test_type = test_config[0] if len(test_config) > 0 else "UNKNOWN"
            
            # Use description as the test name
            name = description

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
    parser.add_argument("--test-suite-file", type=str, help="Load test suite from JSON file")

    args = parser.parse_args()

    tester = TestSerialHello()
    if not args.test_suite_file and not args.image_type:
        print("Error: Please specify --test-suite-file or --image-type to select a test suite.")
        sys.exit(1)
    tester.image_type = args.image_type  # Set image type before setup
    tester.setUp()
    try:
        results = tester.run_all_tests(args.image_type, args.test_suite_file)
        if args.save_report:
            report_generator = TestReportGenerator()
            report_generator.save_report_to_file(results, args.save_report, ["Check for", "Hardware check", "Wait for", "Wait"])
    finally:
        tester.tearDown()