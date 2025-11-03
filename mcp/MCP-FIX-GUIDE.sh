#!/bin/bash
# MCP Server Fix and Validation Guide
# Complete script to diagnose, fix, and validate MCP setup
# Run: bash MCP-FIX-GUIDE.sh

set -e

PROJECT_ROOT="/home/eirikr/Playground/minix-analysis"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}MINIX Analysis MCP Diagnostic and Fix${NC}"
echo -e "${BLUE}========================================${NC}"

# ==============================================================================
# SECTION 1: ENVIRONMENT SETUP
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 1] Environment Setup${NC}"
echo "Setting up required environment variables..."

# Check if variables are already set
if [ -z "$GITHUB_TOKEN" ]; then
  echo -e "${RED}✗ GITHUB_TOKEN not set${NC}"
  echo "Please create a GitHub Personal Access Token:"
  echo "  1. Go to https://github.com/settings/tokens"
  echo "  2. Generate new token with 'repo' and 'read:org' scopes"
  echo "  3. Copy token and set: export GITHUB_TOKEN='ghp_...'"
  echo ""
  read -p "Enter GitHub token (or press Enter to skip): " GITHUB_TOKEN
  if [ -n "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN
    echo -e "${GREEN}✓ GITHUB_TOKEN set${NC}"
  else
    echo -e "${RED}✗ GITHUB_TOKEN skipped - some tests will fail${NC}"
  fi
else
  echo -e "${GREEN}✓ GITHUB_TOKEN already set${NC}"
fi

if [ -z "$DOCKER_HUB_USERNAME" ]; then
  echo -e "${YELLOW}⚠ DOCKER_HUB_USERNAME not set (optional)${NC}"
  read -p "Enter Docker Hub username (or press Enter to skip): " DOCKER_HUB_USERNAME
  if [ -n "$DOCKER_HUB_USERNAME" ]; then
    export DOCKER_HUB_USERNAME
    echo -e "${GREEN}✓ DOCKER_HUB_USERNAME set${NC}"
  fi
else
  echo -e "${GREEN}✓ DOCKER_HUB_USERNAME already set${NC}"
fi

if [ -z "$DOCKER_HUB_TOKEN" ]; then
  echo -e "${YELLOW}⚠ DOCKER_HUB_TOKEN not set (optional)${NC}"
  read -p "Enter Docker Hub token (or press Enter to skip): " DOCKER_HUB_TOKEN
  if [ -n "$DOCKER_HUB_TOKEN" ]; then
    export DOCKER_HUB_TOKEN
    echo -e "${GREEN}✓ DOCKER_HUB_TOKEN set${NC}"
  fi
else
  echo -e "${GREEN}✓ DOCKER_HUB_TOKEN already set${NC}"
fi

# ==============================================================================
# SECTION 2: SYSTEM REQUIREMENTS CHECK
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 2] System Requirements Check${NC}"

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
  echo -e "${GREEN}✓ Docker installed${NC}"
  docker_version=$(docker --version)
  echo "  Version: $docker_version"
else
  echo -e "${RED}✗ Docker not found${NC}"
  echo "  Install from: https://docs.docker.com/get-docker/"
fi

# Check Docker daemon
echo -n "Checking Docker daemon... "
if docker ps > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Docker daemon running${NC}"
else
  echo -e "${RED}✗ Docker daemon not accessible${NC}"
  echo "  Try: sudo systemctl start docker"
fi

# Check docker-compose
echo -n "Checking docker-compose... "
if command -v docker-compose &> /dev/null; then
  echo -e "${GREEN}✓ docker-compose installed${NC}"
  compose_version=$(docker-compose --version)
  echo "  Version: $compose_version"
else
  echo -e "${RED}✗ docker-compose not found${NC}"
  echo "  Try: pip3 install docker-compose"
fi

# Check Node/npm
echo -n "Checking Node.js and npm... "
if command -v node &> /dev/null && command -v npm &> /dev/null; then
  node_version=$(node --version)
  npm_version=$(npm --version)
  echo -e "${GREEN}✓ Node.js and npm installed${NC}"
  echo "  Node: $node_version, npm: $npm_version"
else
  echo -e "${YELLOW}⚠ Node.js/npm not found (needed for MCP servers)${NC}"
  echo "  MCP servers require Node.js 16+ and npm"
fi

# Check Python
echo -n "Checking Python 3... "
if command -v python3 &> /dev/null; then
  python_version=$(python3 --version)
  echo -e "${GREEN}✓ Python 3 installed${NC}"
  echo "  Version: $python_version"
else
  echo -e "${RED}✗ Python 3 not found${NC}"
fi

# Check user in docker group
echo -n "Checking docker group membership... "
if groups $(whoami) | grep -q docker; then
  echo -e "${GREEN}✓ User in docker group${NC}"
else
  echo -e "${YELLOW}⚠ User not in docker group${NC}"
  echo "  Run: sudo usermod -aG docker \$(whoami)"
  echo "  Then: newgrp docker"
  echo "  Or logout and login for changes to take effect"
fi

