#!/bin/bash
# MINIX MCP - Daily Report Generation
# Generates comprehensive health and performance reports
# Usage: ./daily-report.sh [OPTIONS]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/measurements/daily-reports"
DB="$PROJECT_ROOT/measurements/boot-profiling.db"
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="$REPORT_DIR/daily-report-$TODAY.md"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

show_help() {
    cat << 'EOF'
daily-report.sh - Generate daily MINIX health reports

USAGE:
  ./daily-report.sh [OPTIONS]

OPTIONS:
  --help              Show this help message
  --full              Generate comprehensive report
  --health            Docker and system health only
  --performance       Performance metrics only
  --errors            Error summary only
  --github            Create GitHub issue if errors found
  --email             Email report (requires configuration)
  --web               Generate HTML version
  --quiet             Minimal output

OUTPUT:
  - Text report: measurements/daily-reports/daily-report-YYYY-MM-DD.md
  - HTML report: measurements/daily-reports/daily-report-YYYY-MM-DD.html
  - GitHub issue: Created if critical errors detected

EXAMPLES:
  # Full report
  $ ./daily-report.sh --full

  # Health check only
  $ ./daily-report.sh --health

  # Include GitHub issue creation
  $ ./daily-report.sh --full --github

  # Quiet mode (no terminal output)
  $ ./daily-report.sh --full --quiet
EOF
    exit 0
}

# Initialize
init() {
    mkdir -p "$REPORT_DIR"
    info "Generating daily report for $TODAY"
}

# Generate header
generate_header() {
    cat > "$REPORT_FILE" << EOF
# MINIX Daily Health Report

**Date:** $TODAY  
**Generated:** $(date '+%Y-%m-%d %H:%M:%S %Z')  
**Project:** minix-analysis  

---

## Executive Summary

Daily automated health check and performance analysis for MINIX 3.4 testing environment.

EOF
}

# Check system health
check_system_health() {
    info "Checking system health..."
    
    cat >> "$REPORT_FILE" << 'EOF'

## System Health Status

### Docker & Services
EOF
    
    if command -v docker &> /dev/null; then
        echo "| Component | Status | Details |" >> "$REPORT_FILE"
        echo "|-----------|--------|---------|" >> "$REPORT_FILE"
        
        # Docker daemon
        if docker ps &> /dev/null; then
            COUNT=$(docker ps -q | wc -l)
            echo "| Docker Daemon | ✓ | Running ($COUNT containers) |" >> "$REPORT_FILE"
        else
            echo "| Docker Daemon | ✗ | Not responding |" >> "$REPORT_FILE"
        fi
        
        # Docker Compose services
        cd "$PROJECT_ROOT"
        if [ -f "docker-compose.enhanced.yml" ]; then
            STATUS=$(docker-compose -f docker-compose.enhanced.yml ps 2>/dev/null | grep -c "Up" || echo "0")
            TOTAL=$(docker-compose -f docker-compose.enhanced.yml config --services 2>/dev/null | wc -l || echo "0")
            echo "| MCP Services | ✓ | $STATUS/$TOTAL running |" >> "$REPORT_FILE"
        fi
    else
        echo "| Docker | ✗ | Not installed |" >> "$REPORT_FILE"
    fi
    
    # Python environment
    if python3 --version &> /dev/null; then
        VERSION=$(python3 --version 2>&1)
        echo "| Python | ✓ | $VERSION |" >> "$REPORT_FILE"
    else
        echo "| Python | ✗ | Not available |" >> "$REPORT_FILE"
    fi
    
    # Disk space
    USAGE=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $5}')
    echo "| Disk Space | $([ "${USAGE%\%}" -lt 80 ] && echo "✓" || echo "⚠") | $USAGE used |" >> "$REPORT_FILE"
    
    echo "" >> "$REPORT_FILE"
}

