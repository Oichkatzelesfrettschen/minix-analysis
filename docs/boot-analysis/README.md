# Minix Kernel Boot Sequence Analyzer

A POSIX-compliant toolkit for systematically dissecting the Minix kernel boot sequence using pure shell tools (grep, awk, sed, find).

## What This Does

This project demonstrates how to **systematically analyze kernel initialization** by:

1. **Tracing function calls** from `kmain()` through the entire boot sequence
2. **Finding function definitions** across the source tree
3. **Extracting documentation** and source code for each function
4. **Building call graphs** showing initialization order
5. **Deep-diving** into specific functions with full context

## The Tools

### 1. `trace_boot_sequence.sh` - Boot Sequence Tracer

**What it does:** Starts from `kmain()` and traces all function calls, finding their definitions

**Usage:**
```bash
./trace_boot_sequence.sh [minix_root] [max_depth]

# Example:
./trace_boot_sequence.sh /home/eirikr/Playground/minix 2
```

**Output:**
- `boot_trace_output/call_graph.txt` - Complete call graph with file locations
- `boot_trace_output/functions_summary.txt` - Summary statistics

**What you get:**
```
kmain [depth=0]
  Calls:
    -> cstart
       Found in: /path/to/minix/kernel/main.c
    -> proc_init
       Found in: /path/to/minix/kernel/proc.c
    -> memory_init
       Found in: /path/to/minix/kernel/memory.c
    ...
```

### 2. `deep_dive.sh` - Deep Function Analyzer

**What it does:** Extracts complete information about a function:
- Documentation comments
- Full source code with line numbers
- All functions it calls
- Recursive analysis of called functions

**Usage:**
```bash
./deep_dive.sh [minix_root] [function_name] [output_file]

# Examples:
./deep_dive.sh /home/eirikr/Playground/minix kmain kmain_deep.md
./deep_dive.sh /home/eirikr/Playground/minix proc_init proc_init_deep.md
./deep_dive.sh /home/eirikr/Playground/minix cstart cstart_deep.md
```

**Output:** Markdown file with complete analysis including:
- Function location
- Documentation/comments
- List of functions called
- Full source code
- Recursive analysis of dependencies

### 3. `extract_functions.sh` - Function Call Extractor

**What it does:** Extracts all function calls from a specific function in a C file

**Usage:**
```bash
./extract_functions.sh <source_file> <function_name>

# Example:
./extract_functions.sh /path/to/main.c kmain
```

**Output:** List of unique function names called

### 4. `find_definition.sh` - Function Definition Finder

**What it does:** Searches the entire source tree for where a function is defined

**Usage:**
```bash
./find_definition.sh <source_root> <function_name>

# Example:
./find_definition.sh /home/eirikr/Playground/minix proc_init
```

**Output:** Files and line numbers where the function is defined

## Quick Start

### Trace the entire boot sequence:
```bash
cd /home/eirikr/Playground/minix-boot-analyzer
./trace_boot_sequence.sh /home/eirikr/Playground/minix 3
cat boot_trace_output/call_graph.txt
```

### Deep-dive into kmain():
```bash
./deep_dive.sh /home/eirikr/Playground/minix kmain kmain_analysis.md
cat kmain_analysis.md
```

### Find specific functions:
```bash
# What does proc_init call?
./extract_functions.sh /home/eirikr/Playground/minix/minix/kernel/proc.c proc_init

# Where is memory_init defined?
./find_definition.sh /home/eirikr/Playground/minix memory_init
```

## What We Discovered

From the `kmain()` boot sequence:

### Initialization Order

1. **Early Bootstrap** (`cstart`)
   - `prot_init()` - Protection initialization
   - `init_clock()` - Clock initialization
   - `intr_init()` - Interrupt initialization
   - `arch_init()` - Architecture-specific init

2. **Process Table Setup** (`proc_init`)
   - Clear process table
   - Set up kernel tasks
   - Initialize idle process

3. **Memory Management** (`memory_init`)
   - Physical memory detection
   - Page allocator setup

