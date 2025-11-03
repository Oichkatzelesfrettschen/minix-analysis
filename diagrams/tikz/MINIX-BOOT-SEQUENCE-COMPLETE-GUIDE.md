# MINIX 3.4.0 Complete Boot Sequence Guide
## From GRUB Bootloader to Userspace Execution

**Purpose**: Comprehensive pedagogical walkthrough of MINIX boot process
**Scope**: Kernel entry (kmain), privilege transitions, and userspace servers
**Audience**: Operating systems students, MINIX researchers, systems programmers
**Diagrams**: Three complementary TikZ visualizations (530 KB total)

---

## Overview: Three-Part Documentation Strategy

This guide uses three complementary diagrams to teach the MINIX boot process:

1. **boot-sequence-complete.pdf** (142 KB)
   - **Level**: Overview / Big Picture
   - **Shows**: 4 boot phases from GRUB to userspace
   - **Use**: Start here for high-level understanding

2. **kmain-initialization-detailed.pdf** (205 KB)
   - **Level**: Detailed / Implementation
   - **Shows**: 12-step kmain() initialization process
   - **Use**: Deep dive into kernel setup

3. **kernel-to-userspace-transition.pdf** (183 KB)
   - **Level**: Critical Transition / Architecture
   - **Shows**: Ring 0 → Ring 3 privilege change mechanism
   - **Use**: Understand x86 protection and IRET instruction

**Total**: 530 KB of detailed, source-referenced visualizations

---

## The Boot Process: Four Phases

### Phase 1: Bootloader (GRUB)
**Duration**: ~500ms
**Privilege Level**: Real mode → Protected mode
**Key Events**:

```
BIOS POST
  ↓
Master Boot Record (MBR)
  ↓
GRUB Stage 1 (boot.img in MBR)
  ↓
GRUB Stage 2 (core.img, reads grub.conf)
  ↓
Load kernel image to 0x100000 (1 MB physical)
  ↓
Multiboot handoff (EBX = multiboot_info struct)
  ↓
Jump to kernel entry: kmain()
```

**Multiboot Info Structure** contains:
- Boot command line
- Memory map (usable, reserved, ACPI)
- Boot modules (servers: PM, RS, VM, VFS, etc.)
- Framebuffer info (if present)

**Source Reference**: kernel/arch/i386/pre_init.c (multiboot entry point)

**Diagram**: boot-sequence-complete.pdf (Phase 1)

---

### Phase 2: Kernel Initialization (kmain)
**Duration**: 50-200ms
**Privilege Level**: Ring 0 (kernel mode)
**Entry Point**: `void kmain(kinfo_t *local_cbi)` at kernel/main.c:115

**12-Step Initialization Process**:

#### Step 1: BSS Sanity Check (main.c:123-125)
```c
assert(bss_test == 0);  // Verify zero-initialized section
bss_test = 1;           // Prevent re-entry
```
**Purpose**: Catch bootloader errors in memory initialization

#### Step 2: Copy Boot Parameters (main.c:128-129)
```c
memcpy(&kinfo, local_cbi, sizeof(kinfo));  // Boot info
memcpy(&kmess, kinfo.kmess, sizeof(kmess)); // Kernel messages
```
**Purpose**: Preserve multiboot info before memory is reallocated

#### Step 3: cstart() - Low-Level Initialization (main.c:147)
**Substeps**:
```c
prot_init();    // GDT, IDT, TSS setup
init_clock();   // PIT/APIC timer
env_get();      // Boot parameters (no_apic, no_smp)
intr_init(0);   // Interrupt controllers
arch_init();    // x86-specific (FPU, CPUID)
```

**GDT Layout** (Global Descriptor Table):
```
Index  Selector  Type        DPL  Description
0x00   0x00      NULL        -    Null descriptor
0x08   0x08      Code        0    Kernel code segment
0x10   0x10      Data        0    Kernel data segment
0x18   0x1B      Code        3    User code segment (RPL=3)
0x20   0x23      Data        3    User data segment (RPL=3)
0x28   0x28      TSS         0    Task State Segment
```

