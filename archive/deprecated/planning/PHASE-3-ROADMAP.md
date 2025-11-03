# Phase 3: MCP Integration - Detailed Roadmap

**Project**: MINIX CPU Interface Analysis
**Phase**: 3 of 4 (MCP Integration)
**Timeline**: Estimated 2-3 weeks
**Status**: Planning Complete, Ready for Implementation

---

## Executive Summary

Phase 3 implements **Model Context Protocol (MCP) servers** to expose MINIX analysis capabilities, source code access, and documentation to AI assistants. This creates a standardized, extensible interface for querying the MINIX architecture, analyzing code patterns, and accessing project knowledge.

**Key Deliverables**:
1. Custom `minix-analysis-mcp` server (Python SDK)
2. `minix-filesystem-mcp` server for codebase access
3. DeepWiki MCP integration for online documentation
4. Unified MCP configuration for Claude Desktop, Cursor, and other MCP hosts

---

## Research Foundation (Web Search Results)

### MCP Architecture (2025 State)

**Protocol**: Open standard by Anthropic (November 2024), adopted by OpenAI (March 2025), Google DeepMind (April 2025)

**Architecture**: Client-server model similar to Language Server Protocol (LSP)
- **MCP Hosts**: AI applications (Claude Desktop, Cursor, ChatGPT)
- **MCP Clients**: Intermediaries maintaining secure connections
- **MCP Servers**: Lightweight programs providing specific functionalities

**Core Primitives**:
- **Resources**: Structured data included in LLM context (files, analysis results)
- **Tools**: Executable functions LLMs can call (analyze_syscall, query_architecture)
- **Prompts**: Instruction templates for common queries

**Communication**: JSON-RPC messages over stdio, SSE, or HTTP transports

**SDKs Available**: Python, TypeScript, C#, Java (official implementations)

### Implementation Best Practices

**Language Choice**:
- **Python**: FastMCP (official MCP Python SDK) - recommended for MINIX analysis (ctags, graph generation already in Python)
- **TypeScript**: Express + official TypeScript SDK - considered for future web-based tools

**Critical Patterns**:
- Tools registered before `connect()` call
- Logging to `stderr` or file (never stdout - corrupts stdio transport)
- OAuth/auth management for production
- Request retry logic and comprehensive error handling
- Sub-50ms cold start targets for real-time interactions

**Production Considerations**:
- Caching strategies for frequently accessed data
- Monitoring: request volumes, latencies, errors
- Integration tests against `/capabilities` and `/run` endpoints
- Minimal response times (<100ms ideal) for real-time UX

---

## Phase 3.1: Planning & Setup (Week 1, Days 1-2)

### 3.1.1: Environment Setup ✓ REQUIRED

**Goal**: Configure Python MCP SDK and development environment

**Tasks**:
```bash
# Install official MCP Python SDK
pip install mcp

# Alternative: FastMCP (now part of official SDK)
pip install fastmcp

# Development dependencies
pip install pytest pytest-asyncio black mypy

# Create project structure
mkdir -p mcp-servers/minix-analysis
mkdir -p mcp-servers/minix-filesystem
mkdir -p mcp-servers/tests
```

**Deliverable**: Python virtual environment with MCP SDK installed

---

### 3.1.2: Architecture Design ✓ REQUIRED

**Goal**: Design MCP server architecture and tool interfaces

**Tools to Expose**:
1. **`query_architecture`**: Answer questions about MINIX i386 architecture
   - Input: Natural language question (e.g., "How does SYSCALL work in i386?")
   - Output: Structured answer from MINIX-ARCHITECTURE-SUMMARY.md

2. **`analyze_syscall`**: Analyze specific syscall mechanism
   - Input: Mechanism name ("INT", "SYSENTER", "SYSCALL")
   - Output: Flow diagram reference, register usage, performance data

3. **`search_symbols`**: Search extracted symbols from Phase 1
   - Input: Symbol name pattern (regex)
   - Output: Symbol definitions, file locations, call relationships

4. **`generate_call_graph`**: Generate call graph for specified files
   - Input: File pattern (e.g., "mpx.S", "protect.c")
   - Output: DOT format graph, node/edge counts

5. **`get_paging_info`**: Retrieve i386 paging architecture details
   - Input: None or specific topic ("CR3", "PDE", "TLB")
   - Output: Structured paging information with constants

