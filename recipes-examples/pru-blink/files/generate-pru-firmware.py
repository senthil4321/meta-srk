#!/usr/bin/env python3
"""
Generate PRU firmware files for AM335x PRU cores
Creates ELF format firmware compatible with remoteproc driver
"""

import struct
import sys

def generate_pru_elf_firmware(output_file, pru_num):
    """Generate PRU firmware in ELF format"""
    
    # ELF Header (52 bytes for 32-bit ELF)
    # e_ident: ELF magic + class/data/version
    e_ident = b'\x7fELF'  # Magic
    e_ident += b'\x01'     # ELFCLASS32 (32-bit)
    e_ident += b'\x01'     # ELFDATA2LSB (little endian)
    e_ident += b'\x01'     # EV_CURRENT (version 1)
    e_ident += b'\x00' * 9  # EI_PAD (padding)
    
    e_type = 2          # ET_EXEC (executable file)
    e_machine = 144     # EM_TI_PRU (TI PRU - unofficial, but used)
    e_version = 1       # EV_CURRENT
    e_entry = 0         # Entry point (PRU starts at 0)
    e_phoff = 52        # Program header offset (right after ELF header)
    e_shoff = 0         # Section header offset (none for minimal ELF)
    e_flags = 0         # Processor-specific flags
    e_ehsize = 52       # ELF header size
    e_phentsize = 32    # Program header entry size
    e_phnum = 1         # Number of program headers
    e_shentsize = 0     # Section header entry size
    e_shnum = 0         # Number of section headers
    e_shstrndx = 0      # Section header string table index
    
    elf_header = e_ident
    elf_header += struct.pack('<HHIIIIIHHHHHH',
                              e_type, e_machine, e_version, e_entry,
                              e_phoff, e_shoff, e_flags, e_ehsize,
                              e_phentsize, e_phnum, e_shentsize,
                              e_shnum, e_shstrndx)
    
    # PRU code (simple infinite loop with NOP)
    # Format: 32-bit little endian instructions
    code = []
    # Loop: MOV r0, r0 (NOP) and JMP to start
    for i in range(8):
        code.append(0x2F000000)  # MOV r0, r0 (NOP)
    code.append(0x2100E0E0)  # HALT
    
    code_bytes = struct.pack('<' + 'I' * len(code), *code)
    code_size = len(code_bytes)
    
    # Program Header (32 bytes)
    # Describes a loadable segment
    p_type = 1          # PT_LOAD (loadable segment)
    p_offset = 52 + 32  # Offset in file (after ELF header + program header)
    p_vaddr = 0         # Virtual address (PRU instruction memory starts at 0)
    p_paddr = 0         # Physical address
    p_filesz = code_size  # Size in file
    p_memsz = code_size   # Size in memory
    p_flags = 5         # PF_R | PF_X (readable and executable)
    p_align = 4         # Alignment
    
    program_header = struct.pack('<IIIIIIII',
                                 p_type, p_offset, p_vaddr, p_paddr,
                                 p_filesz, p_memsz, p_flags, p_align)
    
    # Combine all parts
    firmware = elf_header + program_header + code_bytes
    
    # Write firmware file
    with open(output_file, 'wb') as f:
        f.write(firmware)
    
    print(f"Generated {output_file} ({len(firmware)} bytes)")
    print(f"  ELF header: {len(elf_header)} bytes")
    print(f"  Program header: {len(program_header)} bytes")
    print(f"  Code section: {code_size} bytes")
    
    # Display hex dump of first 128 bytes
    print(f"\nFirst 128 bytes of {output_file}:")
    for i in range(0, min(128, len(firmware)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in firmware[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in firmware[i:i+16])
        print(f"{i:08x}  {hex_str:<48}  |{ascii_str}|")

if __name__ == '__main__':
    print("=== PRU ELF Firmware Generator ===")
    
    # Generate firmware for both PRU cores
    generate_pru_elf_firmware('am335x-pru0-fw', 0)
    print()
    generate_pru_elf_firmware('am335x-pru1-fw', 1)
    
    print("\nELF firmware files generated successfully!")