**IDT Setup** (Interrupt Descriptor Table):
- 256 entries (0x00-0xFF)
- Handlers for: exceptions (0-31), IRQs (32-47), syscalls (0x33)

#### Step 4: BKL_LOCK() - Acquire Big Kernel Lock (main.c:149)
**Purpose**: SMP safety (only on CONFIG_SMP builds)
**Effect**: Prevent other CPUs from running kernel code simultaneously

#### Step 5: proc_init() - Initialize Process Table (main.c:157)
```c
// Clear all process slots
for (rp = BEG_PROC_ADDR; rp < END_PROC_ADDR; ++rp) {
    rp->p_rts_flags = RTS_SLOT_FREE;
    rp->p_magic = PMAGIC;
    // Set up endpoint mapping
}
```

**Process Table Structure**:
- Size: NR_PROCS (256 on i386)
- Layout: [Kernel tasks | System processes | User processes]
- Indices: Negative for tasks, 0+ for processes

#### Step 6: IPCF_POOL_INIT() - IPC Filter Pool (main.c:158)
**Purpose**: Message filtering for security
**Mechanism**: Bitmap of allowed IPC targets per process

#### Step 7: Boot Image Loop - Process Creation (main.c:165-272)
**Iterates**: i = 0 to NR_BOOT_PROCS (kernel tasks + servers)

**For each process**:
```c
ip = &image[i];              // Get boot image entry
rp = proc_addr(ip->proc_nr); // Get process slot

// Copy name (tasks only)
if (ip->proc_nr < 0)
    strncpy(rp->p_name, ip->proc_name, P_NAME_LEN);

// Set endpoint
rp->p_endpoint = ip->endpoint;

// Privilege assignment
if (iskerneln(proc_nr) || isrootsysn(proc_nr) || proc_nr == VM_PROC_NR) {
    // Kernel task, root system process, or VM
    get_priv(rp, static_priv_id(proc_nr));
    priv(rp)->s_flags |= TASK_F | VM_F | RSYS_F;
    priv(rp)->s_trap_mask = KERNEL_TRAP_MASK;
    fill_sendto_mask(rp, &priv(rp)->s_ipc_to);
    set_kernel_call_mask(rp);
} else {
    // Regular process - no privileges yet
    RTS_SET(rp, RTS_NO_PRIV | RTS_NO_QUANTUM);
}

// Architecture-specific setup
arch_boot_proc(ip, rp);

// Set scheduling flags
rp->p_rts_flags |= RTS_VMINHIBIT;    // Wait for VM pagetable
rp->p_rts_flags |= RTS_BOOTINHIBIT;  // Wait for boot completion
rp->p_rts_flags |= RTS_PROC_STOP;    // Held until ready
rp->p_rts_flags &= ~RTS_SLOT_FREE;   // Slot is in use
```

**Boot Image Contents** (typical):
```
Index  Process        Type           Endpoint
  -5   IDLE           Kernel task    IDLE
  -4   CLOCK          Kernel task    CLOCK
  -3   SYSTEM         Kernel task    SYSTEM
  -2   HARDWARE       Kernel task    HARDWARE
  -1   (unused)
   0   PM             System server  PM
   1   VFS            System server  VFS
   2   RS             System server  RS
   3   VM             System server  VM
   4   LOG            Driver         LOG
   5   TTY            Driver         TTY
   6   MFS            Server         MFS
   7   PFS            Server         PFS
   8   SCHED          Scheduler      SCHED
   9   (more drivers and servers...)
```

#### Step 8: arch_post_init() (main.c:283)
**Purpose**: Final architecture-specific initialization
**Example (i386)**: Set up local APIC if CONFIG_SMP

