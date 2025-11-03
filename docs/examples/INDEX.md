# MINIX Examples and Guides - Quick Index

**Purpose**: Quick reference table for all example guides
**Organization Date**: 2025-11-01
**Location**: `/home/eirikr/Playground/minix-analysis/docs/Examples/`

---

## Complete Guide Index

| # | Guide Name | Complexity | Time | Use Case | Source File |
|---|------------|-----------|------|----------|-------------|
| 1 | [MCP Quick Start](MCP-QUICK-START.md) | ⭐⭐ | 5-10 min | Configure Model Context Protocol | START-HERE-MCP-FIXED.md |
| 2 | [Profiling Quick Start](PROFILING-QUICK-START.md) | ⭐⭐ | 5-15 min | Install profiling tools and run first boot profile | README-PROFILING.md |
| 3 | [CLI Execution Guide](CLI-EXECUTION-GUIDE.md) | ⭐⭐⭐ | 20-30 min | Complete CLI workflow for MINIX development | MINIX-CLI-EXECUTION-GUIDE.md |
| 4 | [Runtime Setup Guide](RUNTIME-SETUP-GUIDE.md) | ⭐⭐⭐⭐ | 30-60 min | Set up QEMU or Docker for MINIX 3.4.0-RC6 | MINIX-RUNTIME-SETUP.md |
| 5 | [MCP Integration Guide](MCP-INTEGRATION-GUIDE.md) | ⭐⭐⭐⭐ | 45-90 min | Full MCP server integration with automation | MINIX-MCP-Integration.md |
| 6 | [Profiling Enhancement Guide](PROFILING-ENHANCEMENT-GUIDE.md) | ⭐⭐⭐⭐ | 6-8 hrs | Add granular metrics to boot profiler | PROFILING-ENHANCEMENT-IMPLEMENTATION-GUIDE.md |

---

## By Complexity Level

### Beginner-Intermediate (⭐⭐)

| Guide | Time | Primary Topic | Key Skills |
|-------|------|---------------|------------|
| [MCP Quick Start](MCP-QUICK-START.md) | 5-10 min | MCP Configuration | JSON config, env variables |
| [Profiling Quick Start](PROFILING-QUICK-START.md) | 5-15 min | Boot Profiling | perf, flamegraph, QEMU |

### Intermediate (⭐⭐⭐)

| Guide | Time | Primary Topic | Key Skills |
|-------|------|---------------|------------|
| [CLI Execution Guide](CLI-EXECUTION-GUIDE.md) | 20-30 min | MINIX Development | TAP networking, serial console, bash scripting |

### Advanced (⭐⭐⭐⭐)

| Guide | Time | Primary Topic | Key Skills |
|-------|------|---------------|------------|
| [Runtime Setup Guide](RUNTIME-SETUP-GUIDE.md) | 30-60 min | Environment Setup | QEMU, Docker, ISO installation |
| [MCP Integration Guide](MCP-INTEGRATION-GUIDE.md) | 45-90 min | Automation | MCP servers, Docker compose, GitHub API |
| [Profiling Enhancement Guide](PROFILING-ENHANCEMENT-GUIDE.md) | 6-8 hrs | Advanced Profiling | Python, perf integration, strace, regex |

---

## By Topic

### Profiling and Performance

| Guide | Complexity | Time | Covers |
|-------|-----------|------|--------|
| [Profiling Quick Start](PROFILING-QUICK-START.md) | ⭐⭐ | 5-15 min | perf, flamegraph, basic boot profiling |
| [Profiling Enhancement Guide](PROFILING-ENHANCEMENT-GUIDE.md) | ⭐⭐⭐⭐ | 6-8 hrs | Serial logging, perf integration, strace, unified JSON |

### Environment Setup

| Guide | Complexity | Time | Covers |
|-------|-----------|------|--------|
| [Runtime Setup Guide](RUNTIME-SETUP-GUIDE.md) | ⭐⭐⭐⭐ | 30-60 min | QEMU, Docker, ISO installation, disk images |
| [CLI Execution Guide](CLI-EXECUTION-GUIDE.md) | ⭐⭐⭐ | 20-30 min | TAP networking, serial console, interactive boot |

### Model Context Protocol (MCP)

