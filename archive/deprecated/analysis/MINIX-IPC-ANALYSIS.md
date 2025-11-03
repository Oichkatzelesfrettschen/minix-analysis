# MINIX 3.4 Inter-Process Communication (IPC) Analysis

**Generated**: 2025-10-31
**Focus**: Message structures, routing, and performance

## Message Structures Overview

Total message types defined: 11

| Message Type | Fields | Size | Purpose |
|--------------|--------|------|----------|
| mess_u8 | 56 bytes | 56 | Byte array variant |
| mess_u16 | 28 words | 56 | 16-bit array variant |
| mess_u32 | 14 dwords | 56 | 32-bit array variant |
| mess_u64 | 7 qwords | 56 | 64-bit array variant |
| mess_1 | 4 ints + 4 ptrs | 56 | Generic syscalls |
| mess_2 | Mixed types | 56 | Large integers + signals |
| mess_3 | 2 ints + 1 ptr + path | 56 | Path operations |
| mess_4 | Large integers | 56 | Time/long values |
| mess_7 | 5 ints + 2 ptrs | 56 | Multiple integers |
| mess_9 | 2 qwords + longs | 56 | Extended data |
| mess_10 | qword + ints + longs | 56 | Mixed large types |

## IPC Message Flow


# MINIX 3.4 IPC Message Flow Analysis

## Message Structure Overview

MINIX uses a unified message type with multiple message fields organized into
different message variants (mess_1, mess_2, ..., mess_10, etc.) for different
types of communication.

## Key Message Types

### Kernel Syscall Messages
- `SYS_FORK`: Process creation request
- `SYS_EXEC`: Process execution context update
- `SYS_KILL`: Process termination signal
- `SYS_PRIVCTL`: Privilege control operations
- `SYS_SCHEDULE`: Process scheduling operations

### IPC Operations

#### Send (SEND)
- Sends a message from sender to receiver
- Receiver must already be receiving
- Blocks if receiver not ready
- Returns when message transferred

#### Receive (RECEIVE)
- Process waits for message from any sender
- Blocked until message arrives
- Message source stored in process state
- Returns immediately when message available

#### Send/Receive (SENDREC)
- Combined send + receive operation
- Atomic from sender perspective
- Used for synchronous RPC-like calls
- Returns when reply received

## Message Routing

1. Sender process encodes message in memory
2. Sender calls IPC operation (INT 0x30 syscall)
3. Kernel validates sender/receiver endpoints
4. Kernel copies message to receiver's buffer
5. Receiver wakes up if blocked
6. Receiver reads and processes message
7. Receiver sends reply (if sendrec)
8. Kernel returns control to sender

## Endpoint Mechanism

- Endpoints are process identifiers (32-bit values)
- Encode process slot, generation number
- Allow kernel to detect stale references
- Prevent use-after-free type bugs

## Message Fields

MINIX uses multiple message types for different purposes:

- **mess_1**: Generic integers and pointers (most common)
- **mess_2**: Large integers and signal sets
- **mess_3**: Path strings and small data
- **mess_4**: Long integers
- **mess_7**: Multiple integers and pointers
- **mess_9**: Large integers and longs
- **mess_10**: Mixed integers and longs

## CPU Context During IPC

### Sender Side
1. Builds message in user memory (Ring 3)
2. Issues INT 0x30 syscall (privilege transition)
3. Kernel validates message parameters
4. Kernel copies message (kernel memory operation)
5. Kernel may block sender if receiver not ready
6. Returns to user code when operation complete

### Receiver Side
1. Issues RECEIVE syscall to wait for messages
2. Kernel blocks receiver if no messages pending
3. When message arrives, kernel wakes receiver
4. Kernel provides message to receiver buffer
5. Receiver processes message in Ring 3
6. Receiver issues SEND for reply (if needed)

## IPC Synchronization

- Kernel maintains per-process message buffers
- Sender/receiver state managed in process table
- Blocking tracked via process state flags
- Delivery guaranteed at kernel level

## Performance Characteristics

### Latency Factors
- Syscall entry/exit overhead (context switch)
- Message validation
- Memory copy operations
- Receiver scheduling delay
- Context switching on return

### Optimization Opportunities
- Message batching (multiple messages per syscall)
- Shared memory for large message payloads
- Grant-based copy-on-write mechanism
- Cached endpoint validations

## IPC in MINIX Design

MINIX uses IPC as the fundamental OS mechanism:
- All inter-process communication uses IPC
- Kernel itself is minimal (< 10KB core)
- Most OS services run as regular processes
- Microkernel design enables isolation
- Fault tolerance through process restart

## Key IPC Syscalls

### SEND
- **Purpose**: Send message from sender to receiver
- **Blocking**: Yes (blocks until receiver ready)
- **Return**: When message transferred

### RECEIVE
- **Purpose**: Receive message from any sender
- **Blocking**: Yes (blocks until message available)
- **Return**: When message received

### SENDREC
- **Purpose**: Send + receive combined (RPC-style)
- **Blocking**: Yes (blocks until reply)
- **Return**: When reply received

## Endpoint Mechanism

MINIX 3.4 uses a 32-bit endpoint value encoding:
```
Endpoint Structure:
- Process slot (index into process table)
- Generation number (prevents reuse)
- Special endpoints: KERNEL, HARDWARE, etc.
```

Benefits:
- Detects stale process references
- Prevents use-after-free style bugs
- Enables safe process cleanup

