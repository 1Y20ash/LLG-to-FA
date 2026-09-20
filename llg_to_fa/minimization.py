from dataclasses import dataclass, field
from typing import Set, Dict, List, FrozenSet
from .dfa import DFA

@dataclass
class MinimizedDFA:
    states: List[str]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, str]]
    start_state: str
    final_states: List[str]
    partition_history: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "states": self.states,
            "alphabet": self.alphabet,
            "transitions": self.transitions,
            "start_state": self.start_state,
            "final_states": self.final_states,
            "partition_history": self.partition_history
        }

def format_partition_name(group: Set[str]) -> str:
    """Format partition group into clean state name."""
    if len(group) == 1:
        return list(group)[0]
    return "{" + ", ".join(sorted(list(group))) + "}"

def minimize_dfa(dfa: DFA) -> MinimizedDFA:
    """
    Minimizes a DFA using Hopcroft's partition refinement algorithm.
    """
    all_states = set(dfa.states)
    final_set = set(dfa.final_states)
    non_final_set = all_states - final_set

    # Initial partition P = { F, Q \ F }
    partitions: List[Set[str]] = []
    if final_set:
        partitions.append(final_set)
    if non_final_set:
        partitions.append(non_final_set)

    # Worklist W
    worklist: List[Set[str]] = [p.copy() for p in partitions]

    history: List[dict] = [{
        "step": 0,
        "description": "Initial partition into Accepting (F) and Non-Accepting (Q \\ F) states",
        "partitions": [[sorted(list(p)) for p in partitions]]
    }]

    step_counter = 1

    while worklist:
        A = worklist.pop(0)

        for c in dfa.alphabet:
            # X = set of states that transition into A on symbol c
            X: Set[str] = set()
            for state in all_states:
                target = dfa.transitions.get(state, {}).get(c)
                if target and target in A:
                    X.add(state)

            # Check partitions Y in P that can be split by X
            new_partitions: List[Set[str]] = []
            for Y in partitions:
                inter = Y & X
                diff = Y - X

                if inter and diff:
                    new_partitions.append(inter)
                    new_partitions.append(diff)

                    if Y in worklist:
                        worklist.remove(Y)
                        worklist.append(inter)
                        worklist.append(diff)
                    else:
                        if len(inter) <= len(diff):
                            worklist.append(inter)
                        else:
                            worklist.append(diff)

                    history.append({
                        "step": step_counter,
                        "description": f"Split partition group on symbol '{c}'",
                        "splitter": sorted(list(A)),
                        "symbol": c,
                        "split_group": sorted(list(Y)),
                        "result_groups": [sorted(list(inter)), sorted(list(diff))]
                    })
                    step_counter += 1
                else:
                    new_partitions.append(Y)

            partitions = new_partitions

    # Reconstruct Minimized DFA
    state_mapping: Dict[str, str] = {}
    min_states: List[str] = []
    min_final_states: Set[str] = set()

    for p in partitions:
        p_name = format_partition_name(p)
        min_states.append(p_name)
        for state in p:
            state_mapping[state] = p_name
        if any(state in dfa.final_states for state in p):
            min_final_states.add(p_name)

    min_start_state = state_mapping[dfa.start_state]
    min_transitions: Dict[str, Dict[str, str]] = {}

    for p_name in min_states:
        min_transitions[p_name] = {}

    for src_state, symbol_map in dfa.transitions.items():
        src_group = state_mapping[src_state]
        for symbol, dst_state in symbol_map.items():
            dst_group = state_mapping[dst_state]
            min_transitions[src_group][symbol] = dst_group

    return MinimizedDFA(
        states=min_states,
        alphabet=dfa.alphabet,
        transitions=min_transitions,
        start_state=min_start_state,
        final_states=sorted(list(min_final_states)),
        partition_history=history
    )
