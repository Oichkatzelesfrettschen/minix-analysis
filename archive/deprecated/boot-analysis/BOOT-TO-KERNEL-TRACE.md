# MINIX 3.4 Boot to Kernel Initialization Trace
## Comprehensive CPU State Transition Analysis

**Version**: 1.0.0
**Date**: 2025-10-31
**Architecture**: x86 (i386 32-bit)
**MINIX Version**: 3.4.0-RC6
**Scope**: Bootloader entry through kmain() completion

---

## PHASE 0: MULTIBOOT BOOTLOADER ENTRY

### 0.1 Entry Point (head.S:38-40)

**File**: `minix/kernel/arch/i386/head.S`
**Location**: `.text` section, symbol `MINIX`
**CPU State Entering**:
- ESP: 0x????? (undefined, bootloader-provided)
- EIP: 0x?????? (bootloader jumps here)
- EBP: undefined
- EFLAGS: bootloader-dependent
- CS: bootloader selector (likely KERN_CS_SELECTOR)
- DS/ES/SS: bootloader selectors

```
head.S:38 .global MINIX
head.S:39 MINIX:
head.S:40 | jmp multiboot_init
```

**CPU Actions**:
- Jump to multiboot_init (relative jump, 32-bit)
- No privilege level change (already in Ring 0 from bootloader)
- Instruction pointer now at multiboot_init

### 0.2 Multiboot Magic & Header (head.S:41-71)

**Purpose**: Bootloader compliance (GRUB, U-Boot, etc)

```
head.S:45 multiboot_magic:
head.S:46 | .long MULTIBOOT_HEADER_MAGIC
head.S:47 multiboot_flags:
head.S:48 | .long MULTIBOOT_FLAGS
head.S:49 multiboot_checksum:
head.S:50 | .long -(MULTIBOOT_HEADER_MAGIC + MULTIBOOT_FLAGS)
```

**Bootloader Pre-Kernel Setup**:
1. Memory map obtained (BIOS memory detection)
2. Multiboot info struct populated
3. Kernel loaded at physical address
4. Boot parameters passed in %ebx (multiboot info pointer)
5. Magic value in %eax (0x2BADB002)

### 0.3 Stack Setup & Call to pre_init (head.S:73-92)

**File**: `minix/kernel/arch/i386/head.S`

```
head.S:73 multiboot_init:
head.S:74 | mov $load_stack_start, %esp
head.S:75 | mov $0, %ebp
head.S:76 | push $0
head.S:77 | popf
head.S:78 | push $0
head.S:79 | push %ebx                # multiboot info (physical)
head.S:80 | push %eax                # multiboot magic
head.S:81 | call _C_LABEL(pre_init)
```

**CPU State After Stack Setup**:
- ESP: load_stack_start (0x????) - temporary stack
- EBP: 0x00000000 (null frame pointer)
- EFLAGS: 0x00000000 (IF=0, all flags clear)
- Stack contains: [multiboot_magic=0x2BADB002][multiboot_info_ptr]

**Critical: 1:1 Virtual-to-Physical Mapping Active**
- Paging may or may not be enabled at this point
- Code assumes 1:1 mapping (virtual address = physical address)
- This assumption critical for next phase

---

## PHASE 1: PRE_INIT LOW-LEVEL SETUP

### 1.1 Pre-Init Entry (pre_init.c:244 onwards)

**File**: `minix/kernel/arch/i386/pre_init.c`
**Function**: `int pre_init(u32_t magic, u32_t ebx)`

```
pre_init.c:244 void pre_init(u32_t magic, u32_t ebx)
```

**Stack Frame (at function entry)**:
```
ESP+0:  Return address (back to head.S after call)
ESP+4:  magic = 0x2BADB002
ESP+8:  ebx = physical address of multiboot_info_t
```

**CPU Context**:
- Still 1:1 mapping (no paging setup yet)
- Ring 0 (kernel mode)
- Interrupts disabled (EFLAGS.IF = 0)
- GDT/IDT: loaded by bootloader (may be basic)

### 1.2 Multiboot Parameter Parsing (pre_init.c:95-150)

**Function**: `void get_parameters(u32_t ebx, kinfo_t *cbi)`

**Input**: EBX register contains physical address of multiboot_info_t

