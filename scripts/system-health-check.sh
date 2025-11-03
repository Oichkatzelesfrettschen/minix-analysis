#!/usr/bin/env bash
# system-health-check.sh
# Comprehensive system health verification for MINIX analysis and MCP integration
# Checks all components: Docker, Python, MCP servers, tools, and configurations
#
# Usage: ./system-health-check.sh [--verbose] [--json] [--fix] [--monitor]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_FILE="/tmp/minix-health-check-$(date +%s).txt"
JSON_REPORT="/tmp/minix-health-check-$(date +%s).json"

# Counters
CHECKS_TOTAL=0
CHECKS_PASSED=0
CHECKS_WARNING=0
CHECKS_FAILED=0

# Status tracking
declare -A STATUS_MAP=()

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Output options
VERBOSE=false
JSON_OUTPUT=false
AUTO_FIX=false
MONITOR_MODE=false

# Logging
log() {
    echo "$@" | tee -a "$REPORT_FILE"
}

header() {
    echo -e "\n${MAGENTA}========== $@ ==========${NC}" | tee -a "$REPORT_FILE"
}

pass() {
    echo -e "${GREEN}✓ PASS${NC}: $@" | tee -a "$REPORT_FILE"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    STATUS_MAP["$(echo $@ | head -c 50)"]="PASS"
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $@" | tee -a "$REPORT_FILE"
    CHECKS_WARNING=$((CHECKS_WARNING + 1))
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    STATUS_MAP["$(echo $@ | head -c 50)"]="WARN"
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $@" | tee -a "$REPORT_FILE"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    STATUS_MAP["$(echo $@ | head -c 50)"]="FAIL"
}

info() {
    [ "$VERBOSE" = true ] && echo -e "${BLUE}[INFO]${NC}: $@" | tee -a "$REPORT_FILE"
    true
}

# Check functions
check_docker() {
    header "Docker & Container Runtime"
    
    # Check Docker installed
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if command -v docker &>/dev/null; then
        pass "Docker is installed"
        DOCKER_VERSION=$(docker --version 2>/dev/null || echo "unknown")
        info "Version: $DOCKER_VERSION"
    else
        fail "Docker is not installed"
        [ "$AUTO_FIX" = true ] && {
            info "Attempting to install Docker..."
            sudo apt-get update && sudo apt-get install -y docker.io || true
        }
        return 1
    fi
    
    # Check Docker daemon
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if sudo systemctl is-active --quiet docker; then
        pass "Docker daemon is running"
    else
        fail "Docker daemon is not running"
        [ "$AUTO_FIX" = true ] && {
            info "Attempting to start Docker..."
            sudo systemctl start docker || true
        }
        return 1
    fi
    
    # Check Docker access
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if docker ps &>/dev/null; then
        pass "User can access Docker"
    else
        warn "User cannot access Docker (may need group membership)"
        [ "$AUTO_FIX" = true ] && {
            info "Adding user to docker group..."
            sudo usermod -aG docker $USER || true
        }
    fi
    
    # Check Docker Compose
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if command -v docker-compose &>/dev/null; then
        pass "Docker Compose is installed"
        COMPOSE_VERSION=$(docker-compose --version 2>/dev/null || echo "unknown")
        info "Version: $COMPOSE_VERSION"
    else
        fail "Docker Compose is not installed"
        [ "$AUTO_FIX" = true ] && {
            info "Attempting to install Docker Compose..."
            sudo apt-get install -y docker-compose || true
        }
        return 1
    fi
}

check_python() {
    header "Python & Dependencies"
    
    # Check Python 3
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if command -v python3 &>/dev/null; then
        pass "Python 3 is installed"
        PYTHON_VERSION=$(python3 --version 2>&1)
        info "Version: $PYTHON_VERSION"
    else
        fail "Python 3 is not installed"
        return 1
    fi
    
    # Check Python modules
    local required_modules=("json" "re" "argparse" "pathlib" "sys")
    for module in "${required_modules[@]}"; do
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        if python3 -c "import $module" 2>/dev/null; then
            pass "Python module '$module' is available"
        else
            fail "Python module '$module' is missing"
        fi
    done
    
    # Check MCP packages (optional)
    local mcp_packages=("mcp-sqlite" "mcp-docker" "mcp-github")
    for package in "${mcp_packages[@]}"; do
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        if python3 -m pip show "$package" &>/dev/null; then
            pass "Python package '$package' is installed"
        else
            warn "Python package '$package' is not installed (optional)"
            [ "$AUTO_FIX" = true ] && {
                info "Attempting to install $package..."
                python3 -m pip install --quiet "$package" || true
            }
        fi
    done
}

