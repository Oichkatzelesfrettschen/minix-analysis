# MINIX fork() and Process Creation with CPU Context Switching
## Detailed Trace of Process Duplication and Context Management

**Version**: 1.0.0
**Date**: 2025-10-31
**Architecture**: x86 (i386 32-bit)
**MINIX Version**: 3.4.0-RC6

---

## OVERVIEW: FORK SYSCALL SEQUENCE

**Fork Request Path**:
```
User Process (Ring 3)
    |
    v [INT 0x30 / SYSENTER / SYSCALL]
Ring 0 Entry (mpx.S)
    |
    v SAVE_PROCESS_CTX
Process Table Entry
    |
    v Call handler
do_fork() (system/do_fork.c)
    |
    v [Duplicate process table entry]
Child Process
    |
    v [Return from syscall]
Ring 3 Child Code
```

---

## SECTION 1: FORK SYSCALL ENTRY

### 1.1 User Process Issues Fork Syscall

**Code** (pseudo-C from libc):
```c
pid_t fork_result = fork();
```

**Libc Implementation** (libsys/fork.c):
```c
int sys_fork(void) {
  message m;
  m.m_type = SYS_FORK;
  
  // Parent process slot for kernel
  m.m_lsys_krn_sys_fork.endpt = sys_getpid();
  
  // Request child slot from kernel
  m.m_lsys_krn_sys_fork.slot = <request new slot>;
  
  // Flags for VM coordination
  m.m_lsys_krn_sys_fork.flags = PFF_VMINHIBIT;
  
  // Syscall via INT 0x30 (x86 MINIX convention)
  return sendrec(SYSTEM, &m);
}
```

**CPU State Before INT Instruction**:
```
EIP:    0x08048xxx (user code in libc)
EBX:    saved (caller-saved)
ECX:    1st parameter (fork syscall number)
EDX:    return address or param
ESI:    message pointer
EDI:    preserved (callee-saved)
ESP:    user stack
CS:     0x1b (user code, DPL=3)
DS/ES:  0x23 (user data, DPL=3)
SS:     0x23 (user stack, DPL=3)
EFLAGS: IF=1 (interrupts enabled)
```

### 1.2 INT 0x30 Instruction (Software Interrupt)

**Instruction**: `INT 0x30`

**CPU Hardware Actions**:
1. Check EFLAGS.IF (interrupt enabled) - YES
2. Acknowledge interrupt (CPU internal)
3. Push EIP, CS, EFLAGS onto kernel stack
4. Load kernel stack pointer from TSS.ESP0
5. Load kernel stack selector from TSS.SS0
6. Load new EIP, CS from IDT entry 48 (0x30)
7. Check privilege level in new CS (Ring 0)
8. Jump to IDT[48].EIP (kernel handler)

**Stack State After INT 0x30**:
```
Kernel Stack (ESP = TSS.ESP0):
[ESP+0]:   EIP (user instruction after INT)
[ESP+4]:   CS  (user code selector 0x1b)
[ESP+8]:   EFLAGS (with IF set)
```

**CPU State After INT 0x30 (Before Handler)**:
```
EIP:    0x80000xxx (handler address from IDT[48])
ESP:    kernel stack (from TSS.ESP0)
CS:     0x08 (kernel code selector)
DS/ES/SS: may still be user selectors (not yet switched)
EFLAGS: IF=0 (interrupts disabled automatically)
```

### 1.3 Kernel Entry Point (mpx.S)

**File**: `minix/kernel/arch/i386/mpx.S`

**INT 0x30 Handler** (ipc_entry_softint):
```assembly
ENTRY(ipc_entry_softint_orig)
  # At this point:
  # - User context on stack: EIP, CS, EFLAGS
  # - Kernel stack active (ESP from TSS.ESP0)
  # - Interrupts disabled (EFLAGS.IF=0)
  
  # Test if interrupt in kernel or user
  TEST_INT_IN_KERNEL(4, 0f)    # Check CS value at [ESP+4]
  
  # User interrupt path:
  SAVE_PROCESS_CTX(0, KTS_IRET)    # Save full user context
  
  # Jump to C handler
  jmp _C_LABEL(sys_call)
```

---

## SECTION 2: CONTEXT SAVE AND SYSCALL DISPATCH

### 2.1 SAVE_PROCESS_CTX Macro