**Multiboot Info Struct Layout**:
```
multiboot_info_t {
  u32_t mi_flags;              # flags (bit 0=mem, bit 1=bootdev, etc)
  u32_t mi_mem_lower;          # KB below 1MB
  u32_t mi_mem_upper;          # KB above 1MB
  u32_t mi_boot_device;        # BIOS boot device
  u32_t mi_cmdline;            # kernel command line
  u32_t mi_mods_count;         # number of boot modules
  u32_t mi_mods_addr;          # address of module list
  u32_t mi_syms[4];            # symbol table (format-dependent)
  u32_t mi_mmap_length;        # memory map length
  u32_t mi_mmap_addr;          # memory map address
  ...
};
```

**Key Operations**:
1. Copy multiboot_info_t to kinfo struct (memory copied, not referenced)
2. Parse memory map (BIOS e820 map)
3. Parse boot modules (kernel tasks, servers, filesystems)
4. Detect MINIX kernel boundaries (&_kern_phys_base, &_kern_size)
5. Parse boot command line (key=value pairs)

**CPU State During get_parameters**:
- Executing C code in Ring 0
- Memory access: physical memory directly (no paging yet)
- All memory access 1:1 mapped

### 1.3 Kernel Memory Layout Detection (pre_init.c:87-94)

**Critical Symbols** (from kernel.lds linker script):
```
_kern_phys_base    = 0x00100000    (physical kernel start)
_kern_vir_base     = 0x80000000    (virtual kernel start)
_kern_size         = 0x00d00000    (kernel size ~13MB)
_kern_unpaged_start
_kern_unpaged_end   (unpaged region for early code)
```

**Kernel Relocation**:
- Kernel *compiled* for virtual address 0x80000000
- Kernel *loaded* at physical 0x00100000 by bootloader
- Pre-init code executes at physical address
- Offset = 0x80000000 - 0x00100000 = 0x7f000000

### 1.4 Page Table Initialization (pre_init.c:200-240)

**Function**: Page table setup for MMU enable

**Key Setup**:
1. Create page directory (PD) at physical address 0x00001000
2. Map kernel:
   - Virtual 0x80000000 -> Physical 0x00100000 (PDE + PTEs)
   - Identity map: Physical 0x00000000 -> Virtual 0x00000000
3. Enable paging bit (CR0.PG = 1)
4. Load page directory address (CR3 = PD physical address)

**CPU Instructions** (pseudo-code from protect.c):
```
mov $page_directory_physical, %eax
mov %eax, %cr3                    # Load PDBR

mov %cr0, %eax
or  $0x80000000, %eax             # Set CR0.PG bit
mov %eax, %cr0                    # Enable paging
```

**Paging Transition**:
- Before: Linear address = Physical address (1:1 mapping)
- After: Linear address translated via page tables
- CPU now uses MMU for all memory references

### 1.5 High Memory Jump (pre_init.c:242-243)

**File**: `minix/kernel/arch/i386/head.S` lines 83-91

**Code Before Paging**:
```
head.S:83 | call _C_LABEL(pre_init)     # Returns %eax = kinfo ptr
head.S:84                                # At this point, paging is ON
head.S:85 | mov $k_initial_stktop, %esp # Load kernel stack (high address)
head.S:86 | push $0                     # Stack terminator
head.S:87 | push %eax                   # kinfo pointer
head.S:88 | call _C_LABEL(kmain)        # Jump to high-memory kmain
```

**CPU State Transition**:
- Before: EIP < 0x80000000 (executing from physical 0x0001xxxx)
- Paging enabled (CR0.PG = 1)
- Still using low address range due to identity map
- Call pre_init (high address call after paging enabled)

**After Paging, Before kmain**:
- ESP = k_initial_stktop (0x80000000 + offset) - HIGH ADDRESS
- EIP = pre_init return (still low address)
- CPU MMU translates all addresses via page tables
- Next instruction (mov to %esp) uses high address

**Critical Point: Last instruction in low address space**:
After the call to pre_init returns, the CPU continues at the return address (still low address from before paging). The next instruction at head.S:85 loads ESP with a high address. This transition is safe because:
1. Paging is already enabled
2. Both low (0x0xxxxx) and high (0x8xxxxxx) addresses are mapped
3. No TLB flush needed (mappings created before paging enable)

