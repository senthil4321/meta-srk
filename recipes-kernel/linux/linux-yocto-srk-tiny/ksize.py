#!/usr/bin/env python3
#
# Copyright (c) 2011, Intel Corporation.
#
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Display details of the kernel build size, broken up by built-in.[o,a]. Sort
# the objects by size. Run from the top level kernel build directory.
# Updated to handle initramfs images and perform size calculations.
#
# Author: Darren Hart <dvhart@linux.intel.com>
# Updated: SRK Development Team
#

import sys
import getopt
import os
import tempfile
import subprocess
from subprocess import *

def usage():
    prog = os.path.basename(sys.argv[0])
    print('Usage: %s [OPTION]... [FILE]...' % prog)
    print('  -d,                 display an additional level of drivers detail')
    print('  -i, --initramfs     analyze initramfs image(s)')
    print('  -k, --kernel        analyze kernel image(s) (default)')
    print('  -z, --zimage        analyze zImage file(s)')
    print('  -a, --all          analyze both kernel and initramfs')
    print('  -h, --help          display this help and exit')
    print('')
    print('Run %s from the top-level Linux kernel build directory.' % prog)
    print('For initramfs analysis, specify .cpio, .cpio.gz, or .cpio.xz files.')
    print('For zImage analysis, specify .bin files or zImage files.')
    print('')
    print('Examples:')
    print('  %s                    # Analyze kernel sizes' % prog)
    print('  %s -i initramfs.cpio  # Analyze initramfs' % prog)
    print('  %s -z zImage.bin      # Analyze zImage' % prog)
    print('  %s -a                 # Analyze both kernel and initramfs' % prog)

def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

class InitramfsAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.total_size = 0
        self.compressed_size = 0
        self.file_count = 0
        self.files = []
        self.directories = []
        self.executables = []
        self.libraries = []
        self.scripts = []
        self.others = []

        self._analyze_initramfs()

    def _analyze_initramfs(self):
        """Analyze the initramfs image and extract file information."""
        try:
            # Get compressed file size
            self.compressed_size = os.path.getsize(self.filepath)

            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract initramfs based on file type
                if self.filepath.endswith('.cpio.gz') or self.filepath.endswith('.cpio.xz'):
                    # Decompress first
                    if self.filepath.endswith('.gz'):
                        cmd = f"gunzip -c '{self.filepath}' | cpio -id --no-absolute-filenames -D '{temp_dir}' 2>/dev/null"
                    elif self.filepath.endswith('.xz'):
                        cmd = f"xz -dc '{self.filepath}' | cpio -id --no-absolute-filenames -D '{temp_dir}' 2>/dev/null"
                    else:
                        cmd = f"cpio -id --no-absolute-filenames -D '{temp_dir}' < '{self.filepath}' 2>/dev/null"
                else:
                    # Assume uncompressed cpio
                    cmd = f"cpio -id --no-absolute-filenames -D '{temp_dir}' < '{self.filepath}' 2>/dev/null"

                # Extract files
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                # Don't fail on extraction errors - some files might still be extracted

                # If extraction mostly failed, try to get file listing without extraction
                if not os.listdir(temp_dir):
                    self._get_file_listing_from_cpio()

                # Analyze extracted files even if extraction had warnings
                self._analyze_extracted_files(temp_dir)

        except Exception as e:
            print(f"Error analyzing {self.filepath}: {e}")
            # Try fallback method
            self._get_file_listing_from_cpio()

    def _get_file_listing_from_cpio(self):
        """Get file listing from cpio archive without extraction."""
        try:
            # Use cpio -t to list files without extracting
            if self.filepath.endswith('.cpio.gz'):
                cmd = f"gunzip -c '{self.filepath}' | cpio -t"
            elif self.filepath.endswith('.cpio.xz'):
                cmd = f"xz -dc '{self.filepath}' | cpio -t"
            else:
                cmd = f"cpio -t < '{self.filepath}'"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                self.file_count = len([f for f in files if f.strip()])

                # Create basic file entries (without size info)
                for filename in files:
                    if filename.strip():
                        file_info = {
                            'path': filename,
                            'size': 0,  # Unknown size
                            'type': self._guess_file_type_from_name(filename)
                        }
                        self.files.append(file_info)

                        # Basic categorization
                        if file_info['type'] == 'executable':
                            self.executables.append(file_info)
                        elif file_info['type'] == 'script':
                            self.scripts.append(file_info)
                        else:
                            self.others.append(file_info)

        except Exception as e:
            print(f"Warning: Could not get file listing: {e}")

    def _guess_file_type_from_name(self, filename):
        """Guess file type from filename when file command is not available."""
        if filename.startswith('bin/') or filename.startswith('sbin/') or 'busybox' in filename:
            return 'executable'
        elif filename.endswith(('.sh', '.py', '.pl', '.awk')):
            return 'script'
        elif 'lib' in filename or filename.endswith('.so'):
            return 'library'
        else:
            return 'other'

    def _analyze_extracted_files(self, temp_dir):
        """Analyze the extracted files from initramfs."""
        total_size = 0
        file_count = 0

        try:
            for root, dirs, files in os.walk(temp_dir):
                # Count directories
                for d in dirs:
                    self.directories.append(os.path.join(root, d))

                # Analyze files
                for f in files:
                    filepath = os.path.join(root, f)
                    try:
                        if os.path.exists(filepath) and os.path.isfile(filepath):
                            stat = os.stat(filepath)
                            file_size = stat.st_size
                            total_size += file_size
                            file_count += 1

                            # Categorize files
                            file_info = {
                                'path': filepath.replace(temp_dir, ''),
                                'size': file_size,
                                'type': self._get_file_type(filepath)
                            }

                            self.files.append(file_info)

                            # Categorize by type
                            if file_info['type'] == 'executable':
                                self.executables.append(file_info)
                            elif file_info['type'] == 'library':
                                self.libraries.append(file_info)
                            elif file_info['type'] == 'script':
                                self.scripts.append(file_info)
                            else:
                                self.others.append(file_info)

                    except OSError:
                        continue
        except Exception as e:
            print(f"Warning: Error during file analysis: {e}")

        self.total_size = total_size
        self.file_count = file_count
        """Analyze the extracted files from initramfs."""
        total_size = 0
        file_count = 0

        try:
            for root, dirs, files in os.walk(temp_dir):
                # Count directories
                for d in dirs:
                    self.directories.append(os.path.join(root, d))

                # Analyze files
                for f in files:
                    filepath = os.path.join(root, f)
                    try:
                        if os.path.exists(filepath) and os.path.isfile(filepath):
                            stat = os.stat(filepath)
                            file_size = stat.st_size
                            total_size += file_size
                            file_count += 1

                            # Categorize files
                            file_info = {
                                'path': filepath.replace(temp_dir, ''),
                                'size': file_size,
                                'type': self._get_file_type(filepath)
                            }

                            self.files.append(file_info)

                            # Categorize by type
                            if file_info['type'] == 'executable':
                                self.executables.append(file_info)
                            elif file_info['type'] == 'library':
                                self.libraries.append(file_info)
                            elif file_info['type'] == 'script':
                                self.scripts.append(file_info)
                            else:
                                self.others.append(file_info)

                    except OSError:
                        continue
        except Exception as e:
            print(f"Warning: Error during file analysis: {e}")

        self.total_size = total_size
        self.file_count = file_count

    def _get_file_type(self, filepath):
        """Determine file type using file command or extension."""
        try:
            result = subprocess.run(['file', filepath], capture_output=True, text=True)
            if result.returncode == 0:
                file_output = result.stdout.lower()
                if 'executable' in file_output or 'elf' in file_output:
                    return 'executable'
                elif 'shared object' in file_output or 'library' in file_output:
                    return 'library'
                elif 'script' in file_output or 'shell script' in file_output:
                    return 'script'
                else:
                    return 'other'
            else:
                # Fallback to extension
                if filepath.endswith(('.sh', '.py', '.pl', '.awk')):
                    return 'script'
                else:
                    return 'other'
        except:
            return 'other'

    def show_summary(self):
        """Display initramfs analysis summary."""
        print(f"\n{'='*80}")
        print(f"Initramfs Analysis: {self.filename}")
        print(f"{'='*80}")
        print(f"Compressed Size: {human_readable_size(self.compressed_size)}")
        print(f"Extracted Size:  {human_readable_size(self.total_size)}")
        print(f"Total Files:     {self.file_count}")
        print(f"Directories:     {len(self.directories)}")
        print(f"Executables:     {len(self.executables)}")
        print(f"Libraries:       {len(self.libraries)}")
        print(f"Scripts:         {len(self.scripts)}")
        print(f"Other Files:     {len(self.others)}")

        # Show compression ratio
        if self.compressed_size > 0:
            ratio = self.total_size / self.compressed_size
            print(".2f")

    def show_detailed_breakdown(self):
        """Show detailed file size breakdown."""
        print(f"\n{'='*80}")
        print(f"Detailed File Breakdown: {self.filename}")
        print(f"{'='*80}")

        # Sort files by size (largest first)
        sorted_files = sorted(self.files, key=lambda x: x['size'], reverse=True)

        print("<50")
        print("-" * 80)

        for file_info in sorted_files[:20]:  # Show top 20 largest files
            print("<50")

        if len(sorted_files) > 20:
            print(f"... and {len(sorted_files) - 20} more files")

        # Show category summaries
        print(f"\n{'='*40}")
        print("Category Breakdown:")
        print(f"{'='*40}")

        categories = [
            ("Executables", self.executables),
            ("Libraries", self.libraries),
            ("Scripts", self.scripts),
            ("Other Files", self.others)
        ]

    def show_detailed_breakdown(self):
        """Show detailed file size breakdown."""
        print(f"\n{'='*80}")
        print(f"Detailed File Breakdown: {self.filename}")
        print(f"{'='*80}")

        # Sort files by size (largest first)
        sorted_files = sorted(self.files, key=lambda x: x['size'], reverse=True)

        print("<50")
        print("-" * 80)

        for file_info in sorted_files[:20]:  # Show top 20 largest files
            print("<50")

        if len(sorted_files) > 20:
            print(f"... and {len(sorted_files) - 20} more files")

        # Show category summaries
        print(f"\n{'='*40}")
        print("Category Breakdown:")
        print(f"{'='*40}")

        categories = [
            ("Executables", self.executables),
            ("Libraries", self.libraries),
            ("Scripts", self.scripts),
            ("Other Files", self.others)
        ]

        for name, files in categories:
            if files:
                total_size = sum(f['size'] for f in files)
                print("<15")

class ZImageAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.total_size = 0
        self.header_size = 64  # Yocto adds 64-byte header
        self.zimage_size = 0
        self.kernel_size = 0
        self.initramfs_size = 0
        self.compression_info = {}

        self._analyze_zimage()

    def _analyze_zimage(self):
        """Analyze the zImage file structure."""
        try:
            self.total_size = os.path.getsize(self.filepath)

            with open(self.filepath, 'rb') as f:
                # Skip Yocto header
                f.seek(self.header_size)

                # Read zImage header (first 4 bytes should be magic)
                magic = f.read(4)
                if magic != b'\x00\x00\xa0\xe1':  # ARM zImage magic
                    print(f"Warning: Unexpected zImage magic: {magic.hex()}")

                # Read zImage header (52 bytes total)
                f.seek(self.header_size)
                header = f.read(52)

                # Extract information from header
                # zImage header format (ARM):
                # 0-3: magic
                # 4-7: start address
                # 8-11: end address
                # 12-15: initrd start
                # 16-19: initrd end

                if len(header) >= 20:
                    start_addr = int.from_bytes(header[4:8], 'little')
                    end_addr = int.from_bytes(header[8:12], 'little')
                    initrd_start = int.from_bytes(header[12:16], 'little')
                    initrd_end = int.from_bytes(header[16:20], 'little')

                    # Calculate sizes
                    if initrd_start > 0 and initrd_end > initrd_start:
                        self.initramfs_size = initrd_end - initrd_start
                        self.kernel_size = initrd_start - start_addr
                        self.zimage_size = end_addr - start_addr
                    else:
                        # No initramfs embedded
                        self.kernel_size = end_addr - start_addr
                        self.zimage_size = self.kernel_size
                        self.initramfs_size = 0

                # Try to find initramfs in the file
                f.seek(0)
                data = f.read()

                # Look for CPIO magic or gzip magic after the header
                cpio_magic = b'07070'
                gzip_magic = b'\x1f\x8b'

                cpio_pos = data.find(cpio_magic, self.header_size)
                gzip_pos = data.find(gzip_magic, self.header_size)

                if cpio_pos > 0:
                    self.initramfs_offset = cpio_pos
                    # Estimate initramfs size (from CPIO to end of file)
                    self.initramfs_size = len(data) - cpio_pos
                    self.kernel_size = cpio_pos - self.header_size
                elif gzip_pos > 0:
                    self.initramfs_offset = gzip_pos
                    self.initramfs_size = len(data) - gzip_pos
                    self.kernel_size = gzip_pos - self.header_size

        except Exception as e:
            print(f"Error analyzing zImage {self.filepath}: {e}")

    def show_summary(self):
        """Display zImage analysis summary."""
        print(f"\n{'='*80}")
        print(f"zImage Analysis: {self.filename}")
        print(f"{'='*80}")
        print(f"Total File Size: {human_readable_size(self.total_size)}")
        print(f"Yocto Header:    {human_readable_size(self.header_size)}")
        print(f"zImage Size:     {human_readable_size(self.zimage_size)}")
        print(f"Kernel Portion:  {human_readable_size(self.kernel_size)}")
        print(f"Initramfs Portion: {human_readable_size(self.initramfs_size)}")

        if self.total_size > 0:
            kernel_percent = (self.kernel_size / self.total_size) * 100
            initramfs_percent = (self.initramfs_size / self.total_size) * 100
            header_percent = (self.header_size / self.total_size) * 100

            print(f"")
            print(f"Kernel:     {kernel_percent:.1f}%")
            print(f"Initramfs:  {initramfs_percent:.1f}%")
            print(f"Header:     {header_percent:.1f}%")

        if hasattr(self, 'initramfs_offset'):
            print(f"Initramfs Offset: 0x{self.initramfs_offset:08x} ({self.initramfs_offset} bytes)")

    def show_detailed_info(self):
        """Show detailed zImage information."""
        print(f"\n{'='*60}")
        print("zImage Technical Details:")
        print(f"{'='*60}")

        try:
            with open(self.filepath, 'rb') as f:
                # Read and display header information
                f.seek(self.header_size)
                header = f.read(52)

                if len(header) >= 20:
                    print("zImage Header (ARM):")
                    print(f"  Magic:           {header[0:4].hex()}")
                    print(f"  Start Address:   0x{int.from_bytes(header[4:8], 'little'):08x}")
                    print(f"  End Address:     0x{int.from_bytes(header[8:12], 'little'):08x}")

                    initrd_start = int.from_bytes(header[12:16], 'little')
                    initrd_end = int.from_bytes(header[16:20], 'little')

                    if initrd_start > 0:
                        print(f"  Initrd Start:    0x{initrd_start:08x}")
                        print(f"  Initrd End:      0x{initrd_end:08x}")
                        print(f"  Initrd Size:     {human_readable_size(initrd_end - initrd_start)}")
                    else:
                        print("  Initrd:          None (separate initramfs)")

        except Exception as e:
            print(f"Error reading zImage header: {e}")

    def compare_with_separate(self, kernel_file=None, initramfs_file=None):
        """Compare with separate kernel and initramfs files."""
        print(f"\n{'='*60}")
        print("Comparison with Separate Files:")
        print(f"{'='*60}")

        total_separate = 0

        if kernel_file and os.path.exists(kernel_file):
            kernel_size = os.path.getsize(kernel_file)
            total_separate += kernel_size
            print(f"Separate Kernel:   {human_readable_size(kernel_size)} ({kernel_file})")
        else:
            print("Separate Kernel:   Not found")

        if initramfs_file and os.path.exists(initramfs_file):
            initramfs_size = os.path.getsize(initramfs_file)
            total_separate += initramfs_size
            print(f"Separate Initramfs: {human_readable_size(initramfs_size)} ({initramfs_file})")
        else:
            print("Separate Initramfs: Not found")

        if total_separate > 0:
            print(f"Combined Separate: {human_readable_size(total_separate)}")
            print(f"zImage Size:       {human_readable_size(self.total_size)}")

            savings = total_separate - self.total_size
            if savings > 0:
                print(f"Space Saved:       {human_readable_size(savings)} ({(savings/total_separate*100):.1f}%)")
            else:
                print(f"Space Overhead:    {human_readable_size(-savings)}")

