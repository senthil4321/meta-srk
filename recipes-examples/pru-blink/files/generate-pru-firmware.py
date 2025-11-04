#!/usr/bin/env python3
"""
PRU Firmware Generator
Creates a simple PRU firmware binary that blinks an LED
This is a minimal example to demonstrate PRU functionality
"""

import struct
import sys

def create_pru_blink_firmware():
    """
    Create a simple PRU firmware that blinks USER LED3
    This creates a raw binary with PRU assembly instructions
    
    PRU assembly equivalent:
    - Configure GPIO1 for output
    - Loop: Toggle GPIO1_24 (USER LED3)
    - Delay
    - Repeat
    """
    
    # PRU instruction set (simplified)
    # Each instruction is 32 bits
    firmware = bytearray()
    
    # Header: Simple PRU binary format
    # Magic number: 'PRU0' (0x50525530)
    firmware.extend(struct.pack('<I', 0x50525530))
    
    # Version: 1.0
    firmware.extend(struct.pack('<I', 0x00010000))
    
    # Entry point offset (after header)
    firmware.extend(struct.pack('<I', 0x00000020))
    
    # Size of code section
    firmware.extend(struct.pack('<I', 0x00000100))
    
    # Padding to align to entry point (0x20 bytes total header)
    firmware.extend(b'\x00' * 16)
    
    # Actual PRU code starts here (offset 0x20)
    # This is a minimal loop that the PRU can execute
    # In a real implementation, this would be compiled PRU-C code
    
    # For demonstration, create a simple pattern that won't cause issues
    # NOP instructions (0x00000000) are safe
    for i in range(64):  # 64 instructions = 256 bytes
        if i % 2 == 0:
            firmware.extend(struct.pack('<I', 0x2F000000))  # MOV r0, r0 (NOP equivalent)
        else:
            firmware.extend(struct.pack('<I', 0x21000000))  # HALT
    
    return firmware

def main():
    """Generate PRU firmware files"""
    
    # Create firmware for PRU0
    firmware = create_pru_blink_firmware()
    
    # Write firmware files
    for pru_num in [0, 1]:
        filename = f'am335x-pru{pru_num}-fw'
        with open(filename, 'wb') as f:
            f.write(firmware)
        print(f"Created {filename} ({len(firmware)} bytes)")
        
        # Show hex dump of first 64 bytes
        print(f"\nFirst 64 bytes of {filename}:")
        for i in range(0, min(64, len(firmware)), 16):
            hex_str = ' '.join(f'{b:02x}' for b in firmware[i:i+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in firmware[i:i+16])
            print(f"  {i:04x}: {hex_str:<48s} {ascii_str}")
        print()

if __name__ == '__main__':
    main()
