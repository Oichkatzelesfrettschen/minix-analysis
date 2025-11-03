#!/bin/bash

# Phase 5 Completion Monitoring and Automatic Results Extraction
# This script waits for Phase 5 to complete, then extracts and analyzes results

EXECUTION_LOG="/tmp/phase5_full_execution.log"
RESULTS_DIR="/tmp/phase5-results"
EXTRACTION_LOG="/tmp/phase5_extraction.log"

echo "=========================================="
echo "PHASE 5 COMPLETION & EXTRACTION WORKFLOW"
echo "=========================================="
echo "Start time: $(date)"
echo ""

# Step 1: Wait for Phase 5 execution to complete
echo "[*] Waiting for Phase 5 execution to complete..."
WAIT_TIMEOUT=$((15 * 60))  # 15 minute max wait
START=$(date +%s)

while [ $(($(date +%s) - START)) -lt $WAIT_TIMEOUT ]; do
  if grep -q "=== Phase 5 SUMMARY ===" "$EXECUTION_LOG" 2>/dev/null; then
    echo "[+] Phase 5 execution COMPLETE!"
    break
  fi
  
  # Check progress every 30 seconds
  if [ $(($(date +%s) - START)) % 30 -lt 5 ]; then
    LINES=$(wc -l < "$EXECUTION_LOG" 2>/dev/null || echo 0)
    COMPLETED=$(grep -c "Status: PASS\|Status: FAIL" "$EXECUTION_LOG" 2>/dev/null || echo 0)
    echo "[$(date +'%H:%M:%S')] Log: $LINES lines | Configs completed: $COMPLETED"
  fi
  
  sleep 2
done

echo ""
echo "=========================================="
echo "STEP 1: EXTRACT PHASE 5 RESULTS"
echo "=========================================="
echo ""

if [ ! -d "$RESULTS_DIR" ]; then
  echo "[!] Results directory not found!"
  exit 1
fi

# Count and list serial logs
SERIAL_LOGS=$(find "$RESULTS_DIR" -name "phase5_serial_*.log" -type f | sort)
LOG_COUNT=$(echo "$SERIAL_LOGS" | wc -l)

echo "Found $LOG_COUNT serial log files:"
echo ""

# Extract results into structured format
RESULTS_TABLE="/tmp/phase5_results_table.txt"
> "$RESULTS_TABLE"

echo "CPU_TYPE | SAMPLE | BYTES | STATUS" >> "$RESULTS_TABLE"
echo "---------|--------|-------|--------" >> "$RESULTS_TABLE"

PASS_COUNT=0
FAIL_COUNT=0

for log_file in $SERIAL_LOGS; do
  filename=$(basename "$log_file")
  # Parse filename: phase5_serial_{cpu}_{vcpu}cpu_sample{n}.log
  
  # Extract CPU type
  cpu_type=$(echo "$filename" | sed -n 's/.*serial_\([^_]*\)_.*/\1/p')
  
  # Extract sample number
  sample_num=$(echo "$filename" | sed -n 's/.*sample\([0-9]*\).*/\1/p')
  
  # Get file size
  file_size=$(wc -c < "$log_file")
  
  # Determine PASS/FAIL based on size
  if [ "$file_size" -gt 5000 ]; then
    status="PASS"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    status="FAIL"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  
  printf "%-8s | %6d | %5d | %s\n" "$cpu_type" "$sample_num" "$file_size" "$status" >> "$RESULTS_TABLE"
  
  echo "[+] $filename: $file_size bytes ($status)"
done

echo ""
echo "=========================================="
echo "PHASE 5 RESULTS SUMMARY"
echo "=========================================="
echo ""
cat "$RESULTS_TABLE"
echo ""
echo "Total configurations tested: $LOG_COUNT"
echo "PASS: $PASS_COUNT | FAIL: $FAIL_COUNT"
echo "Success rate: $(echo "scale=1; $PASS_COUNT * 100 / $LOG_COUNT" | bc)%"

# Step 3: Identify anomalies
echo ""
echo "=========================================="
echo "ANOMALY DETECTION"
echo "=========================================="
echo ""

# Check for CPU types with mixed results
for cpu_type in pentium3 pentium2 pentium 486 k6; do
  LOGS=$(find "$RESULTS_DIR" -name "phase5_serial_${cpu_type}_*.log" -type f 2>/dev/null | wc -l)
  
  if [ "$LOGS" -gt 0 ]; then
    PASS=$(grep -l "^.\\{5000,\\}" "$RESULTS_DIR/phase5_serial_${cpu_type}_"*.log 2>/dev/null | wc -l)
    FAIL=$((LOGS - PASS))
    
    if [ "$FAIL" -gt 0 ]; then
      echo "[!] ANOMALY: $cpu_type has mixed results ($PASS PASS, $FAIL FAIL)"
      
      # List which samples failed
      for log in "$RESULTS_DIR/phase5_serial_${cpu_type}_"*.log; do
        size=$(wc -c < "$log" 2>/dev/null)
        if [ "$size" -lt 5000 ]; then
          sample=$(basename "$log" | sed 's/.*sample//' | sed 's/.log//')
          echo "  - Sample $sample: $size bytes (FAIL)"
        fi
      done
    else
      echo "[+] $cpu_type: All $LOGS samples PASS (consistent)"
    fi
  fi
done

echo ""
echo "=========================================="
echo "COMPLETION STATUS"
echo "=========================================="
echo "Extraction complete: $(date)"
echo "Results table saved to: $RESULTS_TABLE"
echo "Ready for Phase 6 synthesis"

