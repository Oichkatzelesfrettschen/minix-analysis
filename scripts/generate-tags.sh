#!/usr/bin/env bash
#
# Ctags Generation Script
# Generates and maintains tag files for code navigation
#
# Usage:
#   ./scripts/generate-tags.sh [options]
#
# Options:
#   --incremental, -i     Update tags incrementally (faster)
#   --verbose, -v         Show verbose output
#   --help, -h           Show this help message
#
# Environment Variables:
#   TAGS_FILE            Override tags file location (default: ./tags)
#   CTAGS_BIN           Override ctags binary (default: ctags)
#

set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly TAGS_FILE="${TAGS_FILE:-${PROJECT_ROOT}/tags}"
readonly CTAGS_BIN="${CTAGS_BIN:-ctags}"
readonly TEMP_TAGS="${TAGS_FILE}.tmp"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Options
VERBOSE=false
INCREMENTAL=false

# Logging functions
log_info() {
  echo -e "${GREEN}[ctags]${NC} $*" >&2
}

log_warn() {
  echo -e "${YELLOW}[ctags]${NC} $*" >&2
}

log_error() {
  echo -e "${RED}[ctags]${NC} $*" >&2
}

log_debug() {
  if [[ "$VERBOSE" == "true" ]]; then
    echo -e "${BLUE}[ctags]${NC} $*" >&2
  fi
}

# Show usage information
show_usage() {
  cat << EOF
Ctags Generation Script

Usage:
  $(basename "$0") [options]

Options:
  -i, --incremental    Update tags incrementally (faster for large projects)
  -v, --verbose        Show verbose output including file counts
  -h, --help          Show this help message

Examples:
  # Generate fresh tags file
  $(basename "$0")

  # Incremental update (faster)
  $(basename "$0") --incremental

  # With verbose output
  $(basename "$0") --verbose

Environment Variables:
  TAGS_FILE      Override tags file location (default: ./tags)
  CTAGS_BIN      Override ctags binary (default: ctags)

EOF
}

# Check if ctags is available
check_ctags() {
  if ! command -v "$CTAGS_BIN" &> /dev/null; then
    log_error "ctags is not installed or not in PATH"
    log_error "Please install Universal Ctags:"
    log_error "  Ubuntu/Debian: sudo apt-get install universal-ctags"
    log_error "  macOS: brew install universal-ctags"
    log_error "  From source: https://github.com/universal-ctags/ctags"
    exit 1
  fi

  # Verify it's Universal Ctags
  local version
  version=$("$CTAGS_BIN" --version | head -1)
  log_debug "Using: $version"

  if [[ ! "$version" =~ "Universal Ctags" ]]; then
    log_warn "Warning: Not using Universal Ctags"
    log_warn "Some features may not work correctly"
    log_warn "Consider installing Universal Ctags for best results"
  fi
}