# ==============================================================================
# SECTION 3: DIRECTORY STRUCTURE
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 3] Directory Structure${NC}"

required_dirs=(
  "measurements"
  "measurements/i386"
  "measurements/i386/syscalls"
  "measurements/i386/memory"
  "measurements/arm"
  "measurements/arm/syscalls"
  "measurements/arm/memory"
  "data"
  "logs"
  "mcp-servers"
  "mcp-servers/boot-profiler"
  "mcp-servers/syscall-tracer"
  "mcp-servers/memory-monitor"
)

echo "Creating required directories..."
for dir in "${required_dirs[@]}"; do
  if [ -d "$dir" ]; then
    echo -e "  ${GREEN}✓${NC} $dir"
  else
    mkdir -p "$dir"
    echo -e "  ${GREEN}✓ Created${NC} $dir"
  fi
done

# ==============================================================================
# SECTION 4: CONFIGURATION FILES
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 4] Configuration Files${NC}"

# Check .mcp.json
echo "Checking .mcp.json..."
if [ -f ".mcp.json" ]; then
  echo -e "  ${GREEN}✓${NC} .mcp.json exists"
  
  # Check for old package names
  if grep -q "docker-mcp@latest" .mcp.json; then
    echo -e "  ${RED}✗${NC} Found old package name: docker-mcp@latest"
    echo "    Replace with: @modelcontextprotocol/server-*"
  fi
  
  if grep -q "@github/cli-mcp-server" .mcp.json; then
    echo -e "  ${RED}✗${NC} Found old package name: @github/cli-mcp-server"
    echo "    Replace with: @modelcontextprotocol/server-github"
  fi
  
  # Validate JSON syntax
  if python3 -m json.tool .mcp.json > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} .mcp.json is valid JSON"
  else
    echo -e "  ${RED}✗${NC} .mcp.json has syntax errors"
  fi
else
  echo -e "  ${RED}✗${NC} .mcp.json not found"
fi

# Check docker-compose.enhanced.yml
echo "Checking docker-compose.enhanced.yml..."
if [ -f "docker-compose.enhanced.yml" ]; then
  echo -e "  ${GREEN}✓${NC} docker-compose.enhanced.yml exists"
  
  if docker-compose -f docker-compose.enhanced.yml config > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} docker-compose.enhanced.yml is valid"
  else
    echo -e "  ${RED}✗${NC} docker-compose.enhanced.yml has errors"
    docker-compose -f docker-compose.enhanced.yml config 2>&1 | head -10
  fi
else
  echo -e "  ${RED}✗${NC} docker-compose.enhanced.yml not found"
fi

# ==============================================================================
# SECTION 5: NPM PACKAGE AVAILABILITY
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 5] NPM Package Availability${NC}"

echo "Testing MCP server packages..."

echo -n "  Testing @modelcontextprotocol/server-github... "
if timeout 10 npx -y @modelcontextprotocol/server-github --help > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Available${NC}"
else
  echo -e "${RED}✗ Not available${NC}"
  echo "    Install with: npm install -g @modelcontextprotocol/server-github"
fi

echo -n "  Testing @modelcontextprotocol/server-sqlite... "
if timeout 10 npx -y @modelcontextprotocol/server-sqlite --help > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Available${NC}"
else
  echo -e "${RED}✗ Not available${NC}"
  echo "    Install with: npm install -g @modelcontextprotocol/server-sqlite"
fi

# ==============================================================================
# SECTION 6: DOCKER IMAGE AVAILABILITY
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 6] Docker Image Availability${NC}"

echo "Checking required Docker images..."

required_images=(
  "minix-rc6-i386"
  "python:3.11-slim"
  "node:20-alpine"
  "bash:5.2"
  "prom/prometheus:latest"
)

for image in "${required_images[@]}"; do
  # Skip checking for images that should be built locally
  if [[ "$image" == "minix-rc6-i386" ]]; then
    echo -n "  Checking $image (local build)... "
    if docker images | grep -q "^minix-rc6-i386"; then
      echo -e "${GREEN}✓ Found${NC}"
    else
      echo -e "${YELLOW}⚠ Not found (needs to be built from Dockerfile)${NC}"
    fi
  else
    echo -n "  Checking $image... "
    if docker pull --quiet "$image" 2>/dev/null; then
      echo -e "${GREEN}✓ Available${NC}"
    else
      echo -e "${RED}✗ Not available${NC}"
    fi
  fi
done

# ==============================================================================
# SECTION 7: PYTHON DEPENDENCIES
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 7] Python Dependencies${NC}"

required_packages=(
  "docker"
  "fastapi"
  "uvicorn"
  "pydantic"
  "pyyaml"
)

echo "Checking Python packages..."
for package in "${required_packages[@]}"; do
  echo -n "  Checking $package... "
  if python3 -c "import $package" 2>/dev/null; then
    version=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓${NC} (v$version)"
  else
    echo -e "${RED}✗ Not installed${NC}"
  fi
done

