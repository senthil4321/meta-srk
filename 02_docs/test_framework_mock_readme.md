# Mock Test Framework for SRK

This mock test framework provides a way to test the SRK test framework without requiring actual hardware or network connections.

## Features

- **MockRemoteSerialTester**: Simulates the behavior of the real RemoteSerialTester
- **Comprehensive test coverage**: Tests all test types from the main framework
- **Command-line interface**: Run all tests or specific test types
- **Realistic responses**: Simulates typical Linux/BusyBox command outputs

## Usage

### Run all mock tests

```bash
python3 test_framework_mock.py --run-all
```

### Run a specific test type

```bash
python3 test_framework_mock.py --test-type COMMAND_AND_ASSERT --command 'which hello' --expected 'hello' --description 'Check hello binary'
```

### Get help

```bash
python3 test_framework_mock.py --help
```

## Test Types Supported

- `ASSERT_IN_BUFFER`: Check if text exists in buffer
- `SEND_COMMAND`: Send a command without validation
- `COMMAND_AND_ASSERT`: Send command and check for expected output
- `COMMAND_AND_VERIFY_MULTIPLE`: Verify multiple expected strings
- `COMMAND_AND_EXTRACT`: Extract information from command output
- `WAIT_FOR_CONDITION`: Wait for a specific condition
- `WAIT`: Wait for a specified duration
- `HARDWARE_CHECK`: Check hardware availability
- `HARDWARE_TEST`: Test hardware functionality
- `RESET_TARGET`: Reset the target device

## Mock Responses

The framework includes realistic mock responses for common commands:

- System info: `uname -a`, `uptime`, `busybox`
- Applications: `which hello`, `hello`
- Hardware: `which bbb-03-rtc`, `bbb-03-rtc read/info`
- Security: `which cryptsetup`

## Use Cases

1. **Framework Development**: Test framework changes without hardware
2. **CI/CD Integration**: Automated testing in build pipelines
3. **Debugging**: Isolate test logic from hardware connectivity issues
4. **Documentation**: Demonstrate test framework capabilities
5. **Training**: Learn how to write tests without risking hardware

## Architecture

- `MockRemoteSerialTester`: Simulates SSH/serial connection
- `run_mock_tests()`: Runs comprehensive test suite
- `run_specific_mock_test()`: Tests individual test configurations
- Command-line interface for flexible testing

The mock framework maintains the same API as the real test framework, making it a drop-in replacement for testing purposes.