**Location**: `minix/kernel/arch/i386/sconst.h`

**Macro Expansion** (simplified):
```assembly
SAVE_PROCESS_CTX(0, KTS_IRET):

  cld                      # Clear direction flag
  push %ebp                # Save EBP on stack
  
  # Get current process pointer
  # Calculation: (CURR_PROC_PTR + 4 + 0)(%esp)
  # CURR_PROC_PTR = 20 (from sconst.h)
  # [ESP+0]: EBP (just pushed)
  # [ESP+4]: EIP (from INT)
  # [ESP+8]: CS  (from INT)
  # [ESP+12]: EFLAGS (from INT)
  # [ESP+16]: (would be ESP for Ring 3->0 switch, but not present)
  
  # Actually for soft INT from Ring 3:
  # Stack offset 4 bytes into user trap frame
  movl %ss:0(%esp), %ebp   # Load process ptr from somewhere
  
  # Save general purpose registers
  SAVE_GP_REGS(%ebp)       # Save EAX, EBX, ECX, EDX, ESI, EDI
  
  # Save trap style code
  movl $KTS_IRET, P_KERN_TRAP_STYLE(%ebp)
  
  # Save EBP
  pop %esi
  mov %esi, BPREG(%ebp)
  
  # Restore kernel segments
  RESTORE_KERNEL_SEGS      # DS, ES, FS, GS = kernel selectors
  
  # Save trap context (EIP, CS, EFLAGS, ESP)
  SAVE_TRAP_CTX(0, %ebp, %esi)
```

**Process Table Entry After SAVE_PROCESS_CTX**:
```
struct proc {
  // Saved registers:
  u32_t ax, bx, cx, dx;
  u32_t si, di, bp;
  
  // Saved trap context:
  u32_t pc;        // EIP (instruction at fork call)
  u32_t cs;        // CS (user code selector 0x1b)
  u32_t psw;       // EFLAGS
  u32_t sp;        // ESP (user stack pointer)
  
  // Other fields:
  short p_rts_flags;     // RTS_SYSCALL or RTS_RECEIVING
  char p_kern_trap_style;  // KTS_IRET (type of entry)
};
```

**CPU State During Context Save**:
- EBP: Points to process table entry (proc structure)
- Registers being saved: All general-purpose registers
- Segment registers: Being restored to kernel selectors
- Stack: Kernel stack (original user context on stack frame)

### 2.2 sys_call C Handler

**File**: `minix/kernel/proc.c`
**Function**: `void sys_call(message *m_ptr)`

**Handler Logic**:
```c
void sys_call(message *m_ptr) {
  struct proc *caller_ptr;
  int call_nr;
  
  // Get current process
  caller_ptr = get_cpulocal_var(proc_ptr);
  
  // Extract syscall number from message
  call_nr = m_ptr->m_type;
  
  // Switch on syscall number
  switch (call_nr) {
    case SYS_FORK:
      // Call do_fork with caller context
      return_code = do_fork(caller_ptr, m_ptr);
      break;
      
    case SYS_EXEC:
      // Call do_exec with caller context
      return_code = do_exec(caller_ptr, m_ptr);
      break;
      
    // ... other syscalls ...
  }
  
  // Return status via message
  m_ptr->m_type = return_code;
}
```

**CPU State During sys_call**:
- Ring 0 (kernel mode)
- Process context saved in process table
- EBP: Pointer to process structure
- Kernel stack: Available for C function calls
- Message pointer passed as parameter

---

## SECTION 3: FORK SYSTEM CALL IMPLEMENTATION

### 3.1 do_fork() Entry

**File**: `minix/kernel/system/do_fork.c`
**Function**: `int do_fork(struct proc *caller, message *m_ptr)`

**Parameters**:
```
caller (EBP):        Pointer to parent process structure
m_ptr (ESP+4):       Pointer to syscall message

Message Contents:
m_lsys_krn_sys_fork.endpt:  Parent endpoint
m_lsys_krn_sys_fork.slot:   Child slot number (0-127)
m_lsys_krn_sys_fork.flags:  Fork flags (PFF_VMINHIBIT, etc)

Returns:
OK (0):              Fork succeeded
EINVAL:              Invalid parameters
ENOMEM:              No memory for child
```

