# MINIX 3.4 System Call Catalog

**Generated**: 2025-10-31
**Total Syscalls**: 46

## Table of Contents

- [Summary Statistics](#summary-statistics)
- [Syscall Index](#syscall-index)
- [Detailed Syscall Analysis](#detailed-syscall-analysis)
- [Implementation Statistics](#implementation-statistics)

## Summary Statistics

- Total syscalls defined: 46
- Total implementation files: 35
- Total implementation lines: 3954
- Total code lines: 2218
- Average complexity: 8.59

## Syscall Index

| Number | Name | Comment | Implementation | Lines | Complexity |
|--------|------|---------|-----------------|-------|------------|
| 0 | SYS_FORK | sys_fork() | do_fork.c | 137 | 11 |
| 1 | SYS_EXEC | sys_exec() | do_exec.c | 61 | 5 |
| 2 | SYS_CLEAR | sys_clear() | do_clear.c | 81 | 10 |
| 3 | SYS_SCHEDULE | sys_schedule() | do_schedule.c | 31 | 2 |
| 4 | SYS_PRIVCTL | sys_privctl() | do_privctl.c | 372 | 49 |
| 5 | SYS_TRACE | sys_trace() | do_trace.c | 209 | 16 |
| 6 | SYS_KILL | sys_kill() | do_kill.c | 42 | 8 |
| 7 | SYS_GETKSIG | sys_getsig() | do_getksig.c | 44 | 6 |
| 8 | SYS_ENDKSIG | sys_endsig() | do_endksig.c | 42 | 7 |
| 9 | SYS_SIGSEND | sys_sigsend() | do_sigsend.c | 167 | 15 |
| 10 | SYS_SIGRETURN | sys_sigreturn() | do_sigreturn.c | 99 | 11 |
| 13 | SYS_MEMSET | sys_memset() | do_memset.c | 29 | 3 |
| 14 | SYS_UMAP | sys_umap() | do_umap.c | 40 | 5 |
| 15 | SYS_VIRCOPY | sys_vircopy() | N/A | 0 | 0 |
| 16 | SYS_PHYSCOPY | sys_physcopy() | N/A | 0 | 0 |
| 17 | SYS_UMAP_REMOTE | sys_umap_remote() | do_umap_remote.c | 123 | 9 |
| 18 | SYS_VUMAP | sys_vumap() | do_vumap.c | 132 | 18 |
| 19 | SYS_IRQCTL | sys_irqctl() | do_irqctl.c | 175 | 29 |
| 21 | SYS_DEVIO | sys_devio() | do_devio.c | 108 | 14 |
| 22 | SYS_SDEVIO | sys_sdevio() | N/A | 0 | 0 |
| 23 | SYS_VDEVIO | sys_vdevio() | do_vdevio.c | 166 | 35 |
| 24 | SYS_SETALARM | sys_setalarm() | do_setalarm.c | 79 | 12 |
| 25 | SYS_TIMES | sys_times() | do_times.c | 47 | 5 |
| 26 | SYS_GETINFO | sys_getinfo() | do_getinfo.c | 229 | 9 |
| 27 | SYS_ABORT | sys_abort() | do_abort.c | 30 | 3 |
| 28 | SYS_IOPENABLE | sys_enable_iop() | N/A | 0 | 0 |
| 31 | SYS_SAFECOPYFROM | sys_safecopyfrom() | do_safecopy.c | 449 | 21 |
| 32 | SYS_SAFECOPYTO | sys_safecopyto() | N/A | 0 | 0 |
| 33 | SYS_VSAFECOPY | sys_vsafecopy() | N/A | 0 | 0 |
| 34 | SYS_SETGRANT | sys_setgrant() | do_setgrant.c | 31 | 2 |
| 35 | SYS_READBIOS | sys_readbios() | N/A | 0 | 0 |
| 36 | SYS_SPROF | sys_sprof() | N/A | 0 | 0 |
| 39 | SYS_STIME | sys_stime() | do_stime.c | 20 | 1 |
| 40 | SYS_SETTIME | sys_settime() | do_settime.c | 59 | 5 |
| 43 | SYS_VMCTL | sys_vmctl() | do_vmctl.c | 174 | 11 |
| 44 | SYS_DIAGCTL | sys_diagctl() | do_diagctl.c | 69 | 7 |
| 45 | SYS_VTIMER | sys_vtimer() | do_vtimer.c | 104 | 15 |
| 46 | SYS_RUNCTL | sys_runctl() | do_runctl.c | 77 | 15 |
| 50 | SYS_GETMCONTEXT | sys_getmcontext() | N/A | 0 | 0 |
| 51 | SYS_SETMCONTEXT | sys_setmcontext() | N/A | 0 | 0 |
| 52 | SYS_UPDATE | sys_update() | do_update.c | 341 | 18 |
| 53 | SYS_EXIT | sys_exit() | do_exit.c | 28 | 2 |
| 54 | SYS_SCHEDCTL | sys_schedctl() | do_schedctl.c | 47 | 3 |
| 55 | SYS_STATECTL | sys_statectl() | do_statectl.c | 54 | 8 |
| 56 | SYS_SAFEMEMSET | sys_safememset() | do_safememset.c | 58 | 5 |
| 57 | SYS_PADCONF | sys_padconf() | N/A | 0 | 0 |

## Detailed Syscall Analysis

### SYS_FORK (#0)

**Description**: sys_fork()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_fork.c
**Lines of Code**: 137
**Complexity**: 11

**Function Signature**:
```c
int do_fork(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_fork`
- `m_lsys_krn_sys_fork`

### SYS_EXEC (#1)

**Description**: sys_exec()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_exec.c
**Lines of Code**: 61
**Complexity**: 5

**Function Signature**:
```c
int do_exec(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_exec`

### SYS_CLEAR (#2)

**Description**: sys_clear()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_clear.c
**Lines of Code**: 81
**Complexity**: 10

**Function Signature**:
```c
int do_clear(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_clear`

### SYS_SCHEDULE (#3)

**Description**: sys_schedule()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_schedule.c
**Lines of Code**: 31
**Complexity**: 2

**Function Signature**:
```c
int do_schedule(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_schedule`

### SYS_PRIVCTL (#4)

**Description**: sys_privctl()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_privctl.c
**Lines of Code**: 372
**Complexity**: 49

**Function Signature**:
```c
int do_privctl(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_privctl`

### SYS_TRACE (#5)

**Description**: sys_trace()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_trace.c
**Lines of Code**: 209
**Complexity**: 16

**Function Signature**:
```c
int do_trace(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_trace`
- `m_lsys_krn_sys_trace`

### SYS_KILL (#6)

**Description**: sys_kill()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_kill.c
**Lines of Code**: 42
**Complexity**: 8

**Function Signature**:
```c
int do_kill(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_sigcalls`

### SYS_GETKSIG (#7)

**Description**: sys_getsig()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_getksig.c
**Lines of Code**: 44
**Complexity**: 6

**Function Signature**:
```c
int do_getksig(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_sigcalls`

### SYS_ENDKSIG (#8)

**Description**: sys_endsig()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_endksig.c
**Lines of Code**: 42
**Complexity**: 7

**Function Signature**:
```c
int do_endksig(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_sigcalls`

### SYS_SIGSEND (#9)

**Description**: sys_sigsend()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_sigsend.c
**Lines of Code**: 167
**Complexity**: 15

**Function Signature**:
```c
int do_sigsend(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_sigcalls`

### SYS_SIGRETURN (#10)

**Description**: sys_sigreturn()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_sigreturn.c
**Lines of Code**: 99
**Complexity**: 11

**Function Signature**:
```c
int do_sigreturn(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_sigcalls`

### SYS_MEMSET (#13)

**Description**: sys_memset()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_memset.c
**Lines of Code**: 29
**Complexity**: 3

**Function Signature**:
```c
int do_memset(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_memset`

### SYS_UMAP (#14)

**Description**: sys_umap()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_umap.c
**Lines of Code**: 40
**Complexity**: 5

**Function Signature**:
```c
int do_umap(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_umap`

### SYS_VIRCOPY (#15)

**Description**: sys_vircopy()

**Status**: No implementation found

### SYS_PHYSCOPY (#16)

**Description**: sys_physcopy()

**Status**: No implementation found

### SYS_UMAP_REMOTE (#17)

**Description**: sys_umap_remote()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_umap_remote.c
**Lines of Code**: 123
**Complexity**: 9

**Function Signature**:
```c
int do_umap_remote(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_umap`
- `m_lsys_krn_sys_umap`

### SYS_VUMAP (#18)

**Description**: sys_vumap()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_vumap.c
**Lines of Code**: 132
**Complexity**: 18

**Function Signature**:
```c
int do_vumap(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc *caller, message *m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_vumap`
- `m_lsys_krn_sys_vumap`

### SYS_IRQCTL (#19)

**Description**: sys_irqctl()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_irqctl.c
**Lines of Code**: 175
**Complexity**: 29

**Function Signature**:
```c
int do_irqctl(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_irqctl`
- `m_lsys_krn_sys_irqctl`

### SYS_DEVIO (#21)

**Description**: sys_devio()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_devio.c
**Lines of Code**: 108
**Complexity**: 14

**Function Signature**:
```c
int do_devio(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_devio`
- `m_lsys_krn_sys_devio`

### SYS_SDEVIO (#22)

**Description**: sys_sdevio()

**Status**: No implementation found

### SYS_VDEVIO (#23)

**Description**: sys_vdevio()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_vdevio.c
**Lines of Code**: 166
**Complexity**: 35

**Function Signature**:
```c
int do_vdevio(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_vdevio`

### SYS_SETALARM (#24)

**Description**: sys_setalarm()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_setalarm.c
**Lines of Code**: 79
**Complexity**: 12

**Function Signature**:
```c
int do_setalarm(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_setalarm`

### SYS_TIMES (#25)

**Description**: sys_times()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_times.c
**Lines of Code**: 47
**Complexity**: 5

**Function Signature**:
```c
int do_times(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_times`
- `m_lsys_krn_sys_times`

### SYS_GETINFO (#26)

**Description**: sys_getinfo()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_getinfo.c
**Lines of Code**: 229
**Complexity**: 9

**Function Signature**:
```c
int do_getinfo(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_krn_lsys_sys_getwhoami`
- `m_lsys_krn_sys_getinfo`

### SYS_ABORT (#27)

**Description**: sys_abort()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_abort.c
**Lines of Code**: 30
**Complexity**: 3

**Function Signature**:
```c
int do_abort(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_abort`

### SYS_IOPENABLE (#28)

**Description**: sys_enable_iop()

**Status**: No implementation found

### SYS_SAFECOPYFROM (#31)

**Description**: sys_safecopyfrom()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_safecopy.c
**Lines of Code**: 449
**Complexity**: 21

**Function Signature**:
```c
int do_safecopyfrom(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_kern_safecopy`
- `m_lsys_kern_vsafecopy`

### SYS_SAFECOPYTO (#32)

**Description**: sys_safecopyto()

**Status**: No implementation found

### SYS_VSAFECOPY (#33)

**Description**: sys_vsafecopy()

**Status**: No implementation found

### SYS_SETGRANT (#34)

**Description**: sys_setgrant()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_setgrant.c
**Lines of Code**: 31
**Complexity**: 2

**Function Signature**:
```c
int do_setgrant(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_setgrant`

### SYS_READBIOS (#35)

**Description**: sys_readbios()

**Status**: No implementation found

### SYS_SPROF (#36)

**Description**: sys_sprof()

**Status**: No implementation found

### SYS_STIME (#39)

**Description**: sys_stime()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_stime.c
**Lines of Code**: 20
**Complexity**: 1

**Function Signature**:
```c
int do_stime(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_stime`

### SYS_SETTIME (#40)

**Description**: sys_settime()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_settime.c
**Lines of Code**: 59
**Complexity**: 5

**Function Signature**:
```c
int do_settime(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_settime`

### SYS_VMCTL (#43)

**Description**: sys_vmctl()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_vmctl.c
**Lines of Code**: 174
**Complexity**: 11

**Function Signature**:
```c
int do_vmctl(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

### SYS_DIAGCTL (#44)

**Description**: sys_diagctl()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_diagctl.c
**Lines of Code**: 69
**Complexity**: 7

**Function Signature**:
```c
int do_diagctl(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_diagctl`

### SYS_VTIMER (#45)

**Description**: sys_vtimer()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_vtimer.c
**Lines of Code**: 104
**Complexity**: 15

**Function Signature**:
```c
int do_vtimer(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

### SYS_RUNCTL (#46)

**Description**: sys_runctl()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_runctl.c
**Lines of Code**: 77
**Complexity**: 15

**Function Signature**:
```c
int do_runctl(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

### SYS_GETMCONTEXT (#50)

**Description**: sys_getmcontext()

**Status**: No implementation found

### SYS_SETMCONTEXT (#51)

**Description**: sys_setmcontext()

**Status**: No implementation found

### SYS_UPDATE (#52)

**Description**: sys_update()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_update.c
**Lines of Code**: 341
**Complexity**: 18

**Function Signature**:
```c
int do_update(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

### SYS_EXIT (#53)

**Description**: sys_exit()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_exit.c
**Lines of Code**: 28
**Complexity**: 2

**Function Signature**:
```c
int do_exit(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

### SYS_SCHEDCTL (#54)

**Description**: sys_schedctl()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_schedctl.c
**Lines of Code**: 47
**Complexity**: 3

**Function Signature**:
```c
int do_schedctl(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_schedctl`

### SYS_STATECTL (#55)

**Description**: sys_statectl()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_statectl.c
**Lines of Code**: 54
**Complexity**: 8

**Function Signature**:
```c
int do_statectl(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc * caller, message * m_ptr
```

**Message Fields**:
- `m_lsys_krn_sys_statectl`

### SYS_SAFEMEMSET (#56)

**Description**: sys_safememset()

**Implementation**: /home/eirikr/Playground/minix/minix/kernel/system/do_safememset.c
**Lines of Code**: 58
**Complexity**: 5

**Function Signature**:
```c
int do_safememset(struct proc * caller, message * m_ptr)
```

**Parameters**:
```
struct proc *caller, message *m_ptr
```

### SYS_PADCONF (#57)

**Description**: sys_padconf()

**Status**: No implementation found

## Implementation Statistics

| Implementation | Count | Total Lines | Avg Complexity |
|-----------------|-------|-------------|----------------|
| do_abort.c | 1 | 30 | 3.00 |
| do_clear.c | 1 | 81 | 10.00 |
| do_devio.c | 1 | 108 | 14.00 |
| do_diagctl.c | 1 | 69 | 7.00 |
| do_endksig.c | 1 | 42 | 7.00 |
| do_exec.c | 1 | 61 | 5.00 |
| do_exit.c | 1 | 28 | 2.00 |
| do_fork.c | 1 | 137 | 11.00 |
| do_getinfo.c | 1 | 229 | 9.00 |
| do_getksig.c | 1 | 44 | 6.00 |
| do_irqctl.c | 1 | 175 | 29.00 |
| do_kill.c | 1 | 42 | 8.00 |
| do_memset.c | 1 | 29 | 3.00 |
| do_privctl.c | 1 | 372 | 49.00 |
| do_runctl.c | 1 | 77 | 15.00 |
| do_safecopy.c | 1 | 449 | 21.00 |
| do_safememset.c | 1 | 58 | 5.00 |
| do_schedctl.c | 1 | 47 | 3.00 |
| do_schedule.c | 1 | 31 | 2.00 |
| do_setalarm.c | 1 | 79 | 12.00 |
| do_setgrant.c | 1 | 31 | 2.00 |
| do_settime.c | 1 | 59 | 5.00 |
| do_sigreturn.c | 1 | 99 | 11.00 |
| do_sigsend.c | 1 | 167 | 15.00 |
| do_statectl.c | 1 | 54 | 8.00 |
| do_stime.c | 1 | 20 | 1.00 |
| do_times.c | 1 | 47 | 5.00 |
| do_trace.c | 1 | 209 | 16.00 |
| do_umap.c | 1 | 40 | 5.00 |
| do_umap_remote.c | 1 | 123 | 9.00 |
| do_update.c | 1 | 341 | 18.00 |
| do_vdevio.c | 1 | 166 | 35.00 |
| do_vmctl.c | 1 | 174 | 11.00 |
| do_vtimer.c | 1 | 104 | 15.00 |
| do_vumap.c | 1 | 132 | 18.00 |
