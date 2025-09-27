#!/usr/bin/env python3
"""
Mock Test Framework for SRK Test Suite
Provides mock implementations for testing the test framework without hardware.
"""

__version__ = "1.0.0"
__author__ = "SRK Development Team"
__copyright__ = "Copyright (c) 2025 SRK. All rights reserved."
__license__ = "MIT"

import time
import queue
import threading
import copy
from test_serial_hello import run_generic_test

class MockRemoteSerialTester:
    """Mock implementation of RemoteSerialTester for testing the framework"""

    def __init__(self, host='mock-host', user='mock-user', port='/dev/mock', baudrate=115200, timeout=5, prompt='mock:~$'):
        self.host = host
        self.user = user
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.prompt = prompt  # Use the passed prompt
        self.login_prompt = "mock login:"
        self.client = None
        self.channel = None
        self.output_queue = queue.Queue()
        self.last_command = None
        self.running = False
        self.mock_responses = {}  # command -> response mapping
        self.buffer_content = ""  # simulated buffer content
        self.capture_sessions = {}
        self.active_captures = set()
        self.capture_lock = threading.Lock()

    def connect(self):
        """Mock connection - always succeeds"""
        print(f"Mock connection established to {self.host}:{self.port}")
        return True

    def disconnect(self):
        """Mock disconnect"""
        print("Mock connection closed")
        pass

    def send_command(self, command):
        """Mock send command - simulate command echo and response"""
        self.last_command = command.strip()
        print(f"Mock sent: {command}")

        # Simulate command echo (what socat would send back)
        self.output_queue.put(command)
        self._record_capture(command)

        # Simulate response based on command
        response = self._get_mock_response(command.strip())
        if response:
            # Add some delay to simulate real device
            time.sleep(0.05)
            self.output_queue.put(response)
            self._record_capture(response)

        # Add prompt at the end (this is what the shell sends)
        time.sleep(0.05)
        self.output_queue.put(self.prompt)
        self._record_capture(self.prompt)

    def read_until(self, expected_text, timeout=10):
        """Mock read until expected text"""
        buffer = ""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                data = self.output_queue.get(timeout=0.5)
                buffer += data
                print(f"Mock received: {data.strip()}")
                if expected_text in buffer:
                    return buffer
            except queue.Empty:
                pass

        print(f"Mock timeout waiting for: {expected_text}")
        return buffer

    def get_buffer(self):
        """Mock get buffer content"""
        return self.buffer_content

    def start_capture(self, name="default", metadata=None):
        with self.capture_lock:
            self.capture_sessions[name] = {
                "data": "",
                "chunks": [],
                "start_time": time.time(),
                "end_time": None,
                "metadata": metadata or {}
            }
            self.active_captures.add(name)
        print(f"🎙️ [mock] Started capture '{name}'")

    def stop_capture(self, name=None):
        with self.capture_lock:
            targets = [name] if name else list(self.active_captures)
            for capture_name in targets:
                session = self.capture_sessions.get(capture_name)
                if session:
                    session["end_time"] = time.time()
                self.active_captures.discard(capture_name)
        if name:
            print(f"🛑 [mock] Stopped capture '{name}'")
        elif name is None and targets:
            print("🛑 [mock] Stopped all captures")

    def get_capture_data(self, name="default"):
        with self.capture_lock:
            session = self.capture_sessions.get(name)
            if session:
                return session["data"]
        return None

    def get_capture_session(self, name="default"):
        with self.capture_lock:
            session = self.capture_sessions.get(name)
            if session:
                return copy.deepcopy(session)
        return None

    def get_capture_event_time(self, name, pattern, default=None):
        session = self.get_capture_session(name)
        if not session:
            return None
        if pattern is None:
            return session.get("start_time", default)
        for timestamp, chunk in session.get("chunks", []):
            if pattern in chunk:
                return timestamp
        return default

    def enqueue_output(self, payload):
        if isinstance(payload, list):
            for item in payload:
                self.enqueue_output(item)
            return
        self.output_queue.put(payload)
        self._record_capture(payload)

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

    def _get_mock_response(self, command):
        """Get mock response for a command"""
        responses = {
            "which hello": "/usr/bin/hello",
            "hello": "Hello, World! from meta-srk layer and recipes-srk V2!!!\nHello, World! 20SEP2025 07:28 !!!\nHello, World! 20SEP2025 23:50 !!!",
            "uname -a": "Linux mock-device 6.6.0 #1 SMP PREEMPT_DYNAMIC Mon Sep 23 12:34:56 UTC 2025 armv7l GNU/Linux",
            "uname -v": "#1 SMP PREEMPT_DYNAMIC Mon Sep 23 12:34:56 UTC 2025",
            "cat /etc/timestamp 2>/dev/null || date -r /etc/issue": "20180309123456",
            "uptime": " 12:34:56 up 1 day, 2:34, 1 user, load average: 0.50, 0.45, 0.40",
            "busybox": "BusyBox v1.36.1 (2025-09-23 12:34:56 UTC) multi-call binary.",
            "ps -p 1": "systemd",
            "which cryptsetup": "/usr/sbin/cryptsetup",
            "which bbb-02-rtc": "/usr/bin/bbb-02-rtc",
            "bbb-02-rtc read": "RTC Time: 2025-09-27 12:34:56",
            "bbb-02-rtc info": "RTC Device: /dev/rtc0",
        }
        return responses.get(command, f"Mock response for: {command}")

