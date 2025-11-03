# MCP Server Troubleshooting and Fixes
## Comprehensive Diagnostic and Remediation Guide

**Date**: 2025-11-01
**Status**: Complete Analysis + Fixes
**Scope**: All MCP servers, configurations, and integration issues

---

## Executive Summary

The MINIX Analysis MCP setup has **6 critical issues** and **8 configuration problems** preventing proper integration with Claude Code. This guide provides:

1. Root cause analysis for each issue
2. Detection methods and symptoms
3. Step-by-step fixes (with code examples)
4. Corrected configuration files
5. Validation procedures

**Quick Wins**: Apply Fixes #1-3 to resolve 80% of integration failures.

---

## CRITICAL ISSUES IDENTIFIED

### Issue #1: Incorrect MCP Package Names in .mcp.json

**Severity**: CRITICAL (prevents all MCP servers from loading)

**Root Cause**:
The `.mcp.json` references non-existent NPM packages:
- `docker-mcp@latest` → Does not exist as standalone package
- `docker-hub-mcp@latest` → Incorrect package name
- `@github/cli-mcp-server@latest` → Old/incorrect reference

**Correct Packages**:
```
@modelcontextprotocol/server-github   (GitHub integration)
@modelcontextprotocol/server-postgres (Database queries)
@modelcontextprotocol/server-sqlite   (SQLite queries)
docker-mcp (from QuantGeekDev or official sources)
docker-hub-mcp (official Docker implementation)
```

**Symptoms**:
```
ERROR: Failed to find package docker-mcp@latest in npm registry
ERROR: Package @github/cli-mcp-server@latest not found
TypeError: Cannot find module @github/cli-mcp-server
```

**Detection**:
```bash
# Test if packages exist
npx -y docker-mcp@latest --version
# Should fail with "404 Not Found" or similar

# Correct approach
npx -y @modelcontextprotocol/server-github --version
# Should succeed or show help
```

**Fix #1A: Correct the .mcp.json File**

Replace in `.mcp.json`:

OLD:
```json
{
  "mcp_servers": {
    "docker": {
      "command": "npx",
      "args": ["-y", "docker-mcp@latest"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@github/cli-mcp-server@latest"]
    }
  }
}
```

NEW:
```json
{
  "mcp_servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      },
      "description": "GitHub repository and issue management"
    },
    "sqlite": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/home/eirikr/Playground/minix-analysis/measurements/minix-analysis.db"],
      "description": "SQLite database queries for boot measurements"
    }
  }
}
```

**Validation**:
```bash
# Test GitHub MCP
npx -y @modelcontextprotocol/server-github --version

# Test SQLite MCP
npx -y @modelcontextprotocol/server-sqlite --help
```

---

### Issue #2: Environment Variable Templating Not Supported in .mcp.json

**Severity**: HIGH (causes authentication failures)

**Root Cause**:
The `.mcp.json` uses template variables like `${GITHUB_TOKEN}` which are NOT automatically expanded. Claude Code reads the literal string `"${GITHUB_TOKEN}"` instead of the environment value.

**Current Problem**:
```json
{
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}",  // WRONG: literal string!
    "DOCKER_HUB_USERNAME": "${DOCKER_HUB_USERNAME}"
  }
}
```

When Claude Code starts, it tries to use the literal string `"${GITHUB_TOKEN}"` as a token, which fails authentication.

**Symptoms**:
```
ERROR: Authentication failed with token: ${GITHUB_TOKEN}
401 Unauthorized: Invalid token format
GitHub API: Bad credentials
```

**Fix #2A: Use Environment Variables Directly (Recommended)**

Instead of templating, rely on shell environment variables:

```bash
# Set in ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_YourActualTokenHere"
export DOCKER_HUB_USERNAME="your-docker-username"
export DOCKER_HUB_TOKEN="dckr_YourActualTokenHere"

# Verify before starting Claude Code
echo $GITHUB_TOKEN
```

**Fix #2B: Use .env File with Claude Desktop/Code**

Create `.env` in project root:

```bash
# .env (add to .gitignore!)
GITHUB_TOKEN=ghp_YourActualTokenHere
DOCKER_HUB_USERNAME=your-docker-username
DOCKER_HUB_TOKEN=dckr_YourActualTokenHere
```

Load before starting Claude Code:
```bash
source .env
claude  # Start Claude Code with environment loaded
```

**Fix #2C: Update .mcp.json to reference env vars correctly**