#### Step 9: Register IPC Call Names (main.c:285-290)
```c
IPCNAME(SEND);
IPCNAME(RECEIVE);
IPCNAME(SENDREC);
IPCNAME(NOTIFY);
IPCNAME(SENDNB);
IPCNAME(SENDA);
```
**Purpose**: Debugging - map IPC call numbers to names for tracing

#### Step 10: System Subsystem Init (main.c:293-296)
```c
memory_init();  // Initialize memory allocator
system_init();  // Initialize kernel call handlers
```

**memory_init()**: Set up kernel heap, DMA zones
**system_init()**: Register kernel call table (sys_call_table[])

#### Step 11: Free Bootstrap Memory (main.c:301)
```c
add_memmap(&kinfo, kinfo.bootstrap_start, kinfo.bootstrap_len);
```
**Purpose**: Reclaim memory used by bootloader
**Effect**: Memory becomes available for VM to allocate

#### Step 12: Finish Booting (main.c:316 or 324)
**On SMP**: Call `smp_init()` to start other CPUs
**On UP**: Go directly to `bsp_finish_booting()`

**bsp_finish_booting()** (main.c:38-109):
```c
cpu_identify();               // CPUID detection
vm_running = 0;               // VM not started yet
krandom.random_sources = ...  // RNG setup
proc_ptr = &idle_proc;        // Set idle as current
announce();                   // Print "MINIX 3.4.0 ..."

// Unblock all boot processes (except tasks)
for (i=0; i < NR_BOOT_PROCS - NR_TASKS; i++)
    RTS_UNSET(proc_addr(i), RTS_PROC_STOP);

cycles_accounting_init();     // CPU accounting
boot_cpu_init_timer(system_hz); // Start timer interrupts
fpu_init();                   // FPU/SSE setup
cpu_set_flag(bsp_cpu_id, CPU_IS_READY);
kernel_may_alloc = 0;         // No more kernel alloc

// CRITICAL: Switch to Ring 3
switch_to_user();  // NEVER RETURNS
NOT_REACHABLE;
```

**Diagram**: kmain-initialization-detailed.pdf (complete 12 steps)

---

### Phase 3: Ring 0 → Ring 3 Transition (switch_to_user)
**Duration**: < 1ms (single instruction)
**Privilege Level**: Ring 0 → Ring 3
**Mechanism**: IRET (Interrupt Return) instruction

**Before IRET** (Ring 0 state):
```
CPL = 0 (Current Privilege Level)
CS  = KERNEL_CS (0x08) - Code Segment, DPL=0, RPL=0
DS  = KERNEL_DS (0x10) - Data Segment, DPL=0, RPL=0
SS  = KERNEL_DS (0x10) - Stack in kernel space
ESP = Kernel stack pointer
```

**Assembly Code** (arch/i386/mpx.S):
```asm
switch_to_user:
    ; Get current process pointer
    mov eax, [proc_ptr]

    ; Load user data segments FIRST (before IRET)
    mov cx, USER_DS_SELECTOR | 3   ; 0x20 | 3 = 0x23 (RPL=3)
    mov ds, cx
    mov es, cx
    mov fs, cx
    mov gs, cx

    ; Build IRET stack frame (5 values pushed in order)
    push USER_DS_SELECTOR | 3      ; SS  (0x23)
    push [eax + P_STACKTOP]        ; ESP (user stack pointer)
    pushf                           ; EFLAGS (IF=1, interrupts enabled)
    push USER_CS_SELECTOR | 3      ; CS  (0x1B)
    push [eax + P_PC]              ; EIP (user entry point, usually _start)

    ; Atomic privilege transition
    iret   ; Pop CS, EIP, EFLAGS, SS, ESP
           ; CPL changes from 0 to 3 (Ring 0 → Ring 3)
```

**IRET Privilege Checks** (performed by CPU):
1. New CS.DPL must be >= current CPL (3 >= 0: OK)
2. New SS.DPL must equal new CS.DPL (both 3: OK)
3. New SS.RPL must equal new CS.RPL (both 3: OK)
4. Stack switch occurs if CPL changes (0→3: switch to user stack)
5. Interrupts re-enabled if EFLAGS.IF=1

