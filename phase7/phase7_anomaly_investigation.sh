#!/bin/bash

================================================================================
PHASE 7: ANOMALY INVESTIGATION & ROOT CAUSE ANALYSIS
Extended CPU Sampling for Pentium II, Pentium P5, and 486 Control
================================================================================

set -e

# Configuration
ISO_PATH="/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso"
RESULTS_DIR="/home/eirikr/Playground/minix-analysis/phase7/results"
RESULTS_TABLE="/home/eirikr/Playground/minix-analysis/phase7/phase7_results_table.txt"
ANALYSIS_REPORT="/home/eirikr/Playground/minix-analysis/phase7/PHASE_7_ANOMALY_ANALYSIS.md"

# Test parameters
QEMU_TIMEOUT=120  # 120 seconds per test
QEMU_MEMORY=512   # 512 MB
SUCCESS_THRESHOLD=5000  # bytes

# CPU test configurations (extended sampling)
declare -a TEST_CONFIGS=(
  "pentium2_1vcpu_sample1"
  "pentium2_1vcpu_sample2"
  "pentium2_1vcpu_sample3"
  "pentium2_1vcpu_sample4"
  "pentium2_1vcpu_sample5"
  "pentium2_1vcpu_sample6"
  "pentium2_1vcpu_sample7"
  "pentium2_1vcpu_sample8"
  "pentium2_1vcpu_sample9"
  "pentium2_1vcpu_sample10"
  "pentium_1vcpu_sample1"
  "pentium_1vcpu_sample2"
  "pentium_1vcpu_sample3"
  "pentium_1vcpu_sample4"
  "pentium_1vcpu_sample5"
  "pentium_1vcpu_sample6"
  "pentium_1vcpu_sample7"
  "pentium_1vcpu_sample8"
  "pentium_1vcpu_sample9"
  "pentium_1vcpu_sample10"
  "486_1vcpu_control1"
  "486_1vcpu_control2"
  "486_1vcpu_control3"
  "486_1vcpu_control4"
  "486_1vcpu_control5"
)

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "================================================================================"
echo "PHASE 7: ANOMALY INVESTIGATION & ROOT CAUSE ANALYSIS"
echo "================================================================================"
echo "Start time: $(date)"
echo ""
echo "Configuration:"
echo "  ISO: $ISO_PATH"
echo "  Results directory: $RESULTS_DIR"
echo "  Timeout per test: ${QEMU_TIMEOUT}s"
echo "  Test configurations: ${#TEST_CONFIGS[@]}"
echo ""

# Verify ISO exists
if [ ! -f "$ISO_PATH" ]; then
    echo "[!] ERROR: MINIX ISO not found at $ISO_PATH"
    exit 1
fi

echo "[+] MINIX ISO verified"
echo ""

# Initialize results table
> "$RESULTS_TABLE"
echo "CONFIG | SAMPLE | BYTES | STATUS | DEVIATION | NOTES" > "$RESULTS_TABLE"
echo "--------|--------|-------|--------|-----------|-------" >> "$RESULTS_TABLE"

# Test counters
TOTAL_TESTS=0
PASS_TESTS=0
FAIL_TESTS=0

# Expected output size (from Phase 4b/5 results)
EXPECTED_SIZE=7762

# Run tests
echo "================================================================================"
echo "EXECUTING EXTENDED CPU SAMPLING"
echo "================================================================================"
echo ""