4. **System Services** (`system_init`)
   - System call handlers
   - IPC mechanism

5. **SMP or Single CPU** (`bsp_finish_booting`)
   - CPU identification
   - Timer interrupt setup
   - FPU initialization
   - **Switch to usermode** (`switch_to_user()`)

### Key Functions in kmain()

| Function | Purpose | File |
|----------|---------|------|
| `cstart()` | Early C initialization before main | main.c:403 |
| `proc_init()` | Initialize process table | proc.c |
| `memory_init()` | Memory subsystem setup | memory.c |
| `system_init()` | System services init | system.c |
| `bsp_finish_booting()` | Final boot steps + usermode switch | main.c:38 |

### The Infinite Loop

**There is no infinite loop in kmain!** Instead:
- After all initialization, `bsp_finish_booting()` calls `switch_to_user()`
- This **never returns** (marked `NOT_REACHABLE`)
- The kernel jumps to the scheduler which runs user processes
- From then on, the kernel only runs on interrupts/syscalls

## How It Works (Technical Details)

### POSIX Tools Used

1. **awk** - Function body extraction and parsing
2. **grep** - Pattern matching and function call detection
3. **sed** - Text transformation and cleanup
4. **find** - Recursive file discovery
5. **sort/uniq** - Deduplication

### Algorithm

1. **Parse function body:**
   - Use awk to find function by name
   - Track brace depth to extract complete body
   - Handle nested braces correctly

2. **Extract function calls:**
   - Regex: `\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(`
   - Filter out keywords (if, for, while, etc.)
   - Remove duplicates

3. **Find definitions:**
   - Search pattern: `^return_type function_name(`
   - Limit to `.c` and `.h` files
   - Return first match

4. **Build call graph:**
   - Recursive traversal with depth limit
   - Track visited functions to avoid cycles

## Shell Script Quality

All scripts are:
- **POSIX-compliant** - Work with sh, bash, zsh, dash
- **Safe** - Use `set -eu` for error detection
- **Portable** - No bash-isms or GNU-isms
- **Readable** - Clear variable names and comments
- **Validated** - Can be checked with `shellcheck -s sh`

## Example Output

### Call Graph Extract
```
kmain -> cstart [minix/kernel/main.c]
kmain -> proc_init [minix/kernel/proc.c]
kmain -> memory_init [minix/kernel/memory.c]
kmain -> system_init [minix/kernel/system.c]
kmain -> bsp_finish_booting [minix/kernel/main.c]
cstart -> prot_init [minix/kernel/protect.c]
cstart -> init_clock [minix/kernel/clock.c]
```

### Function Analysis
```markdown
## `kmain()`

**Location:** `minix/kernel/main.c:115`

**Function Calls:** 34 unique functions

**Source Code:**
\`\`\`c
115: void kmain(kinfo_t *local_cbi)
116: {
117: /* Start the ball rolling. */
...
\`\`\`
```

## Future Enhancements

Possible additions:
- [ ] Graphviz DOT output for visual call graphs
- [ ] Variable dependency tracking
- [ ] Macro expansion analysis
- [ ] Cross-reference generation
- [ ] Boot time estimation
- [ ] Critical path analysis

## Why This Is Useful

1. **Understanding kernel initialization** - See exactly what happens at boot
2. **Learning C codebase navigation** - Practical example of code archaeology
3. **POSIX shell scripting** - Real-world awk/sed/grep usage
4. **Documentation generation** - Auto-extract function docs
5. **Debugging** - Trace execution flow without running code

## Author's Notes

This was built to demonstrate:
- Pure POSIX shell can handle complex analysis tasks
- You don't need Python/Ruby for code analysis
- Small, focused tools compose well
- Understanding systems by reading them, not running them

The goal: **Read the source, understand the system.**

---

**Created:** 2025-10-30
**Target:** Minix 3 kernel
**Tools:** POSIX sh, awk, grep, sed, find
**Philosophy:** Read code systematically, not randomly
