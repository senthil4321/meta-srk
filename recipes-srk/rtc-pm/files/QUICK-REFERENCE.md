# RTC Power Management - Quick Reference

## Command Cheat Sheet

### Local Commands (SSH or Serial Console)

```bash
# Sync RTC time with system time
rtc-sync.sh

# Suspend for 30 seconds (default: 60)
rtc-suspend 30

# Set alarm for 60 seconds from now (no suspend)
rtc-wakeup +60

# Set alarm and execute command when triggered
rtc-wakeup +120 "echo 'Alarm!' | wall"

# Clear RTC alarm
echo 0 > /sys/class/rtc/rtc0/wakealarm

# Run diagnostic tests
rtc-pm-test

# Check if alarm is set
cat /sys/class/rtc/rtc0/wakealarm

# View available suspend states
cat /sys/power/state

# Manual suspend (no alarm - must wake manually!)
echo mem > /sys/power/state
```

---

## Web API Quick Reference

### Base URL
```
http://192.168.1.200:8080
```

### Get RTC Status
```bash
curl http://192.168.1.200:8080/api/rtc
```

### Sync RTC Time
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/sync
```

### Run Diagnostics
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/test
```

### Set Alarm (60 seconds)
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/alarm \
  -H "Content-Type: application/json" \
  -d '{"duration": 60}'
```

### Suspend System (30 seconds)
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/suspend \
  -H "Content-Type: application/json" \
  -d '{"duration": 30}'
```

### Clear Alarm
```bash
curl -X POST http://192.168.1.200:8080/api/rtc/clear
```

---

## Common Workflows

### Test Suspend/Resume
```bash
# 1. Run diagnostics
rtc-pm-test

# 2. Short test (30s)
rtc-suspend 30

# 3. Longer test (5 minutes)
rtc-suspend 300
```

### Web UI Workflow
1. Open browser: `http://192.168.1.200:8080`
2. Scroll to "RTC Power Management" card
3. Click "Run Tests" to verify
4. Enter duration (seconds)
5. Click "Suspend" button
6. Wait for auto-resume
7. Check notification popup

### Power Saving Mode
```bash
# Long suspend (1 hour)
rtc-suspend 3600

# Very long suspend (8 hours)
rtc-suspend 28800
```

---

## Troubleshooting Quick Fixes

### Alarm Already Set
```bash
echo 0 > /sys/class/rtc/rtc0/wakealarm
```

### RTC Time Wrong
```bash
rtc-sync.sh
```

### Check Service Status
```bash
systemctl status rtc-sync.service
systemctl status system-monitor.service
```

### View Logs
```bash
journalctl -u rtc-sync.service -n 20
dmesg | grep -i rtc
```

---

## File Locations

### Scripts
- `/usr/sbin/rtc-suspend`
- `/usr/sbin/rtc-wakeup`
- `/usr/sbin/rtc-pm-test`
- `/usr/sbin/rtc-sync.sh`

### Services
- `/lib/systemd/system/rtc-pm.service` (disabled)
- `/lib/systemd/system/rtc-sync.service` (enabled)

### Documentation
- `/usr/share/doc/rtc-pm/README.md` (full documentation)
- `/usr/share/doc/rtc-pm/QUICK-REFERENCE.md` (this file)

### System Interfaces
- `/dev/rtc0` - RTC device
- `/sys/class/rtc/rtc0/wakealarm` - Alarm interface
- `/sys/power/state` - Suspend control

---

## API Response Examples

### Status Response
```json
{
  "available": true,
  "device": "/dev/rtc0",
  "system_time": "2025-11-02 14:35:00",
  "rtc_time": "Sat Nov  2 14:35:00 2025",
  "alarm_set": false,
  "suspend_support": {
    "mem": false,
    "freeze": true
  },
  "pm_firmware": false
}
```

### Success Response
```json
{
  "status": "success",
  "message": "RTC synchronized with system time"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "RTC device not available"
}
```

---

## Duration Presets

| Duration | Seconds | Use Case |
|----------|---------|----------|
| 10s      | 10      | Quick test |
| 30s      | 30      | Standard test |
| 1 min    | 60      | Short sleep |
| 5 min    | 300     | Quick break |
| 15 min   | 900     | Medium sleep |
| 1 hour   | 3600    | Power saving |
| 8 hours  | 28800   | Overnight |

---

## Power Consumption Reference

| State           | Current Draw | Notes |
|-----------------|--------------|-------|
| Active          | ~500mA       | Normal operation |
| S2Idle (freeze) | ~200-300mA   | CPU idle |
| Suspend (mem)   | ~50-100mA    | Requires PM firmware |

---

## See Also

Full documentation: `/usr/share/doc/rtc-pm/README.md`

Web interface: `http://192.168.1.200:8080`

---

**Version:** 1.0  
**Date:** November 2025
