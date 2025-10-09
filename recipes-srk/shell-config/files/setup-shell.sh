#!/bin/sh

# Simple startup script for fixing shell prompt
# This script sets up proper environment for ash shell

# Set hostname if not set
if [ ! -f /etc/hostname ]; then
    echo "srk-device" > /etc/hostname
fi

# Set proper PS1 for ash shell in /etc/profile
cat > /etc/profile << 'EOF'
#!/bin/sh
export PATH="/bin:/sbin:/usr/bin:/usr/sbin"
export TERM=linux

# Simple prompt that works with ash
USER=$(whoami 2>/dev/null || echo "user")
HOST=$(cat /etc/hostname 2>/dev/null || echo "device")
export PS1="$USER@$HOST:\$PWD\$ "

# Update prompt when changing directories
cd() {
    command cd "$@"
    USER=$(whoami 2>/dev/null || echo "user")
    HOST=$(cat /etc/hostname 2>/dev/null || echo "device")
    export PS1="$USER@$HOST:\$PWD\$ "
}
EOF

# Make profile executable
chmod +x /etc/profile