def run_mock_tests():
    """Run mock tests to validate the test framework"""

    # Create mock tester
    tester = MockRemoteSerialTester(prompt="# ")
    tester.connect()

    # Initialize buffer with some mock boot logs
    tester.buffer_content = "U-Boot 2023.04 Linux version 6.6.0 initramfs"

    # Mock test suite - comprehensive examples of all test types
    mock_test_suite = [
        # [test_type, description, command, expected_value, failure_message, kwargs]

        # Buffer checks
        ["ASSERT_IN_BUFFER", "Check U-Boot in buffer", None, "U-Boot", "U-Boot not found"],
        ["ASSERT_IN_BUFFER", "Check kernel in buffer", None, "Linux version", "Kernel not found"],
        ["ASSERT_IN_BUFFER", "Check initramfs in buffer", None, "initramfs", "Initramfs not found"],

        # Command tests
        ["SEND_COMMAND", "Send login command", "srk", None, "Login sent"],
        ["COMMAND_AND_ASSERT", "Check hello binary", "which hello", "hello", "Hello binary not found"],
        ["COMMAND_AND_VERIFY_MULTIPLE", "Test hello output", "hello", [
            "Hello, World! from meta-srk layer",
            "Hello, World! 20SEP2025"
        ], "Hello output verification failed"],

        # Extraction tests
        ["COMMAND_AND_EXTRACT", "Extract kernel version", "uname -a", "Linux", "Kernel version check failed", {"extract_pattern": "Linux"}],
        ["COMMAND_AND_EXTRACT", "Extract build time", "uname -v", "#", "Build time check failed", {"extract_pattern": "#"}],
        ["COMMAND_AND_EXTRACT", "Check timestamp", "cat /etc/timestamp 2>/dev/null || date -r /etc/issue", None, "Timestamp check failed"],
        ["COMMAND_AND_EXTRACT", "Extract uptime", "uptime", "up", "Uptime check failed", {"extract_pattern": "up"}],
        ["COMMAND_AND_EXTRACT", "Extract BusyBox version", "busybox", "BusyBox", "BusyBox check failed", {"extract_pattern": "BusyBox"}],

        # System checks
        ["COMMAND_AND_ASSERT", "Check init system", "ps -p 1", "systemd", "Init system check failed"],
        ["COMMAND_AND_ASSERT", "Check encryption support", "which cryptsetup", "cryptsetup", "Encryption check failed"],

        # Hardware tests
        ["COMMAND_AND_ASSERT", "Check RTC binary", "which bbb-02-rtc", "bbb-02-rtc", "RTC binary not found"],
        ["COMMAND_AND_ASSERT", "Test RTC read", "bbb-02-rtc read", "RTC Time:", "RTC read test failed"],
        ["COMMAND_AND_ASSERT", "Test RTC info", "bbb-02-rtc info", "RTC Device:", "RTC info test failed"],

        # Wait tests
        ["WAIT", "Wait short duration", None, None, None, {"duration": "short"}],
        ["WAIT", "Wait medium duration", None, None, None, {"duration": "medium"}],

        # Hardware checks
        ["HARDWARE_CHECK", "Check hardware availability", "which bbb-02-rtc", "bbb-02-rtc", "Hardware not found"],
        ["HARDWARE_TEST", "Test hardware functionality", "bbb-02-rtc read", "RTC Time:", "Hardware test failed"],

        # Log capture tests
        ["CAPTURE_LOG", "Capture mock boot logs", None, "mock login:", "Failed to capture boot logs", {
            "capture_name": "boot",
            "timeout": 3,
            "wait_for_all": True,
            "preload_output": [
                "Booting kernel...\n",
                "Initializing network driver eth0\n",
                "mock login:\n"
            ]
        }],
        ["CAPTURE_LOG_ASSERT", "Verify boot log contains network driver", None, "Initializing network driver", "Network driver not loaded", {"capture_name": "boot"}],
        ["CAPTURE_CHECK_DURATION", "Boot completes within 30s", None, "mock login:", "Kernel boot exceeded time", {
            "capture_name": "boot",
            "max_seconds": 30,
            "start_pattern": "Booting kernel"
        }]
    ]

    results = []
    print("\n🧪 Running Mock Test Suite")
    print("=" * 50)

    for i, test_config in enumerate(mock_test_suite):
        description = test_config[1] if len(test_config) > 1 else "Unknown test"
        test_type = test_config[0] if len(test_config) > 0 else "UNKNOWN"

        # Clear any leftover data from previous test
        while not tester.output_queue.empty():
            try:
                tester.output_queue.get_nowait()
            except queue.Empty:
                break

        print(f"\n➡️ Mock Test {i+1}: {description}")
        success, message = run_generic_test(tester, test_config)
        results.append((description, success, message))

        if success:
            print(f"✅ PASS: {description} - {message}")
        else:
            print(f"❌ FAIL: {description} - {message}")

    # Summary
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"\n📊 Mock Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All mock tests passed! Framework is working correctly.")
    else:
        print("⚠️  Some mock tests failed. Check framework implementation.")

    tester.disconnect()
    return results

