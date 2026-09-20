from dataclasses import dataclass, field
from typing import Set, Dict, List, FrozenSet
from .converter import NFA

@dataclass
class DFA:
    states: List[str]                            # e.g., ["{q_start}", "{S, A}", ...]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, str]]       # src_state -> { symbol -> dst_state }
    start_state: str
    final_states: List[str]
    subset_table: List[dict] = field(default_factory=list) # Powerset construction rows

    def to_dict(self) -> dict:
        return {
            "states": self.states,
            "alphabet": self.alphabet,
            "transitions": self.transitions,
            "start_state": self.start_state,
            "final_states": self.final_states,
            "subset_table": self.subset_table
        }

def get_epsilon_closure(nfa: NFA, states: Set[str]) -> Set[str]:
    """Compute ε-closure for a set of NFA states."""
    closure = set(states)
    stack = list(states)

    while stack:
        curr = stack.pop()
        eps_targets = nfa.transitions.get(curr, {}).get("ε", set())
        for target in eps_targets:
            if target not in closure:
                closure.add(target)
                stack.append(target)

    return closure

def format_state_set(states: Set[str]) -> str:
    """Format set of NFA states into a clean string name like '{A, S}' or 'q_empty'."""
    if not states:
        return "∅"
    sorted_states = sorted(list(states))
    return "{" + ", ".join(sorted_states) + "}"

def nfa_to_dfa(nfa: NFA) -> DFA:
    """
    Converts NFA (with or without ε-transitions) into a deterministic finite automaton (DFA)
    using the Powerset / Subset Construction algorithm.
    """
    alphabet = sorted(list(nfa.alphabet))
    
    # 1. Start state of DFA is ε-closure of NFA start state
    initial_set = get_epsilon_closure(nfa, {nfa.start_state})
    initial_name = format_state_set(initial_set)

    unmarked_sets: List[FrozenSet[str]] = [frozenset(initial_set)]
    dsets_to_name: Dict[FrozenSet[str], str] = {frozenset(initial_set): initial_name}
    
    dfa_states: List[str] = [initial_name]
    dfa_transitions: Dict[str, Dict[str, str]] = {}
    dfa_final_states: Set[str] = set()
    subset_table: List[dict] = []

    if any(q in nfa.final_states for q in initial_set):
        dfa_final_states.add(initial_name)

    processed_sets: Set[FrozenSet[str]] = set()

    while unmarked_sets:
        curr_frozenset = unmarked_sets.pop(0)
        if curr_frozenset in processed_sets:
            continue
        processed_sets.add(curr_frozenset)

        curr_set = set(curr_frozenset)
        curr_name = dsets_to_name[curr_frozenset]
        dfa_transitions[curr_name] = {}

        table_row = {
            "dfa_state": curr_name,
            "nfa_subsets": sorted(list(curr_set)),
            "transitions": {},
            "is_final": curr_name in dfa_final_states
        }

        for symbol in alphabet:
            # Find next states for this symbol
            move_set: Set[str] = set()
            for nfa_state in curr_set:
                targets = nfa.transitions.get(nfa_state, {}).get(symbol, set())
                move_set.update(targets)

            # Take ε-closure of move set
            next_set = get_epsilon_closure(nfa, move_set)
            next_frozenset = frozenset(next_set)
            next_name = format_state_set(next_set)

            if next_frozenset not in dsets_to_name:
                dsets_to_name[next_frozenset] = next_name
                dfa_states.append(next_name)
                unmarked_sets.append(next_frozenset)

                if any(q in nfa.final_states for q in next_set):
                    dfa_final_states.add(next_name)

            dfa_transitions[curr_name][symbol] = next_name
            table_row["transitions"][symbol] = next_name

        subset_table.append(table_row)

    return DFA(
        states=dfa_states,
        alphabet=alphabet,
        transitions=dfa_transitions,
        start_state=initial_name,
        final_states=sorted(list(dfa_final_states)),
        subset_table=subset_table
    )
