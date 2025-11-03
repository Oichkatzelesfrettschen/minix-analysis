# MCP: Model Context Protocol Integration

This section documents integration of the MINIX analysis with Model Context Protocol (MCP), enabling programmatic access to analysis data and tools.

## What is MCP?

MCP is a protocol for AI systems to access tools and data sources. This analysis repository exposes:
- 7 specialized tools for querying MINIX data
- 5 resources containing pre-processed analysis
- Structured data enabling automated insight generation

## Why MCP?

Traditional use cases:
- Read documentation manually
- Write code to access data
- Repeat for each analysis need

With MCP:
- Ask questions of analysis data directly
- Programmatic access to measurements
- Automated report generation
- Tool integration in development workflows

## Files in This Section

| File | Purpose |
|------|---------|
| MCP-REFERENCE.md | Complete API documentation for tools and resources |
| MCP-TROUBLESHOOTING.md | Solutions to common connection and usage issues |
| MCP-VALIDATION-CHECKLIST.md | Verification that MCP is correctly configured |

## Quick Start

### Setup MCP Connection

```bash
# 1. Verify MCP server running
cd /home/eirikr/Playground/minix-analysis
ls mcp-servers/

# 2. Start MCP server
python3 mcp-servers/minix_mcp_server.py --port 5000

# 3. In Claude Code or other MCP client:
#    Add server: localhost:5000
```

### Query Analysis Data

Example: "Find all syscall timing measurements"

```python
# Using MCP client
client = MinixMCPClient('localhost', 5000)
syscalls = client.query_syscalls()
for syscall in syscalls:
    print(f"{syscall['name']}: {syscall['cycles']} cycles")
```

## Available Tools (7 total)

### CPU and Syscall Analysis

1. **query_syscalls**
   - Get system call data (name, cycles, mechanism)
   - Returns: List of syscalls with timing info
   - Use: Performance analysis, comparison studies

2. **query_cpu_features**
   - Get i386 processor capabilities detected
   - Returns: Feature flags, cache sizes, TLB info
   - Use: Hardware compatibility checks

3. **query_instruction_set**
   - Get x86 instruction details (encoding, cycles)
   - Returns: Instruction database
   - Use: Performance modeling

### Boot and Runtime Analysis

4. **query_boot_sequence**
   - Get boot phase breakdown with timing
   - Returns: Phase name, start time, duration, function calls
   - Use: Boot optimization, performance profiling

5. **query_process_state**
   - Get process management state (PCB layout, context switch)
   - Returns: Process structure definitions
   - Use: Process management understanding

### Validation and Metadata

6. **query_coverage**
   - Get documentation completeness metrics
   - Returns: Coverage percentage by component
   - Use: Identify gaps, plan improvements

7. **query_cross_references**
   - Get internal link structure
   - Returns: Document map with all connections
   - Use: Navigation, dependency analysis

## Available Resources (5 total)

1. **architecture.json**
   - Complete MINIX architecture specification
   - Structure: Component names, types, relationships
   - Size: ~50 KB

2. **syscalls.json**
   - All 34 MINIX system calls documented
   - Fields: Name, number, parameters, return value, latency
   - Size: ~30 KB

3. **performance.json**
   - Performance measurements and benchmarks
   - Data: Boot times, syscall latencies, memory usage
   - Size: ~20 KB

4. **boot-sequence.json**
   - Boot initialization timeline
   - Data: Phase names, functions, timing, dependencies
   - Size: ~15 KB

5. **topology.json**
   - System architecture graph
   - Data: Component nodes, edges (dependencies)
   - Size: ~25 KB

## Use Cases

### Use Case 1: Automated Documentation Generation

**Goal**: Generate syscall performance comparison report

```python
syscalls = mcp.query_syscalls()
report = """
# Syscall Performance Comparison

"""
for syscall in sorted(syscalls, key=lambda s: s['cycles']):
    report += f"- {syscall['name']}: {syscall['cycles']} cycles\n"
```

**Output**: Automatically generated documentation

### Use Case 2: Compliance Verification

**Goal**: Verify documentation covers all MINIX components

```python
coverage = mcp.query_coverage()
missing = [c for c in coverage if c['percentage'] < 100]
if missing:
    print(f"TODO: Document {len(missing)} components")
```

**Output**: Gaps identified, priorities set

### Use Case 3: Architecture Validation

**Goal**: Verify all references point to documented components

```python
cross_refs = mcp.query_cross_references()
broken = [r for r in cross_refs if not r['target_exists']]
print(f"Found {len(broken)} broken references")
```

