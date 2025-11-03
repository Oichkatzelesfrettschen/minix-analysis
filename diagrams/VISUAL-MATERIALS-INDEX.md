# VISUAL MATERIALS INDEX
## MINIX 3.4 Educational Diagrams

**Generated**: 2025-10-31
**Location**: `/home/eirikr/Playground/minix-analysis/diagrams/tikz/`
**Formats**: TikZ source (.tex), PDF, PNG

---

## COMPLETE DIAGRAM SET (8 Diagrams)

### 1. MINIX Architecture Overview
- **File**: `minix-architecture.png` (49 KB)
- **Purpose**: System-wide architecture with privilege rings
- **Content**:
  - 4 privilege levels (Ring 0-3)
  - Microkernel components
  - User-space servers
  - Process hierarchy
- **Use Case**: Understanding microkernel design philosophy

### 2. Boot Sequence Timeline
- **File**: `boot-sequence.png` (35 KB)
- **Purpose**: Boot process from power-on to first process
- **Content**:
  - Multiboot entry
  - Kernel initialization stages
  - First process creation
  - Timeline with memory addresses
- **Use Case**: Tracing system initialization

### 3. Process Lifecycle
- **File**: `process-lifecycle.png` (74 KB)
- **Purpose**: Complete process state transitions
- **Content**:
  - 7 process states
  - State transition triggers
  - Scheduling integration
  - Resource management
- **Use Case**: Understanding process management

### 4. Fork Sequence Flow
- **File**: `fork-sequence.png` (30 KB)
- **Purpose**: Process creation via fork()
- **Content**:
  - Parent/child relationship
  - Memory copying
  - PID allocation
  - Return value semantics
- **Use Case**: Tracing process creation

### 5. System Call Flow
- **File**: `syscall-flow.png` (51 KB)
- **Purpose**: Complete syscall execution path
- **Content**:
  - User to kernel transition
  - INT 0x30 mechanism
  - Message passing to servers
  - Return path with IRET
- **Use Case**: Understanding user/kernel boundary

### 6. IPC Message Flow
- **File**: `ipc-flow.png` (21 KB)
- **Purpose**: Inter-process communication
- **Content**:
  - SEND/RECEIVE/SENDREC operations
  - Message structure (56 bytes)
  - Blocking/non-blocking modes
  - Deadlock prevention
- **Use Case**: Understanding microkernel communication

### 7. Memory Layout Evolution
- **File**: `memory-layout.png` (18 KB)
- **Purpose**: Memory organization during boot
- **Content**:
  - Physical memory map
  - Kernel segment setup
  - Process memory allocation
  - Address space transitions
- **Use Case**: Tracking memory initialization

### 8. Virtual Memory Layout
- **File**: `virtual-memory-layout.png` (70 KB)
- **Purpose**: Process address space organization
- **Content**:
  - 32-bit address space
  - User vs kernel space
  - Stack/heap layout
  - Segment purposes
  - MMU translation
- **Use Case**: Understanding memory management

---

## USAGE GUIDE

### For Presentations
Use PNG files directly:
```bash
# View all diagrams
eog *.png  # Eye of GNOME

# Convert to slide deck
pandoc -t beamer -o minix-diagrams.pdf *.png
```

### For Documentation
Embed in Markdown:
```markdown
![MINIX Architecture](diagrams/tikz/minix-architecture.png)
```

### For Modification
Edit TikZ source and recompile:
```bash
# Edit source
vim minix-architecture.tex

# Compile to PDF
pdflatex minix-architecture.tex

# Convert to PNG
magick -density 150 minix-architecture.pdf -quality 90 minix-architecture.png
```

---

## PEDAGOGICAL SEQUENCE

### Beginner Path
1. **minix-architecture.png** - Overall system view
2. **boot-sequence.png** - How system starts
3. **process-lifecycle.png** - Basic process concepts

### Intermediate Path
4. **fork-sequence.png** - Process creation details
5. **syscall-flow.png** - User/kernel interaction
6. **memory-layout.png** - Memory organization

### Advanced Path
7. **ipc-flow.png** - Microkernel communication
8. **virtual-memory-layout.png** - Virtual memory details

---

## QUALITY NOTES

- All diagrams use consistent color scheme:
  - Red: Kernel/privileged components
  - Blue: User space
  - Green: Servers/intermediate privilege
  - Yellow: Data structures
  - Gray: Unmapped/unused

- Resolution: 150 DPI for clarity
- Format: PNG with transparency
- Source: TikZ for professional quality
- Style: Technical but approachable

---

## TOTAL VISUAL MATERIALS

- **8 TikZ source files** (.tex)
- **8 PDF documents** (vector graphics)
- **8 PNG images** (raster for embedding)
- **Total size**: ~350 KB (PNG), ~400 KB (PDF)

All materials ready for educational use in the Lions/xv6 style pedagogical framework.