# MINIX + Model Context Protocol (MCP) Integration Guide

**Source**: MINIX-MCP-Integration.md
**Date Organized**: 2025-11-01
**Purpose**: Full MCP server integration for MINIX analysis, Docker, GitHub, and automated diagnostics
**Complexity Level**: ⭐⭐⭐⭐ (Advanced)
**Estimated Time**: 45-90 minutes

---


**Version**: 2.0
**Date**: 2025-11-01
**Status**: Complete
**Scope**: Full MCP server integration for MINIX analysis, Docker container management, GitHub integration, and automated error diagnostics

---

## Table of Contents

1. [Overview](#overview)
2. [MCP Servers in This Setup](#mcp-servers-in-this-setup)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Common Workflows](#common-workflows)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Overview

**Model Context Protocol (MCP)** enables Claude Code to interact with external systems and tools through standardized protocol connections. This integration provides:

1. **Docker MCP** - Control MINIX containers, fetch logs, monitor status
2. **Docker Hub MCP** - Search and manage MINIX images on Docker Hub
3. **GitHub MCP** - Create issues for errors found, manage PRs, track diagnostics
4. **SQLite MCP** - Query boot profiling measurements and analyze data
5. **Custom MCP Servers** - Boot profiler, syscall tracer, memory monitor

**Key Benefits**:
- Claude Code can control MINIX boot instances directly
- Automated error diagnosis with Python + MCP
- GitHub integration for issue tracking
- Real-time monitoring of boot logs and system state
- Programmatic access to measurement data

---

## MCP Servers in This Setup

### 1. Docker MCP Server

**Purpose**: Control Docker containers (MINIX instances, analysis services)

**Tools Available**:
- `docker_list_containers` - List running/stopped MINIX instances
- `docker_get_container_logs` - Fetch boot log from container
- `docker_get_container_stats` - Real-time CPU/memory usage
- `docker_start_container` - Start MINIX i386/ARM instance
- `docker_stop_container` - Stop instance cleanly
- `docker_restart_container` - Restart instance
- `docker_inspect_container` - Get detailed container config
- `docker_execute_command` - Run command inside container

**Configuration** (in `.mcp.json`):
```json
"docker": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "docker-mcp@latest"],
  "env": {
    "DOCKER_HOST": "unix:///var/run/docker.sock"
  }
}
```

**Example Use**:
```bash
# Start MINIX container
docker_start_container minix-rc6-i386

# Fetch boot log
docker_get_container_logs minix-rc6-i386 | head -100

# Check resource usage
docker_get_container_stats minix-rc6-i386
```

**In Claude Code**:
```
I can now start the MINIX i386 container using the Docker MCP server.
```

---

### 2. Docker Hub MCP Server

**Purpose**: Search and manage container images

**Tools Available**:
- `hub_search_repositories` - Find MINIX images on Docker Hub
- `hub_get_repository_details` - Get image metadata
- `hub_list_repository_tags` - List available versions
- `hub_get_image_manifest` - Get image layer information
- `hub_get_dockerfile` - Retrieve Dockerfile used to build image
- `hub_search_images` - Full-text image search
- `hub_get_image_stats` - View download counts, popularity

**Configuration** (in `.mcp.json`):
```json
"docker-hub": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "docker-hub-mcp@latest"],
  "env": {
    "DOCKER_HUB_USERNAME": "your-docker-username",
    "DOCKER_HUB_TOKEN": "your-pat-token"
  }
}
```

**Setup**:
```bash
# 1. Create Docker Hub Personal Access Token:
#    - Go to https://hub.docker.com/settings/security
#    - Generate new token with read/write permissions
#    - Copy token value

# 2. Export to environment:
export DOCKER_HUB_USERNAME="your-username"
export DOCKER_HUB_TOKEN="ghp_YourTokenHere"

# 3. Verify in claude_desktop_config.json or .mcp.json
```

**Example Use**:
```bash
# Search for MINIX images
hub_search_repositories madworx minix

# Get image details
hub_get_repository_details madworx minix

# List available tags
hub_list_repository_tags madworx minix
```

---

### 3. GitHub MCP Server

**Purpose**: Create issues, manage PRs, track diagnostics in GitHub

**Tools Available**:
- `github_list_issues` - List open/closed issues
- `github_create_issue` - Create new issue for discovered error
- `github_get_issue` - Get issue details
- `github_update_issue` - Update issue status
- `github_list_pull_requests` - List PRs
- `github_create_pull_request` - Create PR with fixes
- `github_list_repository_contents` - Browse repo files
- `github_get_repository_info` - Get repo metadata
- `github_search_code` - Full-text code search

**Configuration** (in `.mcp.json`):
```json
"github": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@github/cli-mcp-server@latest"],
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}",
    "GITHUB_REPOSITORY": "oaich/minix-analysis"
  }
}
```

**Setup**:
```bash
# 1. Create GitHub Personal Access Token:
#    - Go to https://github.com/settings/tokens
#    - Generate new token with: repo, read:org scopes
#    - Copy token value

# 2. Export to environment:
export GITHUB_TOKEN="ghp_YourTokenHere"

# 3. Verify with:
gh auth status
```

**Example Use**:
```bash
# Create issue for error found
github_create_issue \
  --title "Boot failure: CD9660 module not loading" \
  --body "Error E003 detected. Suggested fix: upgrade to MINIX RC6"

# Link to measurements
github_create_issue \
  --title "Phase 7.5: Boot profiling completed" \
  --body "Multi-CPU measurements stored in measurements/i386/"
```

---

### 4. SQLite MCP Server

**Purpose**: Query boot profiling measurements database

**Tools Available**:
- `sqlite_query` - Execute SQL queries
- `sqlite_list_tables` - Show tables in database
- `sqlite_get_table_schema` - Get column definitions
- `sqlite_create_record` - Insert measurement record
- `sqlite_read_records` - Query records with conditions
- `sqlite_update_records` - Update existing records

**Configuration** (in `.mcp.json`):
```json
"sqlite": {
  "type": "stdio",
  "command": "python3",
  "args": ["-m", "mcp_sqlite"],
  "env": {
    "DATABASE_PATH": "/home/eirikr/Playground/minix-analysis/measurements/minix-analysis.db"
  }
}
```

**Schema** (created automatically):
```sql
CREATE TABLE boot_measurements (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  architecture TEXT,
  cpu_count INTEGER,
  boot_time_ms INTEGER,
  kernel_time_ms INTEGER,
  markers TEXT,  -- JSON
  error_detected BOOLEAN
);
```

**Example Queries**:
```bash
# Get average boot time by CPU count
sqlite_query "SELECT cpu_count, AVG(boot_time_ms) as avg_ms 
              FROM boot_measurements 
              GROUP BY cpu_count"

# Find fastest boot
sqlite_query "SELECT * FROM boot_measurements 
              ORDER BY boot_time_ms ASC LIMIT 1"

# Correlation: CPU count vs boot time
sqlite_query "SELECT cpu_count, boot_time_ms, kernel_time_ms 
              FROM boot_measurements 
              ORDER BY cpu_count"
```

---

## Quick Start

### 1. Install and Enable MCP Servers

**Option A: Via Claude Desktop (Easiest)**

```bash
# 1. Start Claude Desktop
# 2. Settings → Model Preferences → MCP
# 3. Add servers:
#    - Name: docker-mcp
#    - Type: stdio
#    - Command: npx -y docker-mcp@latest

# 4. Add environment variables (or set in ~/.bashrc):
export GITHUB_TOKEN="ghp_YourToken"
export DOCKER_HUB_USERNAME="your-username"
export DOCKER_HUB_TOKEN="your-hub-token"

# 5. Restart Claude Desktop
```

**Option B: Via Configuration File**

```bash
# 1. Use provided .mcp.json:
cp /home/eirikr/Playground/minix-analysis/.mcp.json ~/.claude/

# 2. Edit ~/.claude/.mcp.json:
# Update GITHUB_TOKEN, DOCKER_HUB_USERNAME, DOCKER_HUB_TOKEN

# 3. Restart Claude Code
```

### 2. Start MINIX with Docker Compose

```bash
cd /home/eirikr/Playground/minix-analysis

# Start all services (MINIX + MCP servers)
docker-compose -f docker-compose.enhanced.yml up -d

# Or start just MINIX
docker-compose -f docker-compose.enhanced.yml up -d minix-i386

# Check status
docker-compose -f docker-compose.enhanced.yml ps
```

### 3. Verify MCP Servers are Working

In Claude Code:

```
Test Docker MCP: Can you list the Docker containers I have running?
# Should show minix-rc6-i386, minix-rc6-arm, etc.

Test GitHub MCP: What issues are in the minix-analysis repository?
# Should list GitHub issues

Test SQLite MCP: Can you query the boot measurements database?
# Should show boot profiling results
```

---

## Detailed Setup

### Environment Variables Required

Set in `~/.bashrc`, `~/.zshrc`, or Docker `.env` file:

```bash
# GitHub integration
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"         # GitHub Personal Access Token

# Docker Hub integration (optional)
export DOCKER_HUB_USERNAME="your-docker-id"
export DOCKER_HUB_TOKEN="xxxxxxxxxxxx"         # Docker Hub Personal Access Token

# Project paths (optional, for scripts)
export MINIX_PROJECT_ROOT="/home/eirikr/Playground/minix-analysis"
export MEASUREMENTS_DIR="$MINIX_PROJECT_ROOT/measurements"
```

### Setting Up GitHub Integration

**Step 1: Create Personal Access Token**

```bash
# Manual: https://github.com/settings/tokens/new
# Or via GitHub CLI:
gh auth login
gh auth token
```

**Step 2: Grant Permissions**

When creating token, enable:
- `repo` (full control of private repositories)
- `read:org` (read organization data)
- `gist` (create gists for logs)

**Step 3: Store Securely**

```bash
# Option 1: In environment (.bashrc)
echo 'export GITHUB_TOKEN="ghp_YourTokenHere"' >> ~/.bashrc
source ~/.bashrc

# Option 2: In ~/.netrc (for command-line tools)
cat >> ~/.netrc << EOF
machine github.com
login your-username
password ghp_YourTokenHere
EOF
chmod 600 ~/.netrc
```

**Step 4: Test**

```bash
gh auth status
gh api repos/oaich/minix-analysis/issues
```

### Setting Up Docker Hub Integration

**Step 1: Create Docker Hub Token**

```bash
# Manual: https://hub.docker.com/settings/security
# Generate → New Access Token
```

**Step 2: Store Token**

```bash
export DOCKER_HUB_USERNAME="your-docker-username"
export DOCKER_HUB_TOKEN="dckr_xxxxxxxxxxxx"
```

**Step 3: Test**

```bash
# Docker Hub MCP will use these in claude_desktop_config.json
```

---

## Common Workflows

### Workflow 1: Boot MINIX and Capture Diagnostics

**Objective**: Start MINIX, capture boot log, diagnose errors automatically

**Steps**:

1. Start MINIX container:
   ```
   I want to start the MINIX i386 container. Can you use the Docker MCP
   server to start "minix-rc6-i386"?
   ```

2. Monitor boot:
   ```
   Show me the last 50 lines of the MINIX boot log from the Docker container.
   ```

3. Diagnose errors:
   ```
   I'll fetch the boot log from the container and analyze it for errors.
   ```

4. Create GitHub issue (if errors found):
   ```
   Based on the errors, please create a GitHub issue with:
   - Title: [MINIX Boot] E003: CD9660 module load failure
   - Description: Include boot log excerpt and suggested fix
   ```

**MCP Tools Used**: Docker MCP, GitHub MCP

---

### Workflow 2: Analyze Boot Performance

**Objective**: Measure boot time across multiple CPU configurations and analyze scaling

**Steps**:

1. Start measurements:
   ```
   Start MINIX with 1 CPU and capture boot time.
   ```

2. Collect data:
   ```
   Repeat with 2, 4, and 8 CPUs. Record boot_time_ms for each.
   ```

3. Store in database:
   ```
   Insert measurements into SQLite database using MCP.
   ```

4. Query results:
   ```
   SELECT cpu_count, AVG(boot_time_ms) FROM boot_measurements 
   GROUP BY cpu_count
   ```

**MCP Tools Used**: Docker MCP, SQLite MCP

---

### Workflow 3: Error Detection and Recovery

**Objective**: Automatically detect boot errors and suggest fixes

**Steps**:

1. Run error triage:
   ```bash
   python3 tools/triage-minix-errors.py measurements/i386/boot.log
   ```

2. MCP-assisted diagnosis:
   ```
   The error triage found E006 (IRQ Check Failed). Using GitHub MCP,
   search the minix-analysis repository for solutions to this error.
   ```

3. Get detailed solution:
   ```
   From MINIX-Error-Registry.md, get the complete solution for E006
   and explain the fix step-by-step.
   ```

4. Apply fix:
   ```
   Modify the docker-compose command to use:
   -net nic,model=ne2k_isa,irq=3,iobase=0x300
   ```

**MCP Tools Used**: Docker MCP, GitHub MCP

---

### Workflow 4: Version Management

**Objective**: Check for latest MINIX images on Docker Hub

**Steps**:

1. Search Docker Hub:
   ```
   Using the Docker Hub MCP, search for the latest MINIX images
   from the madworx repository.
   ```

2. Compare versions:
   ```
   List all available tags for madworx/minix and show their descriptions.
   ```

3. Update image:
   ```
   Pull the latest madworx/minix:latest and rebuild the Docker container.
   ```

**MCP Tools Used**: Docker Hub MCP

---

## Troubleshooting

### Problem: MCP Server Connection Refused

**Symptom**:
```
ERROR: Failed to connect to MCP server: connection refused
```

**Solutions**:

1. **Verify server is running**:
   ```bash
   docker-compose -f docker-compose.enhanced.yml ps | grep mcp
   ```

2. **Check port availability**:
   ```bash
   netstat -tlnp | grep 500[0-2]  # Check MCP ports
   ```

3. **Restart MCP servers**:
   ```bash
   docker-compose -f docker-compose.enhanced.yml down
   docker-compose -f docker-compose.enhanced.yml up -d docker-mcp
   ```

4. **Check logs**:
   ```bash
   docker logs mcp-docker
   docker logs mcp-docker-hub
   ```

---

### Problem: Docker MCP Can't Access Container Socket

**Symptom**:
```
ERROR: Cannot access /var/run/docker.sock
```

**Solutions**:

1. **Verify socket exists**:
   ```bash
   ls -la /var/run/docker.sock
   ```

2. **Add user to docker group**:
   ```bash
   sudo usermod -aG docker $(whoami)
   newgrp docker
   ```

3. **Fix permissions**:
   ```bash
   sudo chmod 666 /var/run/docker.sock
   ```

---

### Problem: GitHub MCP Authentication Failed

**Symptom**:
```
ERROR: GitHub authentication failed
```

**Solutions**:

1. **Check token is set**:
   ```bash
   echo $GITHUB_TOKEN
   ```

2. **Verify token is valid**:
   ```bash
   curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.github.com/user
   ```

3. **Refresh token** (create new one if expired):
   ```bash
   gh auth refresh
   ```

4. **Update configuration**:
   ```bash
   # Update ~/.claude/.mcp.json with new token
   export GITHUB_TOKEN="ghp_NewToken"
   ```

---

### Problem: SQLite Database Not Found

**Symptom**:
```
ERROR: Database not found: /path/to/minix-analysis.db
```

**Solutions**:

1. **Create database**:
   ```bash
   mkdir -p measurements/
   touch measurements/minix-analysis.db
   ```

2. **Initialize schema**:
   ```sql
   CREATE TABLE boot_measurements (
     id INTEGER PRIMARY KEY,
     timestamp TEXT,
     architecture TEXT,
     cpu_count INTEGER,
     boot_time_ms INTEGER
   );
   ```

3. **Verify path in .mcp.json**:
   ```json
   "DATABASE_PATH": "/home/eirikr/Playground/minix-analysis/measurements/minix-analysis.db"
   ```

---

## Advanced Usage

### Custom MCP Server: Boot Profiler

**Purpose**: Specialized MCP server for MINIX boot analysis

**Available Tools**:
- `profile_single_boot` - Boot MINIX and capture metrics
- `profile_multi_cpu` - Test 1, 2, 4, 8 CPU configurations
- `profile_boot_time` - Extract boot time from log
- `profile_kernel_time` - Extract kernel initialization time
- `profile_scaling_efficiency` - Calculate CPU scaling effectiveness

**Usage in Claude Code**:
```
Using the boot profiler MCP, run a multi-CPU test (1, 2, 4, 8 vCPU)
and analyze the scaling efficiency of MINIX SMP scheduler.
```

**Docker Configuration**:
```yaml
mcp-boot-profiler:
  build:
    context: ./mcp-servers/boot-profiler
    dockerfile: Dockerfile
  container_name: mcp-boot-profiler
  ports:
    - "5010:5000"
  volumes:
    - ./measurements:/measurements
  environment:
    - MINIX_I386_CONTAINER=minix-rc6-i386
    - MEASUREMENTS_DIR=/measurements
```

---

### Custom MCP Server: Syscall Tracer

**Purpose**: Capture and analyze MINIX system call sequences

**Available Tools**:
- `trace_syscalls` - Run MINIX with strace equivalent
- `analyze_syscall_frequency` - Statistics on syscall usage
- `correlate_syscalls` - Find patterns and sequences
- `export_syscall_log` - Save trace for analysis

**Usage**:
```
Trace all system calls during MINIX boot and identify the top 10
most frequently called syscalls.
```

---

### Custom MCP Server: Memory Monitor

**Purpose**: Real-time memory usage monitoring during boot

**Available Tools**:
- `monitor_memory` - Start memory monitoring
- `get_memory_snapshot` - Capture current usage
- `analyze_memory_growth` - Detect memory leaks
- `report_memory_usage` - Generate usage report

**Usage**:
```
Monitor MINIX memory usage during boot and identify which subsystems
consume the most RAM.
```

---

### Programmatic Error Diagnosis

**Workflow**: Automated error detection and GitHub issue creation

```python
# In Claude Code (using MCP tools):

# 1. Get boot log from container
boot_log = docker_get_container_logs("minix-rc6-i386")

# 2. Run triage tool (local)
errors = triage_errors(boot_log)

# 3. For each error, create GitHub issue
for error in errors:
    if error['severity'] == 'CRITICAL':
        github_create_issue(
            title=f"[CRITICAL] {error['name']}",
            body=format_error_report(error)
        )

# 4. Query solution from registry
solutions = get_error_solutions(error['id'])
```

---

## Integration with CI/CD

### GitHub Actions Workflow

See `.github/workflows/minix-ci.yml` for automated:
- MINIX boot testing
- Error detection
- Performance benchmarking
- Automatic issue creation for failures

**Triggered by**:
- Push to main branch
- Weekly schedule (Sunday 00:00 UTC)
- Manual workflow dispatch

---

## Performance Optimization

**Tips for optimal MCP usage**:

1. **Batch operations**: Group multiple container operations
2. **Cache results**: Store boot logs locally to avoid repeated reads
3. **Async operations**: Run long-running profiling in background
4. **Monitor context window**: MCP tools consume tokens, monitor usage

---

## References

- **Claude Code MCP Docs**: https://docs.claude.com/en/docs/claude-code/mcp
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **Docker MCP Repository**: https://github.com/QuantGeekDev/docker-mcp
- **GitHub MCP**: https://github.com/anthropics/github-mcp-server
- **SQLite MCP**: https://github.com/anthropics/sqlite-mcp-server

---

**End of MINIX-MCP-Integration Guide**

Last updated: 2025-11-01
For issues or questions: Create GitHub issue in minix-analysis repository