check_tools() {
    header "MINIX Analysis Tools"
    
    local tools=(
        "tools/minix_source_analyzer.py"
        "tools/tikz_generator.py"
        "tools/triage-minix-errors.py"
        "scripts/minix-boot-diagnostics.sh"
        "scripts/minix-qemu-launcher.sh"
        "scripts/mcp-docker-setup.sh"
        "scripts/minix-error-recovery.sh"
        "scripts/system-health-check.sh"
        "tests/test-minix-mcp.sh"
    )
    
    for tool in "${tools[@]}"; do
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        local tool_path="$SCRIPT_DIR/$tool"
        if [ -f "$tool_path" ]; then
            if [ -x "$tool_path" ] || [[ "$tool" == *.py ]]; then
                pass "Tool exists: $tool"
            else
                warn "Tool exists but not executable: $tool"
                [ "$AUTO_FIX" = true ] && {
                    info "Making executable: $tool"
                    chmod +x "$tool_path" || true
                }
            fi
        else
            fail "Tool is missing: $tool"
        fi
    done
}

check_configurations() {
    header "Configuration Files"
    
    local configs=(
        ".mcp.json"
        "docker-compose.enhanced.yml"
        "CLAUDE.md"
        ".github/workflows/minix-ci.yml"
    )
    
    for config in "${configs[@]}"; do
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        local config_path="$SCRIPT_DIR/$config"
        if [ -f "$config_path" ]; then
            pass "Configuration found: $config"
            
            # Validate JSON files
            if [[ "$config" == *.json ]]; then
                if python3 -c "import json; json.load(open('$config_path'))" 2>/dev/null; then
                    info "  JSON syntax is valid"
                else
                    fail "  JSON syntax is invalid"
                fi
            fi
            
            # Validate YAML files
            if [[ "$config" == *.yml ]] || [[ "$config" == *.yaml ]]; then
                if docker-compose -f "$config_path" config > /dev/null 2>&1; then
                    info "  YAML syntax is valid"
                else
                    fail "  YAML syntax is invalid"
                fi
            fi
        else
            fail "Configuration missing: $config"
        fi
    done
}

check_docker_compose_services() {
    header "Docker Compose Services"
    
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    local compose_file="$SCRIPT_DIR/docker-compose.enhanced.yml"
    
    if ! [ -f "$compose_file" ]; then
        fail "docker-compose.enhanced.yml not found"
        return 1
    fi
    
    # Extract service names
    local services=$(grep "^  [a-z-]*:$" "$compose_file" | sed 's/[: ]//g' | sort -u)
    
    if [ -z "$services" ]; then
        warn "No services defined in docker-compose.enhanced.yml"
        return 1
    fi
    
    info "Configured services:"
    while IFS= read -r service; do
        [ -z "$service" ] && continue
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        
        # Check if service is running
        if docker-compose -f "$compose_file" ps "$service" 2>/dev/null | grep -q "Up"; then
            pass "Service is running: $service"
        elif docker-compose -f "$compose_file" ps "$service" 2>/dev/null | grep -q "Exit"; then
            warn "Service has exited: $service"
        else
            warn "Service is not running: $service"
        fi
    done <<< "$services"
}

check_mcp_configuration() {
    header "MCP Configuration"
    
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    local mcp_config="$SCRIPT_DIR/.mcp.json"
    
    if ! [ -f "$mcp_config" ]; then
        fail "MCP configuration not found: $mcp_config"
        return 1
    fi
    
    pass "MCP configuration file exists"
    
    # Check configured servers
    local servers=("docker" "dockerhub" "github" "sqlite")
    for server in "${servers[@]}"; do
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        if python3 -c "import json; d=json.load(open('$mcp_config')); exit(0 if '$server' in d.get('mcp_servers', {}) else 1)" 2>/dev/null; then
            pass "MCP server configured: $server"
        else
            warn "MCP server not configured: $server"
        fi
    done
}

check_databases() {
    header "Data Storage"
    
    # Check measurements directory
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    local measurements_dir="$SCRIPT_DIR/measurements"
    if [ -d "$measurements_dir" ]; then
        pass "Measurements directory exists"
        
        # Check database
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        local db_file="$measurements_dir/boot-profiling.db"
        if [ -f "$db_file" ]; then
            pass "SQLite database exists"
            local db_size=$(stat -c%s "$db_file" 2>/dev/null || stat -f%z "$db_file" 2>/dev/null || echo "unknown")
            info "  Size: $db_size bytes"
        else
            info "SQLite database will be created on first use"
        fi
    else
        warn "Measurements directory does not exist"
        [ "$AUTO_FIX" = true ] && {
            info "Creating measurements directory..."
            mkdir -p "$measurements_dir" || true
        }
    fi
    
    # Check subdirectories
    local subdirs=("ci-logs" "recovery-logs")
    for subdir in "${subdirs[@]}"; do
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        if [ -d "$measurements_dir/$subdir" ]; then
            pass "Subdirectory exists: $subdir"
        else
            info "Subdirectory does not exist: $subdir (will be created on use)"
        fi
    done
}

