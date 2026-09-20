from dataclasses import dataclass
from typing import List, Set, Dict, Optional
from .grammar import LeftLinearGrammar, EPSILON_SYMBOLS
from .converter import NFA
from .dfa import DFA, get_epsilon_closure

@dataclass
class SimulationStep:
    step_index: int
    symbol_consumed: Optional[str]
    consumed_prefix: str
    remaining_suffix: str
    active_nfa_states: List[str]
    active_dfa_state: Optional[str]
    grammar_derivation_step: str

@dataclass
class SimulationResult:
    input_string: str
    is_accepted: bool
    final_states: List[str]
    steps: List[SimulationStep]
    derivation_path: List[str]
    explanation: str

    def to_dict(self) -> dict:
        return {
            "input_string": self.input_string,
            "is_accepted": self.is_accepted,
            "final_states": self.final_states,
            "explanation": self.explanation,
            "derivation_path": self.derivation_path,
            "steps": [
                {
                    "step_index": s.step_index,
                    "symbol_consumed": s.symbol_consumed,
                    "consumed_prefix": s.consumed_prefix,
                    "remaining_suffix": s.remaining_suffix,
                    "active_nfa_states": s.active_nfa_states,
                    "active_dfa_state": s.active_dfa_state,
                    "grammar_derivation_step": s.grammar_derivation_step
                }
                for s in self.steps
            ]
        }

def find_llg_derivation(grammar: LeftLinearGrammar, target_string: str) -> Optional[List[str]]:
    """
    Finds a left-derivation sequence for target_string in Left-Linear Grammar G, if one exists.
    Returns list of sentential forms: e.g. ["S", "A b", "b a b"]
    """
    if target_string in EPSILON_SYMBOLS:
        target_string = ""

    # BFS search for derivation matching target_string
    queue = [(grammar.start_symbol, "")] # (current_non_terminal, produced_terminal_suffix)
    visited = set()
    parent_map = {} # (nt, suffix) -> (prev_nt, prev_suffix, rule_used)

    found_start_state = None

    while queue:
        curr_nt, curr_suffix = queue.pop(0)
        state_key = (curr_nt, curr_suffix)

        if state_key in visited:
            continue
        visited.add(state_key)

        if curr_suffix == target_string and curr_nt is None:
            found_start_state = state_key
            break

        # If current suffix is already longer than target string or doesn't match end of target_string
        if curr_suffix and not target_string.endswith(curr_suffix):
            continue

        for rule in grammar.rules:
            if rule.lhs == curr_nt:
                new_nt = rule.rhs_non_terminal
                new_suffix = rule.rhs_terminal + curr_suffix
                new_key = (new_nt, new_suffix)

                if new_key not in parent_map:
                    parent_map[new_key] = (curr_nt, curr_suffix, str(rule))
                    queue.append(new_key)

    if not found_start_state:
        if (None, target_string) in parent_map:
            found_start_state = (None, target_string)
        else:
            return None

    # Reconstruct derivation steps from Start Symbol down to final string
    curr = found_start_state
    steps_rev = []
    while curr in parent_map:
        prev_nt, prev_suffix, rule_str = parent_map[curr]
        sentential_form = (f"{prev_nt} " if prev_nt else "") + prev_suffix
        steps_rev.append(sentential_form.strip())
        curr = (prev_nt, prev_suffix)

    steps_rev.append(grammar.start_symbol)
    derivation = list(reversed(steps_rev))
    derivation.append(target_string if target_string != "" else "ε")
    return derivation

def simulate_llg_and_fa(grammar: LeftLinearGrammar, nfa: NFA, dfa: Optional[DFA], input_string: str) -> SimulationResult:
    """
    Simulates string execution on both NFA/DFA and tracks corresponding LLG derivation.
    Supports ε / eps / lambda representations for empty string.
    """
    if input_string.strip() in EPSILON_SYMBOLS:
        input_string = ""

    curr_nfa_states = get_epsilon_closure(nfa, {nfa.start_state})
    curr_dfa_state = dfa.start_state if dfa else None

    derivation_path = find_llg_derivation(grammar, input_string)

    steps: List[SimulationStep] = []

    # Step 0
    steps.append(SimulationStep(
        step_index=0,
        symbol_consumed=None,
        consumed_prefix="",
        remaining_suffix=input_string,
        active_nfa_states=sorted(list(curr_nfa_states)),
        active_dfa_state=curr_dfa_state,
        grammar_derivation_step=derivation_path[0] if derivation_path else grammar.start_symbol
    ))

    for i, symbol in enumerate(input_string):
        consumed = input_string[:i+1]
        remaining = input_string[i+1:]

        # NFA transition
        next_nfa_raw = set()
        for q in curr_nfa_states:
            targets = nfa.transitions.get(q, {}).get(symbol, set())
            next_nfa_raw.update(targets)

        curr_nfa_states = get_epsilon_closure(nfa, next_nfa_raw)

        # DFA transition
        if dfa and curr_dfa_state:
            curr_dfa_state = dfa.transitions.get(curr_dfa_state, {}).get(symbol, "∅")

        # Map to derivation step if available
        deriv_step = ""
        if derivation_path and i+1 < len(derivation_path):
            deriv_step = derivation_path[i+1]

        steps.append(SimulationStep(
            step_index=i+1,
            symbol_consumed=symbol,
            consumed_prefix=consumed,
            remaining_suffix=remaining,
            active_nfa_states=sorted(list(curr_nfa_states)),
            active_dfa_state=curr_dfa_state,
            grammar_derivation_step=deriv_step
        ))

    is_accepted = any(q in nfa.final_states for q in curr_nfa_states)
    accepted_states = sorted(list(curr_nfa_states & nfa.final_states))

    display_str = "ε (empty string)" if input_string == "" else f"'{input_string}'"

    if is_accepted:
        explanation = (
            f"Input string {display_str} was ACCEPTED by the Automaton. "
            f"Active state(s) at end of input include accepting state(s) {accepted_states}, "
            f"which match the Grammar Start Symbol '{grammar.start_symbol}'."
        )
    else:
        explanation = (
            f"Input string {display_str} was REJECTED by the Automaton. "
            f"Active state(s) at end of input {sorted(list(curr_nfa_states))} do not intersect "
            f"with accepting states {sorted(list(nfa.final_states))}."
        )

    return SimulationResult(
        input_string=input_string if input_string != "" else "ε",
        is_accepted=is_accepted,
        final_states=sorted(list(curr_nfa_states)),
        steps=steps,
        derivation_path=derivation_path or [],
        explanation=explanation
    )
