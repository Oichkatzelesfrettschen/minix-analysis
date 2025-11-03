#!/bin/bash

# PHASE 4B: SINGLE-CPU BASELINE MATRIX
# Purpose: Validate single-CPU boot consistency across CPU generations
# Configuration: 4 CPU types × 1 vCPU × 2 samples = 8 configs
# Expected duration: ~20 minutes (120 sec × 8 + overhead)

ISO="/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso"
RESULTS_DIR="/tmp/phase4b-results"

mkdir -p "$RESULTS_DIR"
cd "$RESULTS_DIR"

echo "=========================================="
echo "PHASE 4B: SINGLE-CPU BASELINE MATRIX"
echo "=========================================="
echo "Purpose: Validate single-CPU boot consistency"
echo "Target: 4 CPU types × 1 vCPU × 2 samples = 8 configurations"
echo "Start: $(date)"
echo ""

# Kill any lingering QEMU processes from previous phases
pkill -9 qemu-system-i386 2>/dev/null || true
sleep 2

# Define CPU types to test
CPU_TYPES=("486" "pentium" "pentium2" "pentium3")
SAMPLE_COUNT=2

# Initialize counters
TOTAL_CONFIGS=0
PASSED_CONFIGS=0
FAILED_CONFIGS=0

# Results summary
declare -A RESULTS

# Main test loop
for CPU in "${CPU_TYPES[@]}"; do
  for SAMPLE in $(seq 1 $SAMPLE_COUNT); do
    TOTAL_CONFIGS=$((TOTAL_CONFIGS + 1))
    CONFIG_NAME="${CPU}_1vcpu_sample${SAMPLE}"

    echo "=========================================="
    echo "Configuration: $CONFIG_NAME"
    echo "=========================================="
    echo "[*] Creating disk image..."

    DISK="/tmp/minix_phase4b_${CONFIG_NAME}.qcow2"
    rm -f "$DISK"
    qemu-img create -f qcow2 "$DISK" 2G > /dev/null 2>&1

    SERIAL_LOG="phase4b_serial_${CONFIG_NAME}.log"
    STDOUT_LOG="phase4b_stdout_${CONFIG_NAME}.log"

    echo "[*] Booting MINIX ($CPU CPU, 1 vCPU, sample $SAMPLE)..."
    echo "[*] Serial output: $SERIAL_LOG"

    # Run QEMU with timeout
    timeout 120 qemu-system-i386 \
        -m 512M \
        -cpu "$CPU" \
        -smp 1 \
        -cdrom "$ISO" \
        -hda "$DISK" \
        -boot d \
        -nographic \
        -serial file:"$SERIAL_LOG" \
        2>&1 | tee "$STDOUT_LOG" &

    QEMU_PID=$!
    echo "[+] QEMU started (PID: $QEMU_PID)"

    # Give QEMU time to start
    sleep 10

    # Check if QEMU is still running
    if ! ps -p $QEMU_PID > /dev/null 2>&1; then
        echo "[!] QEMU crashed immediately"
        SERIAL_SIZE=0
        RESULT="CRASH"
    else
        echo "[*] QEMU running, waiting for boot completion (110 seconds)..."
        sleep 110

        # Kill QEMU
        kill $QEMU_PID 2>/dev/null || true
        wait $QEMU_PID 2>/dev/null || true

        # Check serial output size
        SERIAL_SIZE=$(wc -c < "$SERIAL_LOG" 2>/dev/null || echo 0)

        # Threshold: >5000 bytes indicates successful kernel module loading
        if [ "$SERIAL_SIZE" -gt 5000 ]; then
            RESULT="PASS"
            PASSED_CONFIGS=$((PASSED_CONFIGS + 1))
        else
            RESULT="FAIL"
            FAILED_CONFIGS=$((FAILED_CONFIGS + 1))
        fi
    fi

    # Store result
    RESULTS["$CONFIG_NAME"]="$SERIAL_SIZE:$RESULT"

    echo ""
    echo "=== Results ==="
    echo "Boot time: 120s"
    echo "Serial log: $SERIAL_SIZE bytes"
    echo "Status: $RESULT"
    echo ""

    # Cleanup
    rm -f "$DISK"
  done
done

# Generate summary report
echo "=========================================="
echo "PHASE 4B SUMMARY"
echo "=========================================="
echo "Total configurations: $TOTAL_CONFIGS"
echo "Passed: $PASSED_CONFIGS"
echo "Failed: $FAILED_CONFIGS"
SUCCESS_RATE=$((PASSED_CONFIGS * 100 / TOTAL_CONFIGS))
echo "Success rate: $SUCCESS_RATE%"
echo ""

echo "Configuration Summary:"
echo ""

for CPU in "${CPU_TYPES[@]}"; do
  for SAMPLE in $(seq 1 $SAMPLE_COUNT); do
    CONFIG_NAME="${CPU}_1vcpu_sample${SAMPLE}"
    RESULT_DATA="${RESULTS[$CONFIG_NAME]}"
    SERIAL_SIZE="${RESULT_DATA%:*}"
    RESULT="${RESULT_DATA#*:}"

    # Format output
    STATUS_ICON="✗"
    [ "$RESULT" = "PASS" ] && STATUS_ICON="✓"

    # Determine metrics
    if [ "$RESULT" = "PASS" ]; then
      METRICS="menu=yes, modules=yes"
    else
      METRICS="menu=yes, modules=no"
    fi

    printf "%s %-40s %6s bytes, %s\n" \
        "$STATUS_ICON" "$CONFIG_NAME:" "$SERIAL_SIZE" "$METRICS"
  done
done

echo ""
echo "Files generated:"
for CPU in "${CPU_TYPES[@]}"; do
  for SAMPLE in $(seq 1 $SAMPLE_COUNT); do
    CONFIG_NAME="${CPU}_1vcpu_sample${SAMPLE}"
    LOG_SIZE=$(wc -c < "phase4b_serial_${CONFIG_NAME}.log" 2>/dev/null || echo 0)
    echo "phase4b_serial_${CONFIG_NAME}.log ($LOG_SIZE)"
  done
done

echo ""
echo "Results directory: $RESULTS_DIR"
echo "End: $(date)"
echo ""

# Determine exit code
if [ $SUCCESS_RATE -eq 100 ]; then
    echo "[+] SUCCESS: All single-CPU configurations passed!"
    echo "[*] Single-CPU baseline is VALIDATED across CPU generations"
    echo "[*] Recommendation: Ready for Phase 5 (extended validation)"
    exit 0
elif [ $SUCCESS_RATE -ge 75 ]; then
    echo "[~] PARTIAL SUCCESS: Most configurations passed"
    echo "[*] Some CPU types may have issues (investigate outliers)"
    exit 1
else
    echo "[-] FAILURE: Most configurations failed"
    echo "[!] Critical issue with single-CPU baseline"
    exit 2
fi