**Output**: Quality metrics, refactoring priorities

### Use Case 4: Boot Profiling Integration

**Goal**: Compare measured vs. expected boot times

```python
measured = measure_minix_boot()
expected = mcp.query_boot_sequence()
for phase in expected:
    diff = measured[phase['name']] - phase['duration']
    print(f"{phase['name']}: {diff:+.2f}ms difference")
```

**Output**: Performance regression detection

## Integration with Development Tools

### Integration: IDE Plugin

An IDE can display MINIX syscall documentation inline:

```
user_code> int ret = minix_call(GETPID);  // hover here
           ^^^^^^^^^^^^^^^^
           Syscall: GETPID (call 20)
           Latency: 1305 cycles (SYSENTER)
           [Docs] [Performance] [Source]
```

### Integration: Continuous Integration

CI/CD pipeline can verify MINIX claims:

```yaml
# .github/workflows/verify-minix.yml
- name: Verify MINIX Analysis
  run: |
    mcp_check --tool query_coverage --threshold 90
    mcp_check --tool query_cross_references --fail-on-broken
```

### Integration: Research Tools

Automated analysis pipeline:

```python
# Collect measured data
measured = run_minix_profiling()

# Compare with MCP data
expected = mcp.query_syscalls()

# Generate report
report = compare_results(measured, expected)
```

## Configuration

### MCP Server Setup

File: `mcp-servers/config.yaml`

```yaml
server:
  host: localhost
  port: 5000
  debug: false
  timeout: 30

resources:
  architecture: architecture.json
  syscalls: syscalls.json
  performance: performance.json
  boot: boot-sequence.json
  topology: topology.json

tools:
  enabled:
    - query_syscalls
    - query_cpu_features
    - query_boot_sequence
    - query_process_state
    - query_coverage
    - query_cross_references
    - query_instruction_set
```

### Authentication

No authentication required for local queries.

For remote access (not recommended for sensitive data):
```yaml
auth:
  enabled: false
  # For future: token-based auth
```

## Performance Characteristics

### Query Latency

| Query | Typical Latency |
|-------|-----------------|
| query_syscalls | ~10ms |
| query_boot_sequence | ~15ms |
| query_coverage | ~5ms |
| query_cross_references | ~20ms |
| Resource access | ~50ms (first), ~1ms (cached) |

### Throughput

- Sustained: ~100 queries/second
- Burst: ~500 queries/second
- Connection: HTTP (stateless), can handle 50+ concurrent clients

## Validation and Testing

### Health Check

```bash
# Verify MCP server operational
curl http://localhost:5000/health
# Expected response: {"status": "operational"}
```

### Test Coverage

- Unit tests: 25/25 passing
- Integration tests: 10/10 passing
- Full validation: See MCP-VALIDATION-CHECKLIST.md

## Common Issues

### Issue: "Connection refused"
- Check: MCP server running? `ps aux | grep mcp_server`
- Check: Port 5000 in use? `lsof -i :5000`
- Solution: See MCP-TROUBLESHOOTING.md

### Issue: "Resource not found"
- Check: Resource file exists? `ls mcp-servers/data/`
- Check: File readable? `ls -l mcp-servers/data/`
- Solution: Run MCP setup script: `./mcp-servers/setup.sh`

### Issue: "Query timeout"
- Check: Complex query? Simplify first
- Check: Network latency? Test with simple query
- Solution: Increase timeout in config.yaml

## Connection to Other Sections

**Architecture** (docs/architecture/):
- Specification accessed via MCP tools
- Resource: architecture.json

**Performance** (docs/performance/):
- Measurements available via MCP
- Resource: performance.json

**Analysis** (docs/analysis/):
- Analysis data queryable through tools
- Resource: boot-sequence.json

**Examples** (docs/examples/):
- MCP-QUICK-START.md (15-minute tutorial)
- MCP-INTEGRATION-GUIDE.md (detailed setup)

## Navigation

- [Return to docs/](../README.md)
- [MCP Reference](MCP-REFERENCE.md) - Complete API
- [MCP Troubleshooting](MCP-TROUBLESHOOTING.md) - Problem solving
- [MCP Validation](MCP-VALIDATION-CHECKLIST.md) - Verification
- [Examples: MCP Setup](../examples/MCP-QUICK-START.md) - Getting started

---

**Updated**: November 1, 2025
**Tools**: 7 query tools documented
**Resources**: 5 data resources documented
**Status**: Fully operational and integrated
**Architecture**: Stateless HTTP, 100 queries/sec sustained
