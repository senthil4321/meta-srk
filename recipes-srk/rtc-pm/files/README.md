# RTC Power Management Tools

Utilities for RTC-based alarm wakeup and suspend-to-RAM power management on BeagleBone Black.

## Table of Contents
- [Overview](#overview)
- [Command-Line Tools](#command-line-tools)
  - [rtc-suspend](#rtc-suspend)
  - [rtc-wakeup](#rtc-wakeup)
  - [rtc-sync.sh](#rtc-syncsh)
  - [rtc-pm-test](#rtc-pm-test)
- [Systemd Services](#systemd-services)
- [Web API Reference](#web-api-reference)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

The RTC Power Management suite provides tools for low-power operation on embedded Linux systems. It enables:
- **Suspend to RAM (mem)** - Full power down with RAM retention
- **S2Idle (freeze)** - Lightweight CPU idle state
- **RTC Alarm Wakeup** - Wake system at scheduled time
- **Automatic Time Sync** - Keep hardware RTC synchronized with system time

---

## Command-Line Tools

### rtc-suspend

Suspend the system to RAM with automatic RTC alarm wakeup.

**Location:** `/usr/sbin/rtc-suspend`

#### Usage
```bash
rtc-suspend [DURATION_SECONDS]
```

#### Parameters
- `DURATION_SECONDS` - Time to sleep before auto-wakeup (default: 60 seconds)

#### Behavior
1. Clears any existing RTC alarm
2. Sets new RTC alarm for wakeup
3. Syncs filesystems (3x for safety)
4. Checks available suspend states:
   - Prefers `mem` (Suspend to RAM) if PM firmware loaded
   - Falls back to `freeze` (S2Idle) if PM firmware unavailable
5. Suspends the system
6. Resumes automatically when alarm fires
7. Displays resume information and wake reason

#### Examples
```bash
# Suspend for 30 seconds
rtc-suspend 30

# Suspend for 5 minutes (300 seconds)
rtc-suspend 300

# Suspend for 1 hour
rtc-suspend 3600
```

#### Output
```
========================================
  RTC Suspend to RAM
========================================
Suspend Duration: 30 seconds

[INFO] Clearing existing RTC alarm...
[INFO] RTC alarm cleared
[INFO] Setting RTC alarm for wakeup in 30 seconds...
[OK] Alarm set for: +30
[INFO] Syncing filesystems...
[OK] Filesystems synced
[INFO] Suspending to RAM for 30 seconds
[INFO] Using s2idle (freeze) instead...

========================================
  System Resumed!
========================================
Resume time: Sat Nov  2 14:23:45 UTC 2025
```

---

### rtc-wakeup

Set RTC alarm without suspending the system.

**Location:** `/usr/sbin/rtc-wakeup`

#### Usage
```bash
rtc-wakeup ALARM_TIME [COMMAND]
```

#### Parameters
- `ALARM_TIME` - Time format:
  - Relative: `+SECONDS` (e.g., `+60` for 1 minute from now)
  - Absolute: UNIX timestamp (e.g., `1730556225`)
- `COMMAND` - (Optional) Command to execute when alarm triggers

#### Behavior
1. Displays current system time and RTC time
2. Sets RTC alarm via `/sys/class/rtc/rtc0/wakealarm`
3. Optionally waits for alarm and executes command
4. Returns immediately if no command specified

#### Examples
```bash
# Set alarm for 60 seconds from now
rtc-wakeup +60

# Set alarm and wait, then execute command
rtc-wakeup +120 "echo 'Alarm triggered!' | wall"

# Set alarm for specific timestamp
rtc-wakeup 1730556225
```

#### Output
```
========================================
  RTC Alarm Configuration
========================================
Current Time: Sat Nov  2 14:20:00 UTC 2025
RTC Time:     Sat Nov  2 14:20:00 UTC 2025

[INFO] Setting RTC alarm for: +60
[OK] Alarm set successfully
[INFO] Alarm will trigger at: Sat Nov  2 14:21:00 UTC 2025

Alarm configured. System will wake at the specified time.
```

---

### rtc-sync.sh

Synchronize system time to hardware RTC clock.

**Location:** `/usr/sbin/rtc-sync.sh`

#### Usage
```bash
rtc-sync.sh
```

#### Parameters
None

#### Behavior
1. Checks if RTC device (`/dev/rtc0`) exists
2. Displays current system time and RTC time
3. Synchronizes system time to RTC using `hwclock -w`
4. Displays new RTC time after sync
5. Logs operation to systemd journal

#### Examples
```bash
# Manually sync RTC with system time
rtc-sync.sh
```

#### Output
```
[INFO] RTC Synchronization

System Time: Sat Nov  2 14:25:30 UTC 2025
RTC Time:    Sat Nov  2 14:20:15 UTC 2025

[INFO] Syncing system time to RTC...
[OK] RTC synchronized with system time
New RTC Time: Sat Nov  2 14:25:30 UTC 2025
```

#### Auto-Sync on Boot
Automatically runs at system startup via `rtc-sync.service` (enabled by default).

---

### rtc-pm-test

Comprehensive RTC and power management diagnostics.

**Location:** `/usr/sbin/rtc-pm-test`

#### Usage
```bash
rtc-pm-test
```

#### Parameters
None

#### Behavior
Runs 8 comprehensive tests:
1. **RTC Device Check** - Verifies `/dev/rtc0` exists
2. **RTC Time Reading** - Tests `hwclock` functionality
3. **Wakealarm Interface** - Checks `/sys/class/rtc/rtc0/wakealarm`
4. **Suspend Support** - Verifies available power states
5. **Wakeup Sources** - Lists enabled wakeup devices
6. **Alarm Test** - Sets and clears test alarm
7. **RTC Driver Info** - Displays kernel driver details
8. **PM Capabilities** - Shows suspend modes and features

#### Examples
```bash
# Run all diagnostic tests
rtc-pm-test
```

#### Output
```
========================================
  RTC Power Management Tests
========================================

Test 1: RTC Device Check
[OK] RTC device found: /dev/rtc0

Test 2: RTC Time Reading
Current RTC time: Sat Nov  2 14:30:00 UTC 2025
[OK] RTC time read successfully

Test 3: Wakealarm Interface
[OK] Wakealarm interface available

Test 4: Suspend Support
Available states: freeze mem
[OK] Suspend states available

Test 5: Wakeup Sources
Enabled wakeup sources:
- rtc0
- gpio-keys
[OK] Wakeup sources found

Test 6: Alarm Set/Clear Test
[OK] Alarm set: 1730556660
[OK] Alarm cleared

Test 7: RTC Driver Information
RTC Driver: rtc-omap
[OK] Driver information retrieved

Test 8: PM Capabilities
mem_sleep: [s2idle]
Available: freeze mem
[OK] PM capabilities retrieved

========================================
All tests completed!
Use 'rtc-suspend 30' to test suspend/resume
========================================
```

---

## Systemd Services

### rtc-sync.service

**Status:** Enabled (runs automatically on boot)

**Purpose:** Synchronizes RTC with system time at startup

**Control:**
```bash
# Check status
systemctl status rtc-sync.service

# Manually run sync
systemctl start rtc-sync.service

# View logs
journalctl -u rtc-sync.service
```

### rtc-pm.service

**Status:** Disabled (manual use only)

**Purpose:** Clears RTC alarm on system shutdown

**Control:**
```bash
# Enable for auto-start
systemctl enable rtc-pm.service

# Disable
systemctl disable rtc-pm.service
```

---

## Web API Reference

Access via System Monitor Web Server (port 8080)

### Base URL
```
http://<device-ip>:8080/api/rtc/
```

### Endpoints

#### GET /api/rtc
Get current RTC status and capabilities.

**Response:**
```json
{
  "available": true,
  "device": "/dev/rtc0",
  "system_time": "2025-11-02 14:35:00",
  "rtc_time": "Sat Nov  2 14:35:00 2025  0.000000 seconds",
  "alarm_set": false,
  "alarm_time": "",
  "suspend_support": {
    "mem": false,
    "freeze": true,
    "standby": false
  },
  "pm_firmware": false
}
```

---

#### POST /api/rtc/sync
Synchronize system time to RTC.

**Request:**
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/sync
```

**Response:**
```json
{
  "status": "success",
  "message": "RTC synchronized with system time",
  "output": "[OK] RTC synchronized with system time\nNew RTC Time: ..."
}
```

---

#### POST /api/rtc/test
Run comprehensive RTC diagnostics.

**Request:**
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/test
```

**Response:**
```json
{
  "status": "success",
  "message": "RTC tests completed",
  "output": "Test 1: RTC Device Check\n[OK] RTC device found\n..."
}
```

---

#### POST /api/rtc/alarm
Set RTC alarm (without suspend).

**Request:**
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/alarm \
  -H "Content-Type: application/json" \
  -d '{"duration": 60}'
```

**Parameters:**
- `duration` (integer) - Seconds until alarm (default: 60)

**Response:**
```json
{
  "status": "success",
  "message": "RTC alarm set for 60 seconds",
  "output": "[OK] Alarm set successfully\n..."
}
```

---

#### POST /api/rtc/suspend
Suspend system with RTC wakeup.

**Request:**
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/suspend \
  -H "Content-Type: application/json" \
  -d '{"duration": 30}'
```

**Parameters:**
- `duration` (integer) - Seconds to suspend (default: 30, max: 600)

**Response:**
```json
{
  "status": "success",
  "message": "System will suspend for 30 seconds",
  "duration": 30
}
```

**Note:** System will be unreachable during suspend. Connection will timeout and resume when system wakes.

---

#### POST /api/rtc/clear
Clear RTC alarm.

**Request:**
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/clear
```

**Response:**
```json
{
  "status": "success",
  "message": "RTC alarm cleared"
}
```

---

## Examples

### Example 1: Basic Suspend/Resume Test
```bash
# Run diagnostics first
rtc-pm-test

# Test 30-second suspend
rtc-suspend 30

# System will suspend and auto-resume after 30 seconds
```

### Example 2: Scheduled Wake with Command
```bash
# Set alarm for 5 minutes, execute script when triggered
rtc-wakeup +300 "/usr/local/bin/backup-script.sh"
```

### Example 3: Long-Duration Sleep
```bash
# Suspend for 1 hour for power saving
rtc-suspend 3600
```

### Example 4: Web API - Suspend from Script
```bash
#!/bin/bash
# Suspend system via web API
curl -X POST http://localhost:8080/api/rtc/suspend \
  -H "Content-Type: application/json" \
  -d '{"duration": 120}'
```

### Example 5: Periodic Wakeup Loop
```bash
#!/bin/bash
# Wake every hour, run task, suspend again
while true; do
    echo "Running periodic task..."
    /usr/local/bin/my-task.sh
    
    echo "Suspending for 1 hour..."
    rtc-suspend 3600
done
```

### Example 6: Web UI Workflow
1. Open http://192.168.1.200:8080
2. Navigate to "RTC Power Management" card
3. Click "Run Tests" to verify system
4. Enter duration (e.g., 30 seconds)
5. Click "Suspend" button
6. System suspends and auto-resumes
7. Web page shows notification when alarm triggers

---

## Troubleshooting

### PM Firmware Not Loaded
**Symptom:** Message "PM not initialized for pm33xx"

**Solution:** System will use S2Idle (freeze) instead of Suspend-to-RAM. This is normal for BeagleBone Black without PM firmware.

**Impact:** 
- S2Idle: Lower power savings, faster resume
- Suspend-to-RAM: Higher power savings, requires firmware

---

### Alarm Already Set Error
**Symptom:** "Invalid argument" when setting alarm

**Solution:**
```bash
# Clear existing alarm
echo 0 > /sys/class/rtc/rtc0/wakealarm

# Or use clear API
curl -X POST http://192.168.1.200:8080/api/rtc/clear
```

---

### RTC Time Incorrect
**Symptom:** RTC time doesn't match system time

**Solution:**
```bash
# Manual sync
rtc-sync.sh

# Or via API
curl -X POST http://192.168.1.200:8080/api/rtc/sync

# Verify
hwclock -r
```

---

### System Won't Resume
**Symptom:** System doesn't wake from suspend

**Check:**
1. Verify RTC alarm was set: `cat /sys/class/rtc/rtc0/wakealarm`
2. Check wakeup sources: `cat /sys/kernel/debug/wakeup_sources`
3. Try shorter duration: `rtc-suspend 10`
4. Use S2Idle explicitly: System auto-detects best mode

---

### Web API Connection Refused
**Symptom:** Cannot access web API at port 8080

**Solution:**
```bash
# Check if service is running
systemctl status system-monitor.service

# Start if stopped
systemctl start system-monitor.service

# Check port
netstat -tlnp | grep 8080
```

---

## Additional Resources

### Related Files
- `/sys/class/rtc/rtc0/wakealarm` - RTC alarm interface
- `/sys/power/state` - Available suspend states
- `/sys/kernel/debug/wakeup_sources` - Wakeup event sources
- `/dev/rtc0` - RTC device

### Log Locations
- Systemd journal: `journalctl -u rtc-sync.service`
- Kernel messages: `dmesg | grep -i rtc`
- System log: `grep rtc-suspend /var/log/syslog`

### Power Consumption
Typical power draw (BeagleBone Black):
- Active: ~500mA @ 5V
- S2Idle: ~200-300mA @ 5V
- Suspend-to-RAM: ~50-100mA @ 5V (with firmware)

---

## License
MIT License - See COPYING.MIT

## Version
1.0 - Initial release (November 2025)
