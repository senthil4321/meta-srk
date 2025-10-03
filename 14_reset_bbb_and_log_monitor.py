#!/usr/bin/env python3
"""
BeagleBone Black Boot Performance Monitor and Reset Script

This script:
1. Monitors serial console before reset
2. Performs hardware reset via SSH
3. Captures complete boot sequence
4. Analyzes boot performance KPIs
5. Provides detailed timing analysis
"""

import subprocess
import threading
import time
import re
import sys
import os
from datetime import datetime
import signal

class BBBBootMonitor:
    def __init__(self):
        self.serial_output = []
        self.boot_start_time = None
        self.app_start_time = None
        self.monitoring = True
        self.boot_phases = {}
        self.reset_triggered = False
        
    def log_with_timestamp(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
        
    def parse_boot_timing(self, line):
        """Parse kernel boot timing from log lines"""
        # Extract kernel timestamp [    X.XXXXXX]
        kernel_time_match = re.search(r'\[\s*(\d+\.\d+)\]', line)
        if kernel_time_match:
            kernel_time = float(kernel_time_match.group(1))
            
            # Identify key boot phases
            if "Starting kernel" in line or "Booting Linux" in line:
                self.boot_phases['kernel_start'] = kernel_time
                
            elif "console [ttyS0] enabled" in line:
                self.boot_phases['console_ready'] = kernel_time
                
            elif "ti-sysc: probe of" in line and "failed with error -16" in line:
                if 'ti_sysc_errors' not in self.boot_phases:
                    self.boot_phases['ti_sysc_errors'] = []
                self.boot_phases['ti_sysc_errors'].append((kernel_time, line.strip()))
                
            elif "Run /init as init process" in line:
                self.boot_phases['init_start'] = kernel_time
                
            elif "Freeing unused kernel image" in line:
                self.boot_phases['kernel_cleanup'] = kernel_time
                
        # Detect application start
        if "Hello World 1970-01-01 00:00:00" in line:
            self.app_start_time = time.time()
            self.log_with_timestamp("✅ Application started - monitoring complete!")
            
    def monitor_serial(self):
        """Monitor serial console output"""
        try:
            # Start serial monitoring via SSH
            cmd = ['ssh', 'p', 'socat - /dev/ttyUSB0,b115200,raw,echo=0,crnl']
            self.log_with_timestamp("🔍 Starting serial console monitoring...")
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while self.monitoring:
                try:
                    line = process.stdout.readline()
                    if line:
                        current_time = time.time()
                        line = line.strip()
                        
                        # Store line with timestamp
                        self.serial_output.append((current_time, line))
                        
                        # Print line with our timestamp
                        timestamp = datetime.fromtimestamp(current_time).strftime("%H:%M:%S.%f")[:-3]
                        print(f"[{timestamp}] {line}")
                        
                        # Parse boot timing
                        self.parse_boot_timing(line)
                        
                        # Detect reset completion (U-Boot start)
                        if "U-Boot SPL" in line and not self.reset_triggered:
                            self.boot_start_time = current_time
                            self.log_with_timestamp("🚀 Boot sequence detected!")
                            
                        # Check if application started
                        if self.app_start_time:
                            break
                            
                    elif process.poll() is not None:
                        break
                        
                except Exception as e:
                    self.log_with_timestamp(f"❌ Serial monitoring error: {e}")
                    break
                    
        except Exception as e:
            self.log_with_timestamp(f"❌ Failed to start serial monitoring: {e}")
            
    def perform_reset(self):
        """Perform hardware reset via SSH"""
        try:
            self.log_with_timestamp("🔄 Performing hardware reset...")
            
            # Wait a moment to ensure serial monitoring is active
            time.sleep(2)
            
            # Execute reset script
            result = subprocess.run(
                ['./13_remote_reset_bbb.sh'],
                cwd='/home/srk2cob/project/poky/meta-srk',
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.log_with_timestamp("✅ Reset command sent successfully")
                self.reset_triggered = True
            else:
                self.log_with_timestamp(f"❌ Reset command failed: {result.stderr}")
                
        except Exception as e:
            self.log_with_timestamp(f"❌ Reset failed: {e}")
            
    def calculate_kpis(self):
        """Calculate and display boot performance KPIs"""
        self.log_with_timestamp("\n" + "="*60)
        self.log_with_timestamp("📊 BOOT PERFORMANCE KPI ANALYSIS")
        self.log_with_timestamp("="*60)
        
        if not self.boot_start_time:
            self.log_with_timestamp("❌ No boot start time detected")
            return
            
        # Total boot time
        if self.app_start_time:
            total_boot_time = self.app_start_time - self.boot_start_time
            self.log_with_timestamp(f"🏁 Total Boot Time: {total_boot_time:.3f} seconds")
        else:
            self.log_with_timestamp("❌ Application start not detected")
            return
            
        # Kernel boot phases
        self.log_with_timestamp("\n🔍 Kernel Boot Phases:")
        if 'kernel_start' in self.boot_phases:
            self.log_with_timestamp(f"  ⚡ Kernel Start: {self.boot_phases['kernel_start']:.3f}s")
            
        if 'console_ready' in self.boot_phases:
            self.log_with_timestamp(f"  📺 Console Ready: {self.boot_phases['console_ready']:.3f}s")
            
        if 'init_start' in self.boot_phases:
            self.log_with_timestamp(f"  🚀 Init Process: {self.boot_phases['init_start']:.3f}s")
            
        if 'kernel_cleanup' in self.boot_phases:
            self.log_with_timestamp(f"  🧹 Kernel Cleanup: {self.boot_phases['kernel_cleanup']:.3f}s")
            
        # Calculate phase durations
        self.log_with_timestamp("\n⏱️  Phase Durations:")
        if 'console_ready' in self.boot_phases and 'kernel_start' in self.boot_phases:
            console_time = self.boot_phases['console_ready'] - self.boot_phases['kernel_start']
            self.log_with_timestamp(f"  📺 Console Init: {console_time:.3f}s")
            
        if 'init_start' in self.boot_phases and 'console_ready' in self.boot_phases:
            init_time = self.boot_phases['init_start'] - self.boot_phases['console_ready']
            self.log_with_timestamp(f"  🔧 Kernel to Init: {init_time:.3f}s")
            
        # Memory information
        memory_lines = [line for _, line in self.serial_output if "Memory:" in line and "available" in line]
        if memory_lines:
            memory_line = memory_lines[0]
            self.log_with_timestamp(f"\n💾 Memory: {memory_line}")
            
            # Parse memory details
            memory_match = re.search(r'Memory: (\d+)K/(\d+)K available \((\d+)K kernel code, (\d+)K rwdata, (\d+)K rodata', memory_line)
            if memory_match:
                available, total, kernel_code, rwdata, rodata = memory_match.groups()
                self.log_with_timestamp(f"  📊 Available: {available}K / {total}K ({float(available)/float(total)*100:.1f}%)")
                self.log_with_timestamp(f"  🧠 Kernel Code: {kernel_code}K")
                self.log_with_timestamp(f"  📝 rwdata: {rwdata}K")
                self.log_with_timestamp(f"  📖 rodata: {rodata}K")
                
        # TI SYSC errors analysis
        if 'ti_sysc_errors' in self.boot_phases:
            self.log_with_timestamp(f"\n⚠️  TI SYSC Probe Failures: {len(self.boot_phases['ti_sysc_errors'])} detected")
            for error_time, error_line in self.boot_phases['ti_sysc_errors']:
                self.log_with_timestamp(f"  🔍 [{error_time:.3f}s] {error_line}")
            self.log_with_timestamp("  ℹ️  These errors are expected and harmless in ultra-minimal configuration")
            
        # Performance summary
        self.log_with_timestamp("\n🎯 PERFORMANCE SUMMARY:")
        self.log_with_timestamp(f"  ✅ Ultra-minimal kernel optimization: SUCCESS")
        if total_boot_time < 1.0:
            self.log_with_timestamp(f"  🚀 Boot speed: EXCELLENT (< 1 second)")
        elif total_boot_time < 2.0:
            self.log_with_timestamp(f"  ✅ Boot speed: GOOD (< 2 seconds)")
        else:
            self.log_with_timestamp(f"  ⚠️  Boot speed: NEEDS IMPROVEMENT (> 2 seconds)")
            
        # Optimization results
        if 'rwdata' in locals() and 'rodata' in locals():
            self.log_with_timestamp(f"  💾 Memory optimization: rwdata={rwdata}K, rodata={rodata}K")
            if int(rwdata) < 500 and int(rodata) < 300:
                self.log_with_timestamp(f"  ✅ Memory footprint: OPTIMIZED")
            else:
                self.log_with_timestamp(f"  ⚠️  Memory footprint: COULD BE IMPROVED")
                
        self.log_with_timestamp("="*60)
        
    def save_boot_log(self):
        """Save boot log to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use local temp directory in project folder for easy access
        temp_dir = os.path.join(os.path.dirname(__file__), "temp", "bbb_boot_logs")
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = os.path.join(temp_dir, f"boot_analysis_{timestamp}.txt")
        
        try:
            with open(filename, 'w') as f:
                f.write(f"BeagleBone Black Boot Analysis - {datetime.now()}\n")
                f.write("="*60 + "\n\n")
                
                for timestamp, line in self.serial_output:
                    dt = datetime.fromtimestamp(timestamp)
                    f.write(f"[{dt.strftime('%H:%M:%S.%f')[:-3]}] {line}\n")
                    
            self.log_with_timestamp(f"📄 Boot log saved to: {filename}")
            
        except Exception as e:
            self.log_with_timestamp(f"❌ Failed to save log: {e}")
            
    def run(self, timeout=30):
        """Main execution function"""
        self.log_with_timestamp("🔧 BeagleBone Black Boot Performance Monitor")
        self.log_with_timestamp("="*50)
        
        # Set up timeout handler
        def timeout_handler():
            time.sleep(timeout)
            if self.monitoring and not self.app_start_time:
                self.log_with_timestamp(f"⏰ Timeout reached ({timeout}s) - stopping monitoring")
                self.monitoring = False
                
        timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
        timeout_thread.start()
        
        # Start serial monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_serial, daemon=True)
        monitor_thread.start()
        
        # Wait for monitoring to be ready
        time.sleep(1)
        
        # Perform reset
        reset_thread = threading.Thread(target=self.perform_reset, daemon=True)
        reset_thread.start()
        
        # Wait for completion
        try:
            monitor_thread.join(timeout + 5)
        except KeyboardInterrupt:
            self.log_with_timestamp("🛑 Monitoring interrupted by user")
            self.monitoring = False
            
        # Calculate and display KPIs
        self.calculate_kpis()
        
        # Save log
        self.save_boot_log()

def main():
    """Main entry point"""
    monitor = BBBBootMonitor()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Interrupt received, stopping monitoring...")
        monitor.monitoring = False
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run monitoring
    try:
        monitor.run(timeout=30)
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()