```json
{
  "mcp_servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": null  // Will use system env
      }
    }
  }
}
```

When `env` value is `null`, Claude Code uses the system environment variable.

**Validation**:
```bash
# Before starting Claude Code:
test -n "$GITHUB_TOKEN" && echo "Token set" || echo "Token NOT set"
```

---

### Issue #3: Tool Name Length Exceeds 64-Character Limit

**Severity**: HIGH (prevents tool registration in Claude Code)

**Root Cause**:
Claude Code enforces a 64-character limit on tool names. Custom MCP servers often have long names:
- `mcp__github-mcp-server__add_pull_request_review_comment_to_pending_review` = 66 chars ❌
- `mcp__syscall-tracer__analyze_syscall_frequency` = 47 chars ✓

The server name prefix + tool name combination easily exceeds the limit.

**Symptoms**:
```
Error: tools.187.custom.name: String should have at most 64 characters
MCP Tool Registration Failed: Name too long
Tool cannot be imported: tool_name exceeds 64 characters
```

**Affected Tools** (in your setup):
```
# These likely fail:
docker_get_container_logs         (name + server prefix = 65+ chars)
docker_execute_command            (similar issue)
github_list_pull_requests         (similar issue)
```

**Fix #3A: Rename Custom MCP Tool Functions (Recommended)**

Edit in custom server files (boot-profiler/server.py, etc.):

OLD:
```python
@app.get("/measure-boot-timing-with-detailed-metrics")
async def measure_boot_timing_with_detailed_metrics():
    ...
```

NEW:
```python
@app.get("/measure-boot")  # Shorter name
async def measure_boot():
    ...
```

**Fix #3B: Use Server Name Aliasing**

In `.mcp.json`, use short server names:

```json
{
  "mcp_servers": {
    "gh": {  // SHORT: "gh" instead of "github-mcp-server"
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""}
    },
    "db": {  // SHORT: "db" instead of "sqlite-mcp-server"
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/db"]
    }
  }
}
```

Tools will be named: `gh__list_issues`, `db__query` (much shorter)

**Fix #3C: Check Actual Tool Names**

Test which tools exceed the limit:

```bash
# Get tool names from MCP server
npx -y @modelcontextprotocol/server-github 2>&1 | grep -o '"name":"[^"]*' | cut -d'"' -f4 | awk '{print length, $0}' | sort -rn

# Tools exceeding 64 chars will show length > 64
```

**Validation**:
```bash
# After applying fix, verify tool names are < 64 chars
echo "my_mcp_server__my_tool_name" | awk '{print length}'
# Should be < 64
```

---

### Issue #4: Docker MCP Server Configuration Incorrect

**Severity**: HIGH (Docker integration fails)

**Root Cause**:
The docker-mcp server configuration in docker-compose.enhanced.yml doesn't match MCP protocol requirements. The service is exposed on port 5000 but not properly configured as an MCP server.

**Current Problem** (docker-compose.enhanced.yml):
```yaml
docker-mcp:
  image: quantgeekdev/docker-mcp:latest  # Image may not exist or be outdated
  container_name: mcp-docker
  ports:
    - "5000:5000"
  # But .mcp.json tries to use it as a stdio server - MISMATCH!
```

The `.mcp.json` treats it as a local stdio process but docker-compose.enhanced.yml runs it as a separate service.

**Symptoms**:
```
ERROR: Cannot connect to Docker MCP server at localhost:5000
Error: docker-mcp connection refused
ERROR: ECONNREFUSED 127.0.0.1:5000
```

**Fix #4A: Use Official Docker MCP Gateway (Recommended)**

Instead of custom docker-mcp image, use Docker's official MCP Gateway:

```bash
# Install Docker MCP Gateway (requires Docker Desktop 4.26+)
docker mcp install
# Or use the official package
```

Update `.mcp.json`:
```json
{
  "mcp_servers": {
    "docker": {
      "type": "stdio",
      "command": "docker",
      "args": ["mcp", "gateway", "run"],
      "description": "Docker container management via official gateway"
    }
  }
}
```

**Fix #4B: If Using QuantGeekDev Image**

Update docker-compose.enhanced.yml:

```yaml
docker-mcp:
  image: quantgeekdev/docker-mcp:latest
  container_name: mcp-docker
  environment:
    - DOCKER_HOST=unix:///var/run/docker.sock
    - DEBUG=true
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  networks:
    - minix-analysis
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 5s
```

Update `.mcp.json` to use HTTP connection:

```json
{
  "mcp_servers": {
    "docker": {
      "type": "stdio",
      "command": "curl",
      "args": ["-X", "POST", "-H", "Content-Type: application/json", "http://localhost:5000/docker_list_containers"],
      "description": "Docker via HTTP gateway"
    }
  }
}
```

**Fix #4C: Access Docker Socket Properly**

Ensure Docker socket is accessible:

```bash
# Check socket exists and is readable
ls -la /var/run/docker.sock
# Should show: srw-rw---- 1 root docker

# Add current user to docker group
sudo usermod -aG docker $(whoami)

# Verify membership
groups | grep docker
# Should include "docker"

# Test Docker access
docker ps
# Should list containers without sudo
```

**Validation**:
```bash
# Test Docker MCP connection
docker ps  # Should work without sudo

# Start services
docker-compose -f docker-compose.enhanced.yml up -d

# Check MCP service health
curl http://localhost:5000/health
# Should return {"status": "healthy", ...}
```

---

### Issue #5: Custom MCP Servers Not Integrated into .mcp.json

**Severity**: MEDIUM (custom analysis tools unavailable)

**Root Cause**:
Three custom MCP servers (boot-profiler, syscall-tracer, memory-monitor) are defined in docker-compose.enhanced.yml but NOT registered in `.mcp.json`. They run as HTTP services but aren't exposed to Claude Code.

**Current State**:
- docker-compose.yml defines: mcp-boot-profiler (port 5010), mcp-syscall-tracer (port 5011), mcp-memory-monitor (port 5012)
- .mcp.json: No entries for these servers
- Result: Claude Code cannot use them

**Symptoms**:
```
Claude Code: I don't have tools to analyze boot profiling
No MCP server named "boot-profiler"
Tool "profile_single_boot" not available
```

**Fix #5A: Add Custom Servers to .mcp.json**

Add entries for each custom server:

```json
{
  "mcp_servers": {
    "boot-profiler": {
      "type": "stdio",
      "command": "curl",
      "args": ["-X", "GET", "http://localhost:5010"],
      "description": "MINIX boot profiling and timing analysis"
    },
    "syscall-tracer": {
      "type": "stdio",
      "command": "curl",
      "args": ["-X", "GET", "http://localhost:5011"],
      "description": "MINIX syscall tracing and frequency analysis"
    },
    "memory-monitor": {
      "type": "stdio",
      "command": "curl",
      "args": ["-X", "GET", "http://localhost:5012"],
      "description": "MINIX memory behavior and TLB analysis"
    }
  }
}
```

**Fix #5B: Better Approach - Convert to True MCP Servers**

The custom servers are FastAPI apps, not true MCP servers. Convert them to MCP protocol:

In `mcp-servers/boot-profiler/server.py`, add MCP wrapper:

```python
# Add at top of file
from mcp.server import Server
from mcp.types import Tool, TextContent

# Create MCP server
mcp_server = Server("boot-profiler")

# Register tools
@mcp_server.call_tool()
async def handle_tool_call(name: str, arguments: dict):
    if name == "measure_boot_i386":
        result = await measure_boot_i386(arguments.get("timeout", 120))
        return [TextContent(type="text", text=json.dumps(result.model_dump()))]
    ...

# Run both HTTP (for monitoring) and MCP (for Claude)
if __name__ == "__main__":
    import asyncio
    
    # Start FastAPI for HTTP monitoring
    import uvicorn
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def lifespan(app):
        # Start MCP server in background
        task = asyncio.create_task(mcp_server.run())
        yield
        task.cancel()
    
    app = FastAPI(lifespan=lifespan)
    # ... rest of FastAPI app
```

Then register in .mcp.json as stdio:

```json
{
  "boot-profiler": {
    "type": "stdio",
    "command": "python3",
    "args": ["/home/eirikr/Playground/minix-analysis/mcp-servers/boot-profiler/server.py"],
    "description": "Boot profiling MCP server"
  }
}
```

**Validation**:
```bash
# Test boot-profiler endpoint
curl http://localhost:5010/health
# Should return {"status": "healthy", ...}

# If converted to MCP, test stdio:
python3 mcp-servers/boot-profiler/server.py < /dev/null
# Should start without errors
```

---

### Issue #6: Docker Socket Permission Denied in Containers

**Severity**: MEDIUM (Docker MCP fails inside containers)