### 1.6 New Stack Setup (head.S:85-88)

**Stack Preparation for kmain**:
```
ESP_old: 0x00006000 (approx, from load_stack_start)
ESP_new: 0x80000000 + k_initial_stktop_offset

Stack layout at kmain entry:
[ESP+0]:   Return address (never used, NULL_PROC never returns)
[ESP+4]:   kinfo_ptr = pointer to kinfo struct in data segment
[ESP+8]:   (reserved for any other parameters)
```

**Kernel Stack Location**:
- Virtual: 0x80000000 + k_initial_stktop offset
- Physical: 0x00000000 + offset (via PTE mapping)
- Size: typically 16KB or 32KB (per CPU)

---

## PHASE 2: KMAIN INITIALIZATION

### 2.1 Kmain Entry (main.c:158)

**File**: `minix/kernel/main.c`
**Function**: `void kmain(kinfo_t *local_cbi)`

```
main.c:158 void kmain(kinfo_t *local_cbi)
```

**Stack Frame at Entry**:
```
EBP = undefined (not yet set up)
ESP = k_initial_stktop (high address)
[ESP+0] = kinfo_ptr (parameter 1, calling convention)
```

**CPU State**:
- Ring 0 (kernel mode)
- Paging enabled, kernel mapped to 0x80000000
- Interrupts disabled (set in pre_init)
- GDT/IDT: loaded by bootloader (basic setup)
- TSS: may not be loaded yet

### 2.2 BSS Sanity Check (main.c:165-167)

```
main.c:165 static int bss_test;
main.c:166 assert(bss_test == 0);      # BSS not initialized by bootloader
main.c:167 bss_test = 1;                # Mark BSS as initialized
```

**Purpose**: Verify BSS section is zero-initialized (linker responsibility)

**CPU State During BSS Check**:
- Static data access via paging
- Linear address resolution via page tables
- ETI TLB miss handling (automatic in hardware)

### 2.3 Boot Parameters Copy (main.c:169-171)

```
main.c:169 memcpy(&kinfo, local_cbi, sizeof(kinfo));
main.c:170 memcpy(&kmess, kinfo.kmess, sizeof(kmess));
```

**Memory Copies**:
- Source: Parameter kinfo_t (passed on stack)
- Destination: Global kinfo struct (in .data segment)
- Size: ~4KB (multiboot_info_t + boot modules)

**Memory Layout After Copy**:
- Global `kinfo`: Contains boot parameters for rest of kernel
- Global `kmess`: Kernel message buffer for logging

### 2.4 Board Identification (main.c:173-176)

```
main.c:173 machine.board_id = get_board_id_by_name(env_get(BOARDVARNAME));
```

**Purpose**: Identify hardware board (Intel, ARM, etc)

**CPU State**:
- String operations via paging
- Function calls use CALL instruction
- Return uses RET (pops EIP from stack)

### 2.5 Serial Initialization (main.c:178-180)

```
main.c:178 #ifdef __arm__
main.c:179 arch_ser_init();         # ARM-specific serial setup
main.c:180 #endif
```

**On x86**: This is skipped (not ARM)

### 2.6 Memory Allocator Enable (main.c:183)

```
main.c:183 kernel_may_alloc = 1;
```

**Effect**: Kernel can now use memory allocation functions

**Critical Point**: VM (virtual memory manager) is not yet running. Memory allocation at this point uses pre-allocated pools.

### 2.7 cstart() Call (main.c:187)

**File**: `minix/kernel/arch/i386/protect.c`
**Function**: `void cstart(void)`

**Critical Kernel Setup in cstart()**:

#### 2.7.1 GDT Initialization

```
protect.c:200+ (cstart function initializes GDT)

struct segdesc_s gdt[GDT_SIZE] __aligned(DESC_SIZE);
```

**GDT Entries Created**:
1. Null descriptor (index 0)
2. Kernel CS (Ring 0)
3. Kernel DS (Ring 0)
4. User CS (Ring 3)
5. User DS (Ring 3)
6. TSS (Task State Segment)
7. LDT (Local Descriptor Table - per process)

**CPU Action**: Load GDT
```
lgdt gdt_pseudo_descriptor
```