**Entry Code Analysis**:
```c
int do_fork(struct proc *caller, message *m_ptr) {
  struct proc *rpc;      // Pointer to child (rpc = reverse process control?)
  struct proc *rpp;      // Pointer to parent
  int gen;               // Endpoint generation number
  int p_proc;            // Parent process number
  int namelen;
  
  // 1. Validate parent endpoint
  if(!isokendpt(m_ptr->m_lsys_krn_sys_fork.endpt, &p_proc))
    return EINVAL;
  
  rpp = proc_addr(p_proc);       // Get parent proc pointer
  rpc = proc_addr(m_ptr->m_lsys_krn_sys_fork.slot);  // Get child slot
  
  // Validate: parent must exist, child slot must be free
  if (isemptyp(rpp) || !isemptyp(rpc))
    return EINVAL;
  
  // Parent must be in receiving state
  if(!RTS_ISSET(rpp, RTS_RECEIVING)) {
    return EINVAL;
  }
```

**CPU State During do_fork Entry**:
- Ring 0 (kernel mode)
- Stack frame: Function prologue creates local variables
- EBP: Pointer to parent process structure (caller parameter)
- CPU running C code in kernel context

### 3.2 FPU Context Save

**Critical Step**: Save parent FPU state before copying

```c
/* make sure that the FPU context is saved in parent before copy */
save_fpu(rpp);
```

**Why FPU Save?**:
- FPU registers (ST0-ST7) may not be saved in process table
- FPU state lazy-loaded (only saved on FPU exception)
- Fork must copy ALL parent state to child
- Including FPU state if FPU has been used

**save_fpu() Implementation**:
```c
void save_fpu(struct proc *rp) {
  if (proc_used_fpu(rp)) {
    // Check FPUCW (FPU control word) to see if FPU used
    // If used: execute FNSAVE or XSAVE to save FPU state
    
    #if defined(__i386__)
    asm("fnsave %0" : "=m" (rp->p_seg.fpu_state));
    #endif
  }
}
```

**CPU State During FPU Save**:
- FPU state written to memory
- If FPU instruction executed: automatic context trap
- FPU exception (if not present) caught by kernel

### 3.3 Copy Process Structure

**Critical Step**: Duplicate parent process entry to child

```c
/* Copy parent 'proc' struct to child. */
gen = _ENDPOINT_G(rpc->p_endpoint);     // Save child's generation
#if defined(__i386__)
old_fpu_save_area_p = rpc->p_seg.fpu_state;  // Save child's FPU area
#endif

*rpc = *rpp;                             // COPY ALL PARENT DATA TO CHILD

#if defined(__i386__)
rpc->p_seg.fpu_state = old_fpu_save_area_p;  // Restore child FPU area
// Copy parent FPU state to child
if(proc_used_fpu(rpp))
  memcpy(rpc->p_seg.fpu_state, rpp->p_seg.fpu_state, FPU_XFP_SIZE);
#endif
```

**What Gets Copied**:
- All registers (EAX, EBX, ECX, EDX, ESI, EDI, EBP)
- Instruction pointer (EIP)
- Stack pointer (ESP)
- Segment registers (CS, DS, SS)
- EFLAGS
- Privilege level
- Process name
- FPU state (if used)

**What Gets NOT Copied or Modified**:
- Endpoint (regenerated)
- Process number (from child slot)
- Generation counter (incremented)
- Timers (virtual, profiling)
- Signal handlers (cleared)
- Page tables (CR3, to be set by VM)

**Memory View During Copy**:
```
Process Table Entry (BEFORE copy):
rpc->p_endpoint = 0x0000c002  (child slot 3, gen 0)
rpc->p_priv = USER_PRIV       (user privilege)
rpc->p_reg.EIP = <undefined>

Process Table Entry (AFTER copy):
rpc->p_endpoint = 0x0000c002  (still child slot 3, gen 0)
rpc->p_priv = rpp->p_priv     (COPIED from parent)
rpc->p_reg.EIP = rpp->p_reg.EIP  (COPIED from parent)
```

### 3.4 Update Child Process Fields

**Step**: Customize child entry after copy

