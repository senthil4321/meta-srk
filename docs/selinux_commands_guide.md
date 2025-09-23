# SELinux Commands to Try in srk-10-selinux Initramfs

This guide provides SELinux commands you can experiment with in the SELinux-enabled initramfs environment (srk-10-selinux).

## Available SELinux Tools

The srk-10-selinux initramfs includes these SELinux utilities:

- `sestatus` - Display SELinux status and policy information
- `secon` - Display SELinux context of files/processes
- `semodule` - Manage SELinux policy modules
- `setsebool` - Set SELinux boolean values
- `load_policy` - Load SELinux policy (automatically done in init)

## Basic SELinux Status Commands

### Check SELinux Status

```bash
sestatus
```

Shows SELinux status, policy version, mode (enforcing/permissive), and loaded policy name.

### Check SELinux Context of Current Process

```bash
secon
```

Or for a specific PID:

```bash
secon -p $$
```

### Check SELinux Context of Files

```bash
secon -f /bin/sh
secon -f /init
ls -Z /  # If supported, shows SELinux contexts
```

## SELinux Boolean Management

### List All SELinux Booleans

```bash
setsebool -a
```

Shows all available SELinux booleans and their current values.

### Set a SELinux Boolean (Temporarily)

```bash
setsebool allow_execmem 1
setsebool deny_ptrace 0
```

Note: Changes are temporary and reset on reboot.

### Check Specific Boolean Value

```bash
setsebool -P allow_execmem  # -P makes it persistent
```

## SELinux Policy Module Management

### List Loaded Policy Modules

```bash
semodule -l
```

Shows all currently loaded SELinux policy modules.

### Get Information About a Module

```bash
semodule -i init
semodule -i ssh
```

## SELinux Mode Switching

### Check Current Mode

```bash
sestatus | grep "Current mode"
```

### Switch to Permissive Mode (if in enforcing)

```bash
setenforce 0
```

### Switch to Enforcing Mode

```bash
setenforce 1
```

## SELinux File Context Commands

### Check File Contexts

```bash
ls -Z /bin/sh 2>/dev/null || echo "ls -Z not supported"
```

### Restore File Contexts (if setfiles available)

```bash
# This might not work in minimal initramfs
setfiles -v /etc/selinux/targeted/contexts/files/file_contexts /
```

## SELinux Process Context

### Check Current Process Context

```bash
secon -p $$
```

### Check All Processes with SELinux Context

```bash
ps -eZ 2>/dev/null || ps aux | head -5
```

## SELinux Policy Information

### Check SELinux Mount Point

```bash
mount | grep selinuxfs
ls /sys/fs/selinux/
```

### Check SELinux Policy Capabilities

```bash
cat /sys/fs/selinux/policy_capabilities 2>/dev/null || echo "Policy capabilities not accessible"
```

## Experimentation Commands

### Try Creating a File and Check Its Context

```bash
touch /tmp/testfile
secon -f /tmp/testfile 2>/dev/null || echo "Context check failed"
```

### Test Boolean Effects

```bash
# Check current value
setsebool allow_execmem
# Try to set it
setsebool allow_execmem 1
# Check if it changed
setsebool allow_execmem
```

### Check SELinux Audit Logs (if available)

```bash
dmesg | grep -i selinux
dmesg | grep "avc:"
```

## Troubleshooting SELinux Issues

### If Something Fails Due to SELinux

```bash
# Switch to permissive mode temporarily
setenforce 0
# Try the command again
# Switch back to enforcing
setenforce 1
```

### Check for SELinux Errors

```bash
dmesg | tail -20
```

## Notes

- The initramfs runs in **permissive mode by default** for experimentation
- Most policy modules are loaded automatically during boot
- Changes made with `setsebool` without `-P` are temporary
- The environment is minimal, so some advanced SELinux features may not be available
- Use `exit` or `Ctrl+D` to reboot the system

## Quick Test Sequence

```bash
# 1. Check SELinux status
sestatus

# 2. Check current process context
secon

# 3. List SELinux booleans
setsebool -a | head -5

# 4. Try setting a boolean
setsebool allow_execmem 1

# 5. List loaded modules
semodule -l | head -5

# 6. Check SELinux filesystem
ls /sys/fs/selinux/
```</content>
<parameter name="filePath">/home/srk2cob/project/poky/meta-srk/docs/selinux_commands_guide.md