| Guide | Complexity | Time | Covers |
|-------|-----------|------|--------|
| [MCP Quick Start](MCP-QUICK-START.md) | ⭐⭐ | 5-10 min | Basic MCP config, filesystem and SQLite servers |
| [MCP Integration Guide](MCP-INTEGRATION-GUIDE.md) | ⭐⭐⭐⭐ | 45-90 min | Full integration, Docker, GitHub, automated workflows |

---

## By Use Case

### "I want to profile MINIX boot ASAP"
→ [Profiling Quick Start](PROFILING-QUICK-START.md) (15 min)

### "I want to run commands inside MINIX"
→ [CLI Execution Guide](CLI-EXECUTION-GUIDE.md) (30 min)

### "I want a persistent MINIX environment"
→ [Runtime Setup Guide](RUNTIME-SETUP-GUIDE.md) (60 min)

### "I want automated error detection"
→ [MCP Integration Guide](MCP-INTEGRATION-GUIDE.md) (90 min)

### "I want comprehensive profiling data"
→ [Profiling Enhancement Guide](PROFILING-ENHANCEMENT-GUIDE.md) (8 hrs)

### "I want to use Claude Code with this project"
→ [MCP Quick Start](MCP-QUICK-START.md) (10 min)

---

## By Time Available

### 15 minutes or less
- [MCP Quick Start](MCP-QUICK-START.md) - Configure MCP (10 min)
- [Profiling Quick Start](PROFILING-QUICK-START.md) - First boot profile (15 min)

### 30 minutes
- [CLI Execution Guide](CLI-EXECUTION-GUIDE.md) - Interactive MINIX workflow (30 min)

### 1 hour
- [Runtime Setup Guide](RUNTIME-SETUP-GUIDE.md) - Full environment setup (60 min)

### Half day
- [MCP Integration Guide](MCP-INTEGRATION-GUIDE.md) - Complete automation (90 min)
- [Profiling Enhancement Guide](PROFILING-ENHANCEMENT-GUIDE.md) - Advanced metrics (8 hrs)

---

## Prerequisites Quick Reference

### Software Requirements by Guide

| Guide | Essential Tools | Optional Tools |
|-------|-----------------|----------------|
| MCP Quick Start | Claude Code, npx | None |
| Profiling Quick Start | QEMU, perf, flamegraph | valgrind, py-spy |
| CLI Execution | QEMU, socat, Python 3 | SQLite, git |
| Runtime Setup | QEMU, qemu-img, wget | Docker, docker-compose |
| MCP Integration | Claude Code, Docker, GitHub CLI | Node.js, npm |
| Profiling Enhancement | Python 3, perf, strace | ImageMagick, gnuplot |

### Hardware Requirements (All Guides)

- **CPU**: x86-64 with VT-x/AMD-V (virtualization)
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk**: 10 GB free space
- **Network**: Internet connection for downloads

---

## Learning Paths

### Path 1: Quick Start (Minimal)
**Goal**: Get measurements ASAP
**Time**: 30 minutes

1. [Profiling Quick Start](PROFILING-QUICK-START.md) (15 min)
2. [CLI Execution Guide](CLI-EXECUTION-GUIDE.md) (30 min)

**Outcome**: First boot profile, flamegraph, and measurements

---

### Path 2: Full Development Environment
**Goal**: Complete reproducible setup
**Time**: 2 hours

1. [Runtime Setup Guide](RUNTIME-SETUP-GUIDE.md) (60 min)
2. [CLI Execution Guide](CLI-EXECUTION-GUIDE.md) (30 min)
3. [Profiling Quick Start](PROFILING-QUICK-START.md) (15 min)

**Outcome**: Persistent MINIX, full measurement capability

---

### Path 3: Advanced Automation
**Goal**: Automated analysis pipeline
**Time**: 4-5 hours

1. [MCP Quick Start](MCP-QUICK-START.md) (10 min)
2. [MCP Integration Guide](MCP-INTEGRATION-GUIDE.md) (90 min)
3. [Profiling Enhancement Guide](PROFILING-ENHANCEMENT-GUIDE.md) (8 hrs)

**Outcome**: Fully automated analysis with issue tracking

---

## Key Concepts by Guide