def analyze_zimage_file(filepath):
    """Analyze a zImage file and display results."""
    analyzer = ZImageAnalyzer(filepath)
    analyzer.show_summary()
    analyzer.show_detailed_info()

    # Try to find corresponding separate files for comparison
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)

    # Look for separate kernel
    kernel_file = None
    for ext in ['.bin', '']:
        candidate = os.path.join(dirname, 'vmlinux' + ext)
        if os.path.exists(candidate):
            kernel_file = candidate
            break

    # Look for separate initramfs
    initramfs_file = None
    for pattern in ['*.cpio.gz', '*.cpio.xz', '*.cpio']:
        import glob
        candidates = glob.glob(os.path.join(dirname, pattern))
        if candidates:
            initramfs_file = candidates[0]  # Use first match
            break

    if kernel_file or initramfs_file:
        analyzer.compare_with_separate(kernel_file, initramfs_file)

class Sizes:
    def __init__(self, glob):
        self.title = glob
        p = Popen("size -t " + str(glob), shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        output = p.communicate()[0].splitlines()
        if len(output) > 2:
            sizes = output[-1].split()[0:4]
            self.text = int(sizes[0])
            self.data = int(sizes[1])
            self.bss = int(sizes[2])
            self.total = int(sizes[3])
        else:
            self.text = self.data = self.bss = self.total = 0

    def show(self, indent=""):
        print("%-32s %10d | %10d %10d %10d | %10s" % \
              (indent+self.title, self.total, self.text, self.data, self.bss, human_readable_size(self.total)))


class Report:
    def create(filename, title, subglob=None):
        r = Report(filename, title)
        path = os.path.dirname(filename)

        p = Popen("ls " + str(path) + "/*.o | grep -v built-in.o",
                  shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        glob = ' '.join(p.communicate()[0].splitlines())
        oreport = Report(glob, str(path) + "/*.o")
        oreport.sizes.title = str(path) + "/*.o"
        r.parts.append(oreport)

        if subglob:
            p = Popen("ls " + subglob, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            for f in p.communicate()[0].splitlines():
                path = os.path.dirname(f)
                r.parts.append(Report.create(f, path, str(path) + "/*/built-in.[o,a]"))
            r.parts.sort(reverse=True)

        for b in r.parts:
            r.totals["total"] += b.sizes.total
            r.totals["text"] += b.sizes.text
            r.totals["data"] += b.sizes.data
            r.totals["bss"] += b.sizes.bss

        r.deltas["total"] = r.sizes.total - r.totals["total"]
        r.deltas["text"] = r.sizes.text - r.totals["text"]
        r.deltas["data"] = r.sizes.data - r.totals["data"]
        r.deltas["bss"] = r.sizes.bss - r.totals["bss"]
        return r
    create = staticmethod(create)

    def __init__(self, glob, title):
        self.glob = glob
        self.title = title
        self.sizes = Sizes(glob)
        self.parts = []
        self.totals = {"total":0, "text":0, "data":0, "bss":0}
        self.deltas = {"total":0, "text":0, "data":0, "bss":0}

    def show(self, indent=""):
        rule = str.ljust(indent, 80, '-')
        print("%-32s %10s | %10s %10s %10s | %10s" % \
              (indent+self.title, "total", "text", "data", "bss", "Bytes"))
        print(rule)
        self.sizes.show(indent)
        print(rule)
        for p in self.parts:
            if p.sizes.total > 0:
                p.sizes.show(indent)
        print(rule)
        print("%-32s %10d | %10d %10d %10d | %10s" % \
              (indent+"sum", self.totals["total"], self.totals["text"],
               self.totals["data"], self.totals["bss"], human_readable_size(self.totals["total"])))
        print("%-32s %10d | %10d %10d %10d | %10s" % \
              (indent+"delta", self.deltas["total"], self.deltas["text"],
               self.deltas["data"], self.deltas["bss"], human_readable_size(self.deltas["total"])))
        print("\n")

    def __lt__(this, that):
        if that is None:
            return 1
        if not isinstance(that, Report):
            raise TypeError
        return this.sizes.total < that.sizes.total

    def __cmp__(this, that):
        if that is None:
            return 1
        if not isinstance(that, Report):
            raise TypeError
        if this.sizes.total < that.sizes.total:
            return -1
        if this.sizes.total > that.sizes.total:
            return 1
        return 0


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dhiakz", ["help", "initramfs", "kernel", "all", "zimage"])
    except getopt.GetoptError as err:
        print('%s' % str(err))
        usage()
        sys.exit(2)

    driver_detail = False
    analyze_initramfs = False
    analyze_kernel = True
    analyze_all = False
    analyze_zimage = False

    for o, a in opts:
        if o == '-d':
            driver_detail = True
        elif o in ('-i', '--initramfs'):
            analyze_initramfs = True
            analyze_kernel = False
        elif o in ('-k', '--kernel'):
            analyze_kernel = True
            analyze_initramfs = False
        elif o in ('-a', '--all'):
            analyze_all = True
        elif o in ('-z', '--zimage'):
            analyze_zimage = True
            analyze_kernel = False
            analyze_initramfs = False
        elif o in ('-h', '--help'):
            usage()
            sys.exit(0)
        else:
            assert False, "unhandled option"

    # Analyze zImage files if requested
    if analyze_zimage or (analyze_all and args):
        for filepath in args:
            if os.path.exists(filepath) and (filepath.endswith('.bin') or 'zImage' in filepath):
                analyze_zimage_file(filepath)
        if not args:
            # Look for zImage files in current directory
            import glob
            zimage_files = glob.glob('zImage*.bin')
            for filepath in zimage_files:
                analyze_zimage_file(filepath)

    # Analyze initramfs files if requested
    if analyze_initramfs or analyze_all:
        initramfs_files = []

        # If specific files provided as arguments, use them
        if args:
            initramfs_files = args
        else:
            # Look for common initramfs files in current directory
            common_files = [
                'initramfs.cpio', 'initramfs.cpio.gz', 'initramfs.cpio.xz',
                'core-image-tiny-initramfs-beaglebone-yocto-srk-tiny.cpio.gz',
                'core-image-tiny-initramfs-rpi-zero-debug-beaglebone-yocto-srk-tiny.cpio.gz'
            ]
            for filename in common_files:
                if os.path.exists(filename):
                    initramfs_files.append(filename)

        if initramfs_files:
            print("Analyzing initramfs images...")
            for filepath in initramfs_files:
                if os.path.exists(filepath):
                    analyzer = InitramfsAnalyzer(filepath)
                    analyzer.show_summary()
                    analyzer.show_detailed_breakdown()
                else:
                    print(f"Warning: {filepath} not found")
        else:
            print("No initramfs files found. Specify files or run from build directory.")

    # Analyze kernel if requested
    if analyze_kernel or analyze_all:
        if analyze_all:
            print("\n" + "="*80)
            print("KERNEL SIZE ANALYSIS")
            print("="*80)

        glob = "arch/*/built-in.[o,a] */built-in.[o,a]"
        vmlinux = Report.create("vmlinux",  "Linux Kernel", glob)

        vmlinux.show()
        for b in vmlinux.parts:
            if b.totals["total"] > 0 and len(b.parts) > 1:
                b.show()
            if b.title == "drivers" and driver_detail:
                for d in b.parts:
                    if d.totals["total"] > 0 and len(d.parts) > 1:
                        d.show("    ")


if __name__ == "__main__":
    main()