**After IRET** (Ring 3 state):
```
CPL = 3 (Current Privilege Level)
CS  = USER_CS (0x1B) - Code Segment, DPL=3, RPL=3
DS  = USER_DS (0x23) - Data Segment, DPL=3, RPL=3
SS  = USER_DS (0x23) - Stack in user space
ESP = User stack pointer (from process->p_reg.sp)
EIP = User entry point (from process->p_reg.pc, usually _start)
```

**What User Process Cannot Do** (Ring 3 restrictions):
- Execute privileged instructions (HLT, CLI, STI, LGDT, LIDT, etc.)
- Access I/O ports directly (unless IOPL=3 in EFLAGS)
- Modify control registers (CR0, CR3, CR4)
- Access kernel memory (enforced by paging)
- Change privilege level (must use INT 0x33 syscall)

**What User Process Can Do**:
- Execute non-privileged instructions
- Access own memory (via page tables)
- Make system calls (INT 0x33, SYSENTER, SYSCALL)
- Receive signals from kernel
- Wait on IPC messages

**Diagram**: kernel-to-userspace-transition.pdf (complete Ring 0→3 flow)

---

### Phase 4: Userspace Server Initialization
**Duration**: 100-500ms
**Privilege Level**: Ring 3 (user mode)
**Entry Points**: main() in each server

**Server Startup Order** (typical):
1. PM (Process Manager) - first to run
2. RS (Reincarnation Server) - monitors all others
3. VM (Virtual Memory) - page fault handler
4. VFS (Virtual File System) - file operations
5. Drivers (TTY, Storage, Network)
6. SCHED (Scheduler) - CPU time management
7. MFS/PFS - Filesystem implementations

**Common Server Pattern** (SEF Framework):

```c
// Example: PM (servers/pm/main.c)
int main(void) {
    // SEF (Self-healing Framework) initialization
    sef_local_startup();

    // Infinite message loop
    while (TRUE) {
        // Wait for message
        if (sef_receive_status(ANY, &m_in, &ipc_status) != OK)
            panic("PM sef_receive_status error");

        // Check for notifications (clock, signals)
        if (is_ipc_notify(ipc_status)) {
            if (_ENDPOINT_P(m_in.m_source) == CLOCK)
                expire_timers(m_in.m_notify.timestamp);
            continue;
        }

        // Handle message
        who_e = m_in.m_source;
        call_nr = m_in.m_type;

        // Dispatch to handler
        if (IS_PM_CALL(call_nr)) {
            result = (*call_vec[call_index])();
        }

        // Send reply
        if (result != SUSPEND)
            reply(who_p, result);
    }
    return OK;  // Never reached
}
```

**SEF Framework Functions**:
- `sef_local_startup()`: Register callbacks, wait for READY signal
- `sef_cb_init_fresh()`: First-time initialization
- `sef_cb_signal_handler()`: Handle crash/restart signals
- `sef_receive_status()`: Receive with status (notification or call)

**Server Responsibilities**:

| Server | Purpose | Key Functions |
|--------|---------|---------------|
| PM | Process management | fork(), exec(), exit(), wait(), signal handling |
| RS | Service monitoring | restart crashed servers, update running services |
| VM | Virtual memory | page fault handling, mmap(), brk(), cache |
| VFS | File operations | open(), read(), write(), mount(), path resolution |
| SCHED | Scheduling | set priority, CPU time accounting, load balancing |
| TTY | Terminal I/O | keyboard input, screen output, line discipline |
| MFS | MINIX filesystem | inode management, block allocation, directories |
| PFS | Pipe filesystem | UNIX pipes, FIFOs |

**First User Process**: /sbin/init (PID 1)
- Started by VFS after root filesystem mounted
- Reads /etc/rc configuration
- Starts system daemons
- Spawns login shells