### MCP Quick Start
- Model Context Protocol (MCP) basics
- Filesystem MCP server configuration
- SQLite MCP server configuration
- Environment variable management
- Claude Code integration

### Profiling Quick Start
- perf recording and analysis
- FlameGraph generation
- QEMU boot profiling
- Syscall frequency analysis
- Performance overhead considerations

### CLI Execution Guide
- TAP networking setup
- QEMU serial console access
- MINIX interactive boot
- Network configuration inside MINIX
- Result extraction to host

### Runtime Setup Guide
- MINIX ISO download and verification
- QEMU disk image creation
- MINIX installation to persistent disk
- Docker container setup
- Measurement framework integration

### MCP Integration Guide
- Docker MCP server configuration
- GitHub MCP server setup (deprecated package)
- SQLite MCP database integration
- Automated error diagnosis
- CI/CD workflow integration

### Profiling Enhancement Guide
- Serial logging fixes (mon:stdio)
- perf integration for CPU counters
- Boot marker regex patterns
- strace syscall tracing
- Unified JSON result aggregation

---

## File Locations

All guides are located in:
```
/home/eirikr/Playground/minix-analysis/docs/Examples/
```

Individual files:
```
├── CLI-EXECUTION-GUIDE.md
├── INDEX.md                              # This file
├── MCP-INTEGRATION-GUIDE.md
├── MCP-QUICK-START.md
├── PROFILING-ENHANCEMENT-GUIDE.md
├── PROFILING-QUICK-START.md
├── README.md
└── RUNTIME-SETUP-GUIDE.md
```

Original source files (root directory):
```
/home/eirikr/Playground/minix-analysis/
├── MINIX-CLI-EXECUTION-GUIDE.md
├── MINIX-MCP-Integration.md
├── MINIX-RUNTIME-SETUP.md
├── PROFILING-ENHANCEMENT-IMPLEMENTATION-GUIDE.md
├── README-PROFILING.md
└── START-HERE-MCP-FIXED.md
```

---

## Troubleshooting Quick Links

### Common Issues by Guide

**MCP Quick Start**
- Package not found → Verify npx installation
- Permission denied → Check database file permissions
- ENOENT error → Verify directory structure

**Profiling Quick Start**
- perf not found → `sudo pacman -S perf`
- Empty flamegraph → Use `-g` flag for call graph
- stackcollapse-perf.pl missing → `yay -S flamegraph-git`

**CLI Execution Guide**
- TAP device busy → `sudo ip tuntap del dev tap0 mode tap`
- No serial output → Use `-serial mon:stdio` instead of `-serial file:`
- gcc not found in MINIX → `pkgin install gcc`

**Runtime Setup Guide**
- QEMU won't start → Check VT-x/AMD-V enabled in BIOS
- ISO download fails → Use alternative mirror (SourceForge, Archive.org)
- Boot hangs → Increase memory: `-m 1024`

**MCP Integration Guide**
- GitHub auth failed → Verify GITHUB_TOKEN validity
- Docker socket inaccessible → Add user to docker group
- SQLite database not found → Create with `touch measurements/minix-analysis.db`

**Profiling Enhancement Guide**
- Serial logs empty → Replace `-serial file:` with `-serial mon:stdio`
- perf permission denied → `echo 1 | sudo tee /proc/sys/kernel/perf_event_paranoid`
- strace not found → `sudo pacman -S strace`

---

## Related Documentation

### Core Analysis Documentation
- [Boot Sequence Analysis](../Boot-Sequence/) - Detailed boot phase documentation
- [System Calls Reference](../System-Calls/) - Complete syscall documentation
- [Memory Management](../Memory/) - Virtual memory and paging

### Project Documentation
- [CLAUDE.md](../../CLAUDE.md) - Repository guidance for AI assistance
- [README.md](../../README.md) - Project overview

### External Resources
- MINIX Official: https://www.minix3.org/
- QEMU Manual: https://qemu.weilnetz.de/doc/
- perf Tutorial: https://www.brendangregg.com/perf.html
- FlameGraph: https://github.com/brendangregg/FlameGraph
- MCP Documentation: https://modelcontextprotocol.io/

---

**Last Updated**: 2025-11-01
**Total Guides**: 6
**Status**: Active and Maintained
