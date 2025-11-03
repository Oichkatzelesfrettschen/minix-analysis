#!/bin/bash

# Active monitoring of Phase 5 remaining tests
echo "=========================================="
echo "PHASE 5 ACTIVE COMPLETION MONITOR"
echo "=========================================="
echo "Start time: $(date)"
echo ""

EXECUTION_LOG="/tmp/phase5_full_execution.log"
RESULTS_DIR="/tmp/phase5-results"
TIMEOUT=$((12 * 60))  # 12-minute max (remaining tests should complete in 8-10 min)
START=$(date +%s)

echo "Monitoring K6 and Pentium tests (remaining 3+ configurations)..."
echo ""

while [ $(($(date +%s) - START)) -lt $TIMEOUT ]; do
  if [ -f "$EXECUTION_LOG" ]; then
    # Count completed tests
    COMPLETED=$(grep -c "Status: PASS\|Status: FAIL" "$EXECUTION_LOG" 2>/dev/null || echo 0)
    PASS=$(grep -c "Status: PASS" "$EXECUTION_LOG" 2>/dev/null || echo 0)
    FAIL=$(grep -c "Status: FAIL" "$EXECUTION_LOG" 2>/dev/null || echo 0)
    
    # Check for completion summary
    if grep -q "=== Phase 5 SUMMARY ===" "$EXECUTION_LOG" 2>/dev/null; then
      echo "[+] PHASE 5 EXECUTION COMPLETE!"
      echo "Final Status: $PASS PASS, $FAIL FAIL ($COMPLETED total)"
      break
    fi
    
    # Check for K6 test results in log
    if grep -q "k6_1vcpu_sample2" "$EXECUTION_LOG" 2>/dev/null; then
      echo "[$(date +'%H:%M:%S')] K6 sample2 test detected in progress"
    fi
    
    # Check for Pentium test results
    if grep -q "pentium_1vcpu_sample" "$EXECUTION_LOG" 2>/dev/null; then
      echo "[$(date +'%H:%M:%S')] Pentium tests detected in progress"
    fi
    
    # Display progress
    if [ $COMPLETED -gt 0 ]; then
      echo "[$(date +'%H:%M:%S')] Progress: $COMPLETED tests ($PASS PASS, $FAIL FAIL)"
    fi
  fi
  
  sleep 15
done

echo ""
echo "=========================================="
echo "PHASE 5 FINAL RESULTS"
echo "=========================================="
echo ""

# Count serial log files
if [ -d "$RESULTS_DIR" ]; then
  SERIAL_COUNT=$(find "$RESULTS_DIR" -name "phase5_serial_*.log" -type f 2>/dev/null | wc -l)
  echo "Serial log files created: $SERIAL_COUNT"
  echo ""
  
  echo "Results by CPU type:"
  for cpu_type in pentium3 pentium2 pentium 486 k6; do
    LOGS=$(find "$RESULTS_DIR" -name "phase5_serial_${cpu_type}_*.log" -type f 2>/dev/null | wc -l)
    if [ "$LOGS" -gt 0 ]; then
      PASS=0
      for log in "$RESULTS_DIR"/phase5_serial_${cpu_type}_*.log; do
        SIZE=$(wc -c < "$log" 2>/dev/null || echo 0)
        [ "$SIZE" -gt 5000 ] && PASS=$((PASS + 1))
      done
      FAIL=$((LOGS - PASS))
      printf "  %s: %d tests (%d PASS, %d FAIL)\n" "$cpu_type" "$LOGS" "$PASS" "$FAIL"
    fi
  done
fi

echo ""
echo "Completion time: $(date)"