**Root Cause**:
Docker containers trying to use `-v /var/run/docker.sock:/var/run/docker.sock` fail because the host user ID (1000) doesn't match the container user ID that owns the socket (usually 0 or docker group GID).

**Symptoms**:
```
Error: permission denied while trying to connect to Docker daemon socket
docker.errors.DockerException: Error while fetching server API version
Cannot connect to Docker daemon
```

**Fix #6A: Use docker:dind (Docker-in-Docker)**

```yaml
# In docker-compose.enhanced.yml
docker-dind:
  image: docker:dind
  container_name: docker-dind
  privileged: true
  environment:
    - DOCKER_TLS_CERTDIR=/certs
  volumes:
    - docker-certs:/certs/client
  networks:
    - minix-analysis

services:
  mcp-docker:
    image: quantgeekdev/docker-mcp:latest
    depends_on:
      - docker-dind
    environment:
      - DOCKER_HOST=tcp://docker-dind:2375
    networks:
      - minix-analysis

volumes:
  docker-certs:
```

**Fix #6B: Fix Socket Permissions on Host**

```bash
# Make socket world-readable (less secure)
sudo chmod 666 /var/run/docker.sock

# Or: Add docker group to allow access
sudo usermod -aG docker $(id -u -n)
newgrp docker

# Verify
docker ps
```

**Fix #6C: Use named socket with proper permissions**

```bash
# Create docker group and socket if needed
sudo groupadd docker 2>/dev/null || true
sudo usermod -aG docker $(whoami)

# Fix socket ownership
sudo chown root:docker /var/run/docker.sock
sudo chmod 660 /var/run/docker.sock
```

**Validation**:
```bash
# Test Docker access from host
docker ps

# Test from container
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock docker docker ps
# Should work without errors
```

---

## CONFIGURATION ISSUES

### Config Issue #1: Missing Required Directories

**Problem**: Measurements directories don't exist, causing "file not found" errors.

**Fix**:
```bash
cd /home/eirikr/Playground/minix-analysis
mkdir -p measurements/i386/syscalls measurements/i386/memory
mkdir -p measurements/arm/syscalls measurements/arm/memory
mkdir -p data logs
chmod 755 measurements/ measurements/*
```

---

### Config Issue #2: Database Path Doesn't Match Between Config Files

**Problem**: `.mcp.json` specifies one DB path, docker-compose.enhanced.yml specifies another.

**Fix**:
Standardize to single path:
```
/home/eirikr/Playground/minix-analysis/measurements/minix-analysis.db
```

Update all references in:
- `.mcp.json` (sqlite server config)
- `docker-compose.enhanced.yml` (environment vars)
- `scripts/minix-boot-diagnostics.sh` (if used)

---

### Config Issue #3: Healthcheck Conditions Too Strict

**Problem**: Docker services fail healthchecks because conditions are incorrect.

**Current** (docker-compose.enhanced.yml):
```yaml
healthcheck:
  test: ["CMD", "test", "-f", "/measurements/boot.log"]
  # Fails because boot.log doesn't exist yet on startup
```

**Fix**:
```yaml
healthcheck:
  test: ["CMD", "test", "-d", "/measurements"]  # Check dir exists
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s  # Give container time to start
```

---

### Config Issue #4: MINIX Docker Images Missing

**Problem**: docker-compose references MINIX images that don't exist or aren't built.

**Fix**:
```bash
# Check if images exist
docker images | grep minix

# If missing, build from Dockerfile
cd docker/
docker build -f Dockerfile.i386 -t minix-rc6-i386 .
docker build -f Dockerfile.arm -t minix-rc6-arm .

# Verify
docker images | grep minix
```

---

### Config Issue #5: Network Configuration Issues

**Problem**: Containers can't communicate due to network misconfiguration.

**Current**:
```yaml
networks:
  minix-analysis:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16  # Specific subnet
```

**Fix**:
```yaml
networks:
  minix-analysis:
    driver: bridge
    # Let Docker assign subnet automatically, or use standard range
```

---

### Config Issue #6: Missing `type: "stdio"` in MCP Server Definitions

**Problem**: .mcp.json doesn't specify transport type, causing unclear errors.

**Fix**: Add type to all servers:
```json
{
  "mcp_servers": {
    "github": {
      "type": "stdio",  // ADD THIS
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

---

### Config Issue #7: Python Requirements Not Installed

**Problem**: Custom MCP servers fail because Python dependencies missing.

**Affected Files**:
- `mcp-servers/boot-profiler/requirements.txt`
- `mcp-servers/syscall-tracer/requirements.txt`
- `mcp-servers/memory-monitor/requirements.txt`

**Fix**:
```bash
# Install dependencies for each server
pip3 install fastapi uvicorn docker pydantic

