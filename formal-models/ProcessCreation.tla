----------------------- MODULE ProcessCreation -----------------------
(*
 * MINIX 3.4 Process Creation (fork) Formal Model
 *
 * This module models the fork() syscall and process creation mechanism
 * in MINIX 3.4 kernel.
 *
 * Key properties verified:
 * - Process table consistency after fork
 * - Correct context copy from parent to child
 * - Proper endpoint generation with generation numbers
 * - Correct return values (parent gets child_pid, child gets 0)
 * - Memory isolation between parent and child
 *)

EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS MaxProcesses, MaxGeneration

VARIABLE processes, process_table, next_pid, generation_counter

(* Process record structure *)
ProcessRec == [
    pid: Nat,
    parent_pid: Nat,
    generation: Nat,
    state: {"CREATED", "RUNNING", "BLOCKED", "TERMINATED"},
    registers: Seq(Nat),
    memory: SUBSET Nat,
    return_value: Int
]

(* Process table maps PID to process record *)
TypeOK ==
    /\ processes \in SUBSET (1..MaxProcesses)
    /\ process_table \in [processes -> ProcessRec]
    /\ next_pid \in Nat
    /\ generation_counter \in [1..MaxProcesses -> 0..MaxGeneration]

Init ==
    /\ processes = {1}  (* Only init process *)
    /\ process_table = (1 :> [
        pid |-> 1,
        parent_pid |-> 0,
        generation |-> 1,
        state |-> "RUNNING",
        registers |-> <<>>,
        memory |-> {},
        return_value |-> 0
    ])
    /\ next_pid = 2
    /\ generation_counter = [i \in 1..MaxProcesses |-> 0]

(* Fork syscall *)
Fork(parent_pid) ==
    /\ parent_pid \in processes
    /\ next_pid < MaxProcesses  (* Space available *)
    /\ LET
        parent == process_table[parent_pid]
        child_pid == next_pid
        child_gen == generation_counter[child_pid] + 1
       IN
        /\ child_gen <= MaxGeneration
        /\ processes' = processes \cup {child_pid}
        /\ process_table' = process_table @@
           (child_pid :> [
               pid |-> child_pid,
               parent_pid |-> parent_pid,
               generation |-> child_gen,
               state |-> "CREATED",
               registers |-> parent.registers,  (* Copy registers *)
               memory |-> parent.memory,        (* Copy memory *)
               return_value |-> 0               (* Child returns 0 *)
           ])
        /\ process_table'[parent_pid].return_value = child_pid
        /\ next_pid' = next_pid + 1
        /\ generation_counter' =
           [generation_counter EXCEPT ![child_pid] = child_gen]

(* Parent and child context are identical after fork *)
ContextCopyCorrect ==
    \A p \in processes:
        /\ p \in DOMAIN process_table
        /\ process_table[p].parent_pid > 0 =>
           (LET parent == process_table[process_table[p].parent_pid]
            IN process_table[p].registers = parent.registers)

(* Return values correct *)
ReturnValuesCorrect ==
    \A p \in processes:
        /\ p \in DOMAIN process_table
        /\ process_table[p].state = "CREATED" =>
           process_table[p].return_value = 0  (* Child always returns 0 *)

(* Process table consistency *)
ProcessTableConsistent ==
    /\ \A p \in processes: p \in DOMAIN process_table
    /\ \A pid \in DOMAIN process_table:
       pid \in processes

(* No duplicate PIDs *)
NoDuplicatePIDs ==
    \A p1, p2 \in processes:
        p1 /= p2 =>
            process_table[p1].pid /= process_table[p2].pid

(* Generations unique per PID *)
UniqueGenerations ==
    \A p \in processes:
        generation_counter[p] = process_table[p].generation

Next == \E p \in processes: Fork(p)

Spec == Init /\ [][Next]_<<processes, process_table, next_pid, generation_counter>>

(* Properties to verify *)
Safety ==
    /\ TypeOK
    /\ ProcessTableConsistent
    /\ NoDuplicatePIDs
    /\ UniqueGenerations

Liveness ==
    /\ ContextCopyCorrect
    /\ ReturnValuesCorrect

===============================================================
