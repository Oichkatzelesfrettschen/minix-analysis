# Minix Kernel Boot Sequence Deep Dive

**Entry Point:** `proc_init()`

**Analysis Date:** Thu Oct 30 06:49:51 PM PDT 2025

---

##  `proc_init()`

**Location:** `minix/kernel/proc.c`

**Function Calls:** 6 unique functions

```
arch_proc_reset
_ENDPOINT
get_cpu_var_ptr
proc_addr
proc_nr
set_idle_name
```

**Source Code:**
```c
119: void proc_init(void)
120: {
121: 	struct proc * rp;
122: 	struct priv *sp;
123: 	int i;
124: 
125: 	/* Clear the process table. Announce each slot as empty and set up
126: 	 * mappings for proc_addr() and proc_nr() macros. Do the same for the
127: 	 * table with privilege structures for the system processes. 
128: 	 */
129: 	for (rp = BEG_PROC_ADDR, i = -NR_TASKS; rp < END_PROC_ADDR; ++rp, ++i) {
130: 		rp->p_rts_flags = RTS_SLOT_FREE;/* initialize free slot */
131: 		rp->p_magic = PMAGIC;
132: 		rp->p_nr = i;			/* proc number from ptr */
133: 		rp->p_endpoint = _ENDPOINT(0, rp->p_nr); /* generation no. 0 */
134: 		rp->p_scheduler = NULL;		/* no user space scheduler */
135: 		rp->p_priority = 0;		/* no priority */
136: 		rp->p_quantum_size_ms = 0;	/* no quantum size */
137: 
138: 		/* arch-specific initialization */
139: 		arch_proc_reset(rp);
140: 	}
141: 	for (sp = BEG_PRIV_ADDR, i = 0; sp < END_PRIV_ADDR; ++sp, ++i) {
142: 		sp->s_proc_nr = NONE;		/* initialize as free */
143: 		sp->s_id = (sys_id_t) i;	/* priv structure index */
144: 		ppriv_addr[i] = sp;		/* priv ptr from number */
145: 		sp->s_sig_mgr = NONE;		/* clear signal managers */
146: 		sp->s_bak_sig_mgr = NONE;
147: 	}
148: 
149: 	idle_priv.s_flags = IDL_F;
150: 	/* initialize IDLE structures for every CPU */
151: 	for (i = 0; i < CONFIG_MAX_CPUS; i++) {
152: 		struct proc * ip = get_cpu_var_ptr(i, idle_proc);
153: 		ip->p_endpoint = IDLE;
154: 		ip->p_priv = &idle_priv;
155: 		/* must not let idle ever get scheduled */
156: 		ip->p_rts_flags |= RTS_PROC_STOP;
157: 		set_idle_name(ip->p_name, i);
158: 	}
159: }
```

---

## # `arch_proc_reset()`

**Location:** `minix/kernel/arch/earm/arch_system.c`

**Function Calls:** 3 unique functions

```
assert
iskerneln
memset
```

**Source Code:**
```c
42: void arch_proc_reset(struct proc *pr)
43: {
44: 	assert(pr->p_nr < NR_PROCS);
45: 
46: 	/* Clear process state. */
47: 	memset(&pr->p_reg, 0, sizeof(pr->p_reg));
48: 	if(iskerneln(pr->p_nr)) {
49: 		pr->p_reg.psr = INIT_TASK_PSR;
50: 	} else {
51: 		pr->p_reg.psr = INIT_PSR;
52: 	}
53: }
```

---

### `assert()` - EXTERNAL

Function not found in source tree (likely stdlib, macro, or inline).

### `iskerneln()` - EXTERNAL

Function not found in source tree (likely stdlib, macro, or inline).

### `memset()` - EXTERNAL

Function not found in source tree (likely stdlib, macro, or inline).

### `_ENDPOINT()` - EXTERNAL

Function not found in source tree (likely stdlib, macro, or inline).

### `get_cpu_var_ptr()` - EXTERNAL

Function not found in source tree (likely stdlib, macro, or inline).

### `proc_addr()` - EXTERNAL

Function not found in source tree (likely stdlib, macro, or inline).

### `proc_nr()` - EXTERNAL

Function not found in source tree (likely stdlib, macro, or inline).

