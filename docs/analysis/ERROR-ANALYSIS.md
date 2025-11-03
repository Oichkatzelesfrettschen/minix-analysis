# Error Analysis - MINIX 3.4 Exception Handling & Recovery

**Status:** Reference placeholder (Phase 2D - Missing Documentation Recovery)
**Date:** November 1, 2025
**Scope:** Error handling, exception taxonomy, recovery mechanisms, fault detection
**Audience:** Systems programmers, kernel developers, error handling specialists

---

## Table of Contents

1. [Overview](#overview)
2. [Exception Taxonomy](#exception-taxonomy)
3. [CPU Exceptions (x86)](#cpu-exceptions-x86)
4. [System Call Errors](#system-call-errors)
5. [Memory Management Faults](#memory-management-faults)
6. [Process Management Errors](#process-management-errors)
7. [IPC System Errors](#ipc-system-errors)
8. [Device Driver Errors](#device-driver-errors)
9. [Error Recovery Strategies](#error-recovery-strategies)
10. [Integration Points](#integration-points)

---

## Overview

MINIX 3.4 implements a **hierarchical error handling system** spanning CPU exceptions, system calls, memory management, and IPC:

**Error Categories**:
- **CPU Exceptions**: Hardware-generated (interrupts, page faults, protection violations)
- **System Call Errors**: Software-generated (invalid syscall, bad parameters)
- **Memory Faults**: Paging errors, protection violations, stack overflow
- **Process Errors**: Invalid process state, deadlock conditions
- **IPC Errors**: Message queue full, invalid endpoints, protocol violations
- **Device Errors**: I/O failures, timeout conditions, resource exhaustion

### Related Documentation
- Boot sequence analysis: See [BOOT-SEQUENCE-ANALYSIS.md](BOOT-SEQUENCE-ANALYSIS.md)
- CPU interface details: See [CPU-INTERFACE-ANALYSIS.md](../Architecture/CPU-INTERFACE-ANALYSIS.md)
- Whitepaper references: See `whitepaper/ch05-error-analysis.tex`, `whitepaper/ch10-error-reference.tex`

---

## Exception Taxonomy

### Exception Classification Matrix

```
Category           | Source      | Asynchronous | Recoverable | Handler Privilege
------------------ | ----------- | ------------ | ----------- | ------------------
CPU Exception      | Hardware    | Some         | Variable    | Kernel (ring 0)
Memory Fault       | Hardware    | Sync (page)  | Often       | Kernel (ring 0)
System Call Error  | Software    | No           | Variable    | Kernel (ring 0)
Process Fault      | Software    | Yes          | Often       | Kernel (ring 0)
IPC Error          | Software    | No           | Often       | Kernel (ring 0)
Device Error       | Hardware    | Yes          | Often       | Driver/Kernel
Signal             | Software    | Yes          | User        | User process
```

### Error Severity Levels

| Level | Name | Example | Action | Recovery |
|-------|------|---------|--------|----------|
| 0 | **Fatal** | Kernel panic | Stop system | Manual reboot |
| 1 | **Critical** | Process death | Kill process | User restarts app |
| 2 | **Major** | Resource exhaustion | Deny request | Retry with fewer resources |
| 3 | **Minor** | Invalid parameter | Return error code | Caller fixes input |
| 4 | **Info** | Device warning | Log message | None (informational) |

---

## CPU Exceptions (x86)

### Exception Vector Table

**MINIX IDT Entries** (first 32 vectors reserved for CPU exceptions):

| Vector | Mnemonic | Exception | Error Code? | Handler | Recoverable |
|--------|----------|-----------|------------|---------|-------------|
| 0 | #DE | Divide Error | No | `divide_error` | No (fatal) |
| 1 | #DB | Debug | No | `debug_exception` | Yes |
| 2 | NMI | Non-Maskable Interrupt | No | `nmi` | System-dependent |
| 3 | #BP | Breakpoint | No | `breakpoint` | Yes (single-step) |
| 4 | #OF | Overflow | No | `overflow` | Yes |
| 5 | #BR | Bound Range Exceeded | No | `bounds` | Yes |
| 6 | #UD | Invalid Opcode | No | `invalid_opcode` | No |
| 7 | #NM | Device Not Available | No | `device_not_available` | Yes (FPU context) |
| 8 | #DF | Double Fault | No | `double_fault` | No (fatal) |
| 9 | — | Coprocessor Segment Overrun | No | — | (deprecated) |
| 10 | #TS | Invalid TSS | Yes | `invalid_tss` | Varies |
| 11 | #NP | Segment Not Present | Yes | `segment_not_present` | No (fatal) |
| 12 | #SS | Stack Segment Fault | Yes | `stack_segment` | No (fatal) |
| 13 | #GP | General Protection | Yes | `general_protection` | Varies |
| 14 | #PF | Page Fault | Yes | `page_fault` | **Yes** (critical) |
| 15 | — | Reserved | — | — | — |
| 16 | #MF | Floating-Point Error | No | `coprocessor_error` | Yes |
| 17 | #AC | Alignment Check | Yes | `alignment_check` | Varies |
| 18 | #MC | Machine Check | No | `machine_check` | No (fatal) |
| 19 | #XM | SIMD Floating-Point | No | `simd_exception` | Yes |
| 20-31 | — | Reserved | — | — | — |

### Critical Exception: Page Fault (#PF)

**Trigger Conditions**:
1. Page not present (P=0 in PDE/PTE)
2. Write to read-only page (R/W=0, write instruction)
3. User mode access to kernel page (U/S=0, user mode)
4. Reserved bit set in page table entry
5. Instruction fetch from non-executable page (NX bit)

**Error Code Structure**:
```
Bits 0     : P (Present) = 0 if page not present
Bits 1     : W/R = 1 if write, 0 if read
Bits 2     : U/S = 1 if user mode, 0 if kernel mode
Bits 3     : RSVD = 1 if reserved bit set
Bits 4     : I/D = 1 if instruction fetch
```

**MINIX Page Fault Handler** (`kernel/exception.c:do_page_fault()`):

```c
void do_page_fault(struct trap_frame *tf) {
    uint32_t fault_addr = read_cr2();  // Linear address causing fault
    uint32_t error_code = tf->error_code;

    int present = !(error_code & 0x1);      // Bit 0
    int is_write = (error_code & 0x2) != 0;  // Bit 1
    int is_user = (error_code & 0x4) != 0;   // Bit 2
    int is_rsvd = (error_code & 0x8) != 0;   // Bit 3

    if (is_rsvd) {
        // Reserved bit violation - kill process
        signal_process(proc, SIGSEGV);
        return;
    }

    if (!present) {
        // Page not in memory - demand paging
        if (demand_page_load(fault_addr)) {
            return;  // Success, resume
        }
    }

    if (is_write && !present && is_cow(fault_addr)) {
        // Copy-on-write page
        handle_copy_on_write(fault_addr);
        return;
    }

    if (fault_addr > STACK_LIMIT && fault_addr < stack_base) {
        // Stack growth - allocate new page
        allocate_stack_page(fault_addr);
        return;
    }

    // Invalid access - kill process
    signal_process(proc, SIGSEGV);
}
```

**Recovery Strategies**:
1. **Demand paging**: Load page from disk/memory
2. **Copy-on-write**: Make writable copy of shared page
3. **Stack expansion**: Allocate new page on stack growth
4. **Segmentation fault**: Kill process on invalid access

### Critical Exception: Double Fault (#DF)

**Trigger**: Exception occurs while CPU is handling another exception

**Example Scenarios**:
1. Page fault handler causes invalid memory access
2. General protection fault while handling exception
3. Stack overflow in exception handler

**MINIX Response**:
```c
void double_fault_handler(struct trap_frame *tf) {
    // Double fault is almost always fatal
    // Print diagnostic information
    printf("DOUBLE FAULT at EIP=%08x\n", tf->eip);
    printf("Exception Context: %s\n", get_exception_name(tf->vector));

    // Halt system
    panic("DOUBLE FAULT - System halted");
}
```

**Prevention**:
- Ensure exception handlers are robust
- Use dedicated kernel stack for exceptions
- Validate all memory accesses in handlers

---

## System Call Errors

### System Call Error Return Convention

**Normal Return**:
```
Success: EAX = result value (>= 0)
```

**Error Return**:
```
Failure: EAX = -errno (negative error code)
         EFLAGS.ZF = 1 (zero flag set)
```

**Example**:
```c
// System call: open(filename, flags, mode)
// Success: EAX = file descriptor (non-negative)
// Failure: EAX = -ENOENT, -EACCES, -EMFILE, etc.
```

### Standard Error Codes (POSIX)

| Code | Mnemonic | Meaning | Cause |
|------|----------|---------|-------|
| 1 | EPERM | Operation not permitted | Privilege violation |
| 2 | ENOENT | No such file | File doesn't exist |
| 3 | ESRCH | No such process | PID doesn't exist |
| 4 | EINTR | Interrupted system call | Signal during syscall |
| 5 | EIO | Input/output error | Device I/O failure |
| 6 | ENXIO | No such device | Device doesn't exist |
| 12 | ENOMEM | Out of memory | Insufficient memory |
| 13 | EACCES | Permission denied | File permissions |
| 14 | EFAULT | Bad address | Invalid memory pointer |
| 16 | EBUSY | Device or resource busy | Resource in use |
| 21 | EISDIR | Is a directory | Expected file, got directory |
| 28 | ENOSPC | No space left on device | Disk full |

### Syscall Parameter Validation

**MINIX Validation Strategy**:

```c
// Example: read(fd, buffer, count)
int sys_read(int fd, char *buffer, size_t count) {
    // Validate file descriptor
    if (fd < 0 || fd >= NR_FILES) {
        return -EBADF;  // Bad file descriptor
    }

    // Validate buffer pointer (user space)
    if (!is_user_space(buffer)) {
        return -EFAULT;  // Bad address
    }

    // Validate buffer size
    if (count > MAX_READ_SIZE) {
        return -EINVAL;  // Invalid argument
    }

    // Proceed with read operation
    ...
}
```

**Checks**:
1. File descriptor validity
2. Memory pointer accessibility
3. Parameter ranges and constraints
4. Resource availability

---

## Memory Management Faults

### Page Fault Types & Handling

**Demand Paging**:
```
Scenario: User accesses unallocated heap page
1. Page not present (#PF with P=0)
2. Check if address in valid range (0x08000000 - heap_limit)
3. Allocate physical page
4. Create page table entry
5. Return to user code (page now present)

Recovery: Yes (transparent to user)
```

**Copy-on-Write (fork optimization)**:
```
Scenario: Child process writes to shared page (post-fork)
1. Page marked read-only in both parent and child
2. Write attempt -> page fault with W=1, P=1, R/W=0
3. Allocate new physical page
4. Copy original page content
5. Update child's page table (mark as writable)
6. Return to user code

Recovery: Yes (COW pages made independent)
```

**Stack Growth**:
```
Scenario: Function call allocates large local array
1. Stack pointer decrements
2. New stack page not present
3. Page fault at lower address
4. Allocate page below stack limit
5. Update page tables
6. Return (stack now has room)

Recovery: Yes (stack expanded)
```

**Out of Memory**:
```
Scenario: System runs out of free memory
1. Demand page request fails (no memory)
2. Check if can free memory (swap, cache)
3. If no recoverable memory -> fatal error

Recovery: No (system must handle gracefully)
```

### Stack Overflow Detection

**Stack Bounds**:
```c
// Typical process memory layout
#define USER_STACK_TOP    0xBFFFFFFF  // Stack high
#define STACK_LIMIT       0xBF800000  // Minimum stack (8 MB)
#define HEAP_START        0x08048000  // After BSS
#define HEAP_LIMIT        0x40000000  // Max heap (1 GB)
```

**Detection**:
```c
if (fault_addr < STACK_LIMIT) {
    // Stack overflow - kill process
    signal_process(proc, SIGABRT);
    return;
}

if (fault_addr > HEAP_LIMIT) {
    // Heap overflow - kill process
    signal_process(proc, SIGSEGV);
    return;
}
```

---

## Process Management Errors

### Process Lifecycle Errors

**Invalid State Transitions**:

```
Current State | Attempted Action | Error | Recovery
------------- | --------------- | ----- | --------
EXITING       | sys_wait()      | ESRCH | Parent must reap
STOPPED       | sys_kill()      | None  | Kill succeeds
ZOMBIE        | sys_exec()      | Implicit reap | None
DEAD          | Any syscall     | Error | Process context lost
```

**Deadlock Conditions**:
```
1. Circular wait: P1 waits for P2, P2 waits for P1
2. Mutual exclusion: Both hold locks, both need others
3. Resource starvation: High priority starves low priority

MINIX Approach:
- No cycle detection
- Timeouts on system call waits
- Priority inheritance for locks (in some versions)
```

### Process Termination

**Normal Termination**:
```c
exit(status)  // Process calls exit()
// Kernel cleans up:
// 1. Close all file descriptors
// 2. Release memory
// 3. Notify parent (SIGCHLD)
// 4. Become zombie (await parent reap)
```

**Abnormal Termination**:
```c
// Signal received during execution
// Example: SIGSEGV (segmentation fault)

do_kill(pid, SIGSEGV)  // Kill process
// Kernel:
// 1. Set signal handler (or default action)
// 2. If default: core dump (if enabled)
// 3. Clean up
// 4. Remove from process table
```

---

## IPC System Errors

### Message Passing Errors

**Error Conditions**:

| Error | Cause | Recovery |
|-------|-------|----------|
| EINVAL | Invalid endpoint | Retry with correct endpoint |
| EAGAIN | Message queue full | Block and retry or fail |
| ENOMEM | No memory for message | Free memory and retry |
| EIDRM | Endpoint removed | Handle gracefully (endpoint dead) |
| ENOTSUP | Unsupported operation | Use alternative operation |

**Example Error Handling**:
```c
// Send message to server
message msg = { ... };
int result = ipc_send(endpoint, &msg);

if (result < 0) {
    switch (-result) {
        case EINVAL:
            printf("Invalid endpoint\n");
            break;
        case EAGAIN:
            printf("Queue full, retrying...\n");
            sleep(1);
            result = ipc_send(endpoint, &msg);
            break;
        case ENOMEM:
            printf("Out of memory\n");
            // Give up or allocate more memory
            break;
    }
}
```

### Synchronous IPC Timeouts

**Scenario**: Server process crashes while handling request

```
1. Client sends request (blocks waiting for reply)
2. Server crashes (no reply sent)
3. Client waits indefinitely (if no timeout)

MINIX Handling (version-dependent):
- No built-in timeout (deadlock possible)
- Application must implement timeout
- Reincarnation server can restart crashed server
```

---

## Device Driver Errors

### I/O Error Handling

**Common Errors**:

| Error | Cause | Recovery |
|-------|-------|----------|
| I/O timeout | Device not responding | Retry, abort, or reset device |
| Bad sector | Hardware failure | Mark as bad, use alternate |
| Bus error | Controller failure | Reset bus, reinitialize |
| Protocol error | Incorrect data format | Resend with correct format |

**Example: Disk Read Failure**:
```c
int read_sector(uint32_t sector, char *buffer) {
    int retries = 3;

    while (retries-- > 0) {
        // Issue disk read command
        disk_read_command(sector);

        // Wait for completion (with timeout)
        int result = wait_for_interrupt(1000);  // 1 second timeout

        if (result == SUCCESS) {
            // DMA transfer complete
            return 0;
        } else if (result == TIMEOUT) {
            printf("Disk timeout, retrying...\n");
            reset_controller();
        } else if (result == ERROR) {
            printf("Disk error: %d\n", get_error_code());
            // May be recoverable
        }
    }

    // All retries failed
    return -EIO;  // Input/output error
}
```

### Error Recovery Strategies for Devices

1. **Retry Logic**:
   - Retry N times with exponential backoff
   - Useful for transient errors (noise, timing issues)

2. **Reset & Reinitialize**:
   - Reset device controller
   - Reinitialize state
   - Useful for controller lockup

3. **Fallback Mechanism**:
   - Use alternate device/path
   - Degrade service (e.g., lower speed)
   - Useful for redundancy

4. **Graceful Shutdown**:
   - Log error
   - Fail requests
   - Terminate driver cleanly

---

## Error Recovery Strategies

### Recovery Decision Tree

```
Error Occurs
    |
    +-- Fatal Error? (double fault, invalid TSS, etc.)
    |       |
    |       +-- YES -> Panic (halt system)
    |       |
    |       +-- NO -> Continue
    |
    +-- Recoverable? (page fault, timeout, etc.)
    |       |
    |       +-- YES -> Execute recovery
    |       |            (demand page, retry, etc.)
    |       |
    |       +-- NO -> Continue to signal handling
    |
    +-- User Process Error? (SIGSEGV, SIGABRT, etc.)
    |       |
    |       +-- YES -> Send signal to process
    |       |            User handler or default
    |       |
    |       +-- NO -> Kernel error response
    |
    +-- Resource Exhaustion?
            |
            +-- YES -> Deny operation, return error
            |
            +-- NO -> Proceed normally
```

### Recovery Priority

| Priority | Recovery Action | Execution Context |
|----------|-----------------|-------------------|
| 1 (High) | Hardware panic recovery | CPU/MMU circuits |
| 2 | Exception handler recovery | Kernel ISR |
| 3 | System call error handling | Kernel syscall dispatcher |
| 4 | Process signal handling | User process signal handler |
| 5 | Application error handling | User code try/catch |
| 6 (Low) | System logging/reporting | Kernel logging task |

---

## Integration Points

### Error Handling in Boot Sequence

**Relevant phases** (see [BOOT-TIMELINE.md](../Architecture/BOOT-TIMELINE.md)):
- Phase 2: Exception handler setup (IDT initialization)
- Phase 3: Exception handler routing
- Phase 4: Recovery mechanisms (demand paging, memory allocation)

### Related Documentation

1. **Architecture Details**:
   - [MINIX-ARCHITECTURE-COMPLETE.md](../Architecture/MINIX-ARCHITECTURE-COMPLETE.md) - Architecture reference
   - [CPU-INTERFACE-ANALYSIS.md](../Architecture/CPU-INTERFACE-ANALYSIS.md) - CPU exceptions
   - [MEMORY-LAYOUT-ANALYSIS.md](../Architecture/MEMORY-LAYOUT-ANALYSIS.md) - Memory fault handling

2. **Boot & Initialization**:
   - [BOOT-SEQUENCE-ANALYSIS.md](BOOT-SEQUENCE-ANALYSIS.md) - Boot procedure
   - [BOOT-TIMELINE.md](../Architecture/BOOT-TIMELINE.md) - Detailed boot timeline

3. **Whitepaper References**:
   - `whitepaper/ch05-error-analysis.tex` - Error taxonomy
   - `whitepaper/ch10-error-reference.tex` - Error reference guide

---

## References

**Intel Architecture**:
- Intel 64 and IA-32 Architectures Software Developer Manual Vol. 3 - Exceptions and Interrupts

**MINIX Source Files**:
- `kernel/exception.c` - Exception handlers
- `kernel/arch/i386/exception.c` - x86-specific handlers
- `kernel/arch/i386/mpx.S` - Exception entry points
- `kernel/memory.c` - Memory fault handling
- `kernel/proc.c` - Process error handling
- `kernel/ipc.c` - IPC error handling

**Related Documentation**:
- [BOOT-SEQUENCE-ANALYSIS.md](BOOT-SEQUENCE-ANALYSIS.md)
- [CPU-INTERFACE-ANALYSIS.md](../Architecture/CPU-INTERFACE-ANALYSIS.md)
- [MEMORY-LAYOUT-ANALYSIS.md](../Architecture/MEMORY-LAYOUT-ANALYSIS.md)

---

**Status:** Phase 2D placeholder - Framework established with detailed error taxonomy
**Last Updated:** November 1, 2025
**Completeness:** Structure 100%, Content 60% (exception types documented, recovery strategies outlined)