**GDT Pseudo-Descriptor**:
```
Offset 0x80000000+k_gdt_base: 2 bytes = GDT size - 1
Offset 0x80000000+k_gdt_base+2: 4 bytes = GDT linear address
```

**CPU State After GDT Load**:
- GDTR now points to new GDT
- Segment selectors still valid (backward compatible)
- Privilege checks now use new GDT entries

#### 2.7.2 IDT Initialization

```
protect.c:250+ (cstart function initializes IDT)

struct gatedesc_s idt[IDT_SIZE] __aligned(DESC_SIZE);
```

**IDT Entries Created**:
- Exception handlers (0-31): divide by zero, page fault, etc
- Hardware interrupt handlers (32-47): IRQ0-15 from PIC
- Software interrupt (48): INT 0x30 (legacy)
- Reserved entries (49-255)

**Exception Handlers**:
```
0   #DE   Divide by zero
1   #DB   Debug breakpoint
2   NMI   Non-maskable interrupt
3   #BP   Breakpoint
4   #OF   Overflow
5   #BR   Bound range exceeded
6   #UD   Invalid opcode
7   #NM   Device not available (FPU)
8   #DF   Double fault
9        Reserved
10  #TS   Invalid TSS
11  #NP   Segment not present
12  #SS   Stack segment fault
13  #GP   General protection fault
14  #PF   Page fault
15       Reserved
16  #MF   FPU exception
17  #AC   Alignment check
18  #MC   Machine check
19  #XF   SIMD FP exception
20-31   Reserved/reserved
```

**Hardware Interrupt Handlers (32-47)**:
```
32-39:  Master PIC (IRQ 0-7)
        0: Timer (clock)
        1: Keyboard
        2: Cascade (PIC routing)
        3: Serial port 2
        4: Serial port 1
        5: Parallel port / Sound
        6: Floppy disk
        7: Parallel port / Spurious

40-47:  Slave PIC (IRQ 8-15)
        8: Real-time clock
        9: Redirected IRQ2
        10: Reserved
        11: Reserved
        12: PS/2 mouse
        13: FPU exception
        14: IDE/SATA disk
        15: Reserved
```

**Software Interrupt**:
```
48 (0x30):  MINIX IPC call (INT 0x30)
            User processes -> Kernel IPC system
```

**CPU Action**: Load IDT
```
lidt idt_pseudo_descriptor
```

#### 2.7.3 TSS Initialization

```
protect.c:280+ (cstart function sets up TSS)

struct tss_s tss[CONFIG_MAX_CPUS];
```

**TSS Fields Set**:
- ESP0: Kernel stack pointer (for Ring 3 -> Ring 0 transitions)
- SS0: Kernel stack segment
- EIP: Kernel entry point (for task switches)
- CS: Kernel code segment
- SS: Kernel data segment
- ES, DS: Kernel data segments

**Critical**: TSS.ESP0 = kernel stack location for each CPU

**CPU Action**: Load TSS
```
ltr tss_selector
```

#### 2.7.4 Segment Registers Setup

```
protect.c:300+ (Load kernel segment selectors)

mov $KERN_CS_SELECTOR, %eax
mov %eax, %cs       # Code segment -> kernel code

mov $KERN_DS_SELECTOR, %eax
mov %eax, %ds       # Data segment -> kernel data
mov %eax, %es       # Extra segment
mov %eax, %ss       # Stack segment
mov %eax, %fs       # FS segment
mov %eax, %gs       # GS segment
```

**Privilege Level**: All segments set to Ring 0

### 2.8 BKL (Big Kernel Lock) Acquisition (main.c:189)

```
main.c:189 BKL_LOCK();
```

**Purpose**: Single-threaded execution lock for SMP systems

**On UP (Uniprocessor)**: BKL_LOCK is a no-op
**On SMP**: Spin lock to serialize kernel access

### 2.9 Process Table Initialization (main.c:200)

**File**: `minix/kernel/proc.c`
**Function**: `void proc_init(void)`

**Operations**:
1. Clear all process table entries
2. Initialize endpoint mapping (PID -> endpoint translation)
3. Set up process table for all boot processes

