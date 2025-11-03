# MINIX 3.4 Comprehensive Boot-to-Runtime CPU Trace
## Complete System Initialization and Process Life Cycle

**Version**: 1.0.0
**Date**: 2025-10-31
**Architecture**: x86 (i386 32-bit)
**MINIX Version**: 3.4.0-RC6
**Scope**: Bootloader through complete system operation

---

## EXECUTIVE SUMMARY

This document provides a **unified, granular trace** of MINIX 3.4 operation from bootloader entry through full microkernel runtime. Every CPU state transition is documented with:

- Privilege level changes (Ring 0 <-> Ring 3)
- Register state at critical junctions
- Memory address space transformations
- Process table modifications
- Context switch sequences
- System call dispatch
- Interrupt handling
- Process creation and execution

---

## TABLE OF CONTENTS

**Part I: Boot Sequence (Bootloader → kmain)**
- 0.1-0.3: Bootloader entry and stack setup
- 1.1-1.6: Pre-init low-level setup and paging
- 2.1-2.15: Kernel initialization and scheduling

**Part II: Process Management**
- 3.1-3.8: Process creation (fork syscall)
- 4.1-4.4: Process execution (exec syscall)
- 5.1-5.3: Context switching during fork

**Part III: Microkernel Runtime**
- 6.1-6.5: Interrupt handling and timer events
- 7.1-7.4: System call dispatch and IPC
- 8.1-8.5: Process scheduling and time accounting

**Part IV: Summary and Reference**
- Appendix A: CPU register state reference
- Appendix B: Memory layout reference
- Appendix C: Critical code locations

---

## PART I: BOOT SEQUENCE

See BOOT-TO-KERNEL-TRACE.md for detailed analysis.

**Quick Summary**:
1. Bootloader enters at head.S:40
2. Multiboot parameters parsed in pre_init()
3. Paging enabled, kernel remapped to 0x80000000
4. GDT/IDT/TSS initialized in cstart()
5. Timer enabled, interrupts activated
6. First process scheduled via IRET

**CPU State Transition** (simplified):
```
Bootloader (Real Mode)
    |
    v [Jump to MINIX entry]
Protected Mode, Ring 0, Low Memory (0x0xxxxx)
    |
    v [Enable paging, load high address]
Protected Mode, Ring 0, High Memory (0x8xxxxxx)
    |
    v [Load GDT/IDT/TSS]
Protected Mode, Ring 0, Fully initialized
    |
    v [IRET from switch_to_user]
User Mode, Ring 3, First Process
```

---

## PART II: PROCESS MANAGEMENT

See FORK-PROCESS-CREATION-TRACE.md for detailed analysis.

### Process Creation Flow

**1. fork() Syscall**:
```
User code: fork() -> INT 0x30
    |
    v [CPU automatic]
Kernel: INT handler saves context
    |
    v [Handler calls]
do_fork() in kernel: copies parent to child
    |
    v [Return via]
IRET to user: parent resumes with child PID
      child marked BLOCKED (no memory yet)
```

**2. exec() Syscall**:
```
Child: execve("/bin/ls") -> INT 0x30
    |
    v [Kernel]
do_exec() updates EIP/ESP to new program
    |
    v [Return]
IRET: child at new program entry point
```

**3. Combined fork()+exec()**:
```
Parent: fork()
    |child (Ring 3, same code as parent)
    |parent (Ring 3, continues)
    |
    v [Child calls exec to load new program]
Child: execve() changes EIP/ESP
    |
    v [IRET]
Child: new program /bin/ls running
```

---

## PART III: MICROKERNEL RUNTIME

### 6.1 Interrupt Handling (Timer Example)

**Timeline**:
```
Time 0.0s:  User process running
            EIP = 0x08048500
            EFLAGS.IF = 1

Time 0.010s (10ms later):
            PIT timer fires
            IRQ0 asserted by hardware
            
CPU automatic (atomic):
[CPU Detects interrupt]
  - Check EFLAGS.IF = 1 (enabled)
  - Acknowledge IRQ to PIC
  - Lookup IDT[32] (hwint00)
  - Push EIP, CS, EFLAGS to kernel stack
  - Load kernel stack from TSS.ESP0
  - Load new CS:EIP from IDT

[CPU continues]
  - Jump to hwint00 (0x80000xxx, kernel code)
  - EFLAGS.IF = 0 (auto-disabled)
  - Ring 0 (kernel)
  - Kernel stack active

hwint00 handler:
  - TEST_INT_IN_KERNEL (check CS on stack)
  - SAVE_PROCESS_CTX (save all user registers)
  - call irq_handle(0)  # Clock interrupt
  - movb $END_OF_INT, %al
  - outb $INT_CTL       # EOI to PIC
  - jmp switch_to_user
  
switch_to_user:
  - pick_proc() -> select next process
  - RESTORE_GP_REGS (restore registers)
  - iret               # Return to user
  
CPU automatic (iret):
  - Pop EIP (next process instruction)
  - Pop CS (user selector 0x1b)
  - Pop EFLAGS (with IF restored to 1)
  - Privilege change: Ring 0 -> Ring 3
  - Stack switch: kernel stack -> user stack
  - Jump to user code
  
Time 0.010s (continued):
            User process resumes (may be different process)
            EFLAGS.IF = 1
```

