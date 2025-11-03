#!/bin/bash
# Generalized Docker utility functions for MINIX analysis project
# Provides common operations for Docker container and image management

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CONFIG_FILE="${PROJECT_ROOT}/.config/paths.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        return 1
    fi
    
    if ! docker ps &> /dev/null; then
        log_error "Docker daemon is not running"
        return 1
    fi
    
    log_success "Docker is available"
    return 0
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
            log_error "Docker Compose is not available"
            return 1
        fi
    fi
    
    log_success "Docker Compose is available"
    return 0
}

# Build Docker image
build_image() {
    local dockerfile="${1:?Dockerfile path required}"
    local image_name="${2:?Image name required}"
    local image_tag="${3:-latest}"
    
    if [ ! -f "${dockerfile}" ]; then
        log_error "Dockerfile not found: ${dockerfile}"
        return 1
    fi
    
    log_info "Building image: ${image_name}:${image_tag}"
    
    docker build \
        --file "${dockerfile}" \
        --tag "${image_name}:${image_tag}" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git -C "${PROJECT_ROOT}" rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        "${PROJECT_ROOT}"
    
    log_success "Image built: ${image_name}:${image_tag}"
}

# Start container from compose file
start_compose_service() {
    local compose_file="${1:?Compose file path required}"
    local service="${2:?Service name required}"
    
    if [ ! -f "${compose_file}" ]; then
        log_error "Compose file not found: ${compose_file}"
        return 1
    fi
    
    log_info "Starting service: ${service}"
    
    docker-compose -f "${compose_file}" up -d "${service}"
    
    log_success "Service started: ${service}"
}

# Stop container from compose file
stop_compose_service() {
    local compose_file="${1:?Compose file path required}"
    local service="${2:?Service name required}"
    
    log_info "Stopping service: ${service}"
    
    docker-compose -f "${compose_file}" down "${service}" 2>/dev/null || true
    
    log_success "Service stopped: ${service}"
}

# Execute command in running container
exec_in_container() {
    local container="${1:?Container name/ID required}"
    shift
    
    docker exec -it "${container}" "$@"
}

# Check if container is running
is_container_running() {
    local container="${1:?Container name/ID required}"
    
    docker ps --format '{{.Names}}' | grep -q "^${container}$"
}

# Get container IP address
get_container_ip() {
    local container="${1:?Container name/ID required}"
    
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "${container}"
}

# Stream logs from container
stream_container_logs() {
    local container="${1:?Container name/ID required}"
    local lines="${2:-100}"
    
    docker logs --follow --tail "${lines}" "${container}"
}

# Remove image
remove_image() {
    local image="${1:?Image name required}"
    
    log_info "Removing image: ${image}"
    
    docker rmi -f "${image}" || log_warn "Could not remove image: ${image}"
    
    log_success "Image removed: ${image}"
}

# Cleanup dangling images and containers
cleanup_docker() {
    log_info "Cleaning up Docker artifacts..."
    
    # Remove stopped containers
    docker container prune -f --filter "until=24h" || true
    
    # Remove dangling images
    docker image prune -f || true
    
    # Remove dangling volumes
    docker volume prune -f || true
    
    log_success "Docker cleanup completed"
}

# Display Docker system info
show_docker_info() {
    log_info "Docker System Information:"
    docker version
    echo ""
    log_info "Docker Disk Usage:"
    docker system df
}

# Health check for container
wait_for_container() {
    local container="${1:?Container name/ID required}"
    local max_attempts="${2:-30}"
    local attempt=0
    
    log_info "Waiting for container to be healthy: ${container}"
    
    while [ $attempt -lt "$max_attempts" ]; do
        if is_container_running "${container}"; then
            local health_status=$(docker inspect -f '{{.State.Health.Status}}' "${container}" 2>/dev/null || echo "none")
            
            if [ "${health_status}" = "healthy" ] || [ "${health_status}" = "none" ]; then
                log_success "Container is ready: ${container}"
                return 0
            fi
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    
    log_error "Container failed to become ready: ${container}"
    return 1
}

# Main - display usage if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    cat << EOF
Docker Utility Functions

Available commands:
  check_docker              - Verify Docker installation
  check_docker_compose      - Verify Docker Compose availability
  build_image DOCKERFILE NAME [TAG]
                            - Build Docker image
  start_compose_service FILE SERVICE
                            - Start service from compose file
  stop_compose_service FILE SERVICE
                            - Stop service from compose file
  exec_in_container CONTAINER CMD
                            - Execute command in container
  is_container_running CONTAINER
                            - Check if container is running
  get_container_ip CONTAINER
                            - Get container IP address
  stream_container_logs CONTAINER [LINES]
                            - Stream container logs
  remove_image IMAGE        - Remove Docker image
  cleanup_docker            - Clean up Docker artifacts
  show_docker_info          - Display Docker system info
  wait_for_container CONTAINER [ATTEMPTS]
                            - Wait for container to be ready

Usage:
  source docker_utils.sh
  check_docker
  build_image Dockerfile minix-qemu latest
EOF
fi