```c
/* Increment generation number (for endpoint uniqueness) */
if(++gen >= _ENDPOINT_MAX_GENERATION)
  gen = 1;
rpc->p_endpoint = _ENDPOINT(gen, rpc->p_nr);  // New endpoint

/* Set up return value for child */
rpc->p_reg.retreg = 0;        // EAX = 0 (child sees pid=0)

/* Reset timers */
rpc->p_user_time = 0;
rpc->p_sys_time = 0;

/* Clear process name suffix */
namelen = strlen(rpc->p_name);
#define FORKSTR "*F"
if(namelen+strlen(FORKSTR) < sizeof(rpc->p_name))
  strcat(rpc->p_name, FORKSTR);  // e.g., "bash" -> "bash*F"

/* Mark child as not runnable until VM sets up page tables */
RTS_SET(rpc, RTS_NO_QUANTUM);   // No time quantum yet
RTS_SET(rpc, RTS_VMINHIBIT);    // VM inhibit (if flagged)

/* Reset accounting */
reset_proc_accounting(rpc);
rpc->p_cpu_time_left = 0;
rpc->p_cycles = 0;
```

**Child Process State After Customization**:
```
struct proc (child) {
  // Copied from parent:
  p_reg.ax = rpp->p_reg.ax
  p_reg.bx = rpp->p_reg.bx
  p_reg.sp = rpp->p_reg.sp    // Child gets parent's stack
  p_reg.pc = rpp->p_reg.pc    // Child gets parent's PC
  
  // Modified:
  p_endpoint = 0x0001c003     // New endpoint (gen=1, slot=3)
  p_reg.ax = 0                // Return value = 0 (for child)
  p_name = "bash*F"           // Marked as fork
  p_rts_flags = RTS_NO_QUANTUM | RTS_VMINHIBIT
  p_user_time = 0
  p_sys_time = 0
};
```

### 3.5 Handle Privileged Process Children

**Step**: Strip privileges from children of privileged processes

```c
if (priv(rpp)->s_flags & SYS_PROC) {
  // Parent is a system process (kernel task, server)
  // Child should NOT inherit privileges
  
  rpc->p_priv = priv_addr(USER_PRIV_ID);  // User privileges
  rpc->p_rts_flags |= RTS_NO_PRIV;        // Can't run until privileges set
}
```

**Motivation**: Security isolation
- Kernel tasks (CLOCK, SYSTEM) can fork
- Children should not automatically become kernel tasks
- Parent must explicitly set privileges via SYS_PRIVCTL

### 3.6 Clear Signal Handlers

**Step**: Don't inherit signal handling state

```c
RTS_UNSET(rpc, (RTS_SIGNALED | RTS_SIG_PENDING | RTS_P_STOP));
sigemptyset(&rpc->p_pending);      // Clear pending signal set

// Child doesn't inherit tracing state
RTS_UNSET(rpc, RTS_STEP);          // Not single-step
```

### 3.7 Clear Page Table References

**Step**: Force VM to set up new page tables for child

```c
#if defined(__i386__)
rpc->p_seg.p_cr3 = 0;           // CR3 = 0 (no page table yet)
rpc->p_seg.p_cr3_v = NULL;      // Virtual address of CR3
#elif defined(__arm__)
rpc->p_seg.p_ttbr = 0;          // TTBR = 0 (ARM)
rpc->p_seg.p_ttbr_v = NULL;
#endif
```

**Effect**: Child cannot run until:
1. VM server allocates memory for child
2. VM server creates page tables for child
3. VM server updates kernel's p_seg.p_cr3

### 3.8 Return from do_fork()

**Return Message**:
```c
m_ptr->m_krn_lsys_sys_fork.endpt = rpc->p_endpoint;   // Child endpoint
m_ptr->m_krn_lsys_sys_fork.msgaddr = rpp->p_delivermsg_vir;

return OK;
```

**Message Sent Back to Parent**:
```
Message {
  m_type: OK (0)
  m_krn_lsys_sys_fork.endpt: <child endpoint>
  m_krn_lsys_sys_fork.msgaddr: <msgaddr for parent>
}
```

---

## SECTION 4: RETURN FROM SYSCALL

### 4.1 sys_call Completion

After do_fork() returns, sys_call continues:

```c
/* Store return message */
m_ptr->m_type = return_code;  // OK or EINVAL

/* Return to kernel exit code */
return;
```

**CPU State**:
- Ring 0 (still kernel)
- Process context saved in process table
- EBP: Still points to process structure
- Stack: Return address points to syscall exit code

