#!/usr/bin/env bash
# mcp-docker-setup.sh
# One-click setup script for MCP servers with Docker Compose integration
# Configures Docker MCP, Docker Hub MCP, GitHub MCP, and SQLite MCP servers
#
# Usage: ./mcp-docker-setup.sh [--help] [--interactive] [--auto] [--skip-docker] [--github-token TOKEN]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_CONFIG="$SCRIPT_DIR/.mcp.json"
DOCKER_COMPOSE_FILE="$SCRIPT_DIR/docker-compose.enhanced.yml"
BACKUP_DIR="$SCRIPT_DIR/.mcp-backups"
LOG_FILE="$SCRIPT_DIR/mcp-setup.log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

info() { log "INFO" "$@"; }
warn() { log "WARN" "$@"; }
error() { log "ERROR" "$@"; echo -e "${RED}✗ ERROR: $@${NC}" >&2; }
success() { echo -e "${GREEN}✓ $@${NC}"; log "SUCCESS" "$@"; }
header() { echo -e "${BLUE}=== $@ ===${NC}"; }

# Helper functions
check_command() {
    if command -v "$1" &> /dev/null; then
        success "Found: $1"
        return 0
    else
        error "Missing: $1"
        return 1
    fi
}

check_docker() {
    if ! check_command docker; then
        error "Docker is required. Install with: sudo apt-get install docker.io"
        return 1
    fi
    
    if ! docker ps &>/dev/null; then
        error "Docker daemon is not running or you lack permissions"
        echo "Try: sudo usermod -aG docker \$USER && newgrp docker"
        return 1
    fi
    
    success "Docker is running and accessible"
    return 0
}

check_docker_compose() {
    if ! check_command docker-compose; then
        error "docker-compose is required"
        echo "Install with: sudo apt-get install docker-compose"
        return 1
    fi
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "docker-compose.enhanced.yml not found at $DOCKER_COMPOSE_FILE"
        return 1
    fi
    
    success "docker-compose and enhanced config found"
    return 0
}

validate_docker_compose() {
    header "Validating docker-compose configuration"
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" config > /dev/null 2>&1; then
        success "docker-compose.enhanced.yml is valid"
        return 0
    else
        error "docker-compose.enhanced.yml validation failed"
        docker-compose -f "$DOCKER_COMPOSE_FILE" config
        return 1
    fi
}

check_python() {
    if ! check_command python3; then
        error "Python 3 is required"
        return 1
    fi
    
    # Check for required modules
    python3 -c "import json, sys" 2>/dev/null && success "Python modules available" || {
        error "Missing required Python modules"
        return 1
    }
}

create_backup() {
    header "Creating backup of existing configuration"
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -f "$MCP_CONFIG" ]; then
        local backup_file="$BACKUP_DIR/.mcp.json.$(date +%s).bak"
        cp "$MCP_CONFIG" "$backup_file"
        success "Backed up existing config to $backup_file"
    else
        info "No existing .mcp.json to backup"
    fi
}

