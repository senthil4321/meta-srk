#!/bin/bash

# Kernel Configuration Iteration Script
# Removes options from alldefconfig to defconfig 10 at a time until test passes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_SRK_DIR="$SCRIPT_DIR"
BUILD_DIR="$META_SRK_DIR/../build"
KERNEL_BUILD_DIR="$BUILD_DIR/tmp/work/beaglebone_yocto_srk_tiny-poky-linux-gnueabi/linux-yocto-srk-tiny/6.6.52+git/linux-beaglebone_yocto_srk_tiny-standard-build"
DEFCONFIG_FILE="$META_SRK_DIR/recipes-kernel/linux/linux-yocto-srk-tiny/defconfig"

echo "=== Kernel Configuration Iteration Script ==="
echo "Meta-SRK Dir: $META_SRK_DIR"
echo "Build Dir: $BUILD_DIR"
echo "Kernel Build Dir: $KERNEL_BUILD_DIR"
echo "Defconfig File: $DEFCONFIG_FILE"

# Function to generate alldefconfig
generate_alldefconfig() {
    echo "Configuring kernel..."
    cd "$BUILD_DIR"
    bitbake linux-yocto-srk-tiny -c configure

    echo "Generating alldefconfig..."
    cd "$KERNEL_BUILD_DIR"
    make alldefconfig
    cp .config alldefconfig.full
    echo "All config generated at: $KERNEL_BUILD_DIR/alldefconfig.full"
}

# Function to extract enabled options from alldefconfig that are not in defconfig
extract_missing_options() {
    local alldefconfig="$1"
    local defconfig="$2"

    echo "Extracting missing options from alldefconfig..."

    # Get all enabled options from alldefconfig (lines starting with CONFIG_.*=y or =m)
    grep "^CONFIG_.*=[ym]" "$alldefconfig" | sort > /tmp/alldefconfig_enabled

    # Get all options from defconfig
    grep "^CONFIG_" "$defconfig" | sort > /tmp/defconfig_options

    # Find options that are enabled in alldefconfig but not present in defconfig
    comm -23 /tmp/alldefconfig_enabled /tmp/defconfig_options > /tmp/missing_options

    echo "Found $(wc -l < /tmp/missing_options) missing options"
    cat /tmp/missing_options
}

# Function to remove options from defconfig
remove_options_from_defconfig() {
    local defconfig="$1"
    local options_file="$2"
    local count="$3"

    echo "Removing $count options from defconfig..."

    # Take first N options
    head -n "$count" "$options_file" > /tmp/options_to_remove

    # Backup original defconfig
    cp "$defconfig" "${defconfig}.backup"

    # Remove options by setting to =n
    while IFS= read -r option; do
        option_name=$(echo "$option" | cut -d'=' -f1)
        sed -i "s/^$option_name=y/$option_name=n/" "$defconfig"
    done < /tmp/options_to_remove

    echo "Removed options:"
    cat /tmp/options_to_remove
}

# Function to create trial directory and save configs
create_trial_dir() {
    local trial_num="$1"
    local trial_dir="$META_SRK_DIR/trial$trial_num"

    echo "Creating trial directory: $trial_dir"
    mkdir -p "$trial_dir"

    # Copy current defconfig
    cp "$DEFCONFIG_FILE" "$trial_dir/defconfig"

    # Copy .config if it exists
    if [ -f "$KERNEL_BUILD_DIR/.config" ]; then
        cp "$KERNEL_BUILD_DIR/.config" "$trial_dir/.config"
    fi

    echo "$trial_dir"
}

# Function to build kernel
build_kernel() {
    echo "Building kernel..."
    cd "$BUILD_DIR"
    bitbake linux-yocto-srk-tiny
}

# Function to copy image
copy_image() {
    echo "Copying image to target..."
    cd "$META_SRK_DIR"
    ./04_copy_zImage.sh -i -tiny
}

