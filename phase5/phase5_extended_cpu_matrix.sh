#!/bin/bash

#===============================================================
# PHASE 5: EXTENDED SINGLE-CPU BASELINE VALIDATION
# With Real x86 CPU Specifications
#===============================================================

set -u  # Exit on undefined variable

# ISO and configuration
ISO="/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso"
RESULTS_DIR="/tmp/phase5-results"
EXECUTION_LOG="/tmp/phase5_execution.log"
RESULTS_REPORT="/tmp/PHASE_5_RESULTS_REPORT.md"

# Ensure ISO exists
if [ ! -f "$ISO" ]; then
    echo "[ERROR] ISO not found: $ISO"
    exit 1
fi

# Create results directory
mkdir -p "$RESULTS_DIR"
cd "$RESULTS_DIR"

# Start timing
START_TIME=$(date +'%Y-%m-%d %H:%M:%S %Z')
START_SECONDS=$(date +%s)

# Initialize execution log
cat > "$EXECUTION_LOG" << 'LOG_INIT'
==========================================
PHASE 5: EXTENDED SINGLE-CPU BASELINE
==========================================
Purpose: Validate single-CPU boot across diverse CPU models and vCPU presentations
Target: Extended CPU type coverage with real instruction set data
Start: (timestamp will be added)

CPU Generations Tested:
- Intel 486 (base x86-32, 5-stage pipeline, 8KB cache)
- Intel Pentium (P5, dual-pipe, TSC, 8KB L1)
- Intel Pentium II (P6, out-of-order, 16KB L1, 512KB L2)
- Intel Pentium III (P6 enhanced, SSE support, 256KB on-die L2)
- AMD K6 (in-order, 3DNow!, 32KB L1, 256KB L2)

Test Matrix:
- 5 CPU types × 1 vCPU × 2-3 samples = 12-15 configurations
- ALL tests use -smp 1 (single-CPU mode, per user directive)
- Expected output: 7762 bytes (full MINIX kernel boot sequence)

==========================================
Configuration Results
==========================================

LOG_INIT

echo "Phase 5 started at $START_TIME" >> "$EXECUTION_LOG"
echo "" >> "$EXECUTION_LOG"

# Define CPU types and their specifications
declare -A CPU_TYPES=(
    [486]="486"
    [pentium]="pentium"
    [pentium2]="pentium2"
    [pentium3]="pentium3"
    [k6]="k6"
)

# CPU architecture reference (from Phase 5 research)
declare -A CPU_SPECS=(
    [486]="5-stage pipeline, 8KB unified cache, x87 FPU, 16-133 MHz"
    [pentium]="5-stage dual-pipe, 8KB L1I + 8KB L1D, TSC, CPUID, 60-200 MHz"
    [pentium2]="12-stage P6 μOp, 16KB L1I + 16KB L1D, 512KB L2, MMX, 233-450 MHz"
    [pentium3]="10-stage P6 enhanced, 16KB L1I + 16KB L1D, 256KB on-die L2, SSE, 450-1400 MHz"
    [k6]="6-7 stage, 32KB L1I + 32KB L1D, 256KB L2, MMX + 3DNow!, 166-550 MHz"
)

# Test counters
TOTAL_CONFIGS=0
PASSED_CONFIGS=0
FAILED_CONFIGS=0
ERROR_CONFIGS=0

# Results arrays
declare -a CONFIG_NAMES
declare -a CONFIG_RESULTS
declare -a CONFIG_SIZES
declare -a CONFIG_TIMES

