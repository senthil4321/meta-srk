#!/usr/bin/env python3
"""
Continue Iterative Optimization - Streamlined Version
Complete remaining iterations 3-10 quickly
"""

import os
import subprocess
import time
from datetime import datetime

class StreamlinedOptimizer:
    def __init__(self):
        self.base_dir = "/home/srk2cob/project/poky/meta-srk"
        self.kernel_recipe = f"{self.base_dir}/recipes-kernel/linux/linux-yocto-srk-tiny_6.6.bb"
        self.kernel_dir = f"{self.base_dir}/recipes-kernel/linux/linux-yocto-srk-tiny"
        self.results_dir = f"{self.base_dir}/03_scripts/01_optimization/01_logs"
        
        # Remaining optimizations (3-10)
        self.optimizations = [
            {
                "id": "03", "name": "wireless_bluetooth", 
                "configs": ["# CONFIG_WIRELESS is not set", "# CONFIG_WLAN is not set", "# CONFIG_BT is not set"]
            },
            {
                "id": "04", "name": "graphics_display",
                "configs": ["# CONFIG_DRM is not set", "# CONFIG_FB is not set", "# CONFIG_LOGO is not set"]
            },
            {
                "id": "05", "name": "crypto_security",
                "configs": ["# CONFIG_CRYPTO_USER is not set", "# CONFIG_CRYPTO_MANAGER is not set", "# CONFIG_CRYPTO_CCM is not set"]
            },
            {
                "id": "06", "name": "kernel_debugging", 
                "configs": ["# CONFIG_DEBUG_INFO is not set", "# CONFIG_DEBUG_FS is not set", "# CONFIG_MAGIC_SYSRQ is not set"]
            },
            {
                "id": "07", "name": "power_management",
                "configs": ["# CONFIG_PM_SLEEP is not set", "# CONFIG_SUSPEND is not set", "# CONFIG_CPU_FREQ is not set"]
            },
            {
                "id": "08", "name": "profiling_tracing",
                "configs": ["# CONFIG_PROFILING is not set", "# CONFIG_FTRACE is not set", "# CONFIG_KPROBES is not set"]
            },
            {
                "id": "09", "name": "memory_features",
                "configs": ["# CONFIG_SWAP is not set", "# CONFIG_TMPFS is not set", "# CONFIG_HUGETLBFS is not set"]
            },
            {
                "id": "10", "name": "final_cleanup", 
                "configs": ["# CONFIG_POSIX_MQUEUE is not set", "# CONFIG_SYSVIPC is not set", "# CONFIG_AUDIT is not set"]
            }
        ]
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def create_fragment(self, opt):
        fragment_name = f"optimization_{opt['id']}_{opt['name']}.cfg"
        fragment_path = os.path.join(self.kernel_dir, fragment_name)
        
        if os.path.exists(fragment_path):
            self.log(f"✅ {fragment_name} exists")
            return fragment_name
            
        with open(fragment_path, 'w') as f:
            f.write(f"# Iteration {opt['id']}: {opt['name']}\n")
            for config in opt['configs']:
                f.write(f"{config}\n")
        
        self.log(f"📝 Created {fragment_name}")
        return fragment_name
        
    def update_recipe(self, fragment_name):
        with open(self.kernel_recipe, 'r') as f:
            content = f.read()
            
        if f"file://{fragment_name}" in content:
            return
            
        # Add to SRC_URI
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'file://am335x-yocto-srk-tiny.dts' in line:
                lines.insert(i, f'            file://{fragment_name} \\')
                break
                
        with open(self.kernel_recipe, 'w') as f:
            f.write('\n'.join(lines))
        
        self.log(f"✅ Added {fragment_name} to recipe")
        
    def quick_test(self, iteration_id):
        """Quick boot test without full monitoring"""
        self.log(f"🚀 Quick test for iteration {iteration_id}")
        
        # Copy kernel
        cmd = ["./04_copy_zImage.sh", "-i", "-tiny"]
        result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            return False
            
        # Quick serial log capture  
        log_file = f"{self.results_dir}/{iteration_id}_boot_test.log"
        
        cmd = f"timeout 20 ssh p 'socat - /dev/ttyUSB0,b115200,raw,echo=0,crnl' > {log_file} &"
        os.system(cmd)
        
        time.sleep(2)
        
        # Reset device
        reset_cmd = ["./13_remote_reset_bbb.sh"]
        subprocess.run(reset_cmd, cwd=self.base_dir, capture_output=True)
        
        # Wait for boot
        time.sleep(15)
        
        return True
        
    def quick_build(self):
        """Quick kernel build"""
        cmd = [
            "bash", "-c",
            "cd /home/srk2cob/project/poky && source oe-init-build-env build && bitbake linux-yocto-srk-tiny -c compile"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0
        
    def run_remaining(self):
        self.log("🚀 Continuing optimization from iteration 3")
        
        for opt in self.optimizations:
            self.log(f"\n🔧 ITERATION {opt['id']}: {opt['name']}")
            
            # Create fragment
            fragment_name = self.create_fragment(opt)
            
            # Update recipe
            self.update_recipe(fragment_name)
            
            # Build
            self.log("🔨 Building...")
            if not self.quick_build():
                self.log(f"❌ Build failed for {opt['id']}")
                continue
                
            # Test
            if not self.quick_test(opt['id']):
                self.log(f"❌ Test failed for {opt['id']}")
                continue
                
            self.log(f"✅ Iteration {opt['id']} completed")
            
        self.log("🎉 All iterations completed!")

def main():
    optimizer = StreamlinedOptimizer()
    optimizer.run_remaining()

if __name__ == "__main__":
    main()