generate_mcp_config() {
    local github_token="${1:-}"
    
    header "Generating MCP configuration"
    
    # Prepare environment variables
    local github_token_env="GITHUB_TOKEN"
    [ -z "$github_token" ] && github_token="\${GITHUB_TOKEN}"
    
    # Create MCP config JSON
    cat > "$MCP_CONFIG" << 'EOF'
{
  "mcp_servers": {
    "docker": {
      "command": "npx",
      "args": ["-y", "docker-mcp@latest"],
      "env": {
        "DOCKER_HOST": "unix:///var/run/docker.sock"
      },
      "description": "Docker container management (list, control, inspect containers)",
      "tools": [
        "docker/list_containers",
        "docker/get_container_logs",
        "docker/run_command",
        "docker/inspect_container"
      ]
    },
    "dockerhub": {
      "command": "npx",
      "args": ["-y", "docker-hub-mcp@latest"],
      "env": {},
      "description": "Docker Hub image discovery and management",
      "tools": [
        "dockerhub/search_images",
        "dockerhub/get_image_info",
        "dockerhub/list_tags"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@github/cli-mcp-server@latest"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      },
      "description": "GitHub issue tracking, PR management, code repository access",
      "tools": [
        "github/list_issues",
        "github/create_issue",
        "github/list_pull_requests",
        "github/create_pull_request",
        "github/search_code"
      ]
    },
    "sqlite": {
      "command": "python3",
      "args": ["-m", "mcp_sqlite"],
      "env": {
        "DATABASE_PATH": "./measurements/boot-profiling.db"
      },
      "description": "Query boot profiling measurements and performance data",
      "tools": [
        "sqlite/query",
        "sqlite/list_tables",
        "sqlite/schema_info"
      ]
    }
  },
  "context_limits": {
    "docker_mcp_tokens": 1500,
    "dockerhub_mcp_tokens": 1000,
    "github_mcp_tokens": 2000,
    "sqlite_mcp_tokens": 500
  },
  "auto_disable_threshold": 170000,
  "notes": [
    "GitHub token is required for GitHub MCP. Set via: export GITHUB_TOKEN='ghp_...'",
    "Docker socket path may vary. Check 'docker context inspect' if issues occur",
    "SQLite MCP requires mcp-sqlite package: pip install mcp-sqlite",
    "All environment variables can be overridden in shell before running claude code"
  ]
}
EOF
    
    success "MCP configuration generated at $MCP_CONFIG"
    return 0
}

install_python_dependencies() {
    header "Installing Python MCP dependencies"
    
    # List of MCP packages
    local packages=("mcp-sqlite" "mcp-docker" "mcp-github")
    
    for package in "${packages[@]}"; do
        info "Installing $package..."
        if python3 -m pip install --quiet "$package" 2>/dev/null; then
            success "Installed: $package"
        else
            warn "Could not install $package (may not be required for all features)"
        fi
    done
}

setup_docker_mcp() {
    header "Setting up Docker MCP server"
    
    if ! check_docker; then
        error "Cannot proceed with Docker MCP setup without Docker"
        return 1
    fi
    
    # Verify docker socket accessibility
    if [ ! -S /var/run/docker.sock ]; then
        error "Docker socket not found at /var/run/docker.sock"
        warn "This may indicate Docker is not installed or not running"
        return 1
    fi
    
    success "Docker MCP can access Docker socket"
    
    # Test Docker connectivity
    if docker ps &>/dev/null; then
        local container_count=$(docker ps -q 2>/dev/null | wc -l)
        success "Docker accessible (found $container_count running containers)"
    else
        error "Cannot connect to Docker daemon"
        return 1
    fi
}

setup_github_mcp() {
    local github_token="${1:-}"
    
    header "Setting up GitHub MCP server"
    
    if [ -z "$github_token" ]; then
        # Check environment
        if [ -n "${GITHUB_TOKEN:-}" ]; then
            github_token="$GITHUB_TOKEN"
            info "Using GITHUB_TOKEN from environment"
        else
            warn "GitHub token not provided. Features requiring GitHub auth will not work."
            warn "Set via: export GITHUB_TOKEN='ghp_...'"
            return 0
        fi
    fi
    
    # Validate token format (basic check)
    if [[ $github_token =~ ^ghp_[A-Za-z0-9_]+$ ]] || [[ $github_token =~ ^github_pat_[A-Za-z0-9_]+$ ]]; then
        success "GitHub token format appears valid"
    else
        warn "GitHub token format may be invalid. Please verify token is correct."
    fi
    
    # Update config with token
    if [ -f "$MCP_CONFIG" ]; then
        python3 << PYTHON_EOF
import json
with open('$MCP_CONFIG', 'r') as f:
    config = json.load(f)
config['mcp_servers']['github']['env']['GITHUB_TOKEN'] = '$github_token'
with open('$MCP_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
print("Token configured in MCP config")
PYTHON_EOF
        success "GitHub token configured in MCP config"
    fi
}

setup_sqlite_mcp() {
    header "Setting up SQLite MCP server"
    
    # Create measurements directory if needed
    mkdir -p "$SCRIPT_DIR/measurements"
    
    # Check if database exists
    if [ -f "$SCRIPT_DIR/measurements/boot-profiling.db" ]; then
        local db_size=$(stat -f%z "$SCRIPT_DIR/measurements/boot-profiling.db" 2>/dev/null || \
                       stat --format=%s "$SCRIPT_DIR/measurements/boot-profiling.db" 2>/dev/null || \
                       echo "unknown")
        success "Found existing SQLite database (size: $db_size bytes)"
    else
        info "SQLite database will be created on first use"
    fi
    
    success "SQLite MCP configured to use $SCRIPT_DIR/measurements/boot-profiling.db"
}

start_mcp_servers() {
    header "Starting MCP servers via Docker Compose"
    
    info "Starting services with docker-compose..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" up -d 2>/dev/null; then
        success "Docker Compose services started"
        
        # Wait for services
        sleep 3
        
        # List running services
        info "Running services:"
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps || true
        
        return 0
    else
        error "Failed to start Docker Compose services"
        error "Try: docker-compose -f $DOCKER_COMPOSE_FILE up -d"
        return 1
    fi
}

verify_mcp_setup() {
    header "Verifying MCP setup"
    
    local checks_passed=0
    local checks_total=0
    
    # Check 1: Config file exists
    checks_total=$((checks_total + 1))
    if [ -f "$MCP_CONFIG" ]; then
        success "MCP config file exists"
        checks_passed=$((checks_passed + 1))
    else
        error "MCP config file missing"
    fi
    
    # Check 2: Config is valid JSON
    checks_total=$((checks_total + 1))
    if python3 -c "import json; json.load(open('$MCP_CONFIG'))" 2>/dev/null; then
        success "MCP config is valid JSON"
        checks_passed=$((checks_passed + 1))
    else
        error "MCP config is not valid JSON"
    fi
    
    # Check 3: All required servers configured
    checks_total=$((checks_total + 1))
    local required_servers=("docker" "dockerhub" "github" "sqlite")
    local all_found=true
    for server in "${required_servers[@]}"; do
        if grep -q "\"$server\"" "$MCP_CONFIG"; then
            info "  Found server config: $server"
        else
            warn "  Missing server config: $server"
            all_found=false
        fi
    done
    [ "$all_found" = true ] && checks_passed=$((checks_passed + 1))
    
    # Check 4: Docker Compose file valid
    checks_total=$((checks_total + 1))
    if docker-compose -f "$DOCKER_COMPOSE_FILE" config > /dev/null 2>&1; then
        success "Docker Compose config is valid"
        checks_passed=$((checks_passed + 1))
    else
        error "Docker Compose config is invalid"
    fi
    
    # Check 5: Services running
    checks_total=$((checks_total + 1))
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps 2>/dev/null | grep -q "Up"; then
        success "MCP services are running"
        checks_passed=$((checks_passed + 1))
    else
        warn "MCP services may not be running (this is OK if using --skip-docker)"
    fi
    
    echo ""
    echo "Verification: $checks_passed/$checks_total checks passed"
    
    if [ $checks_passed -ge 4 ]; then
        success "MCP setup verified!"
        return 0
    else
        error "MCP setup incomplete"
        return 1
    fi
}

print_next_steps() {
    header "Next Steps"
    
    cat << 'EOF'

1. START MCP SERVERS (if not already started)
   $ docker-compose -f docker-compose.enhanced.yml up -d

2. VERIFY SERVICES ARE RUNNING
   $ docker-compose -f docker-compose.enhanced.yml ps

3. USE IN CLAUDE CODE
   
   a) Start Claude Code:
      $ claude

   b) Check available MCP servers:
      /mcp list

   c) Try Docker MCP:
      "List my Docker containers"

   d) Try GitHub MCP:
      "Create a GitHub issue about MINIX boot error E003"

   e) Try SQLite MCP:
      "Query the boot profiling measurements database"