6. **`list_diagrams`**: List available TikZ diagrams
   - Input: Optional filter (category)
   - Output: Diagram metadata (filename, title, size, description)

**Resources to Expose**:
1. `file://architecture-summary` → MINIX-ARCHITECTURE-SUMMARY.md
2. `file://phase-1-complete` → PHASE-1-COMPLETE.md
3. `file://phase-2-complete` → PHASE-2-COMPLETE.md
4. `analysis://symbols` → symbols.json (Phase 1 output)
5. `analysis://call-graph` → call_graph.json (Phase 1 output)
6. `diagram://syscall-int` → 05-syscall-int-flow.pdf metadata
7. `diagram://syscall-sysenter` → 06-syscall-sysenter-flow.pdf metadata
8. `diagram://syscall-syscall` → 07-syscall-syscall-flow.pdf metadata
9. `diagram://paging` → 08-page-table-hierarchy.pdf metadata

**Prompts to Expose**:
1. `analyze-syscall-mechanism`: Template for analyzing syscall flows
2. `explain-paging`: Template for explaining i386 paging concepts
3. `trace-call-path`: Template for tracing function call chains

**Deliverable**: `mcp-servers/ARCHITECTURE.md` design document

---

## Phase 3.2: MINIX Analysis MCP Server (Week 1, Days 3-7)

### 3.2.1: Basic Server Implementation ✓ CRITICAL

**Goal**: Create functional MCP server with core tools