# Offer to install missing packages
if ! python3 -c "import docker" 2>/dev/null || ! python3 -c "import fastapi" 2>/dev/null; then
  echo ""
  read -p "Install missing packages? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing required packages..."
    pip3 install --upgrade docker fastapi uvicorn pydantic pyyaml
    echo -e "${GREEN}✓ Packages installed${NC}"
  fi
fi

# ==============================================================================
# SECTION 8: DOCKER SERVICES STATUS
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 8] Docker Services Status${NC}"

echo "Current Docker Compose services..."
if docker-compose -f docker-compose.enhanced.yml ps > /dev/null 2>&1; then
  docker-compose -f docker-compose.enhanced.yml ps
else
  echo -e "${YELLOW}⚠ No services currently running${NC}"
  echo ""
  read -p "Start Docker services now? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting services..."
    docker-compose -f docker-compose.enhanced.yml up -d
    echo "Waiting for services to be healthy..."
    sleep 10
    docker-compose -f docker-compose.enhanced.yml ps
  fi
fi

# ==============================================================================
# SECTION 9: MCP SERVER HEALTH CHECKS
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 9] MCP Server Health Checks${NC}"

echo "Testing custom MCP server endpoints..."

echo -n "  Boot Profiler (port 5010)... "
if timeout 5 curl -s http://localhost:5010/health > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Healthy${NC}"
  curl -s http://localhost:5010/health | python3 -m json.tool 2>/dev/null | head -5
else
  echo -e "${RED}✗ Not responding${NC}"
fi

echo -n "  Syscall Tracer (port 5011)... "
if timeout 5 curl -s http://localhost:5011/health > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Healthy${NC}"
  curl -s http://localhost:5011/health | python3 -m json.tool 2>/dev/null | head -5
else
  echo -e "${RED}✗ Not responding${NC}"
fi

echo -n "  Memory Monitor (port 5012)... "
if timeout 5 curl -s http://localhost:5012/health > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Healthy${NC}"
  curl -s http://localhost:5012/health | python3 -m json.tool 2>/dev/null | head -5
else
  echo -e "${RED}✗ Not responding${NC}"
fi

# ==============================================================================
# SECTION 10: RECOMMENDED FIXES
# ==============================================================================

echo -e "\n${YELLOW}[SECTION 10] Recommended Fixes${NC}"

issues_found=0

# Check for common issues
if grep -q "docker-mcp@latest\|@github/cli-mcp-server" .mcp.json 2>/dev/null; then
  echo -e "${RED}Issue #1: Old package names in .mcp.json${NC}"
  echo "  Fix: Replace with corrected .mcp.json"
  echo "  Command: cp MCP-CORRECTED-CONFIG.json .mcp.json"
  issues_found=$((issues_found + 1))
fi

if [ -z "$GITHUB_TOKEN" ]; then
  echo -e "${RED}Issue #2: GITHUB_TOKEN not set${NC}"
  echo "  Fix: Set environment variable before starting Claude Code"
  echo "  Command: export GITHUB_TOKEN='ghp_YourTokenHere'"
  issues_found=$((issues_found + 1))
fi

if ! docker ps > /dev/null 2>&1; then
  echo -e "${RED}Issue #3: Docker daemon not accessible${NC}"
  echo "  Fix: Start Docker daemon or add user to docker group"
  echo "  Command: sudo systemctl start docker"
  issues_found=$((issues_found + 1))
fi

if ! groups $(whoami) | grep -q docker; then
  echo -e "${RED}Issue #4: User not in docker group${NC}"
  echo "  Fix: Add user to docker group"
  echo "  Command: sudo usermod -aG docker \$(whoami) && newgrp docker"
  issues_found=$((issues_found + 1))
fi

if ! python3 -c "import docker" 2>/dev/null; then
  echo -e "${RED}Issue #5: Python docker package not installed${NC}"
  echo "  Fix: Install with pip"
  echo "  Command: pip3 install docker fastapi uvicorn"
  issues_found=$((issues_found + 1))
fi

# ==============================================================================
# SECTION 11: SUMMARY AND NEXT STEPS
# ==============================================================================

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}DIAGNOSTIC SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $issues_found -eq 0 ]; then
  echo -e "${GREEN}✓ No critical issues detected!${NC}"
  echo ""
  echo "Your MCP setup appears to be correctly configured."
  echo ""
  echo "Next steps:"
  echo "  1. Start Claude Code with environment variables set:"
  echo "     export GITHUB_TOKEN='ghp_...' && claude"
  echo ""
  echo "  2. Test MCP integration by asking Claude:"
  echo "     'List issues in my GitHub repositories'"
  echo ""
else
  echo -e "${RED}Found $issues_found issue(s) that need fixing${NC}"
  echo ""
  echo "Recommended fix order:"
  echo "  1. Update .mcp.json with corrected package names"
  echo "  2. Set required environment variables"
  echo "  3. Ensure Docker daemon is running and accessible"
  echo "  4. Install missing Python packages"
  echo ""
  echo "After fixing, re-run this script to verify:"
  echo "  bash MCP-FIX-GUIDE.sh"
fi

echo ""
echo "For detailed troubleshooting, see: MCP-TROUBLESHOOTING-AND-FIXES.md"
echo ""