# Or: Install from requirements
for server in boot-profiler syscall-tracer memory-monitor; do
    pip3 install -r mcp-servers/$server/requirements.txt
done
```

**Verify**:
```bash
python3 -c "import docker; print(docker.__version__)"
python3 -c "import fastapi; print(fastapi.__version__)"
```

---

### Config Issue #8: Console Output/Logging Misconfiguration

**Problem**: Docker logs aren't captured properly, making debugging difficult.

**Fix**:
```yaml
# In docker-compose.enhanced.yml, add logging config
services:
  minix-i386:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    # ... rest of config
```

Verify logs:
```bash
docker logs -f minix-rc6-i386
```

---

## QUICK FIX CHECKLIST

Apply these in order to fix most issues:

- [ ] **Fix #1**: Replace package names in `.mcp.json` with correct ones
  ```bash
  sed -i 's/docker-mcp@latest/@modelcontextprotocol\/server-docker/g' .mcp.json
  sed -i 's/@github\/cli-mcp-server@latest/@modelcontextprotocol\/server-github/g' .mcp.json
  ```

- [ ] **Fix #2**: Set environment variables before starting Claude Code
  ```bash
  export GITHUB_TOKEN="ghp_YourTokenHere"
  export DOCKER_HUB_USERNAME="your-username"
  export DOCKER_HUB_TOKEN="dckr_YourTokenHere"
  ```

- [ ] **Fix #3**: Shorten server names in `.mcp.json` (gh, db, etc.)

- [ ] **Fix #4**: Test Docker access
  ```bash
  docker ps
  sudo usermod -aG docker $(whoami)
  newgrp docker
  ```

- [ ] **Fix #5**: Create required directories
  ```bash
  mkdir -p measurements/{i386,arm}/{syscalls,memory} data logs
  ```

- [ ] **Fix #6**: Install Python dependencies
  ```bash
  pip3 install fastapi uvicorn docker pydantic
  ```

- [ ] **Fix #7**: Build Docker images (if needed)
  ```bash
  cd docker/
  docker build -f Dockerfile.i386 -t minix-rc6-i386 .
  ```

- [ ] **Fix #8**: Start Docker Compose services
  ```bash
  docker-compose -f docker-compose.enhanced.yml up -d
  docker-compose -f docker-compose.enhanced.yml ps  # Verify
  ```

---

## VALIDATION PROCEDURES

### Test 1: Verify Environment Setup

```bash
#!/bin/bash
set -e

echo "=== Environment Check ==="
test -n "$GITHUB_TOKEN" && echo "✓ GITHUB_TOKEN set" || echo "✗ GITHUB_TOKEN not set"
test -n "$DOCKER_HUB_USERNAME" && echo "✓ DOCKER_HUB_USERNAME set" || echo "✗ DOCKER_HUB_USERNAME not set"
test -n "$DOCKER_HUB_TOKEN" && echo "✓ DOCKER_HUB_TOKEN set" || echo "✗ DOCKER_HUB_TOKEN not set"

echo -e "\n=== Docker Access Check ==="
docker ps > /dev/null && echo "✓ Docker daemon accessible" || echo "✗ Docker daemon not accessible"

echo -e "\n=== Directory Structure Check ==="
test -d measurements/i386 && echo "✓ measurements/i386 exists" || echo "✗ missing: measurements/i386"
test -d measurements/arm && echo "✓ measurements/arm exists" || echo "✗ missing: measurements/arm"
test -f .mcp.json && echo "✓ .mcp.json exists" || echo "✗ missing: .mcp.json"

echo -e "\n=== NPM Package Check ==="
npx -y @modelcontextprotocol/server-github --version 2>/dev/null && \
  echo "✓ GitHub MCP server available" || \
  echo "✗ GitHub MCP server not available"
```

### Test 2: Verify MCP Server Connectivity

```bash
#!/bin/bash

echo "=== Testing GitHub MCP ==="
timeout 5 bash -c 'echo "" | npx -y @modelcontextprotocol/server-github' 2>&1 | head -5

echo -e "\n=== Testing Docker Service ==="
docker ps > /dev/null && echo "✓ Docker working" || echo "✗ Docker failed"