for config in "${TEST_CONFIGS[@]}"; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Parse config: cpu_type_vcpu_identifier
    IFS='_' read -r cpu_type vcpu identifier <<< "$config"

    # Create temporary disk
    TEMP_DISK="/tmp/phase7_${config}.qcow2"
    rm -f "$TEMP_DISK" 2>/dev/null || true
    qemu-img create -f qcow2 "$TEMP_DISK" 2G > /dev/null 2>&1

    # Determine CPU type for QEMU
    case "$cpu_type" in
        "pentium2")  QEMU_CPU="pentium2"; CPU_DISPLAY="Pentium II (P6)" ;;
        "pentium")   QEMU_CPU="pentium"; CPU_DISPLAY="Pentium (P5)" ;;
        "486")       QEMU_CPU="486"; CPU_DISPLAY="486" ;;
        *)           QEMU_CPU="486"; CPU_DISPLAY="Unknown" ;;
    esac

    echo -n "[$(printf '%2d' $TOTAL_TESTS)/25] Testing $CPU_DISPLAY ($identifier): "

    # Run QEMU with serial output to file
    SERIAL_LOG="$RESULTS_DIR/phase7_serial_${config}.log"

    timeout $QEMU_TIMEOUT qemu-system-i386 \
        -m ${QEMU_MEMORY}M \
        -cpu "$QEMU_CPU" \
        -smp 1 \
        -cdrom "$ISO_PATH" \
        -hda "$TEMP_DISK" \
        -boot d \
        -nographic \
        -serial file:"$SERIAL_LOG" \
        2>&1 > /dev/null || true

    # Analyze result
    BYTES=$(wc -c < "$SERIAL_LOG" 2>/dev/null || echo 0)

    if [ "$BYTES" -gt "$SUCCESS_THRESHOLD" ]; then
        STATUS="PASS"
        PASS_TESTS=$((PASS_TESTS + 1))
        DEVIATION="0%"
        NOTES="Normal boot sequence"
    else
        STATUS="FAIL"
        FAIL_TESTS=$((FAIL_TESTS + 1))
        DEVIATION=$(echo "scale=1; ($EXPECTED_SIZE - $BYTES) * 100 / $EXPECTED_SIZE" | bc 2>/dev/null || echo "N/A")
        NOTES="Early termination"
    fi

    echo "$STATUS ($BYTES bytes)"

    # Record result
    printf "%-8s | %6s | %5d | %6s | %8s | %s\n" "$cpu_type" "$identifier" "$BYTES" "$STATUS" "$DEVIATION" "$NOTES" >> "$RESULTS_TABLE"

    # Cleanup
    rm -f "$TEMP_DISK"
done

echo ""
echo "================================================================================"
echo "PHASE 7 EXECUTION COMPLETE"
echo "================================================================================"
echo ""
echo "Results Summary:"
echo "  Total tests: $TOTAL_TESTS"
echo "  PASS: $PASS_TESTS"
echo "  FAIL: $FAIL_TESTS"

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $PASS_TESTS * 100 / $TOTAL_TESTS" | bc 2>/dev/null || echo "0")
    echo "  Success rate: ${SUCCESS_RATE}%"
fi

echo ""
echo "Results table saved to: $RESULTS_TABLE"
echo ""

# Display results table
echo "================================================================================"
echo "DETAILED RESULTS"
echo "================================================================================"
echo ""
cat "$RESULTS_TABLE"
echo ""

# Analyze anomalies
echo "================================================================================"
echo "ANOMALY ANALYSIS"
echo "================================================================================"
echo ""

# Extract results by CPU type
declare -A cpu_results
for line in $(tail -n +3 "$RESULTS_TABLE"); do
    cpu=$(echo "$line" | awk '{print $1}')
    status=$(echo "$line" | awk '{print $4}')
    bytes=$(echo "$line" | awk '{print $3}')

    if [ -n "$cpu" ] && [ -n "$status" ]; then
        if [ -z "${cpu_results[$cpu]}" ]; then
            cpu_results[$cpu]="0:0:0"  # pass:fail:total
        fi

        IFS=':' read -r pass fail total <<< "${cpu_results[$cpu]}"
        total=$((total + 1))

        if [ "$status" = "PASS" ]; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
        fi

        cpu_results[$cpu]="$pass:$fail:$total"
    fi
done

# Display anomaly summary
echo "Results by CPU Type:"
echo ""

for cpu in pentium2 pentium 486; do
    if [ -n "${cpu_results[$cpu]}" ]; then
        IFS=':' read -r pass fail total <<< "${cpu_results[$cpu]}"

        case "$cpu" in
            "pentium2") LABEL="Pentium II (P6)" ;;
            "pentium")  LABEL="Pentium (P5)" ;;
            "486")      LABEL="486" ;;
            *)          LABEL="$cpu" ;;
        esac

        if [ $total -gt 0 ]; then
            success_pct=$(echo "scale=1; $pass * 100 / $total" | bc 2>/dev/null || echo "0")
            printf "  %s: %d/%d PASS (%.1f%%)\n" "$LABEL" "$pass" "$total" "$success_pct"

            # Analyze variance
            if [ "$fail" -gt 0 ]; then
                echo "    Note: $(echo "$fail FAILURES DETECTED - variance anomaly confirmed") "

                # Find failing samples
                for line in $(tail -n +3 "$RESULTS_TABLE" | grep "^$cpu "); do
                    status=$(echo "$line" | awk '{print $4}')
                    sample=$(echo "$line" | awk '{print $2}')
                    bytes=$(echo "$line" | awk '{print $3}')

                    if [ "$status" != "PASS" ]; then
                        deviation=$(echo "$line" | awk '{print $5}')
                        printf "      - Sample %s: %d bytes (%s deviation)\n" "$sample" "$bytes" "$deviation"
                    fi
                done
            else
                echo "    ✓ All samples PASS - consistent behavior"
            fi
        fi
    fi