**Implementation** (`mcp-servers/minix-analysis/server.py`):
```python
#!/usr/bin/env python3
"""MINIX Analysis MCP Server

Provides tools and resources for querying MINIX i386 architecture,
analyzing syscall mechanisms, and accessing project documentation.
"""

import asyncio
import json
from pathlib import Path
from typing import Any
import mcp.server.stdio
import mcp.types as types

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT
ANALYSIS_DIR = PROJECT_ROOT / "analysis" / "output"
DIAGRAMS_DIR = PROJECT_ROOT / "latex" / "figures"

# Load architecture summary once at startup
ARCHITECTURE_SUMMARY = (DOCS_DIR / "MINIX-ARCHITECTURE-SUMMARY.md").read_text()

server = mcp.server.Server("minix-analysis")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available analysis tools."""
    return [
        types.Tool(
            name="query_architecture",
            description="Query MINIX i386 architecture details",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about MINIX architecture"
                    }
                },
                "required": ["question"]
            }
        ),
        types.Tool(
            name="analyze_syscall",
            description="Analyze specific syscall mechanism (INT, SYSENTER, SYSCALL)",
            inputSchema={
                "type": "object",
                "properties": {
                    "mechanism": {
                        "type": "string",
                        "enum": ["INT", "SYSENTER", "SYSCALL"],
                        "description": "Syscall mechanism to analyze"
                    }
                },
                "required": ["mechanism"]
            }
        ),
        types.Tool(
            name="search_symbols",
            description="Search extracted symbols from MINIX source code",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Symbol name pattern (supports regex)"
                    },
                    "kind": {
                        "type": "string",
                        "enum": ["function", "variable", "label", "macro", "all"],
                        "description": "Symbol type filter"
                    }
                },
                "required": ["pattern"]
            }
        ),
        types.Tool(
            name="get_paging_info",
            description="Get i386 paging architecture information",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["overview", "CR3", "PDE", "PTE", "TLB", "constants"],
                        "description": "Specific paging topic (optional)"
                    }
                }
            }
        ),
        types.Tool(
            name="list_diagrams",
            description="List available TikZ/PGFPlots diagrams",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["syscall", "memory", "performance", "all"],
                        "description": "Diagram category filter"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle tool execution."""

    if name == "query_architecture":
        question = arguments["question"].lower()

        # Simple keyword matching for demo - real implementation would use
        # embedding-based search or LLM-powered Q&A
        relevant_sections = []

        if "syscall" in question or "system call" in question:
            relevant_sections.append(extract_section(ARCHITECTURE_SUMMARY,
                "## System Call Mechanisms"))

        if "paging" in question or "page table" in question:
            relevant_sections.append(extract_section(ARCHITECTURE_SUMMARY,
                "## Memory Management"))

        if "register" in question:
            relevant_sections.append(extract_section(ARCHITECTURE_SUMMARY,
                "## i386 Register Set"))

        if not relevant_sections:
            # Return overview if no specific match
            relevant_sections.append(extract_section(ARCHITECTURE_SUMMARY,
                "## Supported Architectures"))

        return [types.TextContent(
            type="text",
            text="\n\n".join(relevant_sections)
        )]

    elif name == "analyze_syscall":
        mechanism = arguments["mechanism"]

        # Extract relevant section from architecture summary
        section_map = {
            "INT": "### 1. INT (Software Interrupt)",
            "SYSENTER": "### 2. SYSENTER (Intel Fast Path)",
            "SYSCALL": "### 3. SYSCALL (AMD/Intel, 32-bit mode)"
        }

        section = extract_section(ARCHITECTURE_SUMMARY, section_map[mechanism])

        # Add diagram reference
        diagram_map = {
            "INT": "05-syscall-int-flow.pdf",
            "SYSENTER": "06-syscall-sysenter-flow.pdf",
            "SYSCALL": "07-syscall-syscall-flow.pdf"
        }

        diagram_path = DIAGRAMS_DIR / diagram_map[mechanism]
        diagram_info = f"\n\n**Diagram**: {diagram_path} ({diagram_path.stat().st_size // 1024} KB)"

        return [types.TextContent(
            type="text",
            text=section + diagram_info
        )]

    elif name == "search_symbols":
        pattern = arguments["pattern"]
        kind = arguments.get("kind", "all")

        # Load symbols.json from Phase 1 output
        symbols_file = ANALYSIS_DIR / "symbols.json"
        if not symbols_file.exists():
            return [types.TextContent(
                type="text",
                text="Error: symbols.json not found. Run Phase 1 analysis first."
            )]

        symbols = json.loads(symbols_file.read_text())

        # Simple pattern matching - real implementation would use regex
        import re
        pattern_re = re.compile(pattern, re.IGNORECASE)

        matches = []
        for symbol in symbols:
            if kind != "all" and symbol["kind"] != kind:
                continue
            if pattern_re.search(symbol["name"]):
                matches.append(symbol)

        if not matches:
            return [types.TextContent(
                type="text",
                text=f"No symbols matching '{pattern}' (kind={kind})"
            )]

        # Format results
        result = f"Found {len(matches)} symbols matching '{pattern}':\n\n"
        for sym in matches[:20]:  # Limit to first 20
            result += f"- **{sym['name']}** ({sym['kind']})\n"
            result += f"  File: {sym['file']}:{sym['line']}\n"
            if sym.get('signature'):
                result += f"  Signature: `{sym['signature']}`\n"
            result += "\n"

        if len(matches) > 20:
            result += f"\n... and {len(matches) - 20} more matches"

        return [types.TextContent(type="text", text=result)]

    elif name == "get_paging_info":
        topic = arguments.get("topic", "overview")

        section_map = {
            "overview": "## Memory Management (i386)",
            "CR3": "**CR3 Register**:",
            "PDE": "### Page Directory Entry (PDE) Format",
            "PTE": "### Page Table Entry (PTE) Format",
            "TLB": "## TLB (Translation Lookaside Buffer)",
            "constants": "**Key Constants**"
        }

        section = extract_section(ARCHITECTURE_SUMMARY, section_map[topic])

        return [types.TextContent(type="text", text=section)]

    elif name == "list_diagrams":
        category = arguments.get("category", "all")

        diagrams = []

        if category in ["syscall", "all"]:
            diagrams.extend([
                {"name": "05-syscall-int-flow.pdf", "title": "INT Syscall Flow",
                 "category": "syscall", "size_kb": 180},
                {"name": "06-syscall-sysenter-flow.pdf", "title": "SYSENTER Flow",
                 "category": "syscall", "size_kb": 180},
                {"name": "07-syscall-syscall-flow.pdf", "title": "SYSCALL Flow (i386)",
                 "category": "syscall", "size_kb": 192}
            ])

        if category in ["memory", "all"]:
            diagrams.extend([
                {"name": "08-page-table-hierarchy.pdf", "title": "i386 2-Level Paging",
                 "category": "memory", "size_kb": 168},
                {"name": "09-tlb-architecture.pdf", "title": "TLB Architecture",
                 "category": "memory", "size_kb": 196}
            ])

        if category in ["performance", "all"]:
            diagrams.extend([
                {"name": "10-syscall-performance.pdf", "title": "Syscall Performance",
                 "category": "performance", "size_kb": 168},
                {"name": "11-context-switch-cost.pdf", "title": "Context Switch Cost",
                 "category": "performance", "size_kb": 176}
            ])

        result = f"Available diagrams (category={category}):\n\n"
        for d in diagrams:
            result += f"- **{d['title']}**\n"
            result += f"  File: latex/figures/{d['name']} ({d['size_kb']} KB)\n"
            result += f"  Category: {d['category']}\n\n"

        return [types.TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")

def extract_section(text: str, heading: str) -> str:
    """Extract section from markdown document by heading."""
    lines = text.split("\n")
    section_lines = []
    capturing = False
    heading_level = heading.count("#")

    for line in lines:
        if line.startswith(heading):
            capturing = True
            section_lines.append(line)
            continue

        if capturing:
            # Stop at next heading of same or higher level
            if line.startswith("#"):
                current_level = len(line) - len(line.lstrip("#"))
                if current_level <= heading_level:
                    break
            section_lines.append(line)

    return "\n".join(section_lines).strip()

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available documentation resources."""
    return [
        types.Resource(
            uri="file://architecture-summary",
            name="MINIX i386 Architecture Summary",
            description="Comprehensive reference: registers, syscalls, paging, TLB",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="file://phase-1-complete",
            name="Phase 1: Core Infrastructure",
            description="Symbol extraction, call graph generation pipeline",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="file://phase-2-complete",
            name="Phase 2: Enhanced Diagrams",
            description="TikZ/PGFPlots visualization documentation",
            mimeType="text/markdown"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content."""
    resource_map = {
        "file://architecture-summary": DOCS_DIR / "MINIX-ARCHITECTURE-SUMMARY.md",
        "file://phase-1-complete": DOCS_DIR / "PHASE-1-COMPLETE.md",
        "file://phase-2-complete": DOCS_DIR / "PHASE-2-COMPLETE.md"
    }

    if uri not in resource_map:
        raise ValueError(f"Unknown resource: {uri}")

    return resource_map[uri].read_text()

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**Deliverable**: Working MCP server with 5 tools, 3 resources

---

### 3.2.2: Testing & Validation ✓ CRITICAL

**Goal**: Verify MCP server functionality and compliance

**Test Suite** (`mcp-servers/tests/test_minix_analysis.py`):
```python
import pytest
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@pytest.mark.asyncio
async def test_server_capabilities():
    """Test server capability discovery."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-servers/minix-analysis/server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test tools
            tools = await session.list_tools()
            assert len(tools) == 5
            assert any(t.name == "query_architecture" for t in tools)

            # Test resources
            resources = await session.list_resources()
            assert len(resources) == 3

@pytest.mark.asyncio
async def test_query_architecture():
    """Test architecture query tool."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-servers/minix-analysis/server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "query_architecture",
                {"question": "How does SYSCALL work in i386?"}
            )

            assert "SYSCALL" in result[0].text
            assert "ECX" in result[0].text

