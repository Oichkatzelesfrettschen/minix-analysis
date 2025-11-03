# MCP Server API Reference

**Model Context Protocol (MCP) Servers for MINIX Analysis**

---

## Overview

The MINIX Analysis codebase now ships with a reusable MCP façade (`shared/mcp/server/`) that reads pipeline artifacts from `diagrams/data/` and can be surfaced via both CLI helpers and MCP transports. A lightweight CLI layer (`python -m os_analysis_toolkit.cli`) already exposes core functionality (`--list-resources`, `--resource`, `--boot-aspect`, `--syscall`).

For agents requiring a full MCP transport, instantiate `MinixAnalysisServer.from_default_data_dir()` inside your server runtime (e.g., Claude's MCP SDK) and map its methods to MCP tools. Legacy guidance for the historical `minix-mcp-servers` project is retained below until the consolidated server is fully deployed.

### CLI Access (Quick Queries)

The project ships a convenience layer for local exploration:

```bash
# Ensure repo package is discoverable
export PYTHONPATH=$(pwd)/src

# List every dataset emitted by `make pipeline`
python -m os_analysis_toolkit.cli --list-resources

# Inspect a single resource
python -m os_analysis_toolkit.cli --resource kernel_structure
python -m os_analysis_toolkit.cli --resource boot_sequence --boot-aspect critical_path

# Summaries and lookups
python -m os_analysis_toolkit.cli --kernel-summary --top-syscalls 3
python -m os_analysis_toolkit.cli --boot-critical-path
python -m os_analysis_toolkit.cli --syscall do_trace

# Use alternate data directory (e.g., freshly generated artifacts)
python -m os_analysis_toolkit.cli --resource statistics --data-dir path/to/diagrams/data
```

Under the hood these commands rely on `shared/mcp/server/`, so any external MCP transport can reuse the same objects.

---

## Installation

### Prerequisites

```bash
# Python 3.10+
python --version

# Virtual environment (recommended)
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
# Installs: mcp>=1.0.0, pydantic>=2.0.0, pytest>=8.0.0
```

### Verify Installation

```bash
pytest -v
# Expected: 39 passed in ~2 seconds
```

---

## Claude Code Configuration

### Configuration File

**Location**: `~/.claude/mcp.json`

**Full Configuration**:
```json
{
  "mcpServers": {
    "minix-analysis": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/home/eirikr/Playground/pkgbuilds/minix-mcp-servers/servers/minix-analysis",
      "env": {
        "MINIX_DATA_PATH": "/home/eirikr/Playground/minix-analysis",
        "PYTHONPATH": "/home/eirikr/Playground/pkgbuilds/minix-mcp-servers/venv/lib/python3.13/site-packages"
      }
    },
    "minix-filesystem": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/home/eirikr/Playground/pkgbuilds/minix-mcp-servers/servers/minix-filesystem",
      "env": {
        "MINIX_SOURCE_ROOT": "/home/eirikr/Playground/minix",
        "PYTHONPATH": "/home/eirikr/Playground/pkgbuilds/minix-mcp-servers/venv/lib/python3.13/site-packages"
      }
    }
  }
}
```

### Environment Variables

**minix-analysis**:
- `MINIX_DATA_PATH`: Path to minix-analysis project root

**minix-filesystem**:
- `MINIX_SOURCE_ROOT`: Path to MINIX source tree

**Both**:
- `PYTHONPATH`: Path to venv site-packages (for MCP SDK)

---

## Analysis Server

### Overview

**Purpose**: Provide structured access to MINIX CPU interface and boot sequence analysis

**Data Sources**:
- `modules/cpu-interface/docs/MINIX-CPU-INTERFACE-ANALYSIS.md`
- `modules/cpu-interface/docs/ISA-LEVEL-ANALYSIS.md`
- `modules/boot-sequence/docs/FINAL_SYNTHESIS_REPORT.md`

**Tools**: 7 total
**Resources**: 5 total

### Tools

#### 1. query_architecture

**Purpose**: Get i386 architecture details (registers, privilege levels, paging)

**Parameters**:
```typescript
{
  query: string          // Search query (e.g., "registers", "paging", "privilege")
}
```

**Returns**:
```typescript
{
  architecture: string   // i386
  registers: {...}       // GPRs, segment, control registers
  privilege_levels: {...}// Ring 0-3 details
  paging: {...}          // 2-level paging structure
}
```

**Example**:
```json
{
  "query": "privilege levels"
}
```

**Response**:
```json
{
  "architecture": "i386",
  "privilege_levels": {
    "ring_0": "Kernel mode (full hardware access)",
    "ring_3": "User mode (restricted)",
    "transition": "INT, SYSENTER, SYSCALL"
  }
}
```

#### 2. analyze_syscall

**Purpose**: Analyze specific system call mechanism (INT, SYSENTER, SYSCALL)

**Parameters**:
```typescript
{
  mechanism: "INT" | "SYSENTER" | "SYSCALL"
}
```

**Returns**:
```typescript
{
  mechanism: string
  entry_point: string     // Assembly label (e.g., ipc_entry_sysenter)
  file: string            // Source file
  instructions: [...]     // CPU instructions used
  performance: {
    cycles: number        // Average cycle count
    relative: string      // Comparison to other mechanisms
  }
  registers: {...}        // Register usage
}
```

**Example**:
```json
{
  "mechanism": "SYSENTER"
}
```

**Response**:
```json
{
  "mechanism": "SYSENTER",
  "entry_point": "ipc_entry_sysenter",
  "file": "minix/kernel/arch/i386/mpx.S:220",
  "instructions": ["SYSENTER", "SYSEXIT"],
  "performance": {
    "cycles": 1305,
    "relative": "Fastest (26% faster than INT)"
  },
  "registers": {
    "esi": "return ESP",
    "edx": "return EIP"
  }
}
```

#### 3. query_performance

**Purpose**: Retrieve performance benchmarks and metrics

**Parameters**:
```typescript
{
  metric: string   // "syscall" | "tlb" | "context_switch" | "all"
}
```

**Returns**:
```typescript
{
  syscalls: {
    INT: number,
    SYSENTER: number,
    SYSCALL: number
  },
  tlb: {
    hit: number,
    miss: number
  },
  context_switch: {
    total: number,
    breakdown: {...}
  }
}
```

**Example**:
```json
{
  "metric": "syscall"
}
```

**Response**:
```json
{
  "syscalls": {
    "INT": 1772,
    "SYSENTER": 1305,
    "SYSCALL": 1439
  },
  "comparison": "SYSENTER is fastest (26% faster than INT)"
}
```

#### 4. compare_mechanisms

**Purpose**: Side-by-side comparison of system call mechanisms

**Parameters**:
```typescript
{
  mechanisms: string[]   // ["INT", "SYSENTER", "SYSCALL"]
}
```

**Returns**:
```typescript
{
  comparison: [
    {
      mechanism: string,
      cycles: number,
      advantages: string[],
      disadvantages: string[]
    }
  ]
}
```

#### 5. explain_diagram

**Purpose**: Get textual description of TikZ diagrams

**Parameters**:
```typescript
{
  diagram_id: string   // e.g., "syscall-int-flow", "page-table-hierarchy"
}
```

**Returns**:
```typescript
{
  diagram_id: string,
  title: string,
  description: string,
  components: [...],
  file: string          // LaTeX source file
}
```

#### 6. query_boot_sequence

**Purpose**: Boot topology and phase information

**Parameters**:
```typescript
{
  query: string   // "phases" | "topology" | "critical_path"
}
```

**Returns**:
```typescript
{
  entry_point: "kmain()",
  phases: [
    {
      phase: number,
      name: string,
      entry: string,
      operations: string[]
    }
  ],
  topology: {
    type: "hub-and-spoke",
    hub: "kmain",
    spokes: number
  }
}
```

#### 7. trace_boot_path

**Purpose**: Critical path through boot process

**Parameters**:
```typescript
{
  from: string,      // Start function (e.g., "kmain")
  to: string         // End function (e.g., "switch_to_user")
}
```

**Returns**:
```typescript
{
  path: string[],    // Function call chain
  depth: number,     // Call depth
  critical: boolean  // Is this on critical path?
}
```

### Resources

#### 1. cpu-interface

**URI**: `analysis://cpu-interface/summary`

**Type**: `application/json`

**Content**: Complete CPU interface analysis summary

#### 2. syscalls

**URI**: `analysis://syscalls/mechanisms`

**Type**: `application/json`

**Content**: All system call mechanism details

#### 3. performance

**URI**: `analysis://performance/benchmarks`

**Type**: `application/json`

**Content**: Performance metrics and benchmarks

#### 4. boot-sequence

**URI**: `analysis://boot-sequence/topology`

**Type**: `application/json`

**Content**: Boot sequence call graph and topology

#### 5. diagrams

**URI**: `analysis://diagrams/metadata`

**Type**: `application/json`

**Content**: List of all available diagrams with descriptions

---

## Filesystem Server

### Overview

**Purpose**: Read-only access to MINIX source code with security restrictions

**Allowed Paths**:
- `minix/kernel/` - Kernel source
- `minix/include/` - System headers
- `minix/lib/` - System libraries

**Forbidden Paths**:
- Outside MINIX source tree
- Absolute paths outside allowed directories
- Path traversal attempts (`../../../etc/passwd`)

**Tools**: 3 total

### Tools

#### 1. read_file

**Purpose**: Read file contents with line limits

**Parameters**:
```typescript
{
  path: string,       // Relative path from MINIX_SOURCE_ROOT
  offset?: number,    // Start line (default: 0)
  limit?: number      // Max lines (default: 1000)
}
```

**Returns**:
```typescript
{
  path: string,
  content: string,    // File contents
  lines: number,      // Total lines in file
  truncated: boolean  // If limit was applied
}
```

**Security**:
- ✅ Path must be within allowed directories
- ✅ No path traversal (`..` components)
- ✅ No absolute paths to sensitive files
- ✅ Error on access denied (clear security message)

**Example**:
```json
{
  "path": "minix/kernel/arch/i386/mpx.S",
  "offset": 220,
  "limit": 50
}
```

**Response**:
```json
{
  "path": "minix/kernel/arch/i386/mpx.S",
  "content": "ipc_entry_sysenter:\n    movl    %esp, %eax\n...",
  "lines": 50,
  "truncated": false
}
```

#### 2. list_directory

**Purpose**: Browse kernel/include directories

**Parameters**:
```typescript
{
  path: string,       // Directory path
  recursive?: boolean,// Recurse subdirectories (default: false)
  max_depth?: number  // Max recursion depth (default: 3)
}
```

**Returns**:
```typescript
{
  path: string,
  entries: [
    {
      name: string,
      type: "file" | "directory",
      size?: number,   // File size in bytes
      path: string     // Full relative path
    }
  ]
}
```

**Security**:
- ✅ Same path restrictions as read_file
- ✅ Max depth limit prevents infinite recursion
- ✅ No symlink following outside allowed paths

**Example**:
```json
{
  "path": "minix/kernel/arch/i386",
  "recursive": true,
  "max_depth": 2
}
```

#### 3. search_files

**Purpose**: Pattern-based file search

**Parameters**:
```typescript
{
  pattern: string,    // Filename pattern (glob)
  directory?: string, // Search root (default: "minix/kernel")
  max_results?: number// Limit results (default: 100)
}
```

**Returns**:
```typescript
{
  pattern: string,
  matches: [
    {
      path: string,
      size: number,
      modified: string  // ISO 8601 timestamp
    }
  ],
  total: number,
  truncated: boolean
}
```

**Example**:
```json
{
  "pattern": "*.S",
  "directory": "minix/kernel/arch/i386"
}
```

**Response**:
```json
{
  "pattern": "*.S",
  "matches": [
    {"path": "mpx.S", "size": 12345},
    {"path": "apic_asm.S", "size": 8192}
  ],
  "total": 2,
  "truncated": false
}
```

---

## Error Handling

### Common Errors

**Analysis Server**:
```json
{
  "error": "KeyError: 'architecture'",
  "message": "MINIX_DATA_PATH not set or data files not found"
}
```

**Solution**: Check `MINIX_DATA_PATH` environment variable

**Filesystem Server**:
```json
{
  "error": "access denied: path outside allowed directories",
  "path": "/etc/passwd"
}
```

**Solution**: Use paths within `minix/kernel/`, `minix/include/`, `minix/lib/`

### Security Violations

**Path Traversal Attempt**:
```json
{
  "path": "../../../etc/passwd"
}
```

**Response**:
```json
{
  "error": "access denied: path outside allowed directories",
  "reason": "security: no path traversal allowed"
}
```

---

## Testing

### Run All Tests

```bash
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers
source venv/bin/activate
pytest -v
```

**Expected Output**:
```
tests/test_minix_analysis.py::test_data_loader_initialization PASSED
tests/test_minix_analysis.py::test_architecture_data_loading PASSED
... (39 total)
================================ 39 passed in 1.85s ================================
```

### Test Individual Server

**Analysis Server**:
```bash
pytest tests/test_minix_analysis.py -v
# 15 tests
```

**Filesystem Server**:
```bash
pytest tests/test_minix_filesystem.py -v
# 24 tests
```

### Coverage Report

```bash
pytest --cov=servers --cov-report=html
# Open htmlcov/index.html
```

---

## Development

### Project Structure

```
minix-mcp-servers/
├── servers/
│   ├── minix-analysis/
│   │   ├── src/
│   │   │   ├── server.py        # MCP server implementation
│   │   │   ├── data_loader.py   # Data loading logic
│   │   │   └── __init__.py
│   │   └── pyproject.toml
│   └── minix-filesystem/
│       ├── src/
│       │   ├── server.py        # MCP server implementation
│       │   └── __init__.py
│       └── pyproject.toml
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_minix_analysis.py   # Analysis server tests (15)
│   └── test_minix_filesystem.py # Filesystem server tests (24)
├── requirements.txt
└── PKGBUILD                     # Arch Linux package
```

### Adding New Tools

**1. Add tool handler**:
```python
# servers/minix-analysis/src/server.py

@server.call_tool()
async def my_new_tool(query: str) -> list[TextContent]:
    """Tool description for MCP clients."""
    result = process_query(query)
    return [TextContent(type="text", text=json.dumps(result))]
```

**2. Add tests**:
```python
# tests/test_minix_analysis.py

def test_my_new_tool():
    result = my_new_tool("test query")
    assert "expected_key" in result
```

**3. Update documentation**:
- Add to this API reference
- Update tool count in Overview
- Document parameters and return types

---

## Related Documentation

- [Installation Guide](../../INSTALLATION.md)
- [Integration Report](../../INTEGRATION-COMPLETE.md)
- [Contributing Guide](../Contributing.md)
- [Testing Guide](../Testing.md)

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0
**Test Coverage**: 100% (39/39 tests pass)