# Function to test kernel
test_kernel() {
    local trial_dir="$1"

    echo "Testing kernel boot..."
    cd "$META_SRK_DIR"

    # Run test and capture output
    if python3 test_serial_hello.py --test-suite image_11_tiny > "$trial_dir/test_output.log" 2>&1; then
        # Check if test passed (look for "PASS" in output)
        if grep -q "✅ PASS" "$trial_dir/test_output.log"; then
            echo "TEST PASSED!"
            cp "$trial_dir/test_output.log" "$trial_dir/test_success.log"
            return 0
        else
            echo "Test completed but did not pass"
            return 1
        fi
    else
        echo "Test failed to run"
        return 1
    fi
}

# Main iteration loop
main() {
    # Source Yocto environment
    source "$META_SRK_DIR/../poky/oe-init-build-env" "$BUILD_DIR"

    # Generate alldefconfig if not exists
    if [ ! -f "$KERNEL_BUILD_DIR/alldefconfig.full" ]; then
        generate_alldefconfig
    fi

    # Backup original defconfig
    cp "$DEFCONFIG_FILE" "$DEFCONFIG_FILE.original"

    # Start with alldefconfig
    cp "$KERNEL_BUILD_DIR/alldefconfig.full" "$DEFCONFIG_FILE"

    # Extract missing options (options to remove)
    extract_missing_options "$KERNEL_BUILD_DIR/alldefconfig.full" "$DEFCONFIG_FILE.original"

    local total_options=$(wc -l < /tmp/missing_options)
    echo "Total options to remove: $total_options"

    if [ "$total_options" -eq 0 ]; then
        echo "No options to remove. Config is already minimal."
        exit 0
    fi

    local batch_size=10
    local trial_num=1
    local remaining_options="$total_options"

    while [ "$remaining_options" -gt 0 ] && [ "$trial_num" -le 10 ]; do
        echo "=== Trial $trial_num ==="

        # Create trial directory
        local trial_dir=$(create_trial_dir "$trial_num")

        # Calculate how many options to add this iteration
        local options_to_add=$batch_size
        if [ "$remaining_options" -lt "$batch_size" ]; then
            options_to_add="$remaining_options"
        fi

        echo "Removing $options_to_add options in trial $trial_num"

        # Remove options from defconfig
        remove_options_from_defconfig "$DEFCONFIG_FILE" "/tmp/missing_options" "$options_to_add"

        # Remove the added options from the missing list
        tail -n +$((options_to_add + 1)) /tmp/missing_options > /tmp/missing_options.tmp
        mv /tmp/missing_options.tmp /tmp/missing_options

        # Build kernel
        if ! build_kernel; then
            echo "Build failed for trial $trial_num"
            echo "BUILD_FAILED" > "$trial_dir/build_status.txt"
            trial_num=$((trial_num + 1))
            remaining_options=$((remaining_options - options_to_add))
            continue
        fi

        echo "BUILD_SUCCESS" > "$trial_dir/build_status.txt"

        # Copy image
        if ! copy_image; then
            echo "Copy failed for trial $trial_num"
            echo "COPY_FAILED" > "$trial_dir/copy_status.txt"
            trial_num=$((trial_num + 1))
            remaining_options=$((remaining_options - options_to_add))
            continue
        fi

        echo "COPY_SUCCESS" > "$trial_dir/copy_status.txt"

        # Test kernel
        if test_kernel "$trial_dir"; then
            echo "SUCCESS: Kernel test passed in trial $trial_num!"
            echo "SUCCESS" > "$trial_dir/final_status.txt"
            exit 0
        else
            echo "Test failed for trial $trial_num"
            echo "TEST_FAILED" > "$trial_dir/final_status.txt"
        fi

        trial_num=$((trial_num + 1))
        remaining_options=$((remaining_options - options_to_add))
    done

    echo "Completed all 10 trials without success"
    exit 1
}

# Run main function
main "$@"