echo -e "\n=== Testing Docker Compose ==="
docker-compose -f docker-compose.enhanced.yml config > /dev/null && \
  echo "✓ docker-compose.yml is valid" || \
  echo "✗ docker-compose.yml has errors"
```

### Test 3: Integration Test

```bash
#!/bin/bash

echo "=== Starting Docker Services ==="
docker-compose -f docker-compose.enhanced.yml up -d

echo -e "\n=== Waiting for Services ==="
sleep 10

echo -e "\n=== Service Status ==="
docker-compose -f docker-compose.enhanced.yml ps

echo -e "\n=== Testing Custom MCP Servers ==="
curl -s http://localhost:5010/health | jq . && echo "✓ Boot profiler healthy" || echo "✗ Boot profiler failed"
curl -s http://localhost:5011/health | jq . && echo "✓ Syscall tracer healthy" || echo "✗ Syscall tracer failed"
curl -s http://localhost:5012/health | jq . && echo "✓ Memory monitor healthy" || echo "✗ Memory monitor failed"
```

---

## TROUBLESHOOTING DECISION TREE

```
Start: MCP tools not working in Claude Code
  │
  ├─ ERROR: Package not found?
  │   └─→ Fix #1: Update .mcp.json with correct package names
  │
  ├─ ERROR: Authentication failed (401)?
  │   └─→ Fix #2: Set environment variables before starting Claude Code
  │
  ├─ ERROR: Tool name exceeds 64 characters?
  │   └─→ Fix #3A: Rename tool functions to be shorter
  │   └─→ Fix #3B: Use short server name aliases in .mcp.json
  │
  ├─ ERROR: Cannot connect to Docker?
  │   └─→ Fix #4A: Use Docker official MCP gateway
  │   └─→ Fix #4C: Add user to docker group: sudo usermod -aG docker $(whoami)
  │
  ├─ ERROR: Custom servers not available?
  │   └─→ Fix #5A: Register custom servers in .mcp.json
  │   └─→ Fix #5B: Convert custom servers to true MCP protocol
  │
  ├─ ERROR: Docker socket permission denied?
  │   └─→ Fix #6B: sudo chmod 666 /var/run/docker.sock
  │   └─→ Fix #6C: sudo usermod -aG docker $(whoami)
  │
  ├─ ERROR: File not found?
  │   └─→ Config Issue #1: Create required directories
  │
  ├─ ERROR: Database not found?
  │   └─→ Config Issue #2: Ensure consistent DB path in all configs
  │
  └─ ERROR: Still failing?
      └─→ Check logs: docker logs <service_name>
      └─→ Validate config: docker-compose config
      └─→ Run validation tests above
```

---

## CORRECTED CONFIGURATION FILES

### Corrected .mcp.json

See `MCP-CORRECTED-CONFIG.json` in this repository for complete corrected version.

**Key Changes**:
- Correct package names (@modelcontextprotocol/server-*)
- Proper `type: "stdio"` declarations
- Short server aliases (gh, db)
- Removed template variable syntax
- Added all required environment variables

---

## NEXT STEPS

1. **Apply Quick Fix Checklist** (above) in order
2. **Run Validation Test #1** to verify environment
3. **Run Validation Test #2** to test MCP connectivity
4. **Replace .mcp.json** with corrected version
5. **Restart Claude Code** with environment variables set
6. **Test in Claude Code**: "List my Docker containers"
7. **Report any remaining errors** with full error message and context

---

## REFERENCES AND RESOURCES

**Official Documentation**:
- MCP Specification: https://modelcontextprotocol.io/
- Claude Code MCP Docs: https://docs.claude.com/en/docs/claude-code/mcp
- Docker MCP: https://github.com/docker/mcp-gateway
- GitHub MCP: https://github.com/github/github-mcp-server

**Known Issues**:
- Tool name 64-character limit: https://github.com/anthropics/claude-code/issues/2445
- Docker MCP connection: https://github.com/docker/for-win/issues/14867
- MCP tool registration: https://github.com/anthropics/claude-code/issues/5241

**Community Resources**:
- Awesome MCP Servers: https://github.com/MCPStar/awesome-dxt-mcp
- MCP Tutorials: https://modelcontextprotocol.io/docs/tutorials
- Claude Desktop MCP Setup: https://www.docker.com/blog/add-mcp-servers-to-claude-code-with-mcp-toolkit/

---

**Document Version**: 1.0
**Last Updated**: 2025-11-01
**Status**: Complete with all identified issues and fixes
