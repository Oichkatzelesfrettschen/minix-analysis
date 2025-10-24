#!/usr/bin/env bash
#
# Gemini Docker Wrapper Script
# Builds and runs Gemini visual regression tests in a Docker container
#
# Usage:
#   ./scripts/gemini-docker.sh [gemini-commands]
#   ./scripts/gemini-docker.sh test
#   ./scripts/gemini-docker.sh update
#   ./scripts/gemini-docker.sh gui
#
# Environment Variables:
#   GEMINI_IMAGE     - Override Docker image name (default: local/gemini-node18)
#   DOCKER_OPTS      - Additional Docker run options
#   FORCE_BUILD      - Force rebuild of Docker image (set to "1")
#

set -euo pipefail
IFS=$'\n\t'

# Configuration
IMAGE_NAME="${GEMINI_IMAGE:-local/gemini-node18}"
DOCKERFILE="${DOCKERFILE:-Dockerfile.gemini}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
  echo -e "${GREEN}[gemini]${NC} $*" >&2
}

log_warn() {
  echo -e "${YELLOW}[gemini]${NC} $*" >&2
}

log_error() {
  echo -e "${RED}[gemini]${NC} $*" >&2
}

# Check if Docker is available
check_docker() {
  if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    log_error "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
  fi

  if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    log_error "Please start Docker and try again"
    exit 1
  fi
}

# Build Docker image if needed
build_image() {
  local force_build="${FORCE_BUILD:-0}"

  if [[ "$force_build" == "1" ]] || ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    log_info "Building Docker image: $IMAGE_NAME"
    log_info "This may take a few minutes on first run..."

    if ! docker build -f "$DOCKERFILE" -t "$IMAGE_NAME" "$PROJECT_ROOT"; then
      log_error "Failed to build Docker image"
      exit 1
    fi

    log_info "Docker image built successfully"
  else
    log_info "Using existing Docker image: $IMAGE_NAME"
  fi
}

# Main execution
main() {
  # Check prerequisites
  check_docker

  # Build image if necessary
  build_image

  # Prepare Docker run options
  local docker_opts=(
    --rm
    -v "$PROJECT_ROOT:/app"
    -w /app
  )

  # Add custom Docker options if provided
  if [[ -n "${DOCKER_OPTS:-}" ]]; then
    read -ra custom_opts <<< "$DOCKER_OPTS"
    docker_opts+=("${custom_opts[@]}")
  fi

  # Handle special case for GUI mode
  if [[ "${1:-}" == "gui" ]]; then
    log_info "Starting Gemini GUI mode"
    docker_opts+=(
      -p 8000:8000
      -e "GUI_MODE=1"
    )
  fi

  log_info "Running Gemini with arguments: ${*:-<none>}"

  # Execute Gemini in Docker container
  exec docker run "${docker_opts[@]}" "$IMAGE_NAME" "$@"
}

# Handle script interruption
trap 'log_error "Script interrupted"; exit 130' INT TERM

# Run main function
main "$@"