@pytest.mark.asyncio
async def test_analyze_syscall():
    """Test syscall analysis tool."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-servers/minix-analysis/server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for mechanism in ["INT", "SYSENTER", "SYSCALL"]:
                result = await session.call_tool(
                    "analyze_syscall",
                    {"mechanism": mechanism}
                )
                assert mechanism in result[0].text
```

**Run Tests**:
```bash
cd /home/eirikr/Playground/minix-cpu-analysis
pytest mcp-servers/tests/ -v
```

**Deliverable**: Passing test suite, verified tool functionality

---

## Phase 3.3: MINIX Filesystem MCP Server (Week 2, Days 1-3)

### 3.3.1: Filesystem Server Implementation ✓ RECOMMENDED

**Goal**: Provide read-only access to MINIX source code via MCP

**Why**: Allows AI to directly read MINIX kernel source files during analysis

**Implementation** (`mcp-servers/minix-filesystem/server.py`):
```python
#!/usr/bin/env python3
"""MINIX Filesystem MCP Server

Provides read-only access to MINIX 3.4.0-RC6 source code.
Based on @modelcontextprotocol/server-filesystem pattern.
"""

import asyncio
from pathlib import Path
from typing import Any
import mcp.server.stdio
import mcp.types as types

# MINIX source root
MINIX_ROOT = Path("/home/eirikr/Playground/minix/minix")
ALLOWED_PATHS = [
    MINIX_ROOT / "kernel" / "arch" / "i386",
    MINIX_ROOT / "include" / "arch" / "i386",
]

server = mcp.server.Server("minix-filesystem")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_file",
            description="Read MINIX source file contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from MINIX kernel root"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="list_directory",
            description="List contents of MINIX source directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from MINIX kernel root"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="search_files",
            description="Search for files matching pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., '*.S', 'mpx.*')"
                    },
                    "base_path": {
                        "type": "string",
                        "description": "Base directory to search from"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent]:

    if name == "read_file":
        rel_path = arguments["path"]
        file_path = MINIX_ROOT / rel_path

        # Security: verify path is within allowed directories
        if not any(file_path.is_relative_to(allowed) for allowed in ALLOWED_PATHS):
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied. Path must be within allowed directories."
            )]

        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"Error: File not found: {rel_path}"
            )]

        content = file_path.read_text()
        return [types.TextContent(
            type="text",
            text=f"File: {rel_path}\n\n```\n{content}\n```"
        )]

    elif name == "list_directory":
        rel_path = arguments["path"]
        dir_path = MINIX_ROOT / rel_path

        if not any(dir_path.is_relative_to(allowed) for allowed in ALLOWED_PATHS):
            return [types.TextContent(
                type="text",
                text="Error: Access denied."
            )]

        if not dir_path.exists() or not dir_path.is_dir():
            return [types.TextContent(
                type="text",
                text=f"Error: Directory not found: {rel_path}"
            )]

        entries = []
        for item in sorted(dir_path.iterdir()):
            entry_type = "DIR" if item.is_dir() else "FILE"
            size = f"({item.stat().st_size} bytes)" if item.is_file() else ""
            entries.append(f"[{entry_type}] {item.name} {size}")

        return [types.TextContent(
            type="text",
            text=f"Directory: {rel_path}\n\n" + "\n".join(entries)
        )]

    elif name == "search_files":
        pattern = arguments["pattern"]
        base_path = arguments.get("base_path", "")
        search_path = MINIX_ROOT / base_path

        matches = []
        for allowed in ALLOWED_PATHS:
            if search_path.is_relative_to(allowed) or allowed.is_relative_to(search_path):
                for match in allowed.rglob(pattern):
                    if match.is_file():
                        rel = match.relative_to(MINIX_ROOT)
                        matches.append(str(rel))

        result = f"Found {len(matches)} files matching '{pattern}':\n\n"
        for m in sorted(matches)[:50]:
            result += f"- {m}\n"

        if len(matches) > 50:
            result += f"\n... and {len(matches) - 50} more matches"

        return [types.TextContent(type="text", text=result)]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**Deliverable**: Filesystem MCP server with read-only MINIX source access

---

### 3.3.2: Integration with DeepWiki MCP ✓ OPTIONAL

**Goal**: Add online MINIX documentation access via existing DeepWiki MCP server

**Configuration** (add to Claude Desktop `~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "deepwiki": {
      "command": "npx",
      "args": ["-y", "mcp-deepwiki@latest"]
    }
  }
}
```

**Usage Example**:
```
User: "Fetch latest MINIX documentation from DeepWiki"
Claude: [Uses deepwiki_fetch tool with URL https://wiki.minix3.org]
```

**Deliverable**: DeepWiki MCP integrated and tested

---

## Phase 3.4: MCP Client Configuration (Week 2, Days 4-5)

### 3.4.1: Claude Desktop Configuration ✓ REQUIRED

**Goal**: Configure Claude Desktop to use custom MCP servers

**Configuration File**: `~/.config/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "minix-analysis": {
      "command": "python",
      "args": [
        "/home/eirikr/Playground/minix-cpu-analysis/mcp-servers/minix-analysis/server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/eirikr/Playground/minix-cpu-analysis"
      }
    },
    "minix-filesystem": {
      "command": "python",
      "args": [
        "/home/eirikr/Playground/minix-cpu-analysis/mcp-servers/minix-filesystem/server.py"
      ]
    },
    "deepwiki": {
      "command": "npx",
      "args": ["-y", "mcp-deepwiki@latest"]
    }
  }
}
```

**Verification**:
1. Restart Claude Desktop
2. Check MCP server status in settings
3. Test tool availability: "List available MINIX analysis tools"
4. Test resource access: "Show me the MINIX architecture summary"

**Deliverable**: Working Claude Desktop configuration

---

### 3.4.2: Cursor IDE Configuration ✓ OPTIONAL

**Goal**: Enable MCP servers in Cursor for in-editor AI assistance

**Configuration File**: `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project)
```json
{
  "mcpServers": {
    "minix-analysis": {
      "command": "python",
      "args": [
        "/home/eirikr/Playground/minix-cpu-analysis/mcp-servers/minix-analysis/server.py"
      ]
    },
    "minix-filesystem": {
      "command": "python",
      "args": [
        "/home/eirikr/Playground/minix-cpu-analysis/mcp-servers/minix-filesystem/server.py"
      ]
    }
  }
}
```

**Deliverable**: Cursor configuration with MCP support

---

## Phase 3.5: Documentation & Testing (Week 2, Days 6-7)

### 3.5.1: Comprehensive Testing ✓ REQUIRED

**Test Coverage**:
- Unit tests: All tools and resources
- Integration tests: End-to-end MCP client-server communication
- Performance tests: Response time <100ms for simple queries
- Error handling: Invalid inputs, missing files, permission errors

**Test Execution**:
```bash
# Unit tests
pytest mcp-servers/tests/ -v --cov=mcp-servers

# Integration tests with actual MCP client
python mcp-servers/tests/integration_test.py

# Performance benchmarks
python mcp-servers/tests/benchmark.py
```

**Success Criteria**:
- All tests passing
- 90%+ code coverage
- Sub-100ms median response time
- Zero critical security issues

**Deliverable**: Complete test suite with CI/CD integration

---

### 3.5.2: User Documentation ✓ REQUIRED

**Create**: `mcp-servers/README.md`

**Content**:
1. **Overview**: What the MCP servers provide
2. **Installation**: Step-by-step setup guide
3. **Configuration**: Claude Desktop, Cursor, other MCP hosts
4. **Tool Reference**: Complete API documentation for all tools
5. **Resource Reference**: Available resources and URIs
6. **Examples**: Common usage patterns and workflows
7. **Troubleshooting**: Common issues and solutions
8. **Development**: Contributing guide, testing, debugging

**Create**: `mcp-servers/EXAMPLES.md`

**Content**:
- Example 1: "Analyze SYSCALL mechanism with MCP"
- Example 2: "Search for specific kernel function"
- Example 3: "Generate call graph for mpx.S"
- Example 4: "Query paging architecture details"
- Example 5: "List and reference diagrams"

**Deliverable**: Complete MCP server documentation

---

## Phase 3.6: Advanced Features (Week 3, Optional)

### 3.6.1: Caching Layer ✓ PERFORMANCE

**Goal**: Cache frequently accessed data for sub-50ms responses

**Implementation**:
```python
from functools import lru_cache
import hashlib

# Cache architecture summary sections
@lru_cache(maxsize=128)
def get_cached_section(heading: str) -> str:
    return extract_section(ARCHITECTURE_SUMMARY, heading)

# Cache symbol lookups
symbol_cache = {}

def search_symbols_cached(pattern: str, kind: str):
    cache_key = hashlib.md5(f"{pattern}:{kind}".encode()).hexdigest()
    if cache_key in symbol_cache:
        return symbol_cache[cache_key]

    result = search_symbols(pattern, kind)
    symbol_cache[cache_key] = result
    return result
```

**Deliverable**: 50%+ faster response times for repeated queries

---

### 3.6.2: Monitoring & Observability ✓ PRODUCTION

**Goal**: Track MCP server performance and usage

**Implementation**:
```python
import time
import logging
from collections import defaultdict

# Request metrics
request_count = defaultdict(int)
request_latency = defaultdict(list)

async def handle_call_tool_instrumented(name, arguments):
    start = time.time()
    request_count[name] += 1

    try:
        result = await handle_call_tool(name, arguments)
        latency = (time.time() - start) * 1000  # ms
        request_latency[name].append(latency)

        logging.info(f"Tool {name} completed in {latency:.2f}ms")
        return result

    except Exception as e:
        logging.error(f"Tool {name} failed: {e}")
        raise

# Metrics endpoint (via tool)
@server.call_tool()
async def get_metrics():
    metrics = {}
    for tool_name in request_count:
        latencies = request_latency[tool_name]
        metrics[tool_name] = {
            "count": request_count[tool_name],
            "avg_latency_ms": sum(latencies) / len(latencies),
            "p50_latency_ms": sorted(latencies)[len(latencies)//2],
            "p95_latency_ms": sorted(latencies)[int(len(latencies)*0.95)]
        }
    return metrics
```

**Deliverable**: Metrics collection and performance monitoring

---

### 3.6.3: Web Interface (Optional) ✓ FUTURE

**Goal**: Provide web-based MCP server testing and documentation

**Implementation**: FastAPI web server exposing MCP tools via HTTP
- SSE transport for streaming responses
- Interactive API documentation (Swagger UI)
- Real-time metrics dashboard

**Deliverable**: Web-based MCP server interface

---

## Success Metrics

### Phase 3 Complete When:

✅ **Functionality**:
- [ ] minix-analysis MCP server implements all 5 core tools
- [ ] minix-filesystem MCP server provides read-only source access
- [ ] DeepWiki MCP integrated for online documentation
- [ ] All tools tested and validated

✅ **Integration**:
- [ ] Claude Desktop configuration working
- [ ] Cursor IDE configuration working (optional)
- [ ] All MCP servers pass health checks

✅ **Documentation**:
- [ ] Complete README with setup instructions
- [ ] API reference for all tools and resources
- [ ] Example usage patterns documented

✅ **Performance**:
- [ ] <100ms median response time for simple queries
- [ ] <500ms for complex analysis (call graph generation)
- [ ] Caching reduces repeated query latency by 50%+

✅ **Quality**:
- [ ] 90%+ test coverage
- [ ] Zero critical security issues
- [ ] Passing CI/CD pipeline

---

## Timeline Summary

| Week | Phase | Tasks | Deliverables |
|------|-------|-------|--------------|
| 1 (Days 1-2) | 3.1 Planning | Environment setup, architecture design | Python env, ARCHITECTURE.md |
| 1 (Days 3-7) | 3.2 Analysis Server | Implement core server, tools, resources, tests | minix-analysis server |
| 2 (Days 1-3) | 3.3 Filesystem | Implement filesystem server, DeepWiki integration | minix-filesystem server |
| 2 (Days 4-5) | 3.4 Configuration | Claude Desktop, Cursor IDE setup | MCP client configs |
| 2 (Days 6-7) | 3.5 Documentation | Testing, user docs, examples | README, test suite |
| 3 (Optional) | 3.6 Advanced | Caching, monitoring, web interface | Performance improvements |

**Total**: 2-3 weeks for full implementation

---

## Dependencies

**Required**:
- Python 3.10+ with MCP SDK (`pip install mcp`)
- Phase 1 output (symbols.json, call_graph.json)
- Phase 2 documentation (MINIX-ARCHITECTURE-SUMMARY.md)

**Optional**:
- Node.js/NPX for DeepWiki MCP
- Claude Desktop or Cursor IDE for testing
- FastAPI for web interface

---

## Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MCP SDK API changes | High | Low | Pin SDK version, monitor changelog |
| Performance issues (>500ms) | Medium | Medium | Implement caching, optimize queries |
| Security: path traversal | High | Low | Strict path validation, allowlist |
| Integration failures | Medium | Low | Comprehensive testing, CI/CD |

---

## Next Steps After Phase 3

**Phase 4 Integration**:
- MCP servers expose analysis tools to AI assistants
- Wiki generation uses MCP to query architecture dynamically
- Interactive documentation leverages MCP for real-time code exploration

**Continuous Improvement**:
- Add more tools based on user feedback
- Expand resource catalog (more diagrams, analysis outputs)
- Optimize performance with advanced caching strategies

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Status**: Ready for Implementation
**Estimated Effort**: 2-3 weeks (1 developer, full-time)
