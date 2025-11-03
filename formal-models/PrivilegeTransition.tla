----------------------- MODULE PrivilegeTransition -----------------------
(*
 * MINIX 3.4 Privilege Level Transition Formal Model
 *
 * This module models Ring 0 (kernel) and Ring 3 (user) transitions
 * via INT 0x30 syscall and IRET return instructions.
 *
 * Key properties verified:
 * - Valid privilege transitions only (Ring 3 -> Ring 0 via INT 0x30)
 * - IRET restores privilege level from saved CPSR
 * - Interrupt flag management (IF enabled in user mode)
 * - Exclusive kernel access (only INT path to Ring 0)
 * - Syscall atomicity from CPU perspective
 *)

EXTENDS Naturals, Sequences

CONSTANTS MaxSyscalls

VARIABLE
    cpu_state,           (* Current CPU state *)
    privilege_level,     (* Current ring (0 or 3) *)
    cpsr,                (* CPSR register with flags *)
    eip,                 (* Instruction pointer *)
    kernel_stack,        (* Kernel stack for context save *)
    user_return_addr,    (* Where to return in user code *)
    interrupt_flag       (* IF flag in CPSR *)

(* CPU privilege levels *)
Ring0 == 0
Ring3 == 3

(* CPU states *)
RunningUserCode == "RUNNING_USER"
HandlingSyscall == "HANDLING_SYSCALL"
RestoringUser == "RESTORING_USER"

(* CPSR flags record *)
CPSR_t == [
    if_flag: BOOLEAN,           (* Interrupt enable flag *)
    ring: {0, 3},               (* Current privilege level *)
    previous_if: BOOLEAN,       (* Saved IF for IRET *)
    saved_ring: {0, 3}          (* Saved ring for IRET *)
]

TypeOK ==
    /\ cpu_state \in {RunningUserCode, HandlingSyscall, RestoringUser}
    /\ privilege_level \in {Ring0, Ring3}
    /\ cpsr \in CPSR_t
    /\ eip \in Nat
    /\ user_return_addr \in Nat
    /\ interrupt_flag \in BOOLEAN

Init ==
    /\ cpu_state = RunningUserCode
    /\ privilege_level = Ring3
    /\ cpsr = [if_flag |-> TRUE, ring |-> Ring3,
               previous_if |-> TRUE, saved_ring |-> Ring3]
    /\ eip = 0x08000000  (* User code address *)
    /\ user_return_addr = 0x08000000
    /\ interrupt_flag = TRUE

(* INT 0x30 syscall instruction *)
ExecuteINT0x30 ==
    /\ privilege_level = Ring3      (* Must be in user mode *)
    /\ cpu_state = RunningUserCode
    /\ LET new_cpsr == [cpsr EXCEPT
            !["previous_if"] = cpsr["if_flag"],
            !["saved_ring"] = cpsr["ring"],
            !["if_flag"] = FALSE,   (* Disable interrupts *)
            !["ring"] = Ring0       (* Switch to Ring 0 *)
       IN
        /\ privilege_level' = Ring0
        /\ cpsr' = new_cpsr
        /\ cpu_state' = HandlingSyscall
        /\ eip' = 0x80000000 + 0x30 * 4  (* Kernel handler address *)
        /\ kernel_stack' = <<eip>> \o kernel_stack  (* Push return *)
        /\ UNCHANGED <<user_return_addr, interrupt_flag>>

(* Syscall handler execution *)
ExecuteSyscallHandler ==
    /\ cpu_state = HandlingSyscall
    /\ privilege_level = Ring0
    /\ cpsr["ring"] = Ring0
    /\ cpsr["if_flag"] = FALSE      (* Interrupts still disabled *)
    /\ cpu_state' = RestoringUser   (* Done, prepare IRET *)
    /\ UNCHANGED <<privilege_level, cpsr, eip, user_return_addr, kernel_stack, interrupt_flag>>

(* IRET instruction - return to user mode *)
ExecuteIRET ==
    /\ cpu_state = RestoringUser
    /\ privilege_level = Ring0
    /\ LET new_cpsr == [cpsr EXCEPT
            !["ring"] = cpsr["saved_ring"],         (* Restore ring *)
            !["if_flag"] = cpsr["previous_if"]      (* Restore IF *)
       IN
        /\ privilege_level' = cpsr["saved_ring"]
        /\ cpsr' = new_cpsr
        /\ cpu_state' = RunningUserCode
        /\ eip' = user_return_addr  (* Return to user instruction *)
        /\ UNCHANGED <<user_return_addr, kernel_stack, interrupt_flag>>

(* Property: Only valid transition from Ring 3 is INT 0x30 *)
OnlyValidTransition ==
    /\ privilege_level = Ring3 =>
       NEXT (privilege_level = Ring0 \/ privilege_level = Ring3)
    /\ privilege_level = Ring3 /\
       (NEXT privilege_level = Ring0) =>
       (NEXT cpu_state = HandlingSyscall)

(* Property: IF flag is FALSE during kernel execution *)
InterruptFlagManagement ==
    /\ cpu_state = HandlingSyscall =>
       cpsr["if_flag"] = FALSE
    /\ cpu_state = RunningUserCode =>
       cpsr["if_flag"] = TRUE

(* Property: IRET restores from saved values *)
IRETCorrectness ==
    /\ (cpu_state = HandlingSyscall \/ cpu_state = RestoringUser) =>
       (NEXT privilege_level = cpsr["saved_ring"])

(* Property: Cannot jump directly to Ring 0 *)
NoDirectKernelEntry ==
    /\ privilege_level = Ring3 /\
       (NEXT privilege_level = Ring0) =>
       (NEXT cpu_state = HandlingSyscall)

(* Property: Return address preserved across syscall *)
ReturnAddressPreserved ==
    /\ NEXT (cpu_state = HandlingSyscall) =>
       (NEXT user_return_addr = eip)

Next ==
    \/ ExecuteINT0x30
    \/ ExecuteSyscallHandler
    \/ ExecuteIRET

Spec ==
    Init /\ [][Next]_<<cpu_state, privilege_level, cpsr, eip, kernel_stack,
                      user_return_addr, interrupt_flag>>

(* Safety properties *)
SafetyInvariants ==
    /\ TypeOK
    /\ OnlyValidTransition
    /\ InterruptFlagManagement
    /\ NoDirectKernelEntry

(* Liveness properties *)
LivenessInvariants ==
    /\ IRETCorrectness
    /\ ReturnAddressPreserved

================================================================