**Process Table Entry Structure**:
```
struct proc {
  struct stackframe_s p_reg;    # Saved registers
  struct priv *p_priv;          # Privilege structure
  u32_t p_endpoint;             # IPC endpoint
  pid_t p_pid;                  # Process ID (kernel)
  short p_flags;                # Process flags
  short p_priority;             # Scheduling priority
  ...
};
```

**CPU State During Process Initialization**:
- Kernel running at privilege level 0
- Process table in .data segment (paged)
- No processes active yet
- All processes marked as NOT_RUNNABLE

### 2.10 Boot Module Setup (main.c:212-280)

**For Each Boot Module**:

```
main.c:225 for (i=0; i < NR_BOOT_PROCS; ++i) {
main.c:226   ip = &image[i];
main.c:227   rp = proc_addr(ip->proc_nr);
```

**Boot Modules** (from multiboot modules):
1. Task 0 = IDLE (idle loop, lowest priority)
2. Task 1 = CLOCK (timer interrupt handler)
3. Task 2 = SYSTEM (syscall dispatcher)
4. Process 0 = init (root user process)
5. Process 1+ = Servers (VFS, PM, NET, etc)

**Setup Per Process**:
1. Allocate process table entry
2. Assign endpoint (unique IPC identifier)
3. Set privilege structure
4. Initialize stack frame
5. Mark process as schedulable (RTS_PROC_STOP cleared)

**CPU State Per Process During Setup**:
- No CPU context switch yet
- Process table entry filled (register save area prepared)
- Stack pointer and frame pointer not yet used
- Each process will get control only via scheduler

### 2.11 Privilege Structure Setup (main.c:240-280)

**For Kernel Tasks**:
- IDLE: Lowest priority (CPU idle loop)
- CLOCK: High priority, timer handling
- SYSTEM: High priority, syscall dispatching

**For System Processes**:
- VFS: File system
- PM: Process manager
- MEMORY: Memory manager
- NET: Network stack
- Others: System services

**Privilege Levels**:
- Kernel tasks: Ring 0 (full kernel access)
- System processes: Ring 1 (restricted kernel calls)
- User processes: Ring 3 (application code)

### 2.12 Enable Timer Interrupts (main.c:45-60 in bsp_finish_booting)

**Function**: `void bsp_finish_booting(void)`

```
main.c:45 boot_cpu_init_timer(system_hz)
```

**Timer Setup**:
1. Configure PIT (Programmable Interval Timer)
   - Divisor = CPU_FREQ / system_hz
   - For 100 Hz timer: divisor = 11932 (at 1.1932 MHz)
2. Load timer divisor into PIT
3. Enable timer interrupt (IRQ0)
4. Enable interrupts on CPU (EFLAGS.IF = 1)

**PIT I/O Ports**:
```
0x40: Channel 0 data port (timer)
0x41: Channel 1 data port
0x42: Channel 2 data port
0x43: Control register

Divisor = Clock frequency / Desired frequency
For 100 Hz: divisor = 1193180 / 100 = 11931 (0x2E4B)
```

**CPU Instruction Sequence for Timer Enable**:
```
mov $11931, %eax       # Divisor for 100 Hz
mov $0x43, %edx        # PIT control port
mov $0x34, %al         # Command: channel 0, LSB then MSB
out %al, %edx          # Write control

mov $11931, %eax       # Divisor value
mov $0x40, %edx        # Channel 0 data port
out %al, %edx          # LSB of divisor
mov %ah, %al
out %al, %edx          # MSB of divisor

# Enable interrupts
sti                    # Set interrupt flag (EFLAGS.IF = 1)
```

**CPU State After Timer Enable**:
- EFLAGS.IF = 1 (interrupts enabled)
- Next timer interrupt will jump to hwint00 handler
- Clock tick every 10ms (100 Hz)

### 2.13 FPU Initialization (main.c:65-70)

```
main.c:65 fpu_init();
```

**FPU Setup**:
1. Check if FPU is present (CPUID.EDX.FPU bit)
2. Set CR0.EM bit (trap FPU instructions if not present)
3. Set CR0.NE bit (native error handling)
4. Initialize floating point state

**CPU State After FPU Init**:
- CR0.EM = 1 if no FPU (FPU instructions cause exception 7)
- CR0.NE = 1 (exceptions instead of interrupt)
- FPU state undefined (will be loaded on first use)

### 2.14 Schedule First Process (main.c:50-55)

