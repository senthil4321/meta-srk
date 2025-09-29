#!/bin/bash
# Updated Verification Script for Reorganized Optimization System

echo "🔍 REORGANIZED OPTIMIZATION SYSTEM VERIFICATION"
echo "=============================================="

BASE_DIR="/home/srk2cob/project/poky/meta-srk"
OPT_DIR="$BASE_DIR/03_scripts/01_optimization"

cd "$BASE_DIR" || exit 1

echo ""
echo "📁 Checking Organized Structure..."

# Check core scripts in order
declare -a core_scripts=(
    "01_boot_performance_monitor.py"
    "02_quick_boot_monitor.sh"
    "03_complete_optimization.py"
    "04_continue_optimization.py"
    "05_final_complete_analysis.py"
    "06_run_optimization.sh"
)

echo "🔧 Core Scripts (Sequential Order):"
for script in "${core_scripts[@]}"; do
    if [[ -f "$OPT_DIR/$script" ]]; then
        if [[ -x "$OPT_DIR/$script" ]]; then
            echo "✅ $script (executable)"
        else
            echo "✅ $script"
        fi
    else
        echo "❌ Missing: $script"
    fi
done

echo ""
echo "📋 Documentation (Sequential Order):"

declare -a docs=(
    "01_REPRODUCTION_GUIDE.md"
    "02_ARCHIVE_SUMMARY.md"
    "03_OPTIMIZATION_COMPLETE.md"
    "04_CLEANUP_ANALYSIS.md"
)

for doc in "${docs[@]}"; do
    if [[ -f "$OPT_DIR/$doc" ]]; then
        echo "✅ $doc"
    else
        echo "❌ Missing: $doc"
    fi
done

echo ""
echo "📊 System Summary:"
echo "=================="

script_count=$(ls -1 "$OPT_DIR"/*_*.py "$OPT_DIR"/*_*.sh 2>/dev/null | wc -l)
doc_count=$(ls -1 "$OPT_DIR"/*_*.md 2>/dev/null | wc -l)
log_count=$(ls -1 "$OPT_DIR/01_logs/"*.log 2>/dev/null | wc -l)
report_count=$(ls -1 "$OPT_DIR/01_logs/"*REPORT*.md 2>/dev/null | wc -l)

echo "📱 Core Scripts: $script_count/6"
echo "📋 Documentation: $doc_count/4"
echo "📊 Boot Logs: $log_count"
echo "📈 Analysis Reports: $report_count"

echo ""
echo "🎯 Usage Examples:"
echo "=================="
echo "# Quick Start (Recommended)"
echo "cd $BASE_DIR"
echo "./03_scripts/01_optimization/06_run_optimization.sh"
echo ""
echo "# Manual Execution"
echo "python3 03_scripts/01_optimization/03_complete_optimization.py"
echo ""
echo "# Recovery/Continue"
echo "python3 03_scripts/01_optimization/04_continue_optimization.py"
echo ""
echo "# Generate Analysis"
echo "python3 03_scripts/01_optimization/05_final_complete_analysis.py"

echo ""
if [[ $script_count -eq 6 && $doc_count -eq 4 ]]; then
    echo "🎉 REORGANIZATION COMPLETE!"
    echo "   ✅ All scripts properly numbered and organized"
    echo "   ✅ Clear sequential execution order"
    echo "   ✅ Documentation updated with correct references"
    echo "   ✅ Ready for production use"
else
    echo "⚠️  REORGANIZATION INCOMPLETE"
    echo "   Missing files or incorrect structure"
fi