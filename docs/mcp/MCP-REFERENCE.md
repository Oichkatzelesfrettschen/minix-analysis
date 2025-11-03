# MINIX 3.4 MCP (Model Context Protocol) Integration Reference

**Status:** Consolidated reference document (Phase 2B)
**Date:** November 1, 2025
**Scope:** Model Context Protocol integration, setup, and usage for MINIX analysis
**Audience:** Claude Code users, AI tool developers, MINIX researchers

---

## Executive Summary

The Model Context Protocol (MCP) enables Claude to access the MINIX analysis codebase through standardized tools and resources. This document consolidates:

- **MCP Overview**: Protocol fundamentals and MINIX integration
- **Setup and Configuration**: Getting MCP running with MINIX analysis
- **Available Tools**: MCP-provided capabilities and usage
- **Troubleshooting**: Common issues and solutions
- **Validation**: Testing MCP connectivity and functionality
- **Best Practices**: Effective usage patterns

---

## Table of Contents

1. [MCP Overview](#mcp-overview)
2. [MCP Architecture](#mcp-architecture)
3. [Setup and Installation](#setup)
4. [Configuration](#configuration)
5. [Available Tools](#available-tools)
6. [Usage Patterns](#usage-patterns)
7. [Performance Characteristics](#performance)
8. [Troubleshooting](#troubleshooting)
9. [Validation Checklist](#validation)
10. [Best Practices](#best-practices)
11. [References](#references)

---

## MCP Overview

### What is the Model Context Protocol?

The Model Context Protocol (MCP) is a standardized interface enabling language models (like Claude) to:

1. **Access External Data Sources**: Files, databases, APIs
2. **Invoke Tools and Functions**: Execute operations beyond LLM computation
3. **Integrate with Workflows**: Connect to external systems and services
4. **Provide Resources**: Expose structured data and tools to AI assistants

### MCP for MINIX Analysis

For the MINIX analysis project, MCP provides:

**File System Access**:
- Read/write MINIX source code files
- Navigate directory structures
- Manage documentation

**Codebase Tools**:
- Search and grep capabilities
- File pattern matching
- Content analysis

**Analysis Integration**:
- Execute Python analysis scripts
- Run profiling tools
- Process measurement data

**Documentation Management**:
- Access existing documentation
- Create and edit reference materials
- Maintain consistency

---

## MCP Architecture

### Protocol Layers

```
┌─────────────────────────────────────┐
│   Claude (Language Model)            │  Layer 3: LLM interaction
├─────────────────────────────────────┤
│   MCP Client                        │  Layer 2: Protocol handler
├─────────────────────────────────────┤
│   MCP Server                        │  Layer 1: Tool/resource provider
├─────────────────────────────────────┤
│   External Systems                  │  Layer 0: Filesystem, processes, APIs
└─────────────────────────────────────┘
```

### Communication Flow

```
User Request (Claude)
    ↓
MCP Client Request (JSON-RPC)
    ↓
MCP Server Processing
    ↓
Tool Execution / Resource Access
    ↓
Response Generation (JSON)
    ↓
Result to Claude
    ↓
User Output
```

### MCP Resources vs Tools

**Tools** (Functions):
- Perform actions (read, write, execute)
- Take parameters
- Return results
- Examples: grep search, file operations

**Resources** (Data):
- Provide access to external information
- Read-only or managed updates
- Represent structured data
- Examples: code files, documentation

---

## Setup and Installation

### Prerequisites

1. **Claude Code CLI**: Install via `npm install -g @anthropic-ai/claude-code`
2. **Node.js**: v16 or later
3. **Project Directory**: MINIX analysis repository
4. **File Access**: Read/write permissions on project directory

### Installation Steps

**Step 1: Install Claude Code**
```bash
npm install -g @anthropic-ai/claude-code
```

**Step 2: Initialize Project**
```bash
cd /home/eirikr/Playground/minix-analysis
claude init
# Generates default configuration
```

**Step 3: Verify Installation**
```bash
claude version
# Should show version information
```

### Docker-Based Setup (Alternative)

For isolated environments:

```bash
# Build custom container
docker build -t minix-analysis-mcp .

# Run with MCP enabled
docker run -it -v $(pwd):/workspace minix-analysis-mcp
```

---

## Configuration

### MCP Configuration File

**Location**: `~/.claude/mcp.json` (or project-level `.mcp.json`)

**Example Configuration**:

```json
{
  "mcp_servers": {
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["/home/eirikr/Playground/minix-analysis"]
    },
    "python_runner": {
      "command": "python3",
      "args": ["-m", "mcp_python_runner"],
      "env": {
        "PYTHONPATH": "/home/eirikr/Playground/minix-analysis"
      }
    },
    "grep_search": {
      "command": "mcp-grep-server"
    }
  }
}
```

### Configuration Options

| Option | Purpose | Example |
|--------|---------|---------|
| command | Server executable | mcp-server-filesystem |
| args | Command arguments | ["/path/to/project"] |
| env | Environment variables | {"VAR": "value"} |
| timeout | Execution timeout (ms) | 30000 |
| auto_restart | Restart on failure | true |

### Environment Variables

```bash
# Python-specific
export PYTHONPATH="/home/eirikr/Playground/minix-analysis"
export MINIX_ROOT="/home/eirikr/Playground/minix"

# Debug mode
export MCP_DEBUG=1
export MCP_LOG_LEVEL=DEBUG
```

---

## Available Tools

### 1. Filesystem Operations

**Read File**:
```
mcp_tool: filesystem_read
  path: "/home/eirikr/Playground/minix-analysis/docs/INDEX.md"
  offset: 0
  limit: 100  # lines
Result: File contents
```

**Write File**:
```
mcp_tool: filesystem_write
  path: "/home/eirikr/Playground/minix-analysis/docs/new-file.md"
  content: "# New Documentation"
  mode: "create"  # or "append"
```

**List Directory**:
```
mcp_tool: filesystem_list
  path: "/home/eirikr/Playground/minix-analysis/docs"
  recursive: true
Result: Directory listing
```

### 2. Search and Grep

**Search Content**:
```
mcp_tool: grep_search
  pattern: "syscall"
  path: "/home/eirikr/Playground/minix-analysis/docs"
  glob_pattern: "*.md"
Result: Matching lines with context
```

**Find Files**:
```
mcp_tool: file_find
  pattern: "MINIX*.md"
  path: "/home/eirikr/Playground/minix-analysis"
Result: Matching file paths
```

### 3. Code Execution

**Run Python Script**:
```
mcp_tool: python_exec
  script: "tools/minix_source_analyzer.py"
  args: ["--output", "/tmp/analysis"]
Result: Script output
```

**Execute Commands**:
```
mcp_tool: shell_exec
  command: "ls -la docs/"
  timeout: 5000
Result: Command output
```

### 4. Git Operations

**Commit Changes**:
```
mcp_tool: git_commit
  message: "docs: consolidate architecture documentation"
  files: ["docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md"]
```

**View Status**:
```
mcp_tool: git_status
Result: Current git status
```

---

## Usage Patterns

### Pattern 1: File Exploration

```
1. List directory structure
   → filesystem_list("/path/to/docs")

2. Read specific files of interest
   → filesystem_read("/path/to/file.md")

3. Search for keywords
   → grep_search("architecture", "/path/to/docs", "*.md")

4. Navigate results
   → Read matching files one by one
```

### Pattern 2: Documentation Maintenance

```
1. Verify documentation consistency
   → grep_search("TODO|FIXME", "/path/to/docs")

2. Update cross-references
   → Read affected files
   → filesystem_write with updated links

3. Commit changes
   → git_commit("docs: update cross-references")
```

### Pattern 3: Code Analysis

```
1. Search for code patterns
   → grep_search("syscall.*handler", "/path/to/kernel")

2. Extract relevant sections
   → filesystem_read with specific lines

3. Generate analysis document
   → filesystem_write analysis results
```

### Pattern 4: Performance Analysis

```
1. Run profiler
   → python_exec("tools/boot-profiler.py")

2. Parse results
   → Read output files
   → grep_search("Phase", results)

3. Generate report
   → filesystem_write summary
   → git_commit with results
```

---

## Performance Characteristics

### Tool Latency

| Operation | Typical Time | Range |
|-----------|--------------|-------|
| File read (small) | 50-100 ms | 10-500 ms |
| File read (large) | 200-1000 ms | 100-5000 ms |
| Grep search | 100-500 ms | 50-2000 ms |
| Python execution | 500-5000 ms | 100-30000 ms |
| Git operation | 100-500 ms | 50-2000 ms |

### Scalability Limits

- **File size**: Up to 10 MB (practical limit)
- **Directory depth**: No limit (but slower with depth)
- **Search scope**: Up to 1000 files
- **Concurrent operations**: 5-10 parallel

### Performance Optimization Tips

1. **Limit Search Scope**: Use glob patterns to reduce files
2. **Cache Results**: Store frequently accessed data locally
3. **Batch Operations**: Combine multiple reads into one operation
4. **Stream Large Files**: Read in chunks rather than all at once

---

## Troubleshooting

### Issue 1: MCP Server Won't Start

**Symptom**: "MCP server connection failed"

**Solutions**:
1. Verify installation: `claude version`
2. Check configuration: `cat ~/.claude/mcp.json`
3. Enable debug logging: `export MCP_DEBUG=1`
4. Restart Claude Code: Close and reopen

### Issue 2: File Operations Fail

**Symptom**: "Permission denied" or "File not found"

**Solutions**:
1. Verify file exists: `ls -la /path/to/file`
2. Check permissions: `chmod 644 file` (readable)
3. Verify path format: Use absolute paths, not relative
4. Check MCP server config: Ensure path is correct

### Issue 3: Grep Search Returns No Results

**Symptom**: "No matches found" for known pattern

**Solutions**:
1. Verify pattern syntax: Use regex, not wildcards
2. Check glob pattern: Ensure it matches files
3. Use literal search: For special characters
4. Test grep manually: `grep -r "pattern" /path`

### Issue 4: Slow Performance

**Symptom**: Operations taking > 10 seconds

**Solutions**:
1. Reduce search scope: Use more specific glob patterns
2. Check file sizes: Large files (> 1 MB) slow down
3. Limit directory depth: Search specific subdirectories
4. Monitor resources: Check system CPU/memory
5. Restart server: `mcp restart`

### Issue 5: Memory Usage High

**Symptom**: Claude Code memory usage growing

**Solutions**:
1. Clear cache: `/mcp clear_cache`
2. Reduce concurrent operations: Run sequentially
3. Restart periodically: Frees unused memory
4. Monitor with: `top -p $(pgrep -f 'claude')`

---

## Validation Checklist

### Pre-Deployment Validation

- [ ] MCP server starts without errors
- [ ] File read operations work
- [ ] File write operations work
- [ ] Search/grep operations return results
- [ ] Python execution succeeds
- [ ] Git operations execute
- [ ] No permission errors on file access
- [ ] Configuration file is valid JSON
- [ ] Environment variables set correctly

### Functional Validation

```bash
# Test file read
claude mcp test read "/home/eirikr/Playground/minix-analysis/docs/INDEX.md"
# Expected: File contents displayed

# Test grep search
claude mcp test search "architecture" "/home/eirikr/Playground/minix-analysis/docs"
# Expected: Matching files listed

# Test directory list
claude mcp test list "/home/eirikr/Playground/minix-analysis/docs"
# Expected: Directory contents shown

# Check MCP status
claude mcp status
# Expected: All servers running
```

### Performance Validation

```bash
# Measure read speed
time claude mcp test read large_file.md

# Measure search speed
time claude mcp test search "keyword" /path

# Monitor resource usage
top -p $(pgrep -f 'claude')
```

---

## Best Practices

### 1. Use Glob Patterns Effectively

**Good**:
```
grep_search("pattern", "/path/to/docs", "*.md")
# Only searches .md files
```

**Avoid**:
```
grep_search("pattern", "/home/eirikr")
# Searches entire home directory
```

### 2. Batch Related Operations

**Good**:
```
1. Read file A
2. Read file B
3. Read file C
4. Process all together
```

**Avoid**:
```
1. Read A, process
2. Read B, process
3. Read C, process
# Slower due to overhead
```

### 3. Cache Frequently Used Data

**Good**:
```
results = grep_search("architecture", "/docs")
# Use 'results' multiple times
```

**Avoid**:
```
# Repeat search each time
grep_search(...) → Process
grep_search(...) → Process
grep_search(...) → Process
```

### 4. Use Relative Paths When Possible

**Good**:
```
path: "./docs/INDEX.md"
# Relative to project root
```

**Avoid**:
```
path: "/home/eirikr/Playground/minix-analysis/docs/INDEX.md"
# Absolute, less portable
```

### 5. Enable Logging for Debugging

```bash
# During development
export MCP_DEBUG=1
export MCP_LOG_LEVEL=DEBUG

# View logs
tail -f ~/.claude/mcp.log
```

---

## References

### Source Files Consolidated

- MCP-CRITICAL-DISCOVERY-REPORT.md
- MCP-DOCUMENTATION-INDEX.md
- MCP-EXECUTION-STATUS-2025-11-01.md
- MCP-QUICK-REFERENCE.md
- MCP-SESSION-SUMMARY-2025-11-01.md
- MCP-SUMMARY.md
- MCP-TROUBLESHOOTING-AND-FIXES.md
- MCP-VALIDATION-AND-READY-TO-TEST.md
- FINAL-MCP-STATUS.md

### Official Documentation

- **MCP Specification**: https://docs.anthropic.com/mcp
- **Claude Code Docs**: https://docs.claude.com/claude-code
- **GitHub MCP Repository**: https://github.com/anthropics/mcp

### Related MINIX Documentation

- [Architecture Complete](../Architecture/MINIX-ARCHITECTURE-COMPLETE.md)
- [Boot Sequence Analysis](../Analysis/BOOT-SEQUENCE-ANALYSIS.md)
- [Performance Guide](COMPREHENSIVE-PROFILING-GUIDE.md)

---

## Document Metadata

**Consolidated From:**
- MCP-CRITICAL-DISCOVERY-REPORT.md
- MCP-DOCUMENTATION-INDEX.md
- MCP-EXECUTION-STATUS-2025-11-01.md
- MCP-QUICK-REFERENCE.md
- MCP-SESSION-SUMMARY-2025-11-01.md
- MCP-SUMMARY.md
- MCP-TROUBLESHOOTING-AND-FIXES.md
- MCP-VALIDATION-AND-READY-TO-TEST.md
- FINAL-MCP-STATUS.md

**Total Source**: 1,800+ lines
**Consolidated**: November 1, 2025
**Format**: Markdown with comprehensive sectioning
**Audience**: Claude Code users, developers, researchers

---

*Last Updated: November 1, 2025*
*Status: Phase 2B Consolidation - MCP Integration*
*Next Phase: Audit consolidation and cross-reference updates*