### 4.2 Syscall Exit Path (mpx.S)

**Conceptual Return Path**:
```assembly
# Return from sys_call() to ipc_entry handler
# Handler decides whether to return to user or continue serving IPC

call _C_LABEL(sys_call)    # Returns here after do_fork()

# Message reply prepared (m_ptr->m_type = OK)

jmp _C_LABEL(switch_to_user)  # Return to user or next process
```

### 4.3 Return to User (IRET)

**Restore Parent Context**:
```assembly
# In switch_to_user:
RESTORE_GP_REGS(%ebp)      # Restore all registers
...
iret                       # Return to user mode
```

**IRET Instruction Actions**:
1. Pop EIP (instruction after INT)
2. Pop CS (user code selector 0x1b)
3. Pop EFLAGS (with IF restored)
4. Switch to user stack (if privilege level changed)
5. Load DS/ES/FS/GS to user selectors (automatic)
6. Jump to user code at EIP

**Parent Process Resumes**:
```
EIP:    0x08048xxx (instruction after fork() call)
EAX:    <child PID>  (return value from syscall)
ESP:    user stack
CS:     0x1b (user code)
EFLAGS: IF=1 (interrupts enabled)
```

### 4.4 Child Process Activation

**Critical Point**: Child is now a separate process entry

**Child Remains Inactive Until**:
1. VM server allocates memory for child
2. VM server creates page tables for child
3. Kernel scheduler selects child to run
4. IRET to child's instruction pointer (same code as parent)

**When Child Runs**:
```
EIP:    <fork call location>  (same as parent)
EAX:    0                     (return value = 0)
ESP:    <parent's stack>      (copied)
All registers: <parent's values>
```

**Parent vs Child Divergence**:
```
Parent Process (after fork returns):
{
  EAX = child_pid    (non-zero)
  if (child_pid > 0) {
    // Parent code: wait for child
  }
}

Child Process (when it runs):
{
  EAX = 0            (child's return value)
  if (0) {           // False branch
    // Parent code: skipped
  } else {
    // Child code: executed
  }
}
```

---

## SECTION 5: CPU CONTEXT SWITCHING DURING FORK

### 5.1 Context Switch During Fork

**Timeline**:
```
Time 0: Parent at fork() syscall
        CPU: Ring 3, running parent code
        Registers: Parent's state

Time 1: INT 0x30, context saved
        CPU: Ring 0, kernel
        Process table: Parent context saved
        
Time 2: do_fork() executes
        CPU: Ring 0, kernel
        Process table: Child entry created (copy of parent)
        
Time 3: IRET to parent
        CPU: Ring 3, parent resumes
        Registers: Parent's state restored
        
Time 4: (Later) Timer interrupt
        CPU: Ring 0, context saved
        Scheduler picks child to run
        
Time 5: IRET to child
        CPU: Ring 3, child runs
        Registers: Child's state (copied from parent)
```

### 5.2 Process Table State During Fork

**Before Fork Syscall**:
```
proc_table[2] (parent):
  {
    p_endpoint = 0x00082002
    p_reg.ax = 2              // Some value
    p_reg.bx = 0x0804abc0
    p_reg.sp = 0x1ff00000
    p_reg.pc = 0x08048f20     // Fork call location
    p_priv = user_priv
    p_rts_flags = RTS_RUNNABLE
  }

proc_table[3] (child slot, empty):
  {
    p_rts_flags = RTS_SLOT_FREE
    // Rest undefined
  }
```

**After Fork Syscall in Kernel**:
```
proc_table[2] (parent):
  {
    // Same as before (saved at interrupt entry)
    p_rts_flags = RTS_RECEIVING  // Waiting for reply
  }

proc_table[3] (child):
  {
    p_endpoint = 0x0001c003     // New endpoint
    p_reg.ax = 0                // Return value for child
    p_reg.bx = 0x0804abc0       // COPIED from parent
    p_reg.sp = 0x1ff00000       // COPIED from parent
    p_reg.pc = 0x08048f20       // COPIED from parent (same code)
    p_priv = user_priv          // COPIED from parent
    p_rts_flags = RTS_NO_QUANTUM | RTS_VMINHIBIT  // Not runnable yet
  }
```

