# MCP Troubleshooting Quick Reference

**For when things break - quick fixes without reading the full guide**

---

## Problem: "Cannot find module docker-mcp"

**Solution**: Wrong package name
```bash
# WRONG (doesn't exist)
npx -y docker-mcp@latest

# RIGHT (correct package)
npx -y @modelcontextprotocol/server-github
```

**Fix .mcp.json**:
```json
{
  "mcp_servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": null}
    }
  }
}
```

---

## Problem: "401 Unauthorized: Bad credentials"

**Solution**: Environment variable not set properly
```bash
# VERIFY variable is set
echo $GITHUB_TOKEN

# If empty, SET IT
export GITHUB_TOKEN="ghp_YourTokenHere"

# Then START Claude Code
claude
```

**Do NOT use** `"${GITHUB_TOKEN}"` in .mcp.json - use `null` instead to inherit from shell environment.

---

## Problem: "Tool name exceeds 64 characters"

**Solution**: Shorten server names
```json
{
  "mcp_servers": {
    "gh": {  // SHORT (was "github-mcp-server")
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

Tools will be: `gh__list_issues` (47 chars) instead of `github-mcp-server__list_pull_requests` (66 chars)

---

## Problem: "Cannot connect to Docker daemon"

**Solution**: Add user to docker group
```bash
# Add user to docker group
sudo usermod -aG docker $(whoami)

# Apply changes
newgrp docker

# Verify
docker ps
```

---

## Problem: "ECONNREFUSED: Docker MCP on port 5000"

**Solution**: Docker socket not accessible
```bash
# Make socket readable
sudo chmod 666 /var/run/docker.sock

# Or: Fix permissions properly
sudo chown root:docker /var/run/docker.sock
sudo chmod 660 /var/run/docker.sock

# Verify
docker ps
```

---

## Problem: Services fail to start

**Solution**: Missing directories
```bash
# Create required directories
mkdir -p measurements/{i386,arm}/{syscalls,memory} data logs

# Verify
ls -la measurements/i386/
```

---

## Problem: "database file not found"

**Solution**: Ensure DB path is consistent
```bash
# Create database if needed
touch measurements/minix-analysis.db

# Update all config files to use same path:
# - .mcp.json
# - docker-compose.enhanced.yml
# - Any scripts

CORRECT_PATH="/home/eirikr/Playground/minix-analysis/measurements/minix-analysis.db"
```

---

## Problem: "Module not found: @modelcontextprotocol/server-github"

**Solution**: Install npm packages
```bash
# Option 1: npx will auto-install on first use
npx -y @modelcontextprotocol/server-github --help

# Option 2: Install globally (faster)
npm install -g @modelcontextprotocol/server-github

# Verify
npm list -g @modelcontextprotocol/server-github
```

---

## Problem: "docker-compose: command not found"

**Solution**: Install docker-compose
```bash
# Install
pip3 install docker-compose

# Or: Use Docker integrated compose (newer)
docker compose version

# If using newer Docker, substitute:
# OLD: docker-compose -f file.yml up
# NEW: docker compose -f file.yml up
```

---

## Problem: "health check failing"

**Solution**: Services take time to start, or health check condition is wrong
```yaml
# WRONG (boot.log doesn't exist yet)
healthcheck:
  test: ["CMD", "test", "-f", "/measurements/boot.log"]

# RIGHT (check directory exists)
healthcheck:
  test: ["CMD", "test", "-d", "/measurements"]
  start_period: 10s  # Give service time to start
```

---

## Problem: "tool name validation failed"

**Solution**: Check actual tool name length
```bash
# See what the tool name will be
echo "gh__list_issues" | wc -c
# Should be < 64

# If too long, shorten either:
# 1. Server name (gh instead of github-mcp-server)
# 2. Tool function name (list_issues instead of list_all_github_issues)
```

---

## Quick Diagnostic Commands

```bash
# Check environment
echo $GITHUB_TOKEN
echo $DOCKER_HUB_USERNAME

# Check Docker
docker ps
docker-compose ps

# Check MCP servers
npx -y @modelcontextprotocol/server-github --help
npx -y @modelcontextprotocol/server-sqlite --help

# Check services
curl http://localhost:5010/health  # boot-profiler
curl http://localhost:5011/health  # syscall-tracer
curl http://localhost:5012/health  # memory-monitor

# Check config validity
python3 -m json.tool .mcp.json
docker-compose -f docker-compose.enhanced.yml config
```

---

## Setup One-Liner (After Fixes)

```bash
#!/bin/bash

# Set environment variables
export GITHUB_TOKEN="ghp_YourTokenHere"
export DOCKER_HUB_USERNAME="your-username"
export DOCKER_HUB_TOKEN="dckr_YourTokenHere"

# Create directories
mkdir -p measurements/{i386,arm}/{syscalls,memory} data logs

# Fix Docker access if needed
sudo usermod -aG docker $(whoami) 2>/dev/null || true

# Replace config with corrected version
cp MCP-CORRECTED-CONFIG.json .mcp.json

# Start services
docker-compose -f docker-compose.enhanced.yml up -d

# Wait for services
sleep 10

# Check status
docker-compose -f docker-compose.enhanced.yml ps

# Start Claude Code
claude
```

---

## Is It Fixed? Checklist

- [ ] `echo $GITHUB_TOKEN` shows token (not empty)
- [ ] `docker ps` works without sudo
- [ ] `.mcp.json` uses `@modelcontextprotocol/server-*` package names
- [ ] `.mcp.json` has `"type": "stdio"` for all servers
- [ ] `docker-compose -f docker-compose.enhanced.yml config` is valid
- [ ] `docker-compose -f docker-compose.enhanced.yml ps` shows services
- [ ] Custom services respond: `curl http://localhost:5010/health`
- [ ] Tool names are < 64 characters

If all checked: **Should be fixed!**

---

## Still Not Working?

1. **Read full guide**: `MCP-TROUBLESHOOTING-AND-FIXES.md`
2. **Run diagnostic script**: `bash MCP-FIX-GUIDE.sh`
3. **Check logs**: `docker logs <service_name>`
4. **Validate config**: `docker-compose config`
5. **Test MCP directly**: `npx -y @modelcontextprotocol/server-github --help`

---

## Common Error Messages and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find module 'docker-mcp'` | Wrong package name | Use `@modelcontextprotocol/server-*` |
| `401 Unauthorized` | Token not set | `export GITHUB_TOKEN='ghp_...'` |
| `ECONNREFUSED 127.0.0.1:5000` | Service not running | `docker-compose up -d` |
| `permission denied` | Docker socket perms | `sudo chmod 666 /var/run/docker.sock` |
| `Tool name exceeds 64 chars` | Name too long | Shorten server name (gh not github-mcp-server) |
| `File not found` | Missing directories | `mkdir -p measurements/{i386,arm}` |
| `command not found: docker-compose` | Not installed | `pip3 install docker-compose` |
| `health check failing` | Service not ready | Add `start_period: 10s` to healthcheck |
| `Syntax error in .mcp.json` | Invalid JSON | `python3 -m json.tool .mcp.json` |
| `Module not found: docker` | Python package missing | `pip3 install docker` |

---

## Need More Help?

1. Full troubleshooting guide: `MCP-TROUBLESHOOTING-AND-FIXES.md`
2. Corrected configs: `MCP-CORRECTED-CONFIG.json`
3. Diagnostic script: `bash MCP-FIX-GUIDE.sh`
4. GitHub issues: https://github.com/anthropics/claude-code/issues
5. MCP spec: https://modelcontextprotocol.io/
6. Docker docs: https://docs.docker.com/
