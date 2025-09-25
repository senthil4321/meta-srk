#!/bin/bash

# Simple Remote BBB Reset Script
# Calls /bin/reset_bbb.sh on the server via SSH to reset the BeagleBone Black

echo "Resetting BBB remotely..."
ssh p "/bin/reset_bbb.sh"
echo "BBB reset command sent."