4. MANAGE ENVIRONMENT VARIABLES
   
   GitHub Token (required for GitHub MCP):
   $ export GITHUB_TOKEN='ghp_YourActualToken'

5. MONITOR SERVICES
   $ docker-compose -f docker-compose.enhanced.yml logs -f

6. STOP SERVICES
   $ docker-compose -f docker-compose.enhanced.yml down

7. TROUBLESHOOTING
   
   - If Docker not found: sudo apt-get install docker.io
   - If permission denied: sudo usermod -aG docker $USER && newgrp docker
   - If services won't start: docker-compose logs mcp-docker
   - If tokens expire: Update and re-export GITHUB_TOKEN

INTEGRATION WITH MINIX TESTING:

- Error triage uses MCP to query boot logs from Docker containers
- GitHub MCP creates issues for critical MINIX boot errors
- Docker MCP monitors container health during tests
- SQLite MCP tracks performance metrics over time

For more details: See MINIX-MCP-Integration.md

EOF
}

print_help() {
    cat << 'EOF'
mcp-docker-setup.sh - One-click MCP server setup

USAGE:
  ./mcp-docker-setup.sh [OPTIONS]

OPTIONS:
  --help              Show this help message
  --interactive       Interactive mode (prompts for configuration)
  --auto              Automatic mode (uses defaults, no prompts)
  --skip-docker       Skip Docker Compose startup
  --github-token TOKEN
                      Provide GitHub token (for non-interactive setup)
  --no-verify         Skip verification checks
  --uninstall         Remove MCP configuration and stop services

EXAMPLES:
  # Interactive setup with prompts
  $ ./mcp-docker-setup.sh --interactive

  # Automatic setup with defaults
  $ ./mcp-docker-setup.sh --auto

  # Setup with GitHub token
  $ ./mcp-docker-setup.sh --auto --github-token "ghp_YourToken"

  # Setup without starting Docker Compose
  $ ./mcp-docker-setup.sh --skip-docker

  # Full setup with GitHub token
  $ export GITHUB_TOKEN="ghp_YourToken"
  $ ./mcp-docker-setup.sh

REQUIREMENTS:
  - Docker (docker.io)
  - Docker Compose
  - Python 3.6+
  - Bash 4+

EOF
}