**Diagram**: boot-sequence-complete.pdf (Phases 3-4)

---

## Critical Data Structures

### 1. kinfo_t (kernel/kernel.h)
```c
typedef struct kinfo {
    phys_bytes code_base;      // Kernel code start
    phys_bytes code_size;
    phys_bytes data_base;      // Kernel data start
    phys_bytes data_size;

    vir_bytes user_sp;         // User stack top
    vir_bytes user_end;        // User data limit

    int nr_procs;              // Total process slots
    int nr_tasks;              // Number of kernel tasks

    struct boot_image *boot_image; // Boot image table

    multiboot_info_t mbi;      // Multiboot info
    struct memory mem[NR_MEMS]; // Memory map

    char release[6];           // "3.4.0"
    char version[6];           // Build version
} kinfo_t;
```

### 2. proc (kernel/proc.h)
```c
struct proc {
    struct stackframe_s p_reg; // Saved registers (including EIP, ESP)
    proc_nr_t p_nr;            // Process slot number
    endpoint_t p_endpoint;     // Unique identifier
    char p_name[P_NAME_LEN];   // Process name

    int p_rts_flags;           // Scheduling flags
    int p_priority;            // Scheduling priority
    int p_quantum_ms;          // CPU time quantum

    struct priv *p_priv;       // Privileges (if any)

    reg_t p_seg[NR_SEGS];      // Segment selectors

    // Message passing
    endpoint_t p_sendto_e;     // Send target
    endpoint_t p_getfrom_e;    // Receive source
    message *p_msgptr;         // Message buffer
};
```

**RTS Flags** (Ready-To-Schedule):
```c
#define RTS_SLOT_FREE      0x01  // Slot unused
#define RTS_PROC_STOP      0x02  // Process stopped
#define RTS_SENDING        0x04  // Blocked sending
#define RTS_RECEIVING      0x08  // Blocked receiving
#define RTS_SIGNALED       0x10  // Signal pending
#define RTS_SIG_PENDING    0x20  // Signal handler queued
#define RTS_P_STOP         0x40  // Stopped by parent
#define RTS_NO_PRIV        0x80  // No privileges assigned
#define RTS_NO_QUANTUM    0x100  // No CPU time quantum
#define RTS_VMINHIBIT     0x200  // Wait for VM pagetable
#define RTS_PAGEFAULT     0x400  // Handling page fault
#define RTS_VMREQUEST     0x800  // VM request pending
#define RTS_BOOTINHIBIT  0x1000  // Wait for boot completion
```

**Process is runnable** when: `p_rts_flags == 0`

### 3. priv (kernel/priv.h)
```c
struct priv {
    proc_nr_t s_proc_nr;       // Process slot number
    int s_flags;               // Privilege flags (TASK_F, VM_F, RSYS_F)

    short s_trap_mask;         // Allowed exception handlers
    sys_map_t s_ipc_to;        // Bitmap of IPC targets
    bitchunk_t s_k_call_mask[SYS_CALL_MASK_SIZE]; // Allowed kernel calls

    endpoint_t s_notify_pending; // Pending notifications
    irq_id_t s_irq_id;         // IRQ ownership (if driver)
};
```

**Privilege Flags**:
```c
#define TASK_F      0x01  // Kernel task
#define VM_F        0x02  // Virtual Memory server
#define RSYS_F      0x04  // Root system process
#define USER_F      0x08  // User process
```

### 4. boot_image[] (kernel/table.c)
```c
struct boot_image {
    proc_nr_t proc_nr;         // Process slot number
    endpoint_t endpoint;       // Endpoint identifier
    char proc_name[P_NAME_LEN]; // Name (for tasks)

    // Executable info (for processes)
    Elf32_Phdr *phdr;          // Program headers
    Elf32_Addr entry;          // Entry point (_start)
    Elf32_Word phnum;          // Number of program headers
};

// Example entries
struct boot_image image[] = {
    { IDLE,    IDLE,    "idle"   },  // Kernel task
    { CLOCK,   CLOCK,   "clock"  },  // Kernel task
    { SYSTEM,  SYSTEM,  "system" },  // Kernel task
    { PM,      PM_EP,   NULL, ... }, // PM server
    { VFS,     VFS_EP,  NULL, ... }, // VFS server
    // ... more entries
};
```