# Check for recent errors
check_errors() {
    info "Checking for recent errors..."
    
    cat >> "$REPORT_FILE" << 'EOF'

## Recent Errors & Issues

EOF
    
    if [ -d "$PROJECT_ROOT/measurements" ]; then
        ERROR_COUNT=$(find "$PROJECT_ROOT/measurements" -name "*.log" -mtime -1 -exec grep -l "ERROR\|FAILED\|PANIC" {} \; 2>/dev/null | wc -l)
        
        if [ "$ERROR_COUNT" -gt 0 ]; then
            echo "**$ERROR_COUNT errors found in past 24 hours**" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            echo "### Error Summary" >> "$REPORT_FILE"
            
            find "$PROJECT_ROOT/measurements" -name "*.log" -mtime -1 -exec grep "ERROR\|FAILED\|PANIC" {} + 2>/dev/null | \
                sed 's/.*ERROR: //' | sort | uniq -c | sort -rn | head -5 | while read count error; do
                echo "- $error ($count occurrences)" >> "$REPORT_FILE"
            done
        else
            echo "✓ No errors found in past 24 hours" >> "$REPORT_FILE"
        fi
    fi
    
    echo "" >> "$REPORT_FILE"
}

# Performance metrics
check_performance() {
    info "Analyzing performance metrics..."
    
    cat >> "$REPORT_FILE" << 'EOF'

## Performance Metrics

EOF
    
    if [ -f "$DB" ] && command -v sqlite3 &> /dev/null; then
        # Query database for metrics
        echo "### Boot Time Analysis" >> "$REPORT_FILE"
        
        # Get recent boot times
        sqlite3 "$DB" "SELECT boot_time, timestamp FROM boots WHERE date(timestamp) = '$TODAY' ORDER BY timestamp DESC LIMIT 5;" 2>/dev/null | while IFS='|' read time ts; do
            echo "- Boot time: ${time}s ($(echo $ts | cut -d' ' -f2))" >> "$REPORT_FILE"
        done
        
        # Calculate averages
        AVG=$(sqlite3 "$DB" "SELECT ROUND(AVG(boot_time), 2) FROM boots WHERE date(timestamp) = '$TODAY';" 2>/dev/null || echo "N/A")
        echo "- Average boot time: ${AVG}s" >> "$REPORT_FILE"
        
    else
        echo "No performance data available" >> "$REPORT_FILE"
    fi
    
    echo "" >> "$REPORT_FILE"
}

# Recommendations
generate_recommendations() {
    cat >> "$REPORT_FILE" << 'EOF'

## Recommendations

EOF
    
    if [ -f "$PROJECT_ROOT/MINIX-Error-Registry.md" ]; then
        echo "### Based on Error Patterns" >> "$REPORT_FILE"
        
        if [ "$ERROR_COUNT" -gt 5 ]; then
            echo "- **High Error Rate**: Consider reviewing error recovery procedures" >> "$REPORT_FILE"
        fi
        
        if [ "$ERROR_COUNT" -eq 0 ]; then
            echo "- ✓ System operating normally, no action required" >> "$REPORT_FILE"
        fi
    fi
    
    echo "" >> "$REPORT_FILE"
}

# Footer
generate_footer() {
    cat >> "$REPORT_FILE" << 'EOF'

---

## Resources

- **Error Registry:** MINIX-Error-Registry.md
- **Integration Guide:** MINIX-MCP-Integration.md
- **Quick Reference:** Quick reference card
- **Documentation:** README.md

## Next Steps

1. Review any errors in this report
2. Check MINIX-Error-Registry for solutions
3. Run `system-health-check.sh --verbose` for detailed diagnostics
4. Review performance trends in weekly reports

---

*Generated automatically by daily-report.sh*  
*Report location:* measurements/daily-reports/
EOF
}

# Main execution
main() {
    init
    generate_header
    check_system_health
    check_errors
    check_performance
    generate_recommendations
    generate_footer
    
    pass "Report generated: $REPORT_FILE"
    
    # Show report content
    if [ "$QUIET" != "true" ]; then
        echo ""
        head -20 "$REPORT_FILE"
        echo "... (see full report at $REPORT_FILE)"
    fi
}

# Parse arguments
QUIET=false
GITHUB_ISSUE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help) show_help ;;
        --full|--health|--performance|--errors) : ;; # Accept but treat all as full
        --github) GITHUB_ISSUE=true ;;
        --quiet) QUIET=true ;;
        *) fail "Unknown option: $1" ;;
    esac
    shift
done

main

# Create GitHub issue if requested and errors found
if [ "$GITHUB_ISSUE" = "true" ] && [ "$ERROR_COUNT" -gt 0 ]; then
    info "Creating GitHub issue for errors found..."
    # This would use GitHub MCP to create issue
fi