uninstall() {
    header "Uninstalling MCP configuration"
    
    if [ -f "$MCP_CONFIG" ]; then
        read -p "Remove MCP config? This cannot be undone. [y/N]: " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$MCP_CONFIG"
            success "Removed $MCP_CONFIG"
        fi
    fi
    
    # Stop services
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        read -p "Stop Docker Compose services? [y/N]: " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f "$DOCKER_COMPOSE_FILE" down
            success "Stopped services"
        fi
    fi
}

interactive_mode() {
    header "MCP Server Setup - Interactive Mode"
    
    echo ""
    echo "This script will configure MCP servers for Claude Code integration."
    echo "You will be prompted for optional configuration values."
    echo ""
    
    # Ask about GitHub token
    local use_github=false
    read -p "Do you want to use GitHub MCP? [y/N]: " -r
    [[ $REPLY =~ ^[Yy]$ ]] && use_github=true
    
    local github_token=""
    if [ "$use_github" = true ]; then
        read -p "Enter GitHub token (or press Enter to skip): " -r github_token
    fi
    
    # Ask about Docker
    local start_docker=true
    read -p "Start Docker Compose services now? [Y/n]: " -r
    [[ $REPLY =~ ^[Nn]$ ]] && start_docker=false
    
    echo ""
    info "Configuration selected:"
    echo "  GitHub MCP: $use_github"
    [ -n "$github_token" ] && echo "  GitHub token: ***provided***"
    echo "  Start Docker: $start_docker"
    echo ""
    
    return 0
}

main() {
    # Parse command line arguments
    local mode="auto"
    local skip_docker=false
    local github_token="${GITHUB_TOKEN:-}"
    local skip_verify=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                print_help
                exit 0
                ;;
            --interactive)
                mode="interactive"
                shift
                ;;
            --auto)
                mode="auto"
                shift
                ;;
            --skip-docker)
                skip_docker=true
                shift
                ;;
            --github-token)
                github_token="$2"
                shift 2
                ;;
            --no-verify)
                skip_verify=true
                shift
                ;;
            --uninstall)
                uninstall
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                print_help
                exit 1
                ;;
        esac
    done
    
    # Start setup
    header "MCP Server Setup"
    info "Mode: $mode"
    info "Log file: $LOG_FILE"
    
    echo ""
    
    # Check prerequisites
    header "Checking prerequisites"
    check_python || exit 1
    check_docker || exit 1
    check_docker_compose || exit 1
    
    echo ""
    
    # Interactive mode
    if [ "$mode" = "interactive" ]; then
        interactive_mode
    fi
    
    # Backup existing config
    create_backup
    
    echo ""
    
    # Generate configuration
    generate_mcp_config "$github_token" || exit 1
    
    echo ""
    
    # Install dependencies
    install_python_dependencies
    
    echo ""
    
    # Setup individual MCP servers
    setup_docker_mcp
    setup_github_mcp "$github_token"
    setup_sqlite_mcp
    
    echo ""
    
    # Validate Docker Compose
    validate_docker_compose || exit 1
    
    echo ""
    
    # Start services (unless skipped)
    if [ "$skip_docker" = false ]; then
        start_mcp_servers || exit 1
    else
        info "Skipping Docker Compose startup (--skip-docker)"
    fi
    
    echo ""
    
    # Verify setup
    if [ "$skip_verify" = false ]; then
        verify_mcp_setup
    else
        info "Skipping verification (--no-verify)"
    fi
    
    echo ""
    
    # Print next steps
    print_next_steps
    
    success "MCP setup completed!"
    info "Configuration saved to: $MCP_CONFIG"
    info "Logs saved to: $LOG_FILE"
}

# Run main function
main "$@"