---

## System Call Mechanism (Ring 3 → Ring 0)

**User Process Needs Kernel Service**:

```
User code (Ring 3)
    ↓
INT 0x33 (legacy) or SYSENTER (Intel) or SYSCALL (AMD)
    ↓
Privilege change: CPL 3 → 0
    ↓
Kernel syscall handler (Ring 0)
    ↓
Process system call (do_fork, do_exec, etc.)
    ↓
IRET or SYSEXIT/SYSRET
    ↓
Privilege change: CPL 0 → 3
    ↓
Return to user code (Ring 3)
```

**INT 0x33 Mechanism** (legacy, always supported):
1. User: `int 0x33` instruction
2. CPU: Look up IDT entry 0x33
3. CPU: Verify privilege (DPL <= CPL)
4. CPU: Switch to kernel stack (from TSS)
5. CPU: Push SS, ESP, EFLAGS, CS, EIP
6. CPU: Set CPL=0, jump to kernel handler
7. Kernel: Save registers, dispatch to syscall
8. Kernel: Restore registers, IRET

**SYSENTER/SYSEXIT Mechanism** (Intel fast path):
- No IDT lookup, no stack switch overhead
- Kernel entry: MSR-configured address (IA32_SYSENTER_EIP)
- Kernel stack: MSR-configured (IA32_SYSENTER_ESP)
- Faster than INT (fewer checks)

**SYSCALL/SYSRET Mechanism** (AMD fast path):
- Similar to SYSENTER but different MSRs
- Entry: MSR IA32_LSTAR (Long mode SYSCALL Target Address Register)

---

## Boot Timeline Summary

| Time | Phase | Event | Privilege |
|------|-------|-------|-----------|
| 0ms | Bootloader | BIOS POST | Real mode |
| +100ms | Bootloader | GRUB Stage 2 | Protected mode (Ring 0) |
| +200ms | Bootloader | Load kernel to 1 MB | Protected mode |
| +300ms | Bootloader | Multiboot handoff | Protected mode |
| +350ms | Kernel | kmain() entry | Ring 0 |
| +360ms | Kernel | cstart() - GDT/IDT | Ring 0 |
| +370ms | Kernel | proc_init() | Ring 0 |
| +380ms | Kernel | Boot image loop | Ring 0 |
| +450ms | Kernel | bsp_finish_booting() | Ring 0 |
| +500ms | Kernel | switch_to_user() (IRET) | Ring 0 → Ring 3 |
| +550ms | Servers | PM main() | Ring 3 |
| +600ms | Servers | RS main() | Ring 3 |
| +650ms | Servers | VM main() | Ring 3 |
| +700ms | Servers | VFS main() | Ring 3 |
| +800ms | Userspace | /sbin/init | Ring 3 |
| +1000ms | Userspace | /bin/sh | Ring 3 |

**Total Boot Time**: 1-3 seconds (hardware dependent)

---

## Source File Reference Map

| Concept | File | Lines | Description |
|---------|------|-------|-------------|
| Kernel entry | kernel/main.c | 115-328 | kmain() function |
| Low-level init | kernel/main.c | 403-475 | cstart() function |
| Boot completion | kernel/main.c | 38-109 | bsp_finish_booting() |
| Ring transition | arch/i386/mpx.S | ~300 | switch_to_user() |
| PM server | servers/pm/main.c | 50-110 | Process Manager main loop |
| RS server | servers/rs/main.c | 38-131 | Reincarnation Server |
| VM server | servers/vm/main.c | - | Virtual Memory |
| VFS server | servers/vfs/main.c | - | Virtual File System |
| Process table | kernel/proc.c | - | proc_init(), scheduling |
| GDT setup | arch/i386/protect.c | - | prot_init() |
| IDT setup | arch/i386/protect.c | - | Interrupt handlers |
| Boot image | kernel/table.c | - | image[] array |

