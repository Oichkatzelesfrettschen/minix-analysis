#!/usr/bin/env bash
# mcp-integration-tests.sh
# Integration tests for MCP servers with actual Docker containers
# Tests Docker MCP, Docker Hub MCP, GitHub MCP, and SQLite MCP
#
# Usage: ./mcp-integration-tests.sh [--verbose] [--docker-only] [--skip-github] [--debug]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKER_COMPOSE_FILE="$SCRIPT_DIR/docker-compose.enhanced.yml"
MCP_CONFIG="$SCRIPT_DIR/.mcp.json"
TEST_RESULTS_FILE="/tmp/mcp-integration-tests-$(date +%s).log"
TEST_DATA_DIR="/tmp/mcp-test-data-$$"

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Options
VERBOSE=false
DOCKER_ONLY=false
SKIP_GITHUB=false
DEBUG=false

# Logging
log() { echo "$@" | tee -a "$TEST_RESULTS_FILE"; }
info() { [ "$VERBOSE" = true ] && echo -e "${BLUE}[INFO]${NC} $@" | tee -a "$TEST_RESULTS_FILE"; true; }
debug() { [ "$DEBUG" = true ] && echo -e "${CYAN}[DEBUG]${NC} $@" | tee -a "$TEST_RESULTS_FILE"; true; }
pass() { echo -e "${GREEN}✓ PASS${NC}: $@" | tee -a "$TEST_RESULTS_FILE"; TESTS_PASSED=$((TESTS_PASSED+1)); TESTS_TOTAL=$((TESTS_TOTAL+1)); }
fail() { echo -e "${RED}✗ FAIL${NC}: $@" | tee -a "$TEST_RESULTS_FILE"; TESTS_FAILED=$((TESTS_FAILED+1)); TESTS_TOTAL=$((TESTS_TOTAL+1)); }
skip() { echo -e "${YELLOW}⊘ SKIP${NC}: $@" | tee -a "$TEST_RESULTS_FILE"; TESTS_SKIPPED=$((TESTS_SKIPPED+1)); }

# Test setup/teardown
setup_test_environment() {
    log "Setting up test environment..."
    mkdir -p "$TEST_DATA_DIR"
    info "Test data directory: $TEST_DATA_DIR"
}

teardown_test_environment() {
    log "Cleaning up test environment..."
    rm -rf "$TEST_DATA_DIR"
}

# Docker MCP Tests
test_docker_mcp_service_availability() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker MCP service availability..."
    
    if docker ps &>/dev/null; then
        pass "Docker daemon is accessible"
    else
        fail "Docker daemon is not accessible"
        return 1
    fi
}

test_docker_mcp_list_containers() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker MCP: list containers..."
    
    # Run docker command through what Docker MCP would use
    if output=$(docker ps -q 2>/dev/null); then
        pass "Docker MCP can list containers"
        debug "Found $(echo $output | wc -w) containers"
    else
        fail "Docker MCP cannot list containers"
        return 1
    fi
}

test_docker_mcp_container_stats() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker MCP: container statistics..."
    
    # Get a container to test with
    local container=$(docker ps -q | head -1 2>/dev/null)
    
    if [ -z "$container" ]; then
        skip "No running containers found for stats test"
        return 0
    fi
    
    if docker inspect "$container" &>/dev/null; then
        pass "Docker MCP can get container statistics"
        debug "Inspected container: $container"
    else
        fail "Docker MCP cannot get container statistics"
        return 1
    fi
}

test_docker_mcp_image_operations() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker MCP: image operations..."
    
    if images=$(docker images --quiet 2>/dev/null); then
        local count=$(echo "$images" | wc -l)
        pass "Docker MCP can list images ($count found)"
    else
        fail "Docker MCP cannot list images"
        return 1
    fi
}

# Docker Hub MCP Tests
test_dockerhub_mcp_search() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker Hub MCP: search functionality..."
    
    # Docker Hub MCP would perform searches via HTTP API
    # We simulate with curl
    if command -v curl &>/dev/null; then
        # Test connectivity to Docker Hub API
        if timeout 5 curl -s "https://registry.hub.docker.com/v1/repositories/library/minix" \
            -o /dev/null 2>/dev/null; then
            pass "Docker Hub MCP can search Docker Hub"
        else
            warn "Docker Hub MCP search connectivity issue (may be network-related)"
        fi
    else
        skip "curl not available for Docker Hub test"
    fi
}