**CPU Register State During Interrupt**:
```
BEFORE interrupt (user code):
EIP:    0x08048500
ESP:    0x1f00xxxx (user stack)
CS:     0x1b
EFLAGS: 0x00000246 (IF=1)

KERNEL SAVES (hwint00):
[stack]:  EIP, CS, EFLAGS
process table:  all registers

KERNEL RESUMES (switch_to_user):
Restored from process table of next process
```

### 6.2 System Call Dispatch

**SYS_FORK Example**:
```
User: INT 0x30
    |
    v [CPU automatic]
hwint00 entry -> sys_call()
    |
    v [Dispatch on m_type]
switch(m_type) {
  case SYS_FORK: return do_fork(caller, msg); break;
  ...
}
    |
    v [Message reply]
m_type = return code
```

**CPU State During Syscall**:
```
Ring: 0 (kernel)
Stack: Kernel stack
Registers: Saved in process table
Execution: C code (do_fork, etc)
```

### 6.3 Process Scheduling (pick_proc)

**Algorithm** (simplified):
```c
struct proc * pick_proc(void) {
  struct proc *p;
  
  // Find runnable process with highest priority
  for (int q = HIGHEST_PRIORITY; q <= LOWEST_PRIORITY; q++) {
    if (run_queue[q]) {
      p = run_queue[q];           // First in queue
      dequeue(p);                 // Remove from queue
      return p;
    }
  }
  
  // No runnable process: return IDLE
  return idle_process;
}
```

**Process States**:
```
RTS_RUNNABLE:       Can run immediately
RTS_NO_QUANTUM:     Out of time (wait for timer)
RTS_RECEIVING:      Waiting for message
RTS_SENDING:        Waiting for receiver
RTS_VMINHIBIT:      Waiting for VM (page tables)
RTS_NO_PRIV:        Waiting for privilege setup
```

**Run Queue Scheduling**:
```
Priority 0 (highest):
  - IDLE (if nothing else runnable)
  - CLOCK (timer handler)
  - SYSTEM (syscall dispatcher)

Priority 1-3:
  - Kernel tasks (MEMORY, VFS, PM, etc)

Priority 4+:
  - User processes

Preemption:
  - Timer tick every 10ms: timer_int()
  - If current process time expired: reschedule()
  - Pick highest priority runnable process
```

---

## PART IV: COMPLETE EXECUTION TIMELINE

### Example: Fork and Exec a Child Process

**Second 0.000: Parent running /bin/sh**
```
Process: init (shell)
State: RTS_RUNNABLE
EIP: 0x08048f20 (fork() call address)
CS: 0x1b (Ring 3)
```

**Second 0.001: fork() syscall issued**
```
Action: INT 0x30
CPU: Automatic INT handling
  - Push EIP, CS, EFLAGS to kernel stack
  - Load kernel stack from TSS.ESP0
  - Jump to hwint00
```

**Second 0.002: In hwint00 handler**
```
CPU Ring: 0 (kernel)
Action: SAVE_PROCESS_CTX
  - Save parent context to process table
  - Jump to sys_call()
```

**Second 0.003: In do_fork()**
```
Action: Copy parent process table to child
  - rpc = parent_entry (copy)
  - Change EAX = 0 (for child)
  - Update endpoint (new generation)
  - Mark child RTS_NO_QUANTUM | RTS_VMINHIBIT
  - Set child page table = 0 (waiting for VM)
```

**Second 0.004: Return from fork() to parent**
```
Syscall returns (EAX = child_pid)
IRET: Switch to parent context
CPU Ring: 3 (user)
Process: init (parent)
  if (fork_result > 0) {
    // Parent code
    wait();
  }
```

**Second 0.010: Timer tick (first interrupt after fork)**
```
Timer fires: PIT -> IRQ0
hwint00: Save current process context
pick_proc(): Select next process
  - Check parent (RTS_RUNNABLE) OK
  - Check child (RTS_VMINHIBIT) BLOCKED
  - Select parent (higher priority in queue)
IRET: Continue parent
```

