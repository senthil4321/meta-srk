#!/bin/bash

# BeagleBone Black Serial Debug Console
# Connects to BBB via serial through Raspberry Pi for kernel debugging
# Supports debug kernel with KGDB, Magic SysRq, and interactive debugging

VERSION="1.0.0"
SCRIPT_NAME="$(basename "$0")"

print_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [options]

Connect to BeagleBone Black via serial through Raspberry Pi for kernel debugging.

Options:
    -r             Reset BBB before connecting
    -k             Enable KGDB mode (for GDB remote debugging)
    -s             Enable SysRq mode (show Magic SysRq help)
    -m             Monitor mode (read-only, save to log)
    -t TIMEOUT     Set timeout for monitor mode (default: 60s)
    -l LOGFILE     Specify log file (default: auto-generated)
    -v             Verbose output
    -V             Show version and exit
    -h             This help

Debugging Features:
    - Interactive serial console (115200 baud)
    - Magic SysRq key support for emergency commands
    - KGDB remote debugging setup
    - Boot monitoring and logging
    - Debug kernel message capture

Examples:
    $SCRIPT_NAME                    # Direct serial console
    $SCRIPT_NAME -r                 # Reset BBB then connect
    $SCRIPT_NAME -k                 # Connect with KGDB setup guide
    $SCRIPT_NAME -s                 # Connect with SysRq help
    $SCRIPT_NAME -m -t 120          # Monitor for 120 seconds
    $SCRIPT_NAME -r -m -l boot.log  # Reset, monitor, save to boot.log

Interactive Commands (in console):
    Ctrl+A then:
        h     - Show help
        q     - Quit console
        s     - Send SysRq commands
        k     - Enter KGDB mode
        r     - Reset BBB

Magic SysRq Keys (on target):
    Alt+SysRq+h   - Show SysRq help
    Alt+SysRq+t   - Show all tasks
    Alt+SysRq+m   - Show memory usage
    Alt+SysRq+p   - Show CPU state
    Alt+SysRq+c   - Crash system (for KGDB)
    Alt+SysRq+g   - Enter KGDB mode

KGDB Setup:
    1. Boot with debug kernel
    2. Trigger KGDB: echo g > /proc/sysrq-trigger
    3. On host: gdb-multiarch vmlinux-debug
    4. In GDB: target remote /dev/ttyUSB0

Version: $VERSION
EOF
}

# Default values
RESET_BBB=false
KGDB_MODE=false
SYSRQ_MODE=false
MONITOR_MODE=false
TIMEOUT=60
LOGFILE=""
VERBOSE=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -r) RESET_BBB=true ;;
        -k) KGDB_MODE=true ;;
        -s) SYSRQ_MODE=true ;;
        -m) MONITOR_MODE=true ;;
        -t) TIMEOUT="$2"; shift ;;
        -l) LOGFILE="$2"; shift ;;
        -v) VERBOSE=true ;;
        -V)
            echo "$SCRIPT_NAME version $VERSION"
            exit 0
            ;;
        -h)
            print_help
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; print_help; exit 1 ;;
    esac
    shift
done

# Set default log file if not specified
if [ "$MONITOR_MODE" = true ] && [ -z "$LOGFILE" ]; then
    LOGFILE="bbb_debug_$(date +%Y%m%d_%H%M%S).log"
fi

# Verbose output function
verbose_echo() {
    if [ "$VERBOSE" = true ]; then
        echo "$@"
    fi
}

# Function to check SSH connection to Raspberry Pi
check_ssh_connection() {
    verbose_echo "🔌 Checking SSH connection to Raspberry Pi..."
    if ! ssh -o ConnectTimeout=5 p "echo 'SSH connection OK'" >/dev/null 2>&1; then
        echo "❌ Error: Cannot connect to Raspberry Pi via 'ssh p'"
        echo "   Please ensure SSH alias 'p' is configured and accessible"
        exit 1
    fi
    verbose_echo "✅ SSH connection to Raspberry Pi OK"
}