**After Fork Returns to User**:
```
proc_table[2] (parent):
  {
    // All registers restored
    p_reg.ax = 0x0001c003       // Child PID in EAX
    p_rts_flags = RTS_RUNNABLE   // Ready to run again
  }

proc_table[3] (child):
  {
    // Waiting for VM to set up page tables
    p_rts_flags = RTS_NO_QUANTUM | RTS_VMINHIBIT
  }
```

### 5.3 Register State During Context Switch

**Parent Before Syscall**:
```
EAX:    2 (some value)
EBX:    0x0804abc0
ECX:    fork_syscall_number
EDX:    (parameter)
ESP:    0x1ff00000 (parent stack)
EIP:    0x08048f20 (fork call address)
EBP:    0x1ff00010 (parent frame)
```

**Kernel Saves (SAVE_PROCESS_CTX)**:
```
Process table:
  AXREG:  2
  BXREG:  0x0804abc0
  CXREG:  fork_syscall_number
  DXREG:  (parameter)
  SPREG:  0x1ff00000
  PCREG:  0x08048f20 (address after INT)
  BPREG:  0x1ff00010
```

**Kernel Copies to Child**:
```
Child process table:
  AXREG:  0          // MODIFIED
  BXREG:  0x0804abc0 // COPIED
  CXREG:  fork_syscall_number  // COPIED
  DXREG:  (parameter)  // COPIED
  SPREG:  0x1ff00000   // COPIED
  PCREG:  0x08048f20   // COPIED (runs same code)
  BPREG:  0x1ff00010   // COPIED
```

**Parent After Return to User**:
```
EAX:    child_pid  (restored from saved context)
EBX:    0x0804abc0
ECX:    fork_syscall_number
EDX:    (parameter)
ESP:    0x1ff00000
EIP:    0x08048f20 (continue after fork call)
EBP:    0x1ff00010
```

**Child When It Runs** (after VM sets up memory):
```
EAX:    0          (different from parent!)
EBX:    0x0804abc0 (same)
ECX:    fork_syscall_number  (same)
EDX:    (parameter) (same)
ESP:    0x1ff00000 (same)
EIP:    0x08048f20 (same - runs fork call location)
EBP:    0x1ff00010 (same)
CR3:    <child page table> (set by VM, different from parent!)
```

---

## SECTION 6: EXEC SYSCALL SEQUENCE

### 6.1 Exec Syscall Overview

After fork creates a child, the child typically calls exec to load a new program:

```c
// Child process after fork:
if (pid == 0) {
  // Child code
  execve("/bin/ls", argv, envp);  // Load new program
}
```

### 6.2 Exec Syscall Entry

**Libc exec() call**:
```c
int execve(const char *path, char *const argv[], char *const envp[]) {
  message m;
  m.m_type = SYS_EXEC;
  
  m.m_lsys_krn_sys_exec.endpt = sys_getpid();  // Calling process
  m.m_lsys_krn_sys_exec.ip = entry_point;     // New entry point
  m.m_lsys_krn_sys_exec.stack = new_sp;       // New stack pointer
  m.m_lsys_krn_sys_exec.name = argv[0];       // Program name
  m.m_lsys_krn_sys_exec.ps_str = ps_strings;  // Process strings
  
  return sendrec(SYSTEM, &m);
}
```

### 6.3 do_exec() Implementation

**File**: `minix/kernel/system/do_exec.c`

```c
int do_exec(struct proc *caller, message *m_ptr) {
  struct proc *rp;
  int proc_nr;
  char name[PROC_NAME_LEN];
  
  // Validate process
  if(!isokendpt(m_ptr->m_lsys_krn_sys_exec.endpt, &proc_nr))
    return EINVAL;
  
  rp = proc_addr(proc_nr);
  
  // Save new program name
  data_copy(caller->p_endpoint, m_ptr->m_lsys_krn_sys_exec.name,
    KERNEL, (vir_bytes) name, sizeof(name) - 1);
  name[sizeof(name)-1] = '\0';
  
  // Update process registers to new program state
  arch_proc_init(rp,
    m_ptr->m_lsys_krn_sys_exec.ip,     // New EIP
    m_ptr->m_lsys_krn_sys_exec.stack,  // New ESP
    m_ptr->m_lsys_krn_sys_exec.ps_str, // PS strings
    name);                              // Program name
  
  // Clear FPU state (new program doesn't inherit FPU)
  rpc->p_misc_flags &= ~MF_FPU_INITIALIZED;
  
  // Unlock process (allow it to run)
  RTS_UNSET(rp, RTS_RECEIVING);
  
  return OK;
}
```