---

## Pedagogical Learning Path

**For Beginners** (first-time OS learners):
1. Start with boot-sequence-complete.pdf
2. Understand 4 phases: Bootloader → Kernel → Servers → Userspace
3. Focus on Ring 0 vs Ring 3 concept
4. Don't worry about assembly code yet

**For Intermediate** (systems programming students):
1. Study kmain-initialization-detailed.pdf
2. Trace the 12 steps of kernel initialization
3. Understand process table, boot image, privileges
4. Read main.c:115-328 alongside diagram
5. Examine cstart() and bsp_finish_booting() code

**For Advanced** (OS developers, researchers):
1. Study kernel-to-userspace-transition.pdf
2. Understand x86 segment descriptors (GDT)
3. Learn IRET instruction mechanics
4. Study privilege checks performed by CPU
5. Read arch/i386/mpx.S (assembly code)
6. Experiment with SYSENTER/SYSEXIT optimizations

**For Implementers** (MINIX hackers):
1. Read all three diagrams
2. Trace execution with QEMU + GDB
3. Set breakpoints: kmain, switch_to_user, PM main
4. Step through IRET instruction
5. Examine segment registers before/after IRET
6. Modify boot image to add new server

---

## Common Questions Answered

**Q: Why does switch_to_user() never return?**
A: After IRET, we're in Ring 3 with user stack and EIP. The kernel code path is abandoned. The process will only return to kernel via INT/SYSENTER (system call) or interrupt, which enters a *different* kernel code path.

**Q: How do processes return to kernel?**
A: Via system calls (INT 0x33, SYSENTER, SYSCALL) or interrupts (timer, keyboard, etc.). These save user state and switch to kernel stack.

**Q: What is the first instruction executed in Ring 3?**
A: Whatever is at the user process's entry point (p_reg.pc), usually the `_start` symbol from the C runtime (crt0.o). This sets up argc/argv and calls main().

