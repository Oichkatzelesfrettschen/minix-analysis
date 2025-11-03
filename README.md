# MINIX 3.4 Unified Analysis Environment

This repository provides a comprehensive, unified environment for the analysis, testing, and documentation of the MINIX 3.4 operating system. It integrates source code, analysis tools, boot analyzers, and pedagogical materials into a single, modular framework.

## Overview

This project is a synthesis of several related efforts, providing a powerful and cohesive toolkit for OS developers, researchers, and students. It includes:

- **Complete MINIX Source:** The full MINIX 3.4 source code is included for direct analysis.
- **Source Code Analysis**: Tools to parse, analyze, and extract data from the MINIX kernel and userland.
- **Boot Sequence Analysis:** Specialized tools for tracing, visualizing, and understanding the MINIX boot process.
- **Automated Testing**: A QEMU-based framework for automated boot testing, error detection, and performance profiling.
- **MCP Integration**: Integration with the Model Context Protocol (MCP) for interaction with AI agents.
- **CI/CD Pipeline**: A GitHub Actions workflow for continuous, automated testing.
- **Pedagogical Documentation:** A framework for creating deep, explanatory documentation in the style of the Lions' Commentary.

## Architecture

The repository is organized into a modular structure to separate concerns and improve maintainability.

### Directory Structure
```
minix-analysis/
├── README.md
├── GEMINI.md                     # Gemini agent's operational log
├── Makefile
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── setup.py
│
├── minix-source/                 # The complete MINIX 3.4 OS source code
│
├── src/                          # Python source for analysis tools
│   └── minix_transport/          # MCP transport library
│
├── tools/                        # Analysis tools and scripts
│   ├── minix_source_analyzer.py  # Core source analysis tool
│   ├── tikz_generator.py         # Diagram generation tool
│   ├── triage-minix-errors.py    # Boot log error analysis
│   └── boot-analysis/            # Scripts for boot sequence analysis
│
├── scripts/                      # Automation and high-level task scripts
│   ├── minix-qemu-launcher.sh    # Intelligent QEMU launcher
│   ├── minix-boot-diagnostics.sh # System capability detection
│   └── mcp-docker-setup.sh       # MCP server setup
│
├── docs/                         # Project documentation
│   ├── AGENTS.md                 # Lions' style guide for agents
│   ├── CLAUDE.md                 # Guidance for the Claude agent
│   └── boot-analysis/            # Documentation from the boot analyzer
│
├── artifacts/                    # Generated files (diagrams, reports, etc.)
│   └── boot-analysis/            # Visualizations from the boot analyzer
│
├── mcp/                          # MCP integration files
│   ├── .mcp.json                 # MCP server configuration
│   └── servers/                  # MCP server implementations
│
├── tests/                        # Test suites
│   └── test-minix-mcp.sh         # Main validation test suite
│
├── archive/                      # Archived and miscellaneous files
│
└── .github/workflows/            # CI/CD workflows
    └── minix-ci.yml
```

## Quick Start

### 1. Verify Environment
```bash
bash tests/test-minix-mcp.sh
```

### 2. Configure MCP Servers
```bash
# This step is required for AI agent integration
export GITHUB_TOKEN='ghp_YourToken'  # Optional, for GitHub integration
bash scripts/mcp-docker-setup.sh --auto
```

### 3. Start MCP Services
```bash
# Note: The docker-compose.enhanced.yml is now in archive/misc
# You may need to restore it or use the primary docker-compose.yml
docker-compose up -d
```

## Common Workflows

### Boot MINIX and Analyze Errors

1.  **Run MINIX:**
    ```bash
    bash scripts/minix-qemu-launcher.sh
    ```
2.  **Analyze for errors:** (Assuming the launcher saves a log)
    ```bash
    python3 tools/triage-minix-errors.py boot.log
    ```

### Analyze the MINIX Source Code

1.  **Run the source analyzer:**
    ```bash
    python3 tools/minix_source_analyzer.py --minix-root minix-source/minix --output artifacts/source-analysis
    ```

### Analyze the Boot Process

1.  **Trace the boot sequence:**
    ```bash
    bash tools/boot-analysis/trace_boot_sequence.sh
    ```
2.  **Generate a boot graph:**
    ```bash
    bash tools/boot-analysis/generate_dot_graph.sh
    ```

## Next Steps

This repository has undergone a significant reorganization. The next steps should be:

1.  **Validate all scripts and tools** to ensure they work with the new directory structure.
2.  **Update the CI/CD pipeline** (`.github/workflows/minix-ci.yml`) to reflect the new file locations.
3.  **Perform a full dependency check** to ensure `requirements.txt` is complete.
4.  **Continue the process of harmonization**, looking for more opportunities to unify scripts and configurations.