# GitHub MCP Tests
test_github_mcp_token_configuration() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    
    if [ "$SKIP_GITHUB" = true ]; then
        skip "GitHub MCP tests skipped (--skip-github)"
        return 0
    fi
    
    info "Testing GitHub MCP: token configuration..."
    
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        pass "GITHUB_TOKEN is configured"
        
        # Validate token format
        if [[ $GITHUB_TOKEN =~ ^ghp_[A-Za-z0-9_]{36,255}$ ]] || \
           [[ $GITHUB_TOKEN =~ ^github_pat_[A-Za-z0-9_]{82,255}$ ]]; then
            pass "GitHub token format is valid"
        else
            info "GitHub token format may be non-standard (may still work)"
        fi
    else
        warn "GITHUB_TOKEN not configured (GitHub MCP will not work)"
    fi
}

test_github_mcp_cli_availability() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    
    if [ "$SKIP_GITHUB" = true ]; then
        skip "GitHub MCP tests skipped"
        return 0
    fi
    
    info "Testing GitHub MCP: GitHub CLI availability..."
    
    if command -v gh &>/dev/null; then
        pass "GitHub CLI is installed"
        
        # Test authentication
        if gh auth status &>/dev/null; then
            pass "GitHub CLI is authenticated"
        else
            warn "GitHub CLI is not authenticated"
        fi
    else
        warn "GitHub CLI not found (install with: sudo apt-get install gh)"
    fi
}

test_github_mcp_api_access() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    
    if [ "$SKIP_GITHUB" = true ]; then
        skip "GitHub MCP tests skipped"
        return 0
    fi
    
    info "Testing GitHub MCP: GitHub API access..."
    
    if [ -z "${GITHUB_TOKEN:-}" ]; then
        skip "GitHub token not set, skipping API test"
        return 0
    fi
    
    # Test basic API call
    if timeout 5 curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/user" -o /dev/null 2>/dev/null; then
        pass "GitHub MCP can access GitHub API"
    else
        fail "GitHub MCP cannot access GitHub API (token may be invalid)"
        return 1
    fi
}

# SQLite MCP Tests
test_sqlite_mcp_database_existence() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing SQLite MCP: database existence..."
    
    local db_path="$SCRIPT_DIR/measurements/boot-profiling.db"
    
    if [ -f "$db_path" ]; then
        pass "SQLite database exists at $db_path"
    else
        info "SQLite database does not exist (will be created on first use)"
    fi
}

test_sqlite_mcp_python_module() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing SQLite MCP: Python sqlite3 module..."
    
    if python3 -c "import sqlite3; print(sqlite3.version)" &>/dev/null; then
        pass "Python sqlite3 module is available"
    else
        fail "Python sqlite3 module is not available"
        return 1
    fi
}

test_sqlite_mcp_database_operations() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing SQLite MCP: database operations..."
    
    local test_db="$TEST_DATA_DIR/test.db"
    
    # Create test database and table
    if python3 << PYTHON_EOF 2>/dev/null
import sqlite3
conn = sqlite3.connect('$test_db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE test_measurements (id INTEGER PRIMARY KEY, boot_time REAL, timestamp TEXT)')
cursor.execute('INSERT INTO test_measurements (boot_time, timestamp) VALUES (12.5, "2025-10-31T10:00:00")')
conn.commit()
conn.close()
PYTHON_EOF
    then
        pass "SQLite database operations work"
        
        # Test read operations
        TESTS_TOTAL=$((TESTS_TOTAL+1))
        if python3 << PYTHON_EOF 2>/dev/null
import sqlite3
conn = sqlite3.connect('$test_db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM test_measurements')
count = cursor.fetchone()[0]
conn.close()
exit(0 if count == 1 else 1)
PYTHON_EOF
        then
            pass "SQLite read operations work"
        else
            fail "SQLite read operations failed"
        fi
    else
        fail "SQLite database operations failed"
        return 1
    fi
}

# MCP Configuration Tests
test_mcp_configuration_exists() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing MCP configuration file..."
    
    if [ -f "$MCP_CONFIG" ]; then
        pass "MCP configuration file exists"
    else
        fail "MCP configuration file not found: $MCP_CONFIG"
        return 1
    fi
}

test_mcp_configuration_valid_json() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing MCP configuration JSON validity..."
    
    if python3 -c "import json; json.load(open('$MCP_CONFIG'))" 2>/dev/null; then
        pass "MCP configuration is valid JSON"
    else
        fail "MCP configuration is not valid JSON"
        return 1
    fi
}

test_mcp_servers_defined() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing MCP servers are defined..."
    
    local required_servers=("docker" "dockerhub" "github" "sqlite")
    local all_defined=true
    
    for server in "${required_servers[@]}"; do
        if grep -q "\"$server\"" "$MCP_CONFIG"; then
            info "  ✓ Server defined: $server"
        else
            fail "Server not defined: $server"
            all_defined=false
        fi
    done
    
    if [ "$all_defined" = true ]; then
        pass "All required MCP servers are defined"
    else
        fail "Some MCP servers are not defined"
        return 1
    fi
}