### 6.4 arch_proc_init() (x86 Specific)

**File**: `minix/kernel/arch/i386/protect.c`

**Effects on CPU State**:
```c
void arch_proc_init(struct proc *rp, u32_t pc, u32_t sp, ...) {
  // Set up segment registers for user mode
  rp->p_reg.cs = USER_CS_SELECTOR;    // 0x1b (Ring 3)
  rp->p_reg.ds = USER_DS_SELECTOR;    // 0x23 (Ring 3)
  rp->p_reg.ss = USER_DS_SELECTOR;    // 0x23 (Ring 3)
  
  // Set new instruction pointer and stack pointer
  rp->p_reg.pc = pc;                  // EIP = entry point
  rp->p_reg.sp = sp;                  // ESP = new stack
  
  // Initialize other registers to sensible values
  rp->p_reg.ax = 0;
  rp->p_reg.bx = 0;
  rp->p_reg.cx = 0;
  rp->p_reg.dx = 0;
  rp->p_reg.si = 0;
  rp->p_reg.di = 0;
  rp->p_reg.bp = sp;                  // Frame pointer at stack top
}
```

---

## SECTION 7: CPU CONTEXT STATE SUMMARY

### 7.1 Fork Sequence CPU States

**State 1: User at Fork Call**
```
Process: parent
EIP: 0x08048f20 (fork() call location)
EAX: (parent data)
CS: 0x1b (Ring 3)
EFLAGS: IF=1
CPL: 3
```

**State 2: Kernel INT Handler**
```
Process: parent (context saved)
EIP: 0x80000xxx (mpx.S hwint handler)
CS: 0x08 (Ring 0)
EFLAGS: IF=0
CPL: 0
Stack: Kernel stack
```

**State 3: In do_fork()**
```
CPU: Ring 0, kernel
Process Table: Parent saved, child copied
Action: Duplicate process entry
```

**State 4: Return to Parent**
```
Process: parent (restored)
EIP: 0x08048f20 (instruction after fork)
EAX: child_pid (new value)
CS: 0x1b (Ring 3)
EFLAGS: IF=1
CPL: 3
```

**State 5: Child Runs (Much Later)**
```
Process: child
EIP: 0x08048f20 (same as parent - at fork call)
EAX: 0 (child return value)
CS: 0x1b (Ring 3)
EFLAGS: IF=1
CPL: 3
CR3: child_page_tables (different from parent)
```

### 7.2 Exec Sequence CPU States

**State 1: Child at Exec Call**
```
Process: child
EIP: 0x08048f40 (execve() call)
ESP: child stack
```

**State 2: After Exec in Kernel**
```
Process table[child]:
  EIP = entry_point_of_new_program (from exec syscall)
  ESP = new_stack_pointer (from exec syscall)
  Other registers: cleared/initialized
```

**State 3: Child Runs New Program**
```
Process: child
EIP: <new program entry point>
ESP: <new program stack>
CS: 0x1b (Ring 3, still user mode)
EFLAGS: IF=1
CPL: 3
// Old program code/data completely replaced
// New program /bin/ls (or similar) starts execution
```

---

## CONCLUSION: FORK + EXEC ORCHESTRATION

**Complete Workflow**:

1. **Fork Creates Child** (identical copy of parent)
   - All registers copied
   - Both processes point to same code
   - EAX differs (parent gets PID, child gets 0)
   - Child's memory awaits VM setup

2. **Exec Replaces Child** (new program)
   - EIP changed to new program entry point
   - ESP changed to new program stack
   - Other registers initialized
   - Old program entirely replaced

3. **CPU Context** Transitions Through:
   - Ring 3 (user) -> Ring 0 (kernel) -> Ring 3 (user)
   - Multiple process table entries
   - Memory address spaces (via CR3 page tables)
   - Instruction sequences (same code vs new code)

4. **Key CPU Invariants**:
   - Privilege level: Kernel syscall entry == Ring 0
   - Stack: User stack during user mode, kernel stack during kernel mode
   - Memory: Page tables isolated per process (CR3 per-process)
   - Registers: Saved/restored across context switches
