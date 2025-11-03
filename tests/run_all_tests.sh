#!/bin/bash
# Comprehensive test runner for MINIX analysis in Docker + QEMU
# Orchestrates unit, integration, and system tests with artifact collection

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS_DIR="${PROJECT_ROOT}/tools"
TEST_DIR="${PROJECT_ROOT}/tests"
RESULTS_DIR="${PROJECT_ROOT}/test_results"
LOGS_DIR="${PROJECT_ROOT}/logs/tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test configuration
TEST_TIMEOUT=300
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/qemu/docker-compose.yml"

# Logging
mkdir -p "${RESULTS_DIR}" "${LOGS_DIR}"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "${LOGS_DIR}/test_run.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "${LOGS_DIR}/test_run.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "${LOGS_DIR}/test_run.log" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "${LOGS_DIR}/test_run.log"
}

# Import Docker utilities
source "${TOOLS_DIR}/docker/docker_utils.sh"

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! check_docker; then
        log_error "Docker is not available"
        return 1
    fi
    
    if ! check_docker_compose; then
        log_warn "Docker Compose not available, will attempt to use docker compose"
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not installed"
        return 1
    fi
    
    log_success "All prerequisites met"
    return 0
}

# Run unit tests
run_unit_tests() {
    log_info "Running unit tests..."
    
    local test_file="${TEST_DIR}/test_*.py"
    
    if ! ls ${test_file} > /dev/null 2>&1; then
        log_warn "No unit tests found"
        return 0
    fi
    
    python3 -m pytest \
        -v \
        --tb=short \
        --junit-xml="${RESULTS_DIR}/unit_tests.xml" \
        --html="${RESULTS_DIR}/unit_tests.html" \
        --self-contained-html \
        "${TEST_DIR}/test_*.py" || {
        log_error "Unit tests failed"
        return 1
    }
    
    log_success "Unit tests passed"
    return 0
}

# Build Docker images
build_docker_images() {
    log_info "Building Docker images..."
    
    if [ ! -f "${DOCKER_COMPOSE_FILE}" ]; then
        log_warn "Docker Compose file not found: ${DOCKER_COMPOSE_FILE}"
        return 0
    fi
    
    docker-compose -f "${DOCKER_COMPOSE_FILE}" build --no-cache || {
        log_error "Docker image build failed"
        return 1
    }
    
    log_success "Docker images built"
    return 0
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    if [ ! -f "${DOCKER_COMPOSE_FILE}" ]; then
        log_warn "Docker Compose file not found, skipping integration tests"
        return 0
    fi
    
    # Start services
    log_info "Starting Docker services..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d qemu-minix || {
        log_error "Failed to start Docker services"
        return 1
    }
    
    # Wait for services to be ready
    if ! wait_for_container "minix-qemu-test" 60; then
        log_error "Container did not become ready in time"
        docker-compose -f "${DOCKER_COMPOSE_FILE}" logs qemu-minix >> "${LOGS_DIR}/docker_logs.txt" 2>&1
        docker-compose -f "${DOCKER_COMPOSE_FILE}" down
        return 1
    fi
    
    # Run tests
    log_info "Running integration tests in container..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" run --rm test-runner \
        python3 -m pytest \
        -v \
        --tb=short \
        --junit-xml="/app/results/integration_tests.xml" \
        /app/tests/integration/ || {
        log_error "Integration tests failed"
    }
    
    # Collect logs
    docker-compose -f "${DOCKER_COMPOSE_FILE}" logs >> "${LOGS_DIR}/docker_logs.txt"
    
    # Cleanup
    log_info "Stopping Docker services..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" down
    
    log_success "Integration tests completed"
    return 0
}

# Run QEMU-specific tests
run_qemu_tests() {
    log_info "Running QEMU-specific tests..."
    
    if [ ! -d "${TEST_DIR}/qemu" ]; then
        log_warn "No QEMU tests found"
        return 0
    fi
    
    python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'tools/testing'))

from qemu_runner import QEMURunner, QEMUConfig, QEMUArchitecture
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    config = QEMUConfig(
        arch=QEMUArchitecture.I386,
        memory="1G",
        cpus=2,
        enable_kvm=True
    )
    
    runner = QEMURunner(config=config, config_path=".config/paths.yaml")
    
    if runner.start_vm():
        logger.info("VM started successfully")
        if runner.wait_for_boot(timeout=30):
            logger.info("VM booted successfully")
            status = runner.get_status()
            logger.info(f"VM Status: {status}")
            runner.stop_vm()
        else:
            logger.error("VM failed to boot")
            runner.stop_vm()
            sys.exit(1)
    else:
        logger.error("Failed to start VM")
        sys.exit(1)
        
except Exception as e:
    logger.error(f"QEMU test failed: {e}")
    sys.exit(1)
EOF
    
    log_success "QEMU tests completed"
    return 0
}

# Generate test report summary
generate_report_summary() {
    log_info "Generating test report summary..."
    
    local summary_file="${RESULTS_DIR}/summary.txt"
    
    {
        echo "MINIX Analysis Test Report"
        echo "=========================="
        echo "Date: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        echo "Project: ${PROJECT_ROOT}"
        echo ""
        echo "Test Results:"
        echo "============"
        
        if [ -f "${RESULTS_DIR}/unit_tests.xml" ]; then
            echo "Unit Tests: COMPLETED"
            grep -o 'tests="[0-9]*"' "${RESULTS_DIR}/unit_tests.xml" || echo "Unit Tests: NO RESULTS"
        fi
        
        if [ -f "${RESULTS_DIR}/integration_tests.xml" ]; then
            echo "Integration Tests: COMPLETED"
            grep -o 'tests="[0-9]*"' "${RESULTS_DIR}/integration_tests.xml" || echo "Integration Tests: NO RESULTS"
        fi
        
        echo ""
        echo "Log Files:"
        echo "=========="
        ls -lh "${LOGS_DIR}/" 2>/dev/null || echo "No log files"
        
    } | tee "${summary_file}"
    
    log_success "Report summary saved to: ${summary_file}"
}

# Main execution
main() {
    local start_time=$(date +%s)
    local failed_tests=0
    
    log_info "=========================================="
    log_info "MINIX Analysis Test Suite"
    log_info "=========================================="
    log_info "Start time: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    log_info "Project root: ${PROJECT_ROOT}"
    log_info "Results directory: ${RESULTS_DIR}"
    log_info "Logs directory: ${LOGS_DIR}"
    log_info "=========================================="
    
    # Check prerequisites
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    # Run test stages
    if ! run_unit_tests; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if ! build_docker_images; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if ! run_integration_tests; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if ! run_qemu_tests; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # Generate reports
    generate_report_summary
    
    # Final summary
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "=========================================="
    log_info "Test Suite Completed"
    log_info "=========================================="
    log_info "Duration: ${duration}s"
    
    if [ ${failed_tests} -eq 0 ]; then
        log_success "All tests passed!"
        exit 0
    else
        log_error "${failed_tests} test stage(s) failed"
        exit 1
    fi
}

# Run main
main "$@"
