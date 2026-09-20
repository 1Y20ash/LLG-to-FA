from dataclasses import dataclass, field
from typing import Set, Dict, List, Tuple, Optional
from .grammar import LeftLinearGrammar

@dataclass
class NFA:
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[str, Dict[str, Set[str]]]  # state -> { symbol -> set of target states }
    start_state: str
    final_states: Set[str]
    conversion_steps: List[dict] = field(default_factory=list)  # Step-by-step mathematical derivation

    def add_transition(self, src: str, symbol: str, dst: str):
        if src not in self.transitions:
            self.transitions[src] = {}
        if symbol not in self.transitions[src]:
            self.transitions[src][symbol] = set()
        self.transitions[src][symbol].add(dst)

    def to_dict(self) -> dict:
        serialized_trans = {}
        for src, sym_map in self.transitions.items():
            serialized_trans[src] = {sym: sorted(list(targets)) for sym, targets in sym_map.items()}

        return {
            "states": sorted(list(self.states)),
            "alphabet": sorted(list(self.alphabet)),
            "transitions": serialized_trans,
            "start_state": self.start_state,
            "final_states": sorted(list(self.final_states)),
            "conversion_steps": self.conversion_steps
        }

def llg_to_nfa(grammar: LeftLinearGrammar) -> NFA:
    """
    Mathematically restructures a Left-Linear Grammar G = (V, Σ, R, S) into an equivalent NFA M = (Q, Σ, δ, q_start, F).
    
    Transformation Rules:
    1. Q = V ∪ { q_start }
    2. Start state = q_start
    3. Final states F = { S } (plus q_start if S -> ε)
    4. For rule A -> B w:
       - If w = a (single terminal): δ(B, a) ∋ A
       - If w = a1 a2 ... ak (string of terminals): B --a1--> q1 --a2--> ... --ak--> A
       - If w = ε: δ(B, ε) ∋ A
    5. For rule A -> w:
       - If w = a: δ(q_start, a) ∋ A
       - If w = a1 a2 ... ak: q_start --a1--> q1 --a2--> ... --ak--> A
       - If w = ε: δ(q_start, ε) ∋ A
    """
    is_valid, errors = grammar.validate_left_linear()
    if not is_valid:
        raise ValueError(f"Grammar is not left-linear: {'; '.join(errors)}")

    start_state = "q_start"
    states = set(grammar.non_terminals)
    states.add(start_state)
    
    alphabet = set(grammar.terminals)
    final_states = {grammar.start_symbol}
    transitions: Dict[str, Dict[str, Set[str]]] = {}

    nfa = NFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state=start_state,
        final_states=final_states,
        conversion_steps=[]
    )

    intermediate_counter = 1

    for rule in grammar.rules:
        lhs = rule.lhs
        rhs_nt = rule.rhs_non_terminal
        rhs_t = rule.rhs_terminal

        step_desc = {
            "rule": str(rule),
            "type": "non_terminal_prefix" if rhs_nt else "terminal_only",
            "added_transitions": []
        }

        if rhs_nt:
            # Rule of form A -> B w
            src = rhs_nt
            dst = lhs

            if not rhs_t:
                # A -> B (unit rule / ε)
                nfa.add_transition(src, "ε", dst)
                step_desc["added_transitions"].append(f"δ({src}, ε) ∋ {dst}")
            elif len(rhs_t) == 1:
                # A -> B a
                symbol = rhs_t[0]
                nfa.add_transition(src, symbol, dst)
                step_desc["added_transitions"].append(f"δ({src}, {symbol}) ∋ {dst}")
            else:
                # A -> B a1 a2 ... ak
                curr_src = src
                for i, symbol in enumerate(rhs_t):
                    if i == len(rhs_t) - 1:
                        curr_dst = dst
                    else:
                        curr_dst = f"q_mid_{intermediate_counter}"
                        intermediate_counter += 1
                        nfa.states.add(curr_dst)
                    
                    nfa.add_transition(curr_src, symbol, curr_dst)
                    step_desc["added_transitions"].append(f"δ({curr_src}, {symbol}) ∋ {curr_dst}")
                    curr_src = curr_dst
        else:
            # Rule of form A -> w
            src = start_state
            dst = lhs

            if not rhs_t:
                # A -> ε
                nfa.add_transition(src, "ε", dst)
                step_desc["added_transitions"].append(f"δ({src}, ε) ∋ {dst}")
                if lhs == grammar.start_symbol:
                    nfa.final_states.add(start_state)
                    step_desc["added_transitions"].append(f"Since S -> ε, added {start_state} to final states F")
            elif len(rhs_t) == 1:
                # A -> a
                symbol = rhs_t[0]
                nfa.add_transition(src, symbol, dst)
                step_desc["added_transitions"].append(f"δ({src}, {symbol}) ∋ {dst}")
            else:
                # A -> a1 a2 ... ak
                curr_src = src
                for i, symbol in enumerate(rhs_t):
                    if i == len(rhs_t) - 1:
                        curr_dst = dst
                    else:
                        curr_dst = f"q_mid_{intermediate_counter}"
                        intermediate_counter += 1
                        nfa.states.add(curr_dst)
                    
                    nfa.add_transition(curr_src, symbol, curr_dst)
                    step_desc["added_transitions"].append(f"δ({curr_src}, {symbol}) ∋ {curr_dst}")
                    curr_src = curr_dst

        nfa.conversion_steps.append(step_desc)

    return nfa