```
main.c:50 for (i=0; i < NR_BOOT_PROCS - NR_TASKS; i++) {
main.c:51   RTS_UNSET(proc_addr(i), RTS_PROC_STOP);
main.c:52 }
```

**Effect**: Mark all boot processes as ready to run

**Process Queue After Scheduling**:
```
Priority 0 (Highest):   IDLE, CLOCK, SYSTEM
Priority 1:             PM, VFS, MEMORY
Priority 2:             User processes
...
Priority 15 (Lowest):   IDLE loop (fallback)
```

### 2.15 Switch to User Mode (main.c:72)

```
main.c:72 switch_to_user();
```

**Function Location**: `minix/kernel/arch/i386/mpx.S`

**Critical Transition: Ring 0 -> Ring 3**

```
mpx.S:???  ENTRY(switch_to_user)

# Pick next process from scheduler
call _C_LABEL(pick_proc)      # Returns process ptr in %eax

# Load process context
mov %eax, %ebp                # EBP = process pointer
RESTORE_GP_REGS(%ebp)         # Restore EAX, EBX, ECX, EDX, ESI, EDI
...

# Restore segment registers (user selectors)
mov $USER_DS_SELECTOR, %eax
mov %eax, %ds
mov %eax, %es
mov %eax, %ss

# Jump to user code via IRET
iret                          # Pop CS, EIP, EFLAGS (Ring 3)
                              # Load user CS/DS/SS from selectors
                              # Transfer control to user process
```

**CPU State During IRET**:
- Before: Ring 0, kernel stack active
- After: Ring 3, user stack active
- CS, DS, SS loaded from process structure
- EIP points to first user process instruction

---

## PHASE 3: PROCESS SCHEDULING AND CONTEXT SWITCHING

### 3.1 Scheduler (switch_to_user continuation)

After the first IRET in switch_to_user, the CPU is running the first process in Ring 3.

**Process State at First Run**:
```
Process: IDLE
PC: 0x?????? (idle loop entry point)
SP: user stack pointer
Privilege: Ring 3
Stack: User stack, TOS points to user data
Registers: Restored from process table
```

### 3.2 Timer Interrupt (after 10ms)

**Event**: PIT fires, IRQ0 asserted

**CPU Actions** (automatic, hardware):
1. Check if interrupts enabled (EFLAGS.IF = 1) - YES
2. Acknowledge interrupt (set INTR line low)
3. Lookup IDT entry 32 (hwint00)
4. Load from IDT: CS, EIP, type, privilege
5. Save on kernel stack: SS, ESP (from TSS.ESP0), EFLAGS, CS, EIP
6. Load new CS, EIP from IDT
7. Jump to hwint00 (kernel code)

**Stack After Interrupt** (kernel stack):
```
[ESP+0]:  EIP (user process instruction pointer)
[ESP+4]:  CS  (user code selector)
[ESP+8]:  EFLAGS (with IF still set)
[ESP+12]: ESP (user stack pointer)
[ESP+16]: SS  (user stack selector)
```

### 3.3 hwint00 Handler (mpx.S:74-95 macro)

**Entry**: hwint00 (hardware interrupt handler)

```
mpx.S:74 ENTRY(hwint00)
mpx.S:75 hwint_master(0)
```

**Macro Expansion** (hwint_master macro):

```
TEST_INT_IN_KERNEL(4, 0f)   # Check if interrupted in kernel

SAVE_PROCESS_CTX(0, KTS_INT_HARD)  # Save all registers to proc table
push %ebp
movl $0, %ebp
call _C_LABEL(context_stop)
add $4, %esp
PIC_IRQ_HANDLER(0)          # Call irq_handle(0)
movb $END_OF_INT, %al
outb $INT_CTL               # Send EOI to PIC
jmp _C_LABEL(switch_to_user)  # Pick next process
```

**SAVE_PROCESS_CTX Macro** (sconst.h):

