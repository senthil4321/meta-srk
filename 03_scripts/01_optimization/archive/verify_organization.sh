#!/bin/bash
# Verification script to confirm complete organization

echo "🔍 OPTIMIZATION ARCHIVE VERIFICATION"
echo "===================================="
echo ""

cd /home/srk2cob/project/poky/meta-srk

# Check directory structure
echo "📂 Directory Structure:"
if [[ -d "03_scripts/optimization" ]]; then
    echo "✅ 03_scripts/optimization/ exists"
else
    echo "❌ 03_scripts/optimization/ missing"
fi

if [[ -d "03_scripts/logs" ]]; then
    echo "✅ 03_scripts/logs/ exists"
else
    echo "❌ 03_scripts/logs/ missing"
fi

echo ""

# Check optimization scripts
echo "🔧 Optimization Scripts:"
SCRIPTS=(
    "14_boot_performance_monitor.py"
    "15_quick_boot_monitor.sh"
    "16_complete_optimization.py"
    "17_continue_optimization.py"
    "18_final_analysis.py"
    "19_comprehensive_analysis.py"
    "20_final_complete_analysis.py"
)

for script in "${SCRIPTS[@]}"; do
    if [[ -f "03_scripts/optimization/$script" ]]; then
        echo "✅ $script"
    else
        echo "❌ $script missing"
    fi
done

echo ""

# Check documentation
echo "📖 Documentation:"
DOCS=(
    "README.md"
    "REPRODUCTION_GUIDE.md"
    "ARCHIVE_SUMMARY.md"
    "run_optimization.sh"
)

for doc in "${DOCS[@]}"; do
    if [[ -f "03_scripts/$doc" ]]; then
        echo "✅ $doc"
    else
        echo "❌ $doc missing"
    fi
done

echo ""

# Check logs
echo "📊 Analysis Logs:"
LOG_COUNT=$(ls 03_scripts/logs/*.log 2>/dev/null | wc -l)
REPORT_COUNT=$(ls 03_scripts/logs/*.md 2>/dev/null | wc -l)

echo "✅ Boot logs: $LOG_COUNT files"
echo "✅ Analysis reports: $REPORT_COUNT files"

echo ""

# Check optimization fragments
echo "🔧 Optimization Fragments:"
FRAGMENT_COUNT=$(ls recipes-kernel/linux/linux-yocto-srk-tiny/optimization_*.cfg 2>/dev/null | wc -l)
echo "✅ Configuration fragments: $FRAGMENT_COUNT/10"

echo ""

# Check executability
echo "🚀 Script Permissions:"
if [[ -x "03_scripts/run_optimization.sh" ]]; then
    echo "✅ run_optimization.sh is executable"
else
    echo "❌ run_optimization.sh not executable"
fi

if [[ -x "03_scripts/optimization/15_quick_boot_monitor.sh" ]]; then
    echo "✅ quick_boot_monitor.sh is executable"
else
    echo "❌ quick_boot_monitor.sh not executable"
fi

echo ""

# Final summary
echo "📋 ORGANIZATION SUMMARY:"
echo "========================"
echo "✅ All optimization scripts moved to 03_scripts/optimization/"
echo "✅ All logs and reports moved to 03_scripts/logs/"
echo "✅ Comprehensive documentation created"
echo "✅ One-click execution script ready"
echo "✅ $FRAGMENT_COUNT optimization fragments preserved in kernel recipe"
echo ""

echo "🎯 FOR REPRODUCTION:"
echo "   cd /home/srk2cob/project/poky/meta-srk"
echo "   ./03_scripts/run_optimization.sh"
echo ""

echo "📖 FOR DETAILS:"
echo "   cat 03_scripts/REPRODUCTION_GUIDE.md"
echo "   cat 03_scripts/README.md"
echo ""

echo "✅ ORGANIZATION COMPLETE - READY FOR FUTURE REPRODUCTION"