done

echo ""
echo "================================================================================"
echo "GENERATING PHASE 7 ANALYSIS REPORT"
echo "================================================================================"
echo ""

# Create analysis report
cat > "$ANALYSIS_REPORT" << 'ANALYSIS_EOF'

================================================================================
PHASE 7: ANOMALY INVESTIGATION ANALYSIS REPORT
================================================================================

EXECUTIVE SUMMARY
================================================================================

This report documents the results of Phase 7 extended CPU sampling investigation,
which aims to determine the root causes of anomalies identified in Phase 5.

PHASE 5 ANOMALIES RECAP
================================================================================

Anomaly 1: Pentium II P6 Variance
  Sample 1: 850 bytes (FAIL) - 89% deviation from expected 7,762 bytes
  Sample 2: 7,762 bytes (PASS) - Normal
  Status: 1/2 PASS (50% pass rate)

Anomaly 2: Pentium P5 Variance
  Sample 1: 7,762 bytes (PASS) - Normal
  Sample 2: 828 bytes (FAIL) - 89% deviation from expected 7,762 bytes
  Status: 1/2 PASS (50% pass rate)

Anomaly 3: K6 (AMD) Incompatibility
  Both samples: 0 bytes - QEMU emulation failure (not MINIX failure)
  Status: 0/2 PASS - Excluded from analysis (TCG limitation)

PHASE 7 EXTENDED SAMPLING DESIGN
================================================================================

Objective: Increase statistical confidence in pass/fail rates for P5 and P6
Sample size: 25 additional tests
  - 10 × Pentium II P6 tests
  - 10 × Pentium P5 tests
  - 5 × 486 control baseline tests (for comparison)

Duration: ~50 minutes of QEMU execution (25 tests × 120 seconds each)

Success criteria:
  ✓ Establish statistical confidence intervals
  ✓ Determine if variance is reproducible or random
  ✓ Identify root cause patterns
  ✓ Provide recommendations for Phase 8+

PHASE 7 RESULTS ANALYSIS
================================================================================

[Results to be inserted from phase7_results_table.txt]

KEY FINDINGS
================================================================================

[Analysis of findings will be populated as tests complete]

STATISTICAL ANALYSIS
================================================================================

[Confidence intervals and statistical summaries will be calculated]

ROOT CAUSE ASSESSMENT
================================================================================

Based on Phase 7 data, the root causes are hypothesized as:

1. For Pentium II/P5 variance (if reproduced):
   - Timing variance in QEMU TCG emulation
   - Microarchitecture-specific initialization edge case
   - Serial output buffering timing issues

2. For differences between CPU types:
   - Early boot initialization differences
   - Microarchitecture-specific instruction timing
   - QEMU emulation accuracy varies by CPU type

RECOMMENDATIONS FOR PHASE 8+
================================================================================

Based on Phase 7 findings, Phase 8 extended matrix should:
  1. Include stabilized CPU types (486, P3 show 100% reliability)
  2. Continue testing P5/P6 if variance is low
  3. Exclude K6 (confirmed QEMU TCG incompatibility)
  4. Consider extended timeouts if timing is root cause
  5. Implement CPU-specific test adjustments if patterns emerge

NEXT STEPS
================================================================================

Phase 8: Proceed to 32-config extended matrix validation
  - 8 CPU types × 4 samples = 32 total configurations
  - Duration: ~65 minutes
  - Target: Comprehensive reliability assessment

Phase 9: Performance profiling and metrics collection
  - Collect CPU cycles, instructions, cache metrics
  - Duration: 60 minutes
  - Target: Performance baseline establishment

Phase 10: Documentation and publication
  - Technical whitepaper
  - Educational materials (Lions' Commentary style)
  - Quick start guide for developers

CONCLUSION
================================================================================

Phase 7 extended sampling provides the statistical evidence needed to
classify CPU microarchitectures and inform deployment decisions for
Phase 8 comprehensive validation.

Report Generated: [timestamp]
Total Tests: 25
Results File: [results_location]

================================================================================

ANALYSIS_EOF

echo "[+] Analysis report template created: $ANALYSIS_REPORT"
echo ""
echo "================================================================================"
echo "PHASE 7 WORKFLOW COMPLETE"
echo "================================================================================"
echo "Completion time: $(date)"
echo ""
echo "Deliverables:"
echo "  ✓ Extended CPU sampling (25 tests executed)"
echo "  ✓ Results table with anomaly tracking"
echo "  ✓ Phase 7 analysis report template"
echo ""
echo "Ready for Phase 8: Extended 32-Config Matrix Validation"
echo ""
