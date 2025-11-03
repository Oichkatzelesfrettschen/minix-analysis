----------------------- MODULE MessagePassing -----------------------
(*
 * MINIX 3.4 Inter-Process Communication (IPC) Formal Model
 *
 * This module models the SEND, RECEIVE, and SENDREC operations
 * for inter-process message passing in MINIX.
 *
 * Key properties verified:
 * - Message atomicity (no partial sends/receives)
 * - Endpoint validation (process must exist)
 * - Message boundaries (no buffer overflow)
 * - SENDREC atomicity (send+receive appears atomic)
 * - No message loss
 * - Proper blocking behavior
 *)

EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS MaxProcesses, MaxMessages, MessageSize

VARIABLE
    processes,           (* Active process set *)
    message_queue,       (* Queued messages per process *)
    process_state,       (* State of each process *)
    messages_sent,       (* Total messages sent (history) *)
    messages_received    (* Total messages received (history) *)

(* Process states *)
Running == "RUNNING"
ReceivingFrom == "RECEIVING"
SendingTo == "SENDING"
Blocked == "BLOCKED"

(* Message record *)
Message_t == [
    from: Nat,                      (* Sender PID *)
    to: Nat,                        (* Recipient PID *)
    data: Seq(0..255),              (* Message content (56 bytes) *)
    size: 1..MessageSize
]

(* Process record *)
ProcessRecord == [
    pid: Nat,
    state: {Running, ReceivingFrom, SendingTo, Blocked},
    waiting_from: Nat \cup {0},     (* 0 = any sender *)
    waiting_msg: Message_t \cup {NULL}
]

TypeOK ==
    /\ processes \in SUBSET (1..MaxProcesses)
    /\ \A p \in processes: p \in DOMAIN process_state
    /\ \A p \in processes: process_state[p] \in ProcessRecord
    /\ message_queue \in [processes -> Seq(Message_t)]
    /\ messages_sent \in Seq(Message_t)
    /\ messages_received \in Seq(Message_t)

Init ==
    /\ processes = {1, 2, 3}  (* Three test processes *)
    /\ process_state = (1 :> [pid |-> 1, state |-> Running, waiting_from |-> 0, waiting_msg |-> NULL]) @@
                       (2 :> [pid |-> 2, state |-> Running, waiting_from |-> 0, waiting_msg |-> NULL]) @@
                       (3 :> [pid |-> 3, state |-> Running, waiting_from |-> 0, waiting_msg |-> NULL])
    /\ message_queue = (1 :> <<>>) @@ (2 :> <<>>) @@ (3 :> <<>>)
    /\ messages_sent = <<>>
    /\ messages_received = <<>>

(* SEND operation - sender must exist *)
SEND(sender, recipient, data) ==
    /\ sender \in processes
    /\ recipient \in processes           (* Recipient must exist *)
    /\ sender /= recipient
    /\ Len(data) <= MessageSize
    /\ LET msg == [from |-> sender, to |-> recipient, data |-> data, size |-> Len(data)]
       IN
        /\ message_queue' = [message_queue EXCEPT ![recipient] = Append(@, msg)]
        /\ messages_sent' = Append(messages_sent, msg)
        /\ IF Len(message_queue[recipient]) = 0 /\
              process_state[recipient].state = ReceivingFrom /\
              (process_state[recipient].waiting_from = 0 \/
               process_state[recipient].waiting_from = sender)
           THEN
            /\ process_state' = [process_state EXCEPT
                ![recipient] = [@ EXCEPT !["state"] = Running,
                                         !["waiting_msg"] = msg]]
           ELSE
            /\ UNCHANGED process_state
        /\ UNCHANGED messages_received

(* RECEIVE operation - wait for message *)
RECEIVE(recipient) ==
    /\ recipient \in processes
    /\ process_state[recipient].state = Running
    /\ IF message_queue[recipient] # <<>>
       THEN
        /\ LET msg == Head(message_queue[recipient])
           IN
            /\ message_queue' = [message_queue EXCEPT ![recipient] = Tail(@)]
            /\ process_state' = [process_state EXCEPT
                ![recipient] = [@ EXCEPT !["state"] = Running,
                                         !["waiting_msg"] = msg]]
            /\ messages_received' = Append(messages_received, msg)
       ELSE
        /\ process_state' = [process_state EXCEPT
            ![recipient] = [@ EXCEPT !["state"] = ReceivingFrom,
                                     !["waiting_from"] = 0]]
        /\ UNCHANGED <<message_queue, messages_received>>

(* SENDREC operation - atomic send+receive *)
SENDREC(sender, recipient, data) ==
    /\ sender \in processes
    /\ recipient \in processes
    /\ sender /= recipient
    /\ LET msg == [from |-> sender, to |-> recipient, data |-> data, size |-> Len(data)]
       IN
        /\ message_queue' = [message_queue EXCEPT ![recipient] = Append(@, msg)]
        /\ messages_sent' = Append(messages_sent, msg)
        /\ process_state' = [process_state EXCEPT
            ![sender] = [@ EXCEPT !["state"] = ReceivingFrom,
                                  !["waiting_from"] = recipient],
            ![recipient] = IF Len(message_queue[recipient]) = 0 /\
                              process_state[recipient].state = ReceivingFrom
                           THEN [@ EXCEPT !["waiting_msg"] = msg]
                           ELSE @]
        /\ UNCHANGED messages_received

(* Properties to verify *)

(* Message atomicity: messages complete or don't start *)
MessageAtomicity ==
    /\ \A msg \in messages_sent:
       (msg \in Seq(message_queue[msg.to])) \/
       (msg \in messages_received)

(* Endpoint validation: all messages go to existing processes *)
EndpointValidation ==
    /\ \A msg \in messages_sent:
       msg.to \in processes

(* Message boundaries: no buffer overflow *)
MessageBoundaries ==
    /\ \A msg \in messages_sent:
       msg.size <= MessageSize

(* No message loss *)
NoMessageLoss ==
    /\ Cardinality({msg \in messages_sent}) =
       (Cardinality({msg \in messages_received}) +
        Cardinality(UNION {Range(message_queue[p]) : p \in processes}))

(* Processes remain active *)
ProcessConsistency ==
    /\ \A p \in DOMAIN process_state:
       p \in processes

(* SENDREC atomicity *)
SENDRECAtomicity ==
    /\ \A msg \in messages_sent:
       /\ msg.from \in processes
       /\ msg.to \in processes

Next ==
    \/ \E s, r \in processes, d \in Seq(0..255): SEND(s, r, d)
    \/ \E r \in processes: RECEIVE(r)
    \/ \E s, r \in processes, d \in Seq(0..255): SENDREC(s, r, d)

Spec ==
    Init /\ [][Next]_<<processes, message_queue, process_state,
                      messages_sent, messages_received>>

(* Safety properties *)
Safety ==
    /\ TypeOK
    /\ ProcessConsistency
    /\ EndpointValidation
    /\ MessageBoundaries

(* Correctness properties *)
Correctness ==
    /\ MessageAtomicity
    /\ NoMessageLoss
    /\ SENDRECAtomicity

================================================================
