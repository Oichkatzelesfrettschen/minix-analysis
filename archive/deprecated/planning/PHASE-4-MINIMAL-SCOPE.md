# Phase 4: Actual Scope (Stripped Down)

**Reality Check Date**: 2025-10-31  
**Status**: Grounded in verified facts, not speculation

---

## What Actually Exists (Verified)

✅ Shared MCP server at `shared/mcp/server/` – **WORKING**
- Tested: `MinixAnalysisServer.from_default_data_dir()` succeeds
- 8 methods: `query_architecture()`, `analyze_syscall()`, `query_boot_sequence()`, etc.

✅ Analysis data at `diagrams/data/` – **ALL FILES PRESENT**
- kernel_structure.json (17 KB)
- boot_sequence.json (353 bytes)
- ipc_system.json (163 bytes)
- memory_layout.json (614 bytes)
- process_table.json (3.8 KB)
- statistics.json (117 bytes)

✅ Make build system – **TARGETS DEFINED**
- `pipeline`, `analyze`, `generate-diagrams`, `compile-tikz`, `convert-png`
- `cpu`, `boot`, `wiki`
- `test`, `clean`

⚠️ CLI at `src/os_analysis_toolkit/cli.py` – **BROKEN BUT FIXABLE**
- Error: Missing `dash` module (dependency issue, not design issue)
- Easy fix: Remove dashboard import or install `dash`

❌ External MCP transport – **DOES NOT EXIST**
- Not found in `/home/eirikr/Playground/`
- Needs to be created from scratch

---

## Actual Work Required (Minimal)

### 1. Fix CLI Dependency (5 min)
```bash
# Option A: Install missing dependency
pip install dash

# Option B: Remove dashboard feature (faster)
# Edit src/os_analysis_toolkit/cli.py line 13
# Comment out: from .dashboard.app import run_dashboard
```

**Done**: CLI can now run

---

### 2. Create Minimal MCP Transport (2 hours)
```bash
# Create skeleton
mkdir -p /home/eirikr/Playground/minix-mcp-transport
cd minix-mcp-transport
git init
mkdir -p src/server

# Create __main__.py that:
# - Imports MinixAnalysisServer from shared.mcp.server
# - Wraps each method as an MCP tool
# - Runs via stdio_server
```

**Minimal code** (~150 lines):
```python
# src/server/__main__.py
import sys
from pathlib import Path

# Point to minix-analysis
MINIX_ROOT = Path("/home/eirikr/Playground/minix-analysis")
sys.path.insert(0, str(MINIX_ROOT / "src"))

from shared.mcp.server import MinixAnalysisServer
from mcp.server import Server, stdio_server

minix = MinixAnalysisServer.from_default_data_dir()
mcp = Server("minix-analysis")

@mcp.tool()
async def query_architecture(top_n: int = 5):
    result = minix.query_architecture(top_n=top_n)
    return json.dumps(result, indent=2)

@mcp.tool()
async def analyze_syscall(name: str):
    result = minix.analyze_syscall(name)
    if not result:
        return f"Syscall '{name}' not found"
    return json.dumps(result, indent=2)

# ... (repeat for each method) ...

async def main():
    async with stdio_server(mcp) as streams:
        await streams.wait_closed()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Done**: Transport callable via MCP

---

### 3. Add Missing CLI Commands (1 hour)
Currently broken:
- `--query-architecture` (should exist, doesn't)
- `--compare-mechanisms` (should exist, doesn't)
- `--explain-diagram` (should exist, doesn't)
- `--query-boot` (should exist, doesn't)
- `--trace-boot` (should exist, doesn't)

Add to `src/os_analysis_toolkit/cli.py`:
```python
if args.query_architecture:
    print(json.dumps(server.query_architecture(), indent=2))
elif args.compare_mechanisms:
    print(json.dumps(server.compare_mechanisms(), indent=2))
elif args.query_boot:
    aspect = getattr(args, 'boot_aspect', 'all') or 'all'
    print(json.dumps(server.query_boot_sequence(aspect=aspect), indent=2))
# ... (repeat for others)
```

**Done**: CLI has feature parity

---

### 4. Verify Pipeline Works (1 hour)
```bash
cd /home/eirikr/Playground/minix-analysis
make pipeline  # Should complete without errors
make cpu       # Should complete without errors
make boot      # Should complete without errors
```

If any fail: fix in Makefile or dependencies.

**Done**: Build system validated

---

### 5. Update README (30 min)
Add one section:
```markdown
## MCP Integration

### Quick Start
```bash
# Run analysis server
python -m minix_mcp_transport

# Query via CLI
python -m os_analysis_toolkit.cli --query-architecture
```

**Done**: Users know how to access MCP layer

---

## Total Effort

| Task | Time | Status |
|------|------|--------|
| Fix CLI dependency | 5 min | Unblocking |
| Create MCP transport | 2 hours | Core work |
| Add CLI commands | 1 hour | Feature parity |
| Verify pipeline | 1 hour | Validation |
| Update README | 30 min | Documentation |
| **TOTAL** | **4.5 hours** | **Doable in 1 day** |

---

## What NOT to Do

❌ Write 600-line execution plans  
❌ Create "reference documents" that point to other documents  
❌ Estimate 3-4 weeks when reality is 1 day of actual work  
❌ Include optional nice-to-haves in the critical path  
❌ Create planning theater instead of shipping  

**Focus**: Get the transport working, CLI complete, README updated. Done.

---

## Next Actions (In Order)

1. **Right now**: Fix CLI dependency (5 min)
   ```bash
   cd /home/eirikr/Playground/minix-analysis
   pip install dash
   # or comment out dashboard import
   ```

2. **Today**: Create transport skeleton and wire shared.mcp.server (2 hours)
   ```bash
   mkdir minix-mcp-transport
   # Copy transport code from this scope
   # Test with: python -m minix_mcp_transport
   ```

3. **Today**: Add 5 missing CLI commands (1 hour)
   ```bash
   # Edit src/os_analysis_toolkit/cli.py
   # Add argument handlers for missing commands
   # Test each: python -m os_analysis_toolkit.cli --<command>
   ```

4. **Today**: Run pipeline validation (1 hour)
   ```bash
   make pipeline && make cpu && make boot
   ```

5. **Done**: Update README with MCP section (30 min)

---

## Success = 5 Things Work

1. ✅ Transport runs: `python -m minix_mcp_transport`
2. ✅ Shared server loads: All 8 methods callable
3. ✅ CLI parity: All 11 commands work
4. ✅ Build clean: `make pipeline && make cpu && make boot`
5. ✅ README updated: Users know how to use MCP

**Anything else is scope creep.**

