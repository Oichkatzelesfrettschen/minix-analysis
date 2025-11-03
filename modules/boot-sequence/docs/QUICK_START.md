# Quick Start Guide: Minix Boot Analysis

## 5-Minute Tour

### Step 1: Trace the boot sequence
```bash
cd /home/eirikr/Playground/minix-boot-analyzer
./trace_boot_sequence.sh /home/eirikr/Playground/minix 2
```

**What you get:**
- Complete list of functions called during boot
- File locations for each function
- Organized call graph

### Step 2: View the call graph
```bash
cat boot_trace_output/call_graph.txt
```

**Output example:**
```
kmain -> cstart [minix/kernel/main.c]
kmain -> proc_init [minix/kernel/proc.c]
kmain -> memory_init [minix/kernel/memory.c]
...
```

### Step 3: Deep dive into a function
```bash
./deep_dive.sh /home/eirikr/Playground/minix kmain kmain_deep.md
cat kmain_deep.md
```

**What you get:**
- Complete source code
- All function calls
- Documentation comments
- Recursive analysis

### Step 4: Generate visual graph (optional)
```bash
./generate_dot_graph.sh boot_trace_output/call_graph.txt boot_graph.dot
dot -Tpng boot_graph.dot -o boot_graph.png  # Requires graphviz
```

## Common Use Cases

### "I want to understand what kmain() does"
```bash
./deep_dive.sh /home/eirikr/Playground/minix kmain kmain_analysis.md
less kmain_analysis.md
```

### "Where is proc_init() defined?"
```bash
./find_definition.sh /home/eirikr/Playground/minix proc_init
```

### "What functions does memory_init() call?"
```bash
# First find where it's defined
DEF=$(./find_definition.sh /home/eirikr/Playground/minix memory_init | head -1 | cut -d: -f1)

# Then extract its calls
./extract_functions.sh "$DEF" memory_init
```

### "Trace the entire boot sequence deeply"
```bash
# Go deeper (depth 4, slower but more complete)
./trace_boot_sequence.sh /home/eirikr/Playground/minix 4
```

### "Analyze multiple key functions"
```bash
# Batch analysis
for func in kmain cstart proc_init memory_init system_init bsp_finish_booting; do
    ./deep_dive.sh /home/eirikr/Playground/minix "$func" "${func}_analysis.md"
done

# Now you have detailed docs for all major boot functions
ls -lh *_analysis.md
```

## Understanding the Output

### Call Graph Format
```
function_name -> called_function [file_location]
```

Example:
```
kmain -> proc_init [minix/kernel/proc.c]
```
Means: `kmain()` calls `proc_init()`, which is defined in `minix/kernel/proc.c`

### EXTERNAL Functions
```
kmain -> memcpy [EXTERNAL]
```
Means: `memcpy` is not in the Minix source (it's stdlib or a macro)

### Deep Dive Markdown
Each analysis file contains:
1. **Location** - Where the function is defined
2. **Documentation** - Comments from the source
3. **Function Calls** - All functions it invokes
4. **Source Code** - Complete implementation with line numbers
5. **Recursive Analysis** - Analysis of functions it calls

## Real-World Example

**Goal:** Understand how Minix initializes processes

```bash
# Step 1: Trace from kmain
./trace_boot_sequence.sh /home/eirikr/Playground/minix 2

# Step 2: See that kmain calls proc_init
grep proc_init boot_trace_output/call_graph.txt

# Step 3: Deep dive into proc_init
./deep_dive.sh /home/eirikr/Playground/minix proc_init proc_init.md

# Step 4: Read the analysis
cat proc_init.md
```

**What you learn:**
- `proc_init()` clears the process table
- It calls `arch_proc_reset()` for each process slot
- It sets up the IDLE process for each CPU
- It initializes privilege structures

**Now trace deeper:**
```bash
./deep_dive.sh /home/eirikr/Playground/minix arch_proc_reset arch_proc_reset.md
```

**Result:** Complete understanding of process initialization!

## Tips & Tricks

### 1. Focus on one subsystem
```bash
# Memory subsystem
for func in memory_init add_memmap alloc_pages; do
    ./deep_dive.sh /home/eirikr/Playground/minix "$func" "mem_${func}.md"
done
```

### 2. Find all calls to a specific function
```bash
# Who calls panic()?
grep "-> panic" boot_trace_output/call_graph.txt
```

### 3. Build a reading list
```bash
# Extract just the filenames
cut -d'[' -f2 boot_trace_output/call_graph.txt | \
    cut -d']' -f1 | \
    grep -v EXTERNAL | \
    sort -u > files_to_read.txt
```

### 4. Analyze incrementally
```bash
# Start shallow
./trace_boot_sequence.sh /home/eirikr/Playground/minix 1

# If you need more detail, go deeper
./trace_boot_sequence.sh /home/eirikr/Playground/minix 3
```

### 5. Grep the analysis files
```bash
# All analyses together
cat *_analysis.md > complete_boot_analysis.md

# Search across all analyses
grep -i "interrupt" *_analysis.md
```

## Script Reference

| Script | Purpose | Speed |
|--------|---------|-------|
| `trace_boot_sequence.sh` | Trace complete boot flow | Medium |
| `deep_dive.sh` | Detailed single function | Fast |
| `extract_functions.sh` | List function calls | Very Fast |
| `find_definition.sh` | Locate function | Very Fast |
| `generate_dot_graph.sh` | Visual graph | Fast |

## Performance Notes

- **Depth 1-2:** Very fast, good for overview
- **Depth 3-4:** Slower, comprehensive analysis
- **Depth 5+:** Can be slow, usually unnecessary

## Next Steps

After understanding the boot sequence:

1. **Read the source files** identified in the call graph
2. **Trace specific subsystems** (memory, IPC, scheduling)
3. **Compare to documentation** in minix/docs/
4. **Build modifications** with full context

## Integration with Your Workflow

### With grep/ag/rg
```bash
# Find all panic calls in the boot path
ag panic $(cut -d'[' -f2 boot_trace_output/call_graph.txt | cut -d']' -f1 | grep -v EXTERNAL)
```

### With ctags
```bash
# Generate tags for boot-related files
ctags $(cut -d'[' -f2 boot_trace_output/call_graph.txt | cut -d']' -f1 | grep -v EXTERNAL)
```

### With your editor
```bash
# Open all boot sequence files in vim
vim $(cut -d'[' -f2 boot_trace_output/call_graph.txt | cut -d']' -f1 | grep -v EXTERNAL | head -20)
```

---

**Remember:** These tools READ the code, they don't RUN it. Safe for analysis without building or executing Minix.