# Phase 5 testing loop
for CPU_TYPE in "${!CPU_TYPES[@]}"; do
    CPU_EMULATION="${CPU_TYPES[$CPU_TYPE]}"
    
    # Determine sample count (2 for most, 3 for Intel 486 baseline)
    if [ "$CPU_TYPE" = "486" ]; then
        SAMPLE_COUNT=3
    else
        SAMPLE_COUNT=2
    fi
    
    echo "" | tee -a "$EXECUTION_LOG"
    echo "========================================" | tee -a "$EXECUTION_LOG"
    echo "CPU Type: $CPU_TYPE" | tee -a "$EXECUTION_LOG"
    echo "Architecture: ${CPU_SPECS[$CPU_TYPE]}" | tee -a "$EXECUTION_LOG"
    echo "Samples: $SAMPLE_COUNT" | tee -a "$EXECUTION_LOG"
    echo "========================================" | tee -a "$EXECUTION_LOG"
    
    for SAMPLE in $(seq 1 $SAMPLE_COUNT); do
        TOTAL_CONFIGS=$((TOTAL_CONFIGS + 1))
        CONFIG_NAME="${CPU_TYPE}_1vcpu_sample${SAMPLE}"
        
        echo "" | tee -a "$EXECUTION_LOG"
        echo "[*] Configuration: $CONFIG_NAME" | tee -a "$EXECUTION_LOG"
        echo "[*] Test $TOTAL_CONFIGS of $(echo "${#CPU_TYPES[@]}" | awk '{print $1 * 2 + 3}')" | tee -a "$EXECUTION_LOG"
        
        # Create disk image
        DISK_PATH="/tmp/minix_phase5_${CONFIG_NAME}.qcow2"
        SERIAL_LOG="phase5_serial_${CONFIG_NAME}.log"
        STDOUT_LOG="phase5_stdout_${CONFIG_NAME}.log"
        
        rm -f "$DISK_PATH" 2>/dev/null
        qemu-img create -f qcow2 "$DISK_PATH" 2G > /dev/null 2>&1
        
        echo "[*] Created disk: $DISK_PATH" | tee -a "$EXECUTION_LOG"
        
        # Record test start time
        TEST_START=$(date +%s%N)
        
        # Boot QEMU with specific CPU and serial output
        echo "[*] Booting MINIX (CPU: $CPU_EMULATION, 1 vCPU)..." | tee -a "$EXECUTION_LOG"
        
        timeout 130 qemu-system-i386 \
            -m 512M \
            -cpu "$CPU_EMULATION" \
            -smp 1 \
            -cdrom "$ISO" \
            -hda "$DISK_PATH" \
            -boot d \
            -nographic \
            -serial file:"$SERIAL_LOG" \
            2>&1 | tee "$STDOUT_LOG" &
        
        QEMU_PID=$!
        echo "[+] QEMU started (PID: $QEMU_PID)" | tee -a "$EXECUTION_LOG"
        
        # Wait for boot to complete (120 seconds)
        sleep 120
        
        # Check if QEMU is still running
        if ps -p $QEMU_PID > /dev/null 2>&1; then
            echo "[*] Terminating QEMU after timeout..." | tee -a "$EXECUTION_LOG"
            kill $QEMU_PID 2>/dev/null || true
            sleep 2
            kill -9 $QEMU_PID 2>/dev/null || true
        fi
        
        wait $QEMU_PID 2>/dev/null || true
        
        # Calculate test duration
        TEST_END=$(date +%s%N)
        TEST_DURATION_MS=$(( (TEST_END - TEST_START) / 1000000 ))
        
        # Check results
        if [ ! -f "$SERIAL_LOG" ]; then
            echo "=== Results ===" | tee -a "$EXECUTION_LOG"
            echo "Status: ERROR (no serial log)" | tee -a "$EXECUTION_LOG"
            CONFIG_RESULTS+=("ERROR")
            CONFIG_SIZES+=(0)
            CONFIG_TIMES+=("$TEST_DURATION_MS")
            ERROR_CONFIGS=$((ERROR_CONFIGS + 1))
        else
            SERIAL_SIZE=$(wc -c < "$SERIAL_LOG" 2>/dev/null || echo 0)
            
            # Success threshold: > 5000 bytes (full boot), expect 7762 bytes
            if [ "$SERIAL_SIZE" -gt 5000 ]; then
                STATUS="PASS"
                PASSED_CONFIGS=$((PASSED_CONFIGS + 1))
                echo "=== Results ===" | tee -a "$EXECUTION_LOG"
                echo "Boot time: 120s (timeout)" | tee -a "$EXECUTION_LOG"
                echo "Serial log: $SERIAL_LOG ($SERIAL_SIZE bytes)" | tee -a "$EXECUTION_LOG"
                echo "Status: PASS" | tee -a "$EXECUTION_LOG"
                CONFIG_RESULTS+=("PASS")
            else
                STATUS="FAIL"
                FAILED_CONFIGS=$((FAILED_CONFIGS + 1))
                echo "=== Results ===" | tee -a "$EXECUTION_LOG"
                echo "Boot time: (early termination)" | tee -a "$EXECUTION_LOG"
                echo "Serial log: $SERIAL_LOG ($SERIAL_SIZE bytes)" | tee -a "$EXECUTION_LOG"
                echo "Status: FAIL" | tee -a "$EXECUTION_LOG"
                CONFIG_RESULTS+=("FAIL")
            fi
            
            CONFIG_SIZES+=("$SERIAL_SIZE")
            CONFIG_TIMES+=("$TEST_DURATION_MS")
        fi
        
        # Show progress bar
        PERCENT=$(( (TOTAL_CONFIGS * 100) / 15 ))
        echo "" | tee -a "$EXECUTION_LOG"
        echo "[Progress] Completed: $TOTAL_CONFIGS/15 ($PERCENT%)" | tee -a "$EXECUTION_LOG"
        
        # Clean up disk
        rm -f "$DISK_PATH" 2>/dev/null
    done
done

# Calculate total duration
END_TIME=$(date +'%Y-%m-%d %H:%M:%S %Z')
END_SECONDS=$(date +%s)
TOTAL_DURATION=$((END_SECONDS - START_SECONDS))
TOTAL_DURATION_MIN=$((TOTAL_DURATION / 60))
TOTAL_DURATION_SEC=$((TOTAL_DURATION % 60))

# Generate summary
echo "" | tee -a "$EXECUTION_LOG"
echo "==========================================" | tee -a "$EXECUTION_LOG"
echo "PHASE 5 SUMMARY" | tee -a "$EXECUTION_LOG"
echo "==========================================" | tee -a "$EXECUTION_LOG"
echo "Total configurations: $TOTAL_CONFIGS" | tee -a "$EXECUTION_LOG"
echo "Passed: $PASSED_CONFIGS" | tee -a "$EXECUTION_LOG"
echo "Failed: $FAILED_CONFIGS" | tee -a "$EXECUTION_LOG"
echo "Errors: $ERROR_CONFIGS" | tee -a "$EXECUTION_LOG"
SUCCESS_RATE=$(( (PASSED_CONFIGS * 100) / TOTAL_CONFIGS ))
echo "Success rate: $SUCCESS_RATE%" | tee -a "$EXECUTION_LOG"
echo "" | tee -a "$EXECUTION_LOG"
echo "Start time: $START_TIME" | tee -a "$EXECUTION_LOG"
echo "End time: $END_TIME" | tee -a "$EXECUTION_LOG"
echo "Total duration: ${TOTAL_DURATION_MIN}m ${TOTAL_DURATION_SEC}s" | tee -a "$EXECUTION_LOG"
echo "" | tee -a "$EXECUTION_LOG"

# List files generated
echo "Files generated:" | tee -a "$EXECUTION_LOG"
ls -lh phase5_serial_*.log 2>/dev/null | wc -l | tee -a "$EXECUTION_LOG"
echo "Results directory: $RESULTS_DIR" | tee -a "$EXECUTION_LOG"
echo "Execution log: $EXECUTION_LOG" | tee -a "$EXECUTION_LOG"

# Final status
if [ "$FAILED_CONFIGS" -eq 0 ] && [ "$ERROR_CONFIGS" -eq 0 ]; then
    echo "" | tee -a "$EXECUTION_LOG"
    echo "[+] SUCCESS: All Phase 5 configurations passed!" | tee -a "$EXECUTION_LOG"
    echo "[*] Extended single-CPU baseline VALIDATED across CPU models" | tee -a "$EXECUTION_LOG"
    EXIT_CODE=0
else
    echo "" | tee -a "$EXECUTION_LOG"
    echo "[!] FAILURE: Some configurations failed" | tee -a "$EXECUTION_LOG"
    EXIT_CODE=1
fi

exit $EXIT_CODE