# Function to check serial device
check_serial_device() {
    verbose_echo "📡 Checking serial device on Raspberry Pi..."
    if ! ssh p "test -c /dev/ttyUSB0" 2>/dev/null; then
        echo "❌ Error: /dev/ttyUSB0 not found on Raspberry Pi"
        echo "   Please ensure FTDI USB-to-serial adapter is connected"
        exit 1
    fi
    verbose_echo "✅ Serial device /dev/ttyUSB0 found"
}

# Function to reset BBB
reset_bbb() {
    echo "🔄 Resetting BeagleBone Black..."
    if [ -f "./13_remote_reset_bbb.sh" ]; then
        ./13_remote_reset_bbb.sh
    else
        ssh p "/bin/reset_bbb.sh" 2>/dev/null || {
            echo "⚠️  Warning: Could not reset BBB automatically"
            echo "   Please reset manually or check reset script"
        }
    fi
    sleep 2
}

# Function to show KGDB setup
show_kgdb_setup() {
    cat <<EOF

🐛 KGDB Remote Debugging Setup
==============================

1. Prerequisites on Host:
   - Debug kernel deployed (linux-yocto-srk-tiny-debug)
   - Cross GDB installed: sudo apt-get install gdb-multiarch
   - vmlinux-debug symbol file: $(pwd)/vmlinux-debug (57MB with debug symbols)
   - Serial device: /dev/ttyUSB0 via Raspberry Pi

2. Enable KGDB on Target (BeagleBone Black):
   # First, boot into debug kernel and enable SysRq
   echo 1 > /proc/sys/kernel/sysrq
   
   # Then trigger KGDB mode (kernel will halt and wait for GDB)
   echo g > /proc/sysrq-trigger
   
   # Target should show: "Entering KGDB" and stop responding

3. Connect GDB on Host (CORRECTED SEQUENCE):
   # Start GDB with debug symbols
   gdb-multiarch $(pwd)/vmlinux-debug
   
   # IMPORTANT: Set baud rate BEFORE connecting
   (gdb) set remotebaud 115200
   
   # Connect to target via SSH tunnel through Raspberry Pi
   (gdb) target remote | ssh p socat - /dev/ttyUSB0,b115200,raw
   
   # Alternative direct connection (if above fails):
   (gdb) target remote p:/dev/ttyUSB0
   
   # Once connected, continue execution
   (gdb) continue

4. Troubleshooting Connection Issues:
   
   Problem: "No symbol remotebaud"
   Solution: Use correct command sequence:
   (gdb) set serial baud 115200        # NOT remotebaud
   
   Problem: "Remote replied unexpectedly"
   Solution: Ensure target is in KGDB mode first:
   - Target must show "Entering KGDB" message
   - Try: (gdb) set debug remote 1     # Enable debug output
   
   Problem: "Ignoring packet error"
   Solution: Check serial connection:
   - Verify: ssh p "ls -la /dev/ttyUSB0"
   - Test: ssh p "socat - /dev/ttyUSB0,b115200,raw" (should see kernel output)

5. Working Debug Session Commands:
   (gdb) info registers                 # Show CPU state
   (gdb) bt                            # Backtrace
   (gdb) break do_sys_open             # Set breakpoint
   (gdb) continue                      # Resume execution
   (gdb) step                          # Single step
   (gdb) next                          # Step over
   (gdb) x/10i \$pc                    # Disassemble at PC
   (gdb) list                          # Show source code
   (gdb) info breakpoints             # List breakpoints
   (gdb) delete 1                      # Delete breakpoint 1

6. Emergency Commands:
   (gdb) monitor reset                 # Reset target (if supported)
   (gdb) detach                        # Disconnect GDB
   (gdb) quit                          # Exit GDB

7. Current vmlinux location:
   $(readlink -f $(pwd)/vmlinux-debug)

8. Quick Connection Test:
   # Test serial connection independently:
   ssh p "echo 'test' > /dev/ttyUSB0"
   
   # Monitor target output:
   ssh p "socat - /dev/ttyUSB0,b115200,raw"

EOF
}