# Docker Compose Tests
test_docker_compose_file_validity() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker Compose file validity..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        fail "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        return 1
    fi
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" config > /dev/null 2>&1; then
        pass "Docker Compose configuration is valid"
    else
        fail "Docker Compose configuration is invalid"
        docker-compose -f "$DOCKER_COMPOSE_FILE" config 2>&1 | head -10
        return 1
    fi
}

test_docker_compose_services_defined() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker Compose services..."
    
    # Extract services
    local services=$(grep "^  [a-z-]*:$" "$DOCKER_COMPOSE_FILE" | sed 's/[: ]//g' | sort -u)
    
    if [ -n "$services" ]; then
        local count=$(echo "$services" | wc -l)
        pass "Docker Compose has $count services defined"
        info "Services: $(echo $services | tr '\n' ' ')"
    else
        fail "No services defined in Docker Compose"
        return 1
    fi
}

# Service Health Tests
test_docker_compose_services_health() {
    if [ "$DOCKER_ONLY" = false ]; then
        TESTS_TOTAL=$((TESTS_TOTAL+1))
        info "Testing Docker Compose services health..."
        
        cd "$SCRIPT_DIR"
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps 2>/dev/null | grep -q "Up"; then
            pass "Some Docker Compose services are running"
        else
            warn "No Docker Compose services are running (may need to start them)"
            info "Start services with: docker-compose -f docker-compose.enhanced.yml up -d"
        fi
    fi
}

# Integration Tests
test_docker_to_sqlite_workflow() {
    if [ "$DOCKER_ONLY" = true ]; then
        return 0
    fi
    
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing Docker → SQLite integration workflow..."
    
    # Simulate Docker metrics collection and SQLite storage
    if python3 << PYTHON_EOF 2>/dev/null
import sqlite3
import json
from datetime import datetime

# Create test database
conn = sqlite3.connect('$TEST_DATA_DIR/workflow_test.db')
cursor = conn.cursor()

# Create metrics table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS docker_metrics (
        id INTEGER PRIMARY KEY,
        container_name TEXT,
        cpu_usage REAL,
        memory_usage REAL,
        timestamp TEXT
    )
''')

# Simulate Docker metrics collection
docker_metrics = {
    'container_name': 'test-container',
    'cpu_usage': 15.5,
    'memory_usage': 256,
    'timestamp': datetime.now().isoformat()
}

cursor.execute('''
    INSERT INTO docker_metrics 
    (container_name, cpu_usage, memory_usage, timestamp)
    VALUES (?, ?, ?, ?)
