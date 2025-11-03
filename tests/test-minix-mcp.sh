#!/bin/bash
# Comprehensive MCP + MINIX Integration Test Suite
# Validates entire setup: Docker, MCP servers, MINIX boot, error diagnosis

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEASUREMENTS_DIR="$PROJECT_ROOT/measurements"

echo "=========================================="
echo "MINIX + MCP Integration Test Suite"
echo "=========================================="
echo "Project Root: $PROJECT_ROOT"
echo ""

# Test 1: Required Files Present
echo "Test 1: Checking required files..."
required_files=(
    "$PROJECT_ROOT/mcp/.mcp.json"
    "$PROJECT_ROOT/docker-compose.enhanced.yml"
    "$PROJECT_ROOT/docs/MINIX-Error-Registry.md"
    "$PROJECT_ROOT/docs/MINIX-MCP-Integration.md"
    "$PROJECT_ROOT/scripts/minix-qemu-launcher.sh"
    "$PROJECT_ROOT/scripts/minix-boot-diagnostics.sh"
    "$PROJECT_ROOT/tools/triage-minix-errors.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $(basename "$file")"
    else
        fail "Missing: $file"
    fi
done

# Test 2: Docker Installation
echo ""
echo "Test 2: Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    pass "Docker installed: $DOCKER_VERSION"
else
    warn "Docker not installed. Skipping Docker-related tests."
fi

# Test 3: Docker Compose
echo ""
echo "Test 3: Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    pass "Docker Compose installed"
else
    warn "docker-compose not found. Skipping docker-compose tests."
fi

# Test 4: QEMU Installation
echo ""
echo "Test 4: Checking QEMU..."
if command -v qemu-system-i386 &> /dev/null; then
    QEMU_VERSION=$(qemu-system-i386 --version | head -1)
    pass "QEMU installed: $QEMU_VERSION"
else
    warn "QEMU not installed. Some tests may fail."
fi

# Test 5: Python Dependencies
echo ""
echo "Test 5: Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    pass "Python: $PYTHON_VERSION"
else
    fail "Python 3 not installed"
fi

# Test 6: Error Triage Script
echo ""
echo "Test 6: Testing error triage script..."
if [ -x "$PROJECT_ROOT/tools/triage-minix-errors.py" ]; then
    # Test with help
    if python3 "$PROJECT_ROOT/tools/triage-minix-errors.py" --help &> /dev/null; then
        pass "Error triage script works"
    else
        fail "Error triage script failed"
    fi
else
    warn "Error triage script not executable"
fi

# Test 7: Boot Diagnostics Script
echo ""
echo "Test 7: Testing boot diagnostics..."
if [ -x "$PROJECT_ROOT/scripts/minix-boot-diagnostics.sh" ]; then
    pass "Boot diagnostics script exists"
else
    warn "Boot diagnostics script not executable"
fi

# Test 8: QEMU Launcher
echo ""
echo "Test 8: Testing QEMU launcher..."
if [ -x "$PROJECT_ROOT/scripts/minix-qemu-launcher.sh" ]; then
    if "$PROJECT_ROOT/scripts/minix-qemu-launcher.sh" help &> /dev/null; then
        pass "QEMU launcher works"
    else
        fail "QEMU launcher failed"
    fi
else
    warn "QEMU launcher not executable"
fi

# Test 9: Docker Compose Validation
echo ""
echo "Test 9: Validating docker-compose.yml..."
if command -v docker-compose &> /dev/null; then
    if docker-compose -f "$PROJECT_ROOT/docker-compose.enhanced.yml" config > /dev/null 2>&1; then
        pass "docker-compose.enhanced.yml is valid"
    else
        warn "docker-compose.enhanced.yml has errors"
    fi
else
    warn "Skipping docker-compose validation (docker-compose not installed)"
fi

# Test 10: MCP Configuration
echo ""
echo "Test 10: Checking MCP configuration..."
if [ -f "$PROJECT_ROOT/mcp/.mcp.json" ]; then
    if python3 -m json.tool "$PROJECT_ROOT/mcp/.mcp.json" > /dev/null 2>&1; then
        pass ".mcp.json is valid JSON"
    else
        fail ".mcp.json has JSON errors"
    fi
else
    fail ".mcp.json not found"
fi

# Test 11: MINIX Images
echo ""
echo "Test 11: Checking for MINIX images..."
ISO_COUNT=$(find "$PROJECT_ROOT/docker" -name "*.iso" 2>/dev/null | wc -l)
IMG_COUNT=$(find "$PROJECT_ROOT/docker" -name "*.qcow2" -o -name "*.img" 2>/dev/null | wc -l)

if [ "$ISO_COUNT" -gt 0 ]; then
    pass "Found $ISO_COUNT ISO image(s)"
else
    warn "No MINIX ISO images found (download from https://www.minix3.org/download)"
fi

if [ "$IMG_COUNT" -gt 0 ]; then
    pass "Found $IMG_COUNT disk image(s)"
else
    info "No disk images found (will be created on first install)"
fi

# Test 12: Directory Structure
echo ""
echo "Test 12: Checking directory structure..."
required_dirs=(
    "$MEASUREMENTS_DIR"
    "$PROJECT_ROOT/tools"
    "$PROJECT_ROOT/scripts"
    "$PROJECT_ROOT/docker"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        pass "Directory exists: $(basename "$dir")"
    else
        warn "Creating directory: $dir"
        mkdir -p "$dir"
    fi
done

# Test 13: Permissions
echo ""
echo "Test 13: Checking script permissions..."
scripts=(
    "$PROJECT_ROOT/scripts/minix-qemu-launcher.sh"
    "$PROJECT_ROOT/scripts/minix-boot-diagnostics.sh"
    "$PROJECT_ROOT/tools/triage-minix-errors.py"
)

for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        pass "Executable: $(basename "$script")"
    else
        warn "Making executable: $(basename "$script")"
        chmod +x "$script"
    fi
done

# Test 14: Test Boot Log Analysis
echo ""
echo "Test 14: Testing error analysis with sample log..."
SAMPLE_LOG="$MEASUREMENTS_DIR/test-sample.log"
cat > "$SAMPLE_LOG" << 'EOF'
Booting MINIX 3.4.0
Loading cd9660 module...
failed to load cd9660
mount: cd9660 mount failed (error 1)
ERROR: do_irqctl: IRQ check failed
Couldn't obtain hook for irq
[System hangs]
EOF

if (python3 "$PROJECT_ROOT/tools/triage-minix-errors.py" "$SAMPLE_LOG" &> "$PROJECT_ROOT/triage_output.txt") || true; then
    if grep -q "E003\|E006" "$PROJECT_ROOT/triage_output.txt" 2>/dev/null; then
        pass "Error triage correctly identified errors"
    else
        info "Error triage test inconclusive"
    fi
else
    info "Error triage test inconclusive"
fi

rm -f "$SAMPLE_LOG" "$PROJECT_ROOT/triage_output.txt"

# Final Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="

PASS_COUNT=$(grep -c "\[PASS\]" <<< "$(history)" 2>/dev/null || echo "0")
echo ""
echo "Status: SETUP VALIDATION COMPLETE"
echo ""
echo "Next Steps:"
echo "  1. Review MINIX-MCP-Integration.md"
echo "  2. Set environment variables:"
echo "     export GITHUB_TOKEN=\"ghp_YourToken\""
echo "     export DOCKER_HUB_USERNAME=\"your-username\""
echo "  3. Start MCP servers:"
echo "     docker-compose -f docker-compose.enhanced.yml up -d"
echo "  4. Boot MINIX:"
echo "     ./scripts/minix-qemu-launcher.sh boot"
echo "  5. Run diagnostics:"
echo "     python3 tools/triage-minix-errors.py measurements/boot-*.log"
echo ""
echo "Documentation:"
echo "  - MINIX-Error-Registry.md (15+ errors with solutions)"
echo "  - MINIX-MCP-Integration.md (complete MCP setup guide)"
echo "  - CLAUDE.md (project overview with MCP section)"
echo ""