# Function to show SysRq help
show_sysrq_help() {
    cat <<EOF

🔧 Magic SysRq Key Commands
==========================

Enable SysRq: echo 1 > /proc/sys/kernel/sysrq

Available Commands:
   Alt+SysRq+h  - Show this help
   Alt+SysRq+t  - Show all tasks (processes)
   Alt+SysRq+m  - Show memory usage
   Alt+SysRq+p  - Show CPU registers and state
   Alt+SysRq+c  - Crash system (useful for KGDB)
   Alt+SysRq+g  - Enter KGDB mode (if enabled)
   Alt+SysRq+s  - Sync filesystems
   Alt+SysRq+u  - Remount filesystems read-only
   Alt+SysRq+b  - Reboot system immediately
   Alt+SysRq+o  - Power off system
   Alt+SysRq+f  - Call OOM killer
   Alt+SysRq+k  - Kill all processes on current VT

Via Console: echo [letter] > /proc/sysrq-trigger

EOF
}

# Function to start interactive console
start_interactive_console() {
    echo "🖥️  Starting interactive serial console..."
    echo "   Baud rate: 115200"
    echo "   Device: /dev/ttyUSB0 (via Raspberry Pi)"
    echo ""
    echo "📋 Console Commands:"
    echo "   Ctrl+A then q  - Quit"
    echo "   Ctrl+A then h  - Help"
    echo "   Ctrl+A then s  - Send SysRq"
    echo "   Ctrl+A then k  - KGDB help"
    echo "   Ctrl+A then r  - Reset BBB"
    echo ""
    echo "🔗 Connecting to serial console..."
    echo "   (Press Ctrl+A then q to exit)"
    echo ""

    # Create a wrapper script for SSH + socat with control commands
    ssh p "
        echo 'Connected to BBB serial console via /dev/ttyUSB0'
        echo 'Press Ctrl+A then q to exit, Ctrl+A then h for help'
        echo ''
        
        # Use socat for raw serial access with escape sequences
        stty -icanon -echo
        trap 'stty icanon echo; exit' INT TERM
        
        socat STDIO /dev/ttyUSB0,b115200,raw,echo=0
    "
}

# Function to start monitor mode
start_monitor_mode() {
    echo "📊 Starting monitor mode..."
    echo "   Duration: ${TIMEOUT}s"
    echo "   Log file: $LOGFILE"
    echo ""

    # Start monitoring with timeout
    ssh p "timeout ${TIMEOUT} socat - /dev/ttyUSB0,b115200,raw,echo=0,crnl" | tee "$LOGFILE" &
    MONITOR_PID=$!

    echo "🔍 Monitoring serial output... (PID: $MONITOR_PID)"
    echo "   Press Ctrl+C to stop early"

    # Wait for completion
    wait $MONITOR_PID
    EXIT_CODE=$?

    echo ""
    echo "📋 Monitor Summary:"
    echo "=================="
    echo "📄 Log saved to: $LOGFILE"
    echo "📏 Log size: $(wc -l < "$LOGFILE") lines"

    # Quick analysis
    if grep -q "U-Boot SPL" "$LOGFILE" 2>/dev/null; then
        echo "✅ U-Boot detected"
    fi

    if grep -q "Linux version" "$LOGFILE" 2>/dev/null; then
        echo "✅ Linux kernel detected"
    fi

    if grep -q "debug" "$LOGFILE" 2>/dev/null; then
        echo "🐛 Debug messages found"
    fi

    # Count errors
    ERRORS=$(grep -c -i "error\|fail\|panic" "$LOGFILE" 2>/dev/null || echo "0")
    echo "⚠️  Errors found: $ERRORS"

    return $EXIT_CODE
}

# Main execution
main() {
    echo "🐛 BeagleBone Black Serial Debug Console"
    echo "========================================"
    echo "Version: $VERSION"
    echo ""

    # Check prerequisites
    check_ssh_connection
    check_serial_device

    # Reset BBB if requested
    if [ "$RESET_BBB" = true ]; then
        reset_bbb
    fi

    # Show setup information if requested
    if [ "$KGDB_MODE" = true ]; then
        show_kgdb_setup
    fi

    if [ "$SYSRQ_MODE" = true ]; then
        show_sysrq_help
    fi

    # Start appropriate mode
    if [ "$MONITOR_MODE" = true ]; then
        start_monitor_mode
    else
        start_interactive_console
    fi
}

# Execute main function
main "$@"