**Q: Can user processes execute privileged instructions?**
A: No. Attempting to execute HLT, CLI, STI, LGDT, LIDT, etc. in Ring 3 causes General Protection Fault (#GP exception).

**Q: How does VM start before having a VM server?**
A: Initially, kernel uses identity mapping (virtual == physical) set up by bootloader. VM server takes over paging after it starts, by handling page faults and providing memory allocation services.

**Q: Why does kmain() have NOT_REACHABLE?**
A: bsp_finish_booting() ends with switch_to_user(), which NEVER returns. If execution somehow continues past it, that's a critical bug. NOT_REACHABLE is a panic() macro for safety.

**Q: What happens on SMP systems?**
A: smp_init() starts application processors (APs). Each AP runs through its own initialization and eventually calls switch_to_user(). The boot processor (BP) goes first.

**Q: How are interrupts handled in Ring 3?**
A: Interrupts always switch to Ring 0 (kernel interrupt handler via IDT). Kernel handles the interrupt, then IRET back to Ring 3 (possibly to a different process if scheduler ran).

---

## Debugging Tips

**Using QEMU + GDB**:
```bash
# Terminal 1: Start MINIX in QEMU with GDB server
qemu-system-i386 -kernel kernel.img -s -S

# Terminal 2: Connect GDB
gdb kernel.elf
(gdb) target remote :1234
(gdb) break kmain
(gdb) continue
(gdb) info registers
(gdb) x/10i $eip
```

**Useful Breakpoints**:
- `break kmain` - Kernel entry
- `break cstart` - Low-level init
- `break switch_to_user` - Just before IRET
- `hbreak *switch_to_user+20` - Hardware breakpoint after IRET

**Inspecting State**:
```gdb
# Segment registers
info registers cs ds es ss

# GDT
info gdt

# IDT
info idt

# Current process
print *proc_ptr
print proc_ptr->p_name

# Boot image
print image[0]@NR_BOOT_PROCS
```

**Serial Console Logging**:
```c
// In kernel code
printf("kmain: Entering switch_to_user\n");
printf("proc_ptr=%p, name=%s, pc=%lx\n",
       proc_ptr, proc_ptr->p_name, proc_ptr->p_reg.pc);
```

---

## Exercises for Students

### Exercise 1: Trace Boot Sequence (Beginner)
1. Boot MINIX in QEMU
2. Observe boot messages on serial console
3. Identify when each phase starts (look for "MINIX", "PM", "RS" messages)
4. Time each phase with stopwatch
5. Compare to timeline in this guide

### Exercise 2: Modify Boot Image (Intermediate)
1. Add a new dummy server to boot image (kernel/table.c)
2. Create minimal main() that just prints "Hello from MY_SERVER"
3. Rebuild kernel, test in QEMU
4. Verify it appears in process list (ps command)

### Exercise 3: Implement New System Call (Advanced)
1. Add new syscall to kernel/system/
2. Register in kernel call table
3. Update PM to dispatch to your handler
4. Write userspace test program
5. Trace syscall with GDB (watch INT 0x33, IRET)

### Exercise 4: Analyze Privilege Transition (Expert)
1. Set GDB breakpoint at switch_to_user
2. Examine CS, DS, SS registers before IRET
3. Single-step through IRET instruction
4. Examine CS, DS, SS registers after IRET
5. Confirm CPL changed from 0 to 3
6. Document segment selector format (RPL, TI, Index)

---

## Conclusion

The MINIX boot process is a masterclass in operating system design:

1. **Modularity**: Clean separation of bootloader, kernel, servers, userspace
2. **Privilege Separation**: Ring 0 for kernel, Ring 3 for everything else
3. **Microkernel Philosophy**: Minimal kernel, services in user processes
4. **SEF Framework**: Self-healing servers that restart on crash
5. **POSIX Compliance**: Familiar system calls (fork, exec, etc.)

**Total Complexity**: ~500 lines of C (kmain), ~50 lines of assembly (switch_to_user), hundreds of servers and drivers - yet elegantly organized and understandable.

**Educational Value**: MINIX shows how real operating systems work without the overwhelming complexity of Linux or Windows. Every concept taught in OS textbooks (processes, memory management, I/O, filesystems) has a clear implementation here.

**Next Steps**:
- Study specific subsystems (VM, VFS, PM)
- Implement new features (schedulers, filesystems)
- Port to new architectures (ARM, RISC-V)
- Contribute to MINIX 4 development

---

## References

1. **MINIX Source Code**: https://github.com/Stichting-MINIX-Research-Foundation/minix
2. **MINIX 3 Book**: "Operating Systems: Design and Implementation" (Tanenbaum & Woodhull)
3. **Intel Manual**: Intel® 64 and IA-32 Architectures Software Developer's Manual, Volume 3A (System Programming)
4. **Multiboot Specification**: https://www.gnu.org/software/grub/manual/multiboot/multiboot.html
5. **x86 Assembly**: "Programming from the Ground Up" (Jonathan Bartlett)

---

## Diagram Files

- `boot-sequence-complete.pdf` (142 KB) - Overview
- `kmain-initialization-detailed.pdf` (205 KB) - Detailed kmain()
- `kernel-to-userspace-transition.pdf` (183 KB) - Ring 0→3 transition

**Total Size**: 530 KB
**Format**: PDF (compiled from TikZ LaTeX)
**License**: Educational use, attribution to MINIX project

---

**Author**: Generated via comprehensive MINIX source analysis
**Date**: 2025-10-31
**MINIX Version**: 3.4.0
**Architecture**: i386 (x86 32-bit)

---

END OF GUIDE