**Second 0.050: VM server processes fork request**
```
VM server wakes up (due to IPC notification)
VM server creates new page tables for child
VM kernel call: Update child's p_cr3
Child now has memory, RTS_VMINHIBIT cleared
Child becomes RTS_RUNNABLE
```

**Second 0.100: Scheduler selects child to run**
```
Timer tick: pick_proc()
Runnable processes: parent, child (same priority)
Scheduler: Select child (next in queue after parent)
IRET: Load child context
CPU Ring: 3 (user, child process)
EIP: 0x08048f20 (same address as parent)
EAX: 0 (return value = 0)
  if (fork_result == 0) {
    // Child code
    execve("/bin/ls");
  }
```

**Second 0.105: Child calls execve()**
```
Child: execve("/bin/ls")
  INT 0x30 (syscall)
hwint00: Save child context
do_exec(): Update child registers
  - EIP = /bin/ls entry point
  - ESP = new stack
  - Name = "ls"
IRET: Jump to /bin/ls entry point
CPU Ring: 3 (user, child running /bin/ls)
```

**Second 0.110-1.0: /bin/ls runs to completion**
```
Program: /bin/ls
Output: File listing printed
Exit: call exit(0)
  INT 0x30 (SYS_EXIT)
```

**Second 1.005: Child exits, parent wakes up**
```
Child process removed from runnable queue
Parent wakes up from wait() syscall
Parent gets exit code via IPC
Parent continues (can now fork another child)
```

---

## APPENDIX A: CPU REGISTER STATE REFERENCE

### x86-32 Register Mapping in MINIX

**General Purpose Registers**:
```
EAX (Accumulator):
  - syscall return value
  - return value register
  - scratch (caller-saved)

EBX (Base):
  - preserved (callee-saved)
  - used for base addresses in some contexts

ECX (Counter):
  - syscall call number
  - loop counter
  - scratch (caller-saved)

EDX (Data):
  - syscall parameter
  - scratch (caller-saved)

ESI (Source Index):
  - string operations
  - preserved (callee-saved)

EDI (Destination Index):
  - string operations
  - preserved (callee-saved)

EBP (Base Pointer):
  - stack frame pointer
  - preserved (callee-saved)

ESP (Stack Pointer):
  - points to top of stack
  - changes with push/pop
```

**Segment Registers**:
```
CS (Code Segment):
  - 0x08: Kernel code (Ring 0, DPL=0)
  - 0x1b: User code (Ring 3, DPL=3)

DS/ES (Data Segments):
  - 0x10: Kernel data (Ring 0)
  - 0x23: User data (Ring 3)

SS (Stack Segment):
  - 0x10: Kernel stack (during kernel mode)
  - 0x23: User stack (during user mode)

FS/GS:
  - Usually 0 (unused in MINIX)
```

**Special Registers**:
```
EIP (Instruction Pointer):
  - Current instruction address
  - Saved on interrupt/call
  - Loaded on return/jump

EFLAGS (Flags):
  - Bit 0 (CF):  Carry flag
  - Bit 2 (PF):  Parity flag
  - Bit 4 (AF):  Auxiliary carry
  - Bit 6 (ZF):  Zero flag
  - Bit 7 (SF):  Sign flag
  - Bit 8 (TF):  Trap flag (single-step)
  - Bit 9 (IF):  Interrupt enable
  - Bit 10 (DF): Direction flag
  - Bit 11 (OF): Overflow flag
  - Bit 12-13 (IOPL): I/O privilege level
  - Bit 14 (NT): Nested task
  - Bit 16 (RF): Resume flag
  - Bit 17 (VM): Virtual mode
  - Bit 18 (AC): Alignment check
```

**Control Registers**:
```
CR0:
  - Bit 0 (PE): Protected mode enable
  - Bit 1 (MP): Math processor
  - Bit 2 (EM): Emulation (no FPU)
  - Bit 3 (TS): Task switched (FPU context)
  - Bit 4 (ET): Extension type
  - Bit 5 (NE): Numeric error
  - Bit 16 (WP): Write protect
  - Bit 18 (AM): Alignment mask
  - Bit 29 (NW): Not write-through
  - Bit 30 (CD): Cache disable
  - Bit 31 (PG): Paging enable

CR3:
  - Page directory base address
  - Low 12 bits: flags
  - High 20 bits: page directory physical address

GDTR (GDT Register):
  - 2 bytes: GDT size - 1
  - 4 bytes: GDT linear address

IDTR (IDT Register):
  - 2 bytes: IDT size - 1
  - 4 bytes: IDT linear address

TR (Task Register):
  - Selector of current TSS
  - 0x28 in MINIX (TSS descriptor in GDT)
```

---

## APPENDIX B: MEMORY LAYOUT REFERENCE

### Virtual Address Space (Per Process)

