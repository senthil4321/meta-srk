#!/usr/bin/env python3
"""
Complete Iterative Kernel Optimization Script

Performs 10 iterations of kernel optimization with automated:
- Configuration fragment creation
- Kernel building  
- Boot performance testing
- Log collection
- Progress reporting
"""

import os
import sys
import subprocess
import time
import shutil
from datetime import datetime

class KernelOptimizer:
    def __init__(self):
        self.base_dir = "/home/srk2cob/project/poky/meta-srk"
        self.kernel_recipe = f"{self.base_dir}/recipes-kernel/linux/linux-yocto-srk-tiny_6.6.bb"
        self.kernel_dir = f"{self.base_dir}/recipes-kernel/linux/linux-yocto-srk-tiny"
        self.results_dir = f"{self.base_dir}/03_scripts/01_optimization/01_logs"
        self.build_dir = "/home/srk2cob/project/poky/build"
        
        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Define optimization iterations
        self.optimizations = [
            {
                "id": "01", 
                "name": "filesystem_optimization",
                "description": "Remove unused filesystem support",
                "configs": [
                    "# CONFIG_EXT2_FS is not set",
                    "# CONFIG_EXT3_FS is not set", 
                    "# CONFIG_EXT4_FS is not set",
                    "# CONFIG_XFS_FS is not set",
                    "# CONFIG_BTRFS_FS is not set",
                    "# CONFIG_F2FS_FS is not set",
                    "# CONFIG_NILFS2_FS is not set",
                    "# CONFIG_REISERFS_FS is not set",
                    "# CONFIG_JFS_FS is not set"
                ]
            },
            {
                "id": "02",
                "name": "sound_multimedia", 
                "description": "Remove sound and multimedia support",
                "configs": [
                    "# CONFIG_SOUND is not set",
                    "# CONFIG_SND is not set",
                    "# CONFIG_MEDIA_SUPPORT is not set",
                    "# CONFIG_VIDEO_DEV is not set",
                    "# CONFIG_DVB_CORE is not set",
                    "# CONFIG_RADIO is not set"
                ]
            },
            {
                "id": "03",
                "name": "wireless_bluetooth",
                "description": "Remove wireless and bluetooth support", 
                "configs": [
                    "# CONFIG_WIRELESS is not set",
                    "# CONFIG_WLAN is not set",
                    "# CONFIG_BT is not set",
                    "# CONFIG_BT_BREDR is not set",
                    "# CONFIG_BT_LE is not set",
                    "# CONFIG_CFG80211 is not set",
                    "# CONFIG_MAC80211 is not set"
                ]
            },
            {
                "id": "04", 
                "name": "graphics_display",
                "description": "Remove graphics and display support",
                "configs": [
                    "# CONFIG_DRM is not set",
                    "# CONFIG_FB is not set", 
                    "# CONFIG_BACKLIGHT_CLASS_DEVICE is not set",
                    "# CONFIG_LCD_CLASS_DEVICE is not set",
                    "# CONFIG_LOGO is not set",
                    "# CONFIG_VGA_CONSOLE is not set"
                ]
            },
            {
                "id": "05",
                "name": "crypto_security", 
                "description": "Remove crypto and security features",
                "configs": [
                    "# CONFIG_CRYPTO_USER is not set",
                    "# CONFIG_CRYPTO_MANAGER is not set",
                    "# CONFIG_CRYPTO_MANAGER2 is not set", 
                    "# CONFIG_CRYPTO_GF128MUL is not set",
                    "# CONFIG_CRYPTO_NULL is not set",
                    "# CONFIG_CRYPTO_CRYPTD is not set",
                    "# CONFIG_CRYPTO_AUTHENC is not set",
                    "# CONFIG_CRYPTO_CCM is not set",
                    "# CONFIG_CRYPTO_GCM is not set"
                ]
            },
            {
                "id": "06",
                "name": "kernel_debugging",
                "description": "Remove kernel debugging features",
                "configs": [
                    "# CONFIG_DEBUG_KERNEL is not set",
                    "# CONFIG_DEBUG_INFO is not set",
                    "# CONFIG_DEBUG_FS is not set", 
                    "# CONFIG_MAGIC_SYSRQ is not set",
                    "# CONFIG_DEBUG_BUGVERBOSE is not set",
                    "# CONFIG_DEBUG_MEMORY_INIT is not set",
                    "# CONFIG_DETECT_HUNG_TASK is not set"
                ]
            },
            {
                "id": "07",
                "name": "power_management",
                "description": "Remove power management features",
                "configs": [
                    "# CONFIG_PM is not set",
                    "# CONFIG_PM_SLEEP is not set",
                    "# CONFIG_SUSPEND is not set",
                    "# CONFIG_HIBERNATION is not set", 
                    "# CONFIG_PM_RUNTIME is not set",
                    "# CONFIG_CPU_FREQ is not set",
                    "# CONFIG_CPU_IDLE is not set"
                ]
            },
            {
                "id": "08", 
                "name": "profiling_tracing",
                "description": "Remove profiling and tracing",
                "configs": [
                    "# CONFIG_PROFILING is not set",
                    "# CONFIG_FTRACE is not set",
                    "# CONFIG_FUNCTION_TRACER is not set",
                    "# CONFIG_STACK_TRACER is not set",
                    "# CONFIG_DYNAMIC_FTRACE is not set",
                    "# CONFIG_KPROBES is not set",
                    "# CONFIG_UPROBE_EVENTS is not set"
                ]
            },
            {
                "id": "09",
                "name": "memory_features", 
                "description": "Remove memory management features",
                "configs": [
                    "# CONFIG_SWAP is not set",
                    "# CONFIG_SHMEM is not set",
                    "# CONFIG_TMPFS is not set",
                    "# CONFIG_HUGETLBFS is not set",
                    "# CONFIG_MEMORY_HOTPLUG is not set",
                    "# CONFIG_MIGRATION is not set",
                    "# CONFIG_COMPACTION is not set"
                ]
            },
            {
                "id": "10",
                "name": "final_cleanup",
                "description": "Final cleanup and optimization",
                "configs": [
                    "# CONFIG_POSIX_MQUEUE is not set",
                    "# CONFIG_SYSVIPC is not set",
                    "# CONFIG_CROSS_MEMORY_ATTACH is not set",
                    "# CONFIG_FHANDLE is not set",
                    "# CONFIG_USELIB is not set",
                    "# CONFIG_AUDIT is not set",
                    "# CONFIG_IKCONFIG is not set",
                    "# CONFIG_NUMA_BALANCING is not set"
                ]
            }
        ]
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def create_optimization_fragment(self, optimization):
        """Create optimization fragment file"""
        fragment_name = f"optimization_{optimization['id']}_{optimization['name']}.cfg"
        fragment_path = os.path.join(self.kernel_dir, fragment_name)
        
        # Skip if already exists
        if os.path.exists(fragment_path):
            self.log(f"✅ Fragment {fragment_name} already exists")
            return fragment_name
            
        self.log(f"📝 Creating {fragment_name}")
        
        with open(fragment_path, 'w') as f:
            f.write(f"# {optimization['description']}\n")
            f.write(f"# Iteration {optimization['id']}: {optimization['id']}_{optimization['name']}\n\n")
            for config in optimization['configs']:
                f.write(f"{config}\n")
            f.write("\n")
            
        return fragment_name
        
    def update_kernel_recipe(self, fragment_name):
        """Add fragment to kernel recipe if not already present"""
        with open(self.kernel_recipe, 'r') as f:
            content = f.read()
            
        if f"file://{fragment_name}" in content:
            self.log(f"✅ {fragment_name} already in recipe")
            return
            
        # Find SRC_URI section and add fragment
        lines = content.split('\n')
        src_uri_end = -1
        
        for i, line in enumerate(lines):
            if 'SRC_URI += "file://defconfig' in line:
                # Find the end of SRC_URI
                for j in range(i, len(lines)):
                    if lines[j].strip().endswith('"'):
                        src_uri_end = j
                        break
                break
                
        if src_uri_end > -1:
            # Insert before the last line of SRC_URI
            lines.insert(src_uri_end, f'            file://{fragment_name} \\')
            
            with open(self.kernel_recipe, 'w') as f:
                f.write('\n'.join(lines))
                
            self.log(f"✅ Added {fragment_name} to recipe")
        else:
            self.log(f"❌ Could not find SRC_URI section")
            
    def build_kernel(self):
        """Build the kernel"""
        self.log("🔨 Building kernel...")
        
        cmd = [
            "bash", "-c", 
            "cd /home/srk2cob/project/poky && source oe-init-build-env build && bitbake linux-yocto-srk-tiny"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            if result.returncode == 0:
                self.log("✅ Kernel build successful")
                return True
            else:
                self.log(f"❌ Kernel build failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.log("❌ Kernel build timed out")
            return False
        except Exception as e:
            self.log(f"❌ Build error: {e}")
            return False
            
    def copy_kernel(self):
        """Copy kernel to target"""
        self.log("📦 Copying kernel to target...")
        
        cmd = ["./04_copy_zImage.sh", "-i", "-tiny"]
        
        try:
            result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                self.log("✅ Kernel copied successfully")
                return True
            else:
                self.log(f"❌ Kernel copy failed: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"❌ Copy error: {e}")
            return False
            
    def run_boot_test(self, iteration_id):
        """Run boot performance test"""
        self.log("🚀 Running boot performance test...")
        
        log_file = f"{self.results_dir}/{iteration_id}_boot_test.log"
        
        try:
            # Run the Python boot monitor
            cmd = ["python3", "14_boot_performance_monitor.py"]
            
            with open(log_file, 'w') as f:
                result = subprocess.run(
                    cmd, 
                    cwd=self.base_dir,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=60
                )
                
            if result.returncode == 0:
                self.log(f"✅ Boot test completed - log saved to {log_file}")
                return True
            else:
                self.log(f"❌ Boot test failed")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("⏰ Boot test timed out")
            return False
        except Exception as e:
            self.log(f"❌ Boot test error: {e}")
            return False
            
    def extract_metrics(self, iteration_id):
        """Extract metrics from boot test log"""
        log_file = f"{self.results_dir}/{iteration_id}_boot_test.log"
        
        metrics = {
            "iteration": iteration_id,
            "boot_time": None,
            "kernel_size": None,
            "rwdata": None,
            "rodata": None,
            "available_memory": None,
            "total_memory": None
        }
        
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                
            # Extract boot time
            import re
            boot_match = re.search(r'Total Boot Time: (\d+\.\d+) seconds', content)
            if boot_match:
                metrics["boot_time"] = float(boot_match.group(1))
                
            # Extract memory info
            memory_match = re.search(r'(\d+)K/(\d+)K available \((\d+)K kernel code, (\d+)K rwdata, (\d+)K rodata', content)
            if memory_match:
                metrics["available_memory"] = int(memory_match.group(1))
                metrics["total_memory"] = int(memory_match.group(2))
                metrics["kernel_size"] = int(memory_match.group(3))
                metrics["rwdata"] = int(memory_match.group(4))
                metrics["rodata"] = int(memory_match.group(5))
                
        except Exception as e:
            self.log(f"❌ Error extracting metrics: {e}")
            
        return metrics
        
    def run_iteration(self, optimization):
        """Run a single optimization iteration"""
        iteration_id = optimization["id"]
        
        self.log(f"\n{'='*60}")
        self.log(f"🔧 ITERATION {iteration_id}: {optimization['description']}")
        self.log(f"{'='*60}")
        
        # Step 1: Create optimization fragment
        fragment_name = self.create_optimization_fragment(optimization)
        
        # Step 2: Update kernel recipe
        self.update_kernel_recipe(fragment_name)
        
        # Step 3: Build kernel
        if not self.build_kernel():
            self.log(f"❌ Iteration {iteration_id} failed at build step")
            return None
            
        # Step 4: Copy kernel
        if not self.copy_kernel():
            self.log(f"❌ Iteration {iteration_id} failed at copy step") 
            return None
            
        # Step 5: Run boot test
        if not self.run_boot_test(iteration_id):
            self.log(f"❌ Iteration {iteration_id} failed at test step")
            return None
            
        # Step 6: Extract metrics
        metrics = self.extract_metrics(iteration_id)
        
        self.log(f"✅ Iteration {iteration_id} completed successfully")
        
        if metrics["boot_time"]:
            self.log(f"📊 Boot time: {metrics['boot_time']:.3f}s")
        if metrics["rwdata"] and metrics["rodata"]:
            self.log(f"💾 Memory: rwdata={metrics['rwdata']}K, rodata={metrics['rodata']}K")
            
        return metrics
        
    def generate_report(self, all_metrics):
        """Generate final optimization report"""
        self.log("\n" + "="*60)
        self.log("📊 GENERATING OPTIMIZATION REPORT")
        self.log("="*60)
        
        report_file = f"{self.results_dir}/optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w') as f:
            f.write("# Kernel Optimization Report\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            f.write("## Optimization Summary\n\n")
            f.write("| Iteration | Description | Boot Time (s) | rwdata (K) | rodata (K) | Available Memory (K) |\n")
            f.write("|-----------|-------------|---------------|------------|------------|---------------------|\n")
            
            for metrics in all_metrics:
                if metrics:
                    f.write(f"| {metrics['iteration']} | {self.optimizations[int(metrics['iteration'])-1]['description']} |")
                    f.write(f" {metrics['boot_time']:.3f} |" if metrics['boot_time'] else " N/A |")
                    f.write(f" {metrics['rwdata']} |" if metrics['rwdata'] else " N/A |")
                    f.write(f" {metrics['rodata']} |" if metrics['rodata'] else " N/A |")
                    f.write(f" {metrics['available_memory']} |\n" if metrics['available_memory'] else " N/A |\n")
                    
            f.write("\n## Performance Trends\n\n")
            
            # Calculate improvements
            if len([m for m in all_metrics if m and m['boot_time']]) > 1:
                first_boot = next(m['boot_time'] for m in all_metrics if m and m['boot_time'])
                last_boot = next(m['boot_time'] for m in reversed(all_metrics) if m and m['boot_time'])
                improvement = first_boot - last_boot
                f.write(f"**Boot Time Improvement**: {improvement:.3f}s ({improvement/first_boot*100:.1f}%)\n\n")
                
            if len([m for m in all_metrics if m and m['rwdata']]) > 1:
                first_rwdata = next(m['rwdata'] for m in all_metrics if m and m['rwdata'])
                last_rwdata = next(m['rwdata'] for m in reversed(all_metrics) if m and m['rwdata'])
                improvement = first_rwdata - last_rwdata
                f.write(f"**rwdata Reduction**: {improvement}K ({improvement/first_rwdata*100:.1f}%)\n\n")
                
        self.log(f"📄 Report saved to: {report_file}")
        
    def run_all_iterations(self):
        """Run all optimization iterations"""
        all_metrics = []
        
        self.log("🚀 Starting iterative kernel optimization")
        self.log(f"📁 Results will be saved to: {self.results_dir}")
        
        for optimization in self.optimizations:
            try:
                metrics = self.run_iteration(optimization)
                all_metrics.append(metrics)
                
                # Brief pause between iterations
                time.sleep(2)
                
            except KeyboardInterrupt:
                self.log("🛑 Optimization interrupted by user")
                break
            except Exception as e:
                self.log(f"❌ Iteration {optimization['id']} failed: {e}")
                all_metrics.append(None)
                
        # Generate final report
        self.generate_report(all_metrics)
        
        self.log("\n🎉 Optimization process completed!")
        
        # Summary
        successful = len([m for m in all_metrics if m])
        self.log(f"✅ Successful iterations: {successful}/{len(self.optimizations)}")

def main():
    optimizer = KernelOptimizer()
    optimizer.run_all_iterations()

if __name__ == "__main__":
    main()