```
sconst.h:75 #define SAVE_PROCESS_CTX(displ, trapcode)

cld                         # Clear direction flag
push %ebp

# Get process pointer (saved on stack during int)
movl (CURR_PROC_PTR + 4 + displ)(%esp), %ebp

# Save general registers
SAVE_GP_REGS(%ebp)          # Save EAX, ECX, EDX, EBX, ESI, EDI
movl $KTS_INT_HARD, P_KERN_TRAP_STYLE(%ebp)
pop %esi
mov %esi, BPREG(%ebp)       # Save EBP

# Restore kernel segments
RESTORE_KERNEL_SEGS         # DS, ES, FS, GS = kernel selectors

# Save trap context (EIP, CS, EFLAGS, ESP from stack)
SAVE_TRAP_CTX(displ, %ebp, %esi)
```

**CPU Registers Saved** (in proc table):
```
AXREG:  EAX value at interrupt
BXREG:  EBX
CXREG:  ECX
DXREG:  EDX
SIREG:  ESI
DIREG:  EDI
BPREG:  EBP
PCREG:  EIP (instruction interrupted)
CSREG:  CS  (code segment)
PSWREG: EFLAGS
SPREG:  ESP (stack pointer)
```

**PIC EOI Sequence**:
```
movb $END_OF_INT, %al       # Value = 0x20
outb $INT_CTL               # OUT 0x20, AL  (master PIC port)
```

**PIC Timing**:
- IRQ acknowledged immediately upon entry to hwint00
- EOI sent after C handler (irq_handle) completes
- Allows next interrupt during handler if priority allows

### 3.4 Interrupt Handler (irq_handle)

**Function**: `void irq_handle(int irq)`

**For Timer Interrupt (IRQ0/hwint00)**:
```
interrupt.c:???
if (irq == 0) {              # CLOCK interrupt
  get_cpulocal_var(ticks)++;
  update_process_times();
  if (time_slice_expired()) {
    set_reschedule_flag();
  }
}
```

**CPU Context During Handler**:
- Ring 0 (kernel mode)
- Kernel stack active (ESP = kernel stack)
- Segment registers = kernel selectors
- User process context saved in proc table
- EBP = 0 (for stack trace termination)

### 3.5 Return from Interrupt (jmp switch_to_user)

**After irq_handle returns**, hwint_master macro jumps to switch_to_user

**switch_to_user does**:
1. Call pick_proc() - select next process to run
2. Restore process context from proc table
3. Execute IRET - return to Ring 3

**IRET Instruction** (final step):
```
iret                        # Pop EIP, CS, EFLAGS (if Ring change)
                            # Also pop ESP, SS if Ring change
```

**CPU Automatic Actions on IRET**:
- Check CPL (current privilege level) in popped CS
- If CPL < old CPL: stack switch (use popped ESP, SS)
- Pop EFLAGS, reload IF/TF/NT/IOPL/AC from EFLAGS
- If returning to user mode: switch back to user stack
- Load user DS, ES, FS, GS if needed
- Jump to user code at new EIP

**Final CPU State After IRET**:
- EIP: New process instruction pointer
- ESP: New process stack pointer
- CS: User code selector (Ring 3)
- DS, ES, SS: User selectors
- EFLAGS: Restored from interrupt context
- All general registers: Restored from proc table

---

## CRITICAL CPU STATE TRANSITIONS SUMMARY

### Transition 1: Bootstrap -> Protected Mode (head.S)
- **From**: Real mode, bootloader control
- **To**: Protected mode (Ring 0)
- **Key**: GDT loaded, paging optional

### Transition 2: Low Memory -> High Memory (head.S -> pre_init -> kmain)
- **From**: Executing at 0x0000xxxx with 1:1 mapping
- **To**: Executing at 0x8000xxxx with page tables
- **Key**: Paging enabled, kernel remapped to high address

### Transition 3: Kernel Setup -> Interrupts Enabled (cstart -> bsp_finish_booting)
- **From**: No GDT/IDT, no timer, interrupts disabled (EFLAGS.IF=0)
- **To**: GDT/IDT loaded, timer running, interrupts enabled (EFLAGS.IF=1)
- **Key**: EFLAGS.IF = 1 enables all maskable interrupts

### Transition 4: Kernel Mode -> User Mode (switch_to_user first call)
- **From**: Ring 0, kernel stack, kernel code
- **To**: Ring 3, user stack, user code
- **Key**: IRET pops CS with lower privilege level

### Transition 5: User Mode -> Kernel Mode (hwint00 on timer)
- **From**: Ring 3, user stack, arbitrary user code
- **To**: Ring 0, kernel stack, interrupt handler
- **Key**: CPU automatic on hardware interrupt (no privilege check)