# Get list of source files
get_source_files() {
  log_debug "Scanning for source files..."
  
  # Find all relevant source files, excluding common build artifacts
  find "$PROJECT_ROOT" -type f \( \
    -name "*.js" \
    -o -name "*.sh" \
    -o -name "*.md" \
    -o -name "*.json" \
    -o -name "*.yml" \
    -o -name "*.yaml" \
    -o -name "Dockerfile*" \
  \) \
    ! -path "*/node_modules/*" \
    ! -path "*/.git/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    ! -path "*/coverage/*" \
    ! -path "*/.nyc_output/*" \
    ! -path "*/gemini-report/*" \
    ! -path "*/.gemini-report/*" \
    ! -path "*/logs/*" \
    ! -name "package-lock.json" \
    ! -name "*.min.js" \
    ! -name "*.map"
}

# Generate tags file
generate_tags() {
  local start_time
  start_time=$(date +%s)
  
  log_info "Generating tags file..."
  log_debug "Target: $TAGS_FILE"
  
  # Build ctags command
  local ctags_opts=(
    --tag-relative=yes
    --fields=+ailmnS
    --extras=+q
    --languages=JavaScript,Sh,Markdown,JSON,Yaml
    -f "$TAGS_FILE"
  )
  
  if [[ "$VERBOSE" == "true" ]]; then
    ctags_opts+=(--verbose)
  fi
  
  # Change to project root for relative paths
  cd "$PROJECT_ROOT"
  
  # Generate tags
  if [[ "$INCREMENTAL" == "true" ]] && [[ -f "$TAGS_FILE" ]]; then
    log_info "Updating tags incrementally..."
    ctags_opts+=(--append)
  fi
  
  # Run ctags
  if "$CTAGS_BIN" "${ctags_opts[@]}" -R . 2>&1 | tee >(
    if [[ "$VERBOSE" == "true" ]]; then cat; else cat > /dev/null; fi
  ); then
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Get tag count
    local tag_count=0
    if [[ -f "$TAGS_FILE" ]]; then
      tag_count=$(grep -v "^!" "$TAGS_FILE" | wc -l)
    fi
    
    log_info "Tags generated successfully!"
    log_info "  Tags file: $TAGS_FILE"
    log_info "  Total tags: $tag_count"
    log_info "  Time: ${duration}s"
    
    return 0
  else
    log_error "Failed to generate tags"
    return 1
  fi
}

# Generate tags with file list (alternative method)
generate_tags_from_list() {
  local start_time
  start_time=$(date +%s)
  
  log_info "Generating tags from file list..."
  
  # Get source files
  local files
  mapfile -t files < <(get_source_files)
  
  if [[ "${#files[@]}" -eq 0 ]]; then
    log_warn "No source files found!"
    return 1
  fi
  
  log_debug "Found ${#files[@]} source files"
  
  # Build ctags command
  local ctags_opts=(
    --tag-relative=yes
    --fields=+ailmnS
    --extras=+q
    -f "$TAGS_FILE"
  )
  
  if [[ "$VERBOSE" == "true" ]]; then
    ctags_opts+=(--verbose)
  fi
  
  # Change to project root for relative paths
  cd "$PROJECT_ROOT"
  
  # Generate tags from file list
  if printf '%s\n' "${files[@]}" | "$CTAGS_BIN" "${ctags_opts[@]}" -L - 2>&1 | tee >(
    if [[ "$VERBOSE" == "true" ]]; then cat; else cat > /dev/null; fi
  ); then
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Get tag count
    local tag_count=0
    if [[ -f "$TAGS_FILE" ]]; then
      tag_count=$(grep -v "^!" "$TAGS_FILE" | wc -l)
    fi
    
    log_info "Tags generated successfully!"
    log_info "  Files processed: ${#files[@]}"
    log_info "  Total tags: $tag_count"
    log_info "  Time: ${duration}s"
    
    return 0
  else
    log_error "Failed to generate tags"
    return 1
  fi
}

# Verify tags file
verify_tags() {
  if [[ ! -f "$TAGS_FILE" ]]; then
    log_error "Tags file not found: $TAGS_FILE"
    return 1
  fi
  
  local tag_count
  tag_count=$(grep -v "^!" "$TAGS_FILE" | wc -l)
  
  if [[ "$tag_count" -eq 0 ]]; then
    log_warn "Tags file is empty!"
    return 1
  fi
  
  log_debug "Tags file verified: $tag_count tags"
  return 0
}

# Parse command line arguments
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -i|--incremental)
        INCREMENTAL=true
        shift
        ;;
      -v|--verbose)
        VERBOSE=true
        shift
        ;;
      -h|--help)
        show_usage
        exit 0
        ;;
      *)
        log_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
    esac
  done
}

# Main execution
main() {
  # Parse arguments
  parse_args "$@"
  
  # Check prerequisites
  check_ctags
  
  # Generate tags
  if generate_tags; then
    verify_tags
    exit 0
  else
    log_error "Tag generation failed"
    exit 1
  fi
}

# Handle script interruption
trap 'log_error "Script interrupted"; exit 130' INT TERM

# Run main function
main "$@"
