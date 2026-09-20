import pytest
from llg_to_fa.parser import parse_llg
from llg_to_fa.converter import llg_to_nfa

def test_llg_to_nfa_conversion():
    grammar_text = """
    S -> A b | B a
    A -> S a | a
    B -> b
    """
    grammar = parse_llg(grammar_text)
    nfa = llg_to_nfa(grammar)

    # 1. States include non-terminals + q_start
    assert "q_start" in nfa.states
    assert "S" in nfa.states
    assert "A" in nfa.states
    assert "B" in nfa.states

    # 2. Start state is q_start
    assert nfa.start_state == "q_start"

    # 3. Final state is S
    assert nfa.final_states == {"S"}

    # 4. Check transitions
    # S -> A b => δ(A, b) ∋ S
    assert "S" in nfa.transitions["A"]["b"]
    # S -> B a => δ(B, a) ∋ S
    assert "S" in nfa.transitions["B"]["a"]
    # A -> S a => δ(S, a) ∋ A
    assert "A" in nfa.transitions["S"]["a"]
    # A -> a => δ(q_start, a) ∋ A
    assert "A" in nfa.transitions["q_start"]["a"]
    # B -> b => δ(q_start, b) ∋ B
    assert "B" in nfa.transitions["q_start"]["b"]