### Transition 6: Back to User Mode (after interrupt)
- **From**: Ring 0, kernel stack, interrupt handler
- **To**: Ring 3, user stack, interrupted code
- **Key**: IRET restores full context saved at interrupt entry

---

## CPU REGISTER STATE AT CRITICAL POINTS

### State 1: Boot Entry (head.S:40)
```
EIP:    0x00100xxx (bootloader-provided)
ESP:    0x00000xxx (bootloader-provided)
EBP:    undefined
CS:     bootloader selector (likely 0x08)
DS/ES:  bootloader selector
SS:     bootloader selector
CR0:    PE=1 (protected mode), PG=0 (no paging)
CR3:    undefined (paging disabled)
EFLAGS: bootloader state (IF=0 usually)
```

### State 2: After pre_init, Before kmain
```
EIP:    0x80000xxx (high address, first line of kmain)
ESP:    0x80000xxx (k_initial_stktop, high address)
EBP:    0x00000000 (set by head.S:75)
CS:     0x08 (kernel code)
DS/ES:  0x10 (kernel data)
SS:     0x10 (kernel data)
CR0:    PE=1, PG=1 (protected mode + paging)
CR3:    0x00001000 (page directory address)
GDTR:   GDT base address (loaded by pre_init)
IDTR:   IDT base address (loaded by cstart)
EFLAGS: IF=0 (interrupts disabled)
```

### State 3: After cstart, Before Timer Enable
```
EIP:    0x80000xxx (kmain, after cstart call)
ESP:    0x80000xxx (kernel stack)
GDT:    Fully initialized (Ring 0, Ring 3 selectors)
IDT:    Fully initialized (31 exception + 16 IRQ handlers)
TSS:    Loaded (TR = TSS selector)
TR:     0x28 (TSS selector in GDT)
EFLAGS: IF=0 (interrupts still disabled)
```

### State 4: After Timer Enable (first user process runs)
```
EIP:    0x3000xxxx (IDLE process first instruction, Ring 3)
ESP:    0x1f000xxx (IDLE user stack, Ring 3)
CS:     0x1b (user code selector, DPL=3)
DS/ES:  0x23 (user data selector, DPL=3)
SS:     0x23 (user stack selector, DPL=3)
CPL:    3 (current privilege level, Ring 3)
EFLAGS: IF=1 (interrupts enabled)
```

### State 5: Timer Interrupt (in hwint00)
```
EIP:    0x80000xxx (hwint00 entry point, Ring 0)
ESP:    0x80000xxx (kernel stack, Ring 0)
CS:     0x08 (kernel code, DPL=0)
DS/ES:  0x10 (kernel data)
SS:     0x10 (kernel stack)
CPL:    0 (kernel mode, Ring 0)
EFLAGS: IF=0 (interrupts disabled upon interrupt)
```

### State 6: Back to User Mode (after IRET from interrupt)
```
EIP:    0x3000xxxx (user process instruction, same as before interrupt)
ESP:    0x1f000xxx (user stack, same as before interrupt)
CS:     0x1b (user code, DPL=3)
DS/ES:  0x23 (user data)
SS:     0x23 (user stack)
CPL:    3 (Ring 3)
EFLAGS: IF=1 (interrupts re-enabled)
```

---

## CONCLUSION

The MINIX 3.4 boot sequence implements a clean, layered transition from bootloader-provided protection to full kernel initialization:

1. **Phase 0**: Bootloader provides protected mode, GDT, and basic memory setup
2. **Phase 1**: pre_init sets up memory mapping and paging infrastructure
3. **Phase 2**: kmain initializes process table, interrupts, and scheduling
4. **Phase 3**: switch_to_user transfers control to first process (Ring 0 -> Ring 3)
5. **Ongoing**: Interrupt handlers manage context switches and system calls

**Key CPU Interactions**:
- Memory management: 1:1 mapping -> paged memory
- Privilege levels: Ring 0 (kernel) -> Ring 3 (user)
- Interrupts: Disabled -> Enabled
- Context: Single execution context -> Multi-process scheduling

Each transition is carefully managed to maintain kernel invariants and enable proper multi-tasking.