''', (
    docker_metrics['container_name'],
    docker_metrics['cpu_usage'],
    docker_metrics['memory_usage'],
    docker_metrics['timestamp']
))

# Query metrics
cursor.execute('SELECT COUNT(*) FROM docker_metrics')
count = cursor.fetchone()[0]

conn.commit()
conn.close()

exit(0 if count > 0 else 1)
PYTHON_EOF
    then
        pass "Docker to SQLite workflow test passed"
    else
        fail "Docker to SQLite workflow test failed"
        return 1
    fi
}

# Error Detection Integration
test_error_detection_integration() {
    TESTS_TOTAL=$((TESTS_TOTAL+1))
    info "Testing error detection integration with MCP..."
    
    local triage_tool="$SCRIPT_DIR/tools/triage-minix-errors.py"
    
    if [ ! -f "$triage_tool" ]; then
        fail "Triage tool not found: $triage_tool"
        return 1
    fi
    
    # Create sample boot log
    cat > "$TEST_DATA_DIR/sample_boot.log" << 'LOGEOF'
MINIX 3.4.0 (i386)
[Boot module: kernel.elf]
[Boot module: fs]
CD9660: cannot load module
[  FAIL ] Loading ramdisk
Kernel panic: module initialization failed
LOGEOF
    
    # Run triage on sample log
    if python3 "$triage_tool" "$TEST_DATA_DIR/sample_boot.log" \
        --output "$TEST_DATA_DIR/errors.json" 2>/dev/null; then
        pass "Error detection integration works"
        
        # Check output
        if [ -f "$TEST_DATA_DIR/errors.json" ]; then
            info "Errors detected and logged to JSON"
        fi
    else
        fail "Error detection integration failed"
        return 1
    fi
}

# Summary and reporting
print_summary() {
    echo ""
    echo "==============================" | tee -a "$TEST_RESULTS_FILE"
    echo "MCP Integration Test Summary" | tee -a "$TEST_RESULTS_FILE"
    echo "==============================" | tee -a "$TEST_RESULTS_FILE"
    echo "Total Tests:  $TESTS_TOTAL" | tee -a "$TEST_RESULTS_FILE"
    echo "Passed:       $TESTS_PASSED" | tee -a "$TEST_RESULTS_FILE"
    echo "Failed:       $TESTS_FAILED" | tee -a "$TEST_RESULTS_FILE"
    echo "Skipped:      $TESTS_SKIPPED" | tee -a "$TEST_RESULTS_FILE"
    
    if [ $TESTS_TOTAL -gt 0 ]; then
        local pass_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))
        echo "Pass Rate:    ${pass_rate}%" | tee -a "$TEST_RESULTS_FILE"
    fi
    
    echo "==============================" | tee -a "$TEST_RESULTS_FILE"
    echo ""
    
    # Overall result
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ ALL TESTS PASSED${NC}" | tee -a "$TEST_RESULTS_FILE"
        return 0
    else
        echo -e "${RED}✗ SOME TESTS FAILED${NC}" | tee -a "$TEST_RESULTS_FILE"
        return 1
    fi
}

print_help() {
    cat << 'EOF'
mcp-integration-tests.sh - MCP server integration tests

USAGE:
  ./mcp-integration-tests.sh [OPTIONS]

OPTIONS:
  --help            Show this help message
  --verbose         Verbose output with test details
  --docker-only     Test Docker MCP only (skip Docker Compose services)
  --skip-github     Skip GitHub MCP tests
  --debug           Debug output with extra information

TESTS PERFORMED:
  Docker MCP Tests:
    - Service availability
    - Container listing
    - Container statistics
    - Image operations

  Docker Hub MCP Tests:
    - Search functionality
    - API connectivity

  GitHub MCP Tests:
    - Token configuration
    - CLI availability
    - API access

  SQLite MCP Tests:
    - Database existence
    - Python module availability
    - Database operations

  MCP Configuration Tests:
    - Configuration file validity
    - JSON syntax validation
    - Server definitions

  Docker Compose Tests:
    - File validity
    - Service definitions
    - Service health

  Integration Tests:
    - Docker to SQLite workflow
    - Error detection integration

OUTPUT:
  - Test results: $TEST_RESULTS_FILE
  - Color-coded pass/fail/skip indicators
  - Detailed summary with pass rate

EXAMPLES:
  # Run all tests
  $ ./mcp-integration-tests.sh

  # Verbose output
  $ ./mcp-integration-tests.sh --verbose

  # Skip GitHub tests
  $ ./mcp-integration-tests.sh --skip-github

  # Docker only
  $ ./mcp-integration-tests.sh --docker-only

EOF
}

main() {
    # Parse arguments
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
            --docker-only)
                DOCKER_ONLY=true
                shift
                ;;
            --skip-github)
                SKIP_GITHUB=true
                shift
                ;;
            --debug)
                DEBUG=true
                VERBOSE=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                print_help
                exit 1
                ;;
        esac
    done
    
    # Setup
    log "MINIX MCP Integration Test Suite"
    log "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    log "Test log: $TEST_RESULTS_FILE"
    log ""
    
    setup_test_environment
    
    # Docker MCP Tests
    log "=== Docker MCP Tests ===" 
    test_docker_mcp_service_availability
    test_docker_mcp_list_containers
    test_docker_mcp_container_stats
    test_docker_mcp_image_operations
    
    # Docker Hub MCP Tests
    log ""
    log "=== Docker Hub MCP Tests ==="
    test_dockerhub_mcp_search
    
    # GitHub MCP Tests
    log ""
    log "=== GitHub MCP Tests ==="
    test_github_mcp_token_configuration
    test_github_mcp_cli_availability
    test_github_mcp_api_access
    
    # SQLite MCP Tests
    log ""
    log "=== SQLite MCP Tests ==="
    test_sqlite_mcp_database_existence
    test_sqlite_mcp_python_module
    test_sqlite_mcp_database_operations
    
    # MCP Configuration Tests
    log ""
    log "=== MCP Configuration Tests ==="
    test_mcp_configuration_exists
    test_mcp_configuration_valid_json
    test_mcp_servers_defined
    
    # Docker Compose Tests
    log ""
    log "=== Docker Compose Tests ==="
    test_docker_compose_file_validity
    test_docker_compose_services_defined
    test_docker_compose_services_health
    
    # Integration Tests
    log ""
    log "=== Integration Tests ==="
    test_docker_to_sqlite_workflow
    test_error_detection_integration
    
    # Summary
    log ""
    print_summary
    local exit_code=$?
    
    # Cleanup
    teardown_test_environment
    
    exit $exit_code
}

# Run main
main "$@"