def run_specific_mock_test(test_type, description="Mock test", command=None, expected=None, failure_msg="Test failed", kwargs=None):
    """Run a specific mock test for debugging"""

    if kwargs is None:
        kwargs = {}

    tester = MockRemoteSerialTester()
    tester.connect()

    test_config = [test_type, description, command, expected, failure_msg, kwargs]

    print(f"🔍 Running specific mock test: {description}")
    success, message = run_generic_test(tester, test_config)

    if success:
        print(f"✅ PASS: {message}")
    else:
        print(f"❌ FAIL: {message}")

    tester.disconnect()
    return success, message

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mock Test Framework for SRK")
    parser.add_argument("--run-all", action="store_true", help="Run all mock tests")
    parser.add_argument("--test-type", type=str, help="Run specific test type")
    parser.add_argument("--description", type=str, default="Mock test", help="Test description")
    parser.add_argument("--command", type=str, help="Test command")
    parser.add_argument("--expected", type=str, help="Expected value")
    parser.add_argument("--failure-msg", type=str, default="Test failed", help="Failure message")

    args = parser.parse_args()

    if args.run_all:
        run_mock_tests()
    elif args.test_type:
        run_specific_mock_test(
            args.test_type,
            args.description,
            args.command,
            args.expected,
            args.failure_msg
        )
    else:
        print("Use --run-all to run all mock tests, or --test-type to run a specific test type")
        print("Example: python3 test_framework_mock.py --test-type COMMAND_AND_ASSERT --command 'which hello' --expected 'hello' --description 'Check hello binary'")