check_qemu() {
    header "QEMU & Emulation"
    
    # Check QEMU i386
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if command -v qemu-system-i386 &>/dev/null; then
        pass "QEMU i386 is installed"
        QEMU_VERSION=$(qemu-system-i386 --version 2>&1 | head -1)
        info "Version: $QEMU_VERSION"
    else
        warn "QEMU i386 is not installed (needed for MINIX boot)"
        [ "$AUTO_FIX" = true ] && {
            info "Attempting to install QEMU..."
            sudo apt-get install -y qemu-system-i386 qemu-utils || true
        }
    fi
    
    # Check KVM support
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if grep -q "vmx\|svm" /proc/cpuinfo 2>/dev/null; then
        pass "KVM virtualization support available"
    else
        warn "KVM virtualization not available (performance will be reduced)"
    fi
    
    # Check MINIX images
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if ls /tmp/minix*.iso 2>/dev/null | grep -q .; then
        pass "MINIX ISO images found"
        ls -lh /tmp/minix*.iso 2>/dev/null | sed 's/^/  /'
    else
        info "No MINIX ISO images found (can boot from URL)"
    fi
}

check_network() {
    header "Network & Connectivity"
    
    # Check internet connectivity
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if ping -c 1 8.8.8.8 &>/dev/null; then
        pass "Internet connectivity verified"
    else
        warn "No internet connectivity (some features may be unavailable)"
    fi
    
    # Check GitHub access
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if command -v git &>/dev/null; then
        pass "Git is installed"
        
        # Check GitHub token
        if [ -n "${GITHUB_TOKEN:-}" ]; then
            pass "GITHUB_TOKEN environment variable is set"
        else
            warn "GITHUB_TOKEN not set (GitHub MCP will not work)"
        fi
    else
        fail "Git is not installed"
    fi
    
    # Check Docker registry access
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if docker pull hello-world &>/dev/null; then
        pass "Docker registry is accessible"
    else
        warn "Cannot pull from Docker registry"
    fi
}

check_permissions() {
    header "File Permissions"
    
    # Check script executability
    local scripts=("scripts/minix-qemu-launcher.sh" "scripts/mcp-docker-setup.sh" 
                   "scripts/minix-error-recovery.sh" "scripts/system-health-check.sh")
    
    for script in "${scripts[@]}"; do
        CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
        local script_path="$SCRIPT_DIR/$script"
        if [ -x "$script_path" ]; then
            pass "Script is executable: $(basename $script)"
        else
            warn "Script is not executable: $(basename $script)"
            [ "$AUTO_FIX" = true ] && {
                info "Making executable: $(basename $script)"
                chmod +x "$script_path" || true
            }
        fi
    done
    
    # Check measurements directory permissions
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if [ -d "$SCRIPT_DIR/measurements" ] && [ -w "$SCRIPT_DIR/measurements" ]; then
        pass "Measurements directory is writable"
    else
        fail "Measurements directory is not writable"
    fi
}

generate_report() {
    header "Health Check Report"
    
    echo ""
    echo "=== SUMMARY ===" | tee -a "$REPORT_FILE"
    echo "Total Checks: $CHECKS_TOTAL" | tee -a "$REPORT_FILE"
    echo "Passed:       $CHECKS_PASSED" | tee -a "$REPORT_FILE"
    echo "Warnings:     $CHECKS_WARNING" | tee -a "$REPORT_FILE"
    echo "Failed:       $CHECKS_FAILED" | tee -a "$REPORT_FILE"
    
    # Calculate pass rate
    local pass_rate=0
    if [ $CHECKS_TOTAL -gt 0 ]; then
        pass_rate=$((CHECKS_PASSED * 100 / CHECKS_TOTAL))
    fi
    echo "Pass Rate:    ${pass_rate}%" | tee -a "$REPORT_FILE"
    
    # Overall status
    echo ""
    if [ $CHECKS_FAILED -eq 0 ]; then
        if [ $CHECKS_WARNING -eq 0 ]; then
            echo -e "${GREEN}STATUS: HEALTHY${NC}" | tee -a "$REPORT_FILE"
            echo "All systems operational and ready for use" | tee -a "$REPORT_FILE"
        else
            echo -e "${YELLOW}STATUS: WARNINGS${NC}" | tee -a "$REPORT_FILE"
            echo "System is functional but has warnings" | tee -a "$REPORT_FILE"
        fi
    else
        echo -e "${RED}STATUS: UNHEALTHY${NC}" | tee -a "$REPORT_FILE"
        echo "System has failures and needs attention" | tee -a "$REPORT_FILE"
    fi
    
    echo "" | tee -a "$REPORT_FILE"
    echo "Report saved to: $REPORT_FILE" | tee -a "$REPORT_FILE"
    
    # Generate JSON report if requested
    if [ "$JSON_OUTPUT" = true ]; then
        generate_json_report
    fi
}

generate_json_report() {
    python3 << PYTHON_EOF > "$JSON_REPORT"
import json
import socket
import datetime

report = {
    "timestamp": datetime.datetime.now().isoformat(),
    "hostname": "$HOSTNAME",
    "summary": {
        "total_checks": $CHECKS_TOTAL,
        "passed": $CHECKS_PASSED,
        "warnings": $CHECKS_WARNING,
        "failed": $CHECKS_FAILED,
        "pass_rate": $([ $CHECKS_TOTAL -gt 0 ] && echo "$((CHECKS_PASSED * 100 / CHECKS_TOTAL))" || echo "0")
    },
    "status": "$([ $CHECKS_FAILED -eq 0 ] && echo "healthy" || echo "unhealthy")"
}

with open("$JSON_REPORT", "w") as f:
    json.dump(report, f, indent=2)

print(f"JSON report saved to: $JSON_REPORT")
PYTHON_EOF
}

monitor_loop() {
    header "System Health Monitor (Continuous)"
    info "Press Ctrl+C to stop monitoring"
    
    while true; do
        clear
        echo -e "${CYAN}=== MINIX System Health Monitor ===${NC}"
        echo "Last update: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        
        # Quick status checks
        docker ps -q | wc -l | xargs -I{} echo -e "Docker containers running: {}"
        
        if command -v docker-compose &>/dev/null; then
            cd "$SCRIPT_DIR"
            docker-compose -f docker-compose.enhanced.yml ps 2>/dev/null | tail -n +2 | \
            awk '{print "  " $1 ": " $(NF)}'  || echo "No services running"
        fi
        
        # Memory usage
        echo ""
        echo "System Resources:"
        free -h | grep Mem | awk '{print "  RAM: " $3 " / " $2 " (" int($3/$2*100) "%)"}'
        
        # Disk usage
        df -h "$SCRIPT_DIR" | tail -1 | awk '{print "  Disk: " $3 " / " $2 " (" $5 ")"}'
        
        echo ""
        echo "Press Ctrl+C to exit. Refreshing in 10 seconds..."
        sleep 10
    done
}

print_help() {
    cat << 'EOF'
system-health-check.sh - MINIX system health verification

USAGE:
  ./system-health-check.sh [OPTIONS]

OPTIONS:
  --help              Show this help message
  --verbose           Verbose output with additional details
  --json              Generate JSON report
  --fix               Automatically fix detected issues (requires sudo)
  --monitor           Continuous monitoring mode
  --report-file FILE  Save report to custom file

EXAMPLES:
  # Basic health check
  $ ./system-health-check.sh

  # Verbose output
  $ ./system-health-check.sh --verbose

  # Auto-fix issues
  $ ./system-health-check.sh --fix

  # JSON report for automation
  $ ./system-health-check.sh --json

  # Continuous monitoring
  $ ./system-health-check.sh --monitor

CHECKS PERFORMED:
  ✓ Docker installation and daemon
  ✓ Python and required modules
  ✓ MINIX analysis tools
  ✓ Configuration files (JSON/YAML validation)
  ✓ Docker Compose services
  ✓ MCP server configuration
  ✓ SQLite database and storage
  ✓ QEMU emulator availability
  ✓ Network connectivity
  ✓ File permissions

REPORT OUTPUT:
  - Text report: /tmp/minix-health-check-*.txt
  - JSON report: /tmp/minix-health-check-*.json (with --json)

STATUS INDICATORS:
  ✓ PASS   - Check passed, system is healthy
  ⚠ WARN   - Warning, non-critical issue detected
  ✗ FAIL   - Failure, requires attention
  [INFO]   - Informational message (--verbose only)

EOF
}

main() {
    # Parse command line
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                print_help
                exit 0
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --json)
                JSON_OUTPUT=true
                shift
                ;;
            --fix)
                AUTO_FIX=true
                shift
                ;;
            --monitor)
                MONITOR_MODE=true
                shift
                ;;
            --report-file)
                REPORT_FILE="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                print_help
                exit 1
                ;;
        esac
    done
    
    # Start checks
    echo -e "${CYAN}MINIX System Health Check${NC}"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Host: $(hostname)"
    echo ""
    
    # Run all checks
    check_docker
    check_python
    check_tools
    check_configurations
    check_docker_compose_services
    check_mcp_configuration
    check_databases
    check_qemu
    check_network
    check_permissions
    
    # Generate report
    generate_report
    
    # Monitor mode
    if [ "$MONITOR_MODE" = true ]; then
        monitor_loop
    fi
    
    # Exit with appropriate status
    if [ $CHECKS_FAILED -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main
main "$@"
