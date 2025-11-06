#!/bin/bash
# DevContainer post-create setup script

set -euo pipefail

echo "==================================================" 
echo "DevContainer Post-Create Setup"
echo "=================================================="
echo ""

# Display environment information
echo "User: $(whoami)"
echo "Home: ${HOME}"
echo "Workspace: ${PWD}"
echo ""

# Install pre-commit hooks if not already installed
if command -v pre-commit >/dev/null 2>&1; then
    echo "Installing pre-commit hooks..."
    pre-commit install || true
    echo "✓ Pre-commit hooks installed"
else
    echo "⚠ pre-commit not found, skipping hook installation"
fi

# Create placeholder script file if directory exists
mkdir -p scripts/netbsd
touch scripts/netbsd/.gitkeep

# Display quick start information
echo ""
echo "=================================================="
echo "NetBSD Environment Quick Start"
echo "=================================================="
echo ""
echo "1. Create NetBSD VM:"
echo "   /opt/netbsd-scripts/create-vm.sh 20G"
echo ""
echo "2. Start NetBSD VM:"
echo "   /opt/netbsd-scripts/start-netbsd.sh"
echo ""
echo "3. Connect via VNC:"
echo "   VNC client to localhost:5900"
echo ""
echo "4. Or use serial console:"
echo "   telnet localhost 9001"
echo ""
echo "Documentation: /opt/netbsd-scripts/README.md"
echo "=================================================="
echo ""

echo "✓ Setup complete!"