```
User Mode (Ring 3):
0x00000000 - 0x7fffffff:  User code/data/heap/stack
0x00000000 - 0x08048000:  (typically) Program entry
0x08048000+:              (typically) Text segment
+:                        Data segment
+:                        BSS segment
~0x1f000000:              Stack (grows downward)

Kernel Mode (Ring 0):
0x80000000 - 0xffffffff:  Kernel code/data/stacks
0x80000000+:              Kernel text (mapped from 0x00100000 phys)
0x80000000+KSIZE:         Kernel data
0x80000000+KSIZE+:        Per-CPU stacks
0x8000xxxx:               Interrupt handlers
~0x8003xxxx:              Process table
~0x8004xxxx:              Privilege table
~0x800xxxxx:              Kernel heap

Physical Address Space:
0x00000000 - 0x00100000:  BIOS/Reserved
0x00100000 - 0x00d00000:  Kernel image (13MB, compressed)
0x00d00000+:              Dynamic kernel data (VM pages)
+:                        Page tables
+:                        Process stacks
+:                        Kernel heap
```

### Page Table Structure (x86 32-bit)

```
CR3:
[31:12] - Page Directory Base Address (physical)
[11:5]  - Reserved
[4]     - PCD (Page Cache Disable)
[3]     - PWT (Page Write-Through)
[2:0]   - Reserved

Page Directory Entry (4 bytes, 1024 entries):
[31:12] - Page Table Address (physical)
[11]    - Reserved
[10]    - Accessed
[9:8]   - Available
[7]     - Page Size (4KB if 0)
[6]     - Global
[5]     - Dirty
[4]     - Write-Through
[3]     - Cache Disable
[2]     - User/Supervisor (DPL)
[1]     - Read/Write
[0]     - Present

Page Table Entry (4 bytes, 1024 entries):
[31:12] - Physical Page Address
[11:9]  - Available
[8]     - Global
[7]     - Dirty
[6]     - Accessed
[5]     - Write-Through
[4]     - Cache Disable
[3]     - User/Supervisor (DPL)
[2]     - Read/Write
[1]     - Reserved
[0]     - Present
```

---

## APPENDIX C: CRITICAL CODE LOCATIONS

### Boot Phase
- `minix/kernel/arch/i386/head.S:38-91` - Multiboot entry, stack setup, kmain call
- `minix/kernel/arch/i386/pre_init.c:244+` - Pre-init: memory setup, paging enable
- `minix/kernel/arch/i386/protect.c:200+` - cstart(): GDT/IDT/TSS initialization
- `minix/kernel/main.c:158+` - kmain(): process table, boot modules setup
- `minix/kernel/main.c:40+` - bsp_finish_booting(): timer enable, first process

### Process Management
- `minix/kernel/system/do_fork.c:31+` - do_fork(): copy parent to child
- `minix/kernel/system/do_exec.c:18+` - do_exec(): update EIP/ESP for new program
- `minix/kernel/arch/i386/mpx.S:201-432` - IPC entry points (SYSENTER, SYSCALL, INT)
- `minix/kernel/arch/i386/sconst.h:75+` - SAVE_PROCESS_CTX, context save macros

### Interrupt Handling
- `minix/kernel/arch/i386/mpx.S:74-157` - hwint00-15: hardware interrupt handlers
- `minix/kernel/interrupt.c:??` - irq_handle(): clock, device interrupt dispatch
- `minix/kernel/arch/i386/mpx.S:???` - switch_to_user(): scheduler, context restore

### Scheduling
- `minix/kernel/proc.c:???` - pick_proc(): runnable process selection
- `minix/kernel/proc.c:???` - switch_to_user continuation: IRET to user

---

## CONCLUSION

MINIX 3.4 implements a clean microkernel architecture with carefully managed CPU state transitions:

1. **Boot**: Transforms bootloader primitives into full kernel
2. **Processes**: Fork creates identical copies; exec replaces code
3. **Interrupts**: Hardware events trigger kernel entry; scheduler picks next process
4. **Scheduling**: Priority queue selects next runnable process
5. **IPC**: Synchronous message passing between user processes and kernel tasks

Every transition between Ring 0 (kernel) and Ring 3 (user) is carefully orchestrated using:
- **INT instructions** (user syscall entry)
- **IRET instructions** (return to user)
- **Hardware interrupts** (automatic privilege elevation)
- **Process table** (saved context per process)
- **Page tables** (per-process address space)

This architecture provides:
- **Isolation**: Each process isolated via paging
- **Security**: Privilege levels enforce separation
- **Efficiency**: Minimal context switch overhead
- **Clarity**: Explicit state transitions (no implicit behavior)

The complete system from bootloader to multi-process execution requires careful CPU state management at every step.
