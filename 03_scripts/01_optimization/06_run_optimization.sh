#!/bin/bash
# Quick Kernel Optimization Execution Script
# This script runs the complete optimization with minimal user interaction

set -e  # Exit on any error

echo "🚀 Starting Kernel Optimization Reproduction"
echo "=============================================="

# Check we're in the right directory
if [[ ! -d "03_scripts/01_optimization" ]]; then
    echo "❌ Error: Must run from meta-srk directory"
    echo "   Expected: /home/srk2cob/project/poky/meta-srk"
    echo "   Current:  $(pwd)"
    exit 1
fi

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Yocto environment
if [[ ! -d "/home/srk2cob/project/poky" ]]; then
    echo "❌ Error: Yocto poky directory not found"
    exit 1
fi

# Check serial device
if [[ ! -c "/dev/ttyUSB0" ]]; then
    echo "⚠️  Warning: /dev/ttyUSB0 not found - check serial connection"
fi

# Check reset script
if [[ ! -x "./13_remote_reset_bbb.sh" ]]; then
    echo "⚠️  Warning: Reset script not found or not executable"
fi

echo "✅ Prerequisites check completed"
echo ""

# Source Yocto environment
echo "🔧 Setting up Yocto environment..."
cd /home/srk2cob/project/poky
source oe-init-build-env build > /dev/null 2>&1
cd /home/srk2cob/project/poky/meta-srk

echo "✅ Yocto environment ready"
echo ""

# Run optimization
echo "🚀 Starting 10-iteration kernel optimization..."
echo "   This will take approximately 20-30 minutes"
echo "   Progress will be shown as each iteration completes"
echo ""

cd 03_scripts/01_optimization

# Check if we should continue or start fresh
if [[ -f "../../recipes-kernel/linux/linux-yocto-srk-tiny/optimization_03_wireless_bluetooth.cfg" ]]; then
    echo "🔄 Found existing optimization fragments - continuing from where left off"
    python3 04_continue_optimization.py
else
    echo "🆕 Starting fresh optimization from iteration 1"
    python3 03_complete_optimization.py
fi

echo ""
echo "✅ Optimization iterations completed!"
echo ""

# Generate final analysis
echo "📊 Generating comprehensive final analysis..."
python3 05_final_complete_analysis.py

echo ""
echo "🎉 OPTIMIZATION COMPLETE!"
echo "=========================="
echo ""

# Show results
echo "📊 Results Summary:"
echo "-------------------"

# Count optimization fragments
FRAGMENT_COUNT=$(ls ../../recipes-kernel/linux/linux-yocto-srk-tiny/optimization_*.cfg 2>/dev/null | wc -l)
echo "✅ Optimization fragments created: $FRAGMENT_COUNT/10"

# Show kernel size
KERNEL_PATH="/home/srk2cob/project/poky/build/tmp/deploy/images/beaglebone-yocto-srk-tiny/zImage-beaglebone-yocto-srk-tiny.bin"
if [[ -L "$KERNEL_PATH" ]]; then
    KERNEL_SIZE=$(stat -L -c%s "$KERNEL_PATH" 2>/dev/null | numfmt --to=iec 2>/dev/null || echo "Unknown")
    echo "✅ Final kernel size: ${KERNEL_SIZE}B"
else
    echo "⚠️  Kernel size: Not available (check build)"
fi

# Show recent reports
LATEST_REPORT=$(ls ../logs/FINAL_COMPLETE_REPORT_*.md 2>/dev/null | tail -1)
if [[ -n "$LATEST_REPORT" ]]; then
    echo "✅ Analysis report: $(basename "$LATEST_REPORT")"
else
    echo "⚠️  Analysis report: Not found"
fi

echo ""
echo "📁 Output Locations:"
echo "  📋 Scripts:     03_scripts/optimization/"
echo "  📊 Logs:        03_scripts/logs/"
echo "  🔧 Fragments:   recipes-kernel/linux/linux-yocto-srk-tiny/optimization_*.cfg"
echo "  📖 Reports:     03_scripts/logs/FINAL_COMPLETE_REPORT_*.md"
echo ""

echo "🔍 Next Steps:"
echo "  1. Review the final analysis report in 03_scripts/logs/"
echo "  2. Test the optimized kernel on target hardware"
echo "  3. Verify all required functionality still works"
echo ""

echo "📖 For detailed instructions, see:"
echo "  📋 03_scripts/README.md"
echo "  📋 03_scripts/REPRODUCTION_GUIDE.md"
echo ""

echo "✅ Kernel optimization reproduction completed successfully!"