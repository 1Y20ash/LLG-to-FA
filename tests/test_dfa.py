import pytest
from llg_to_fa.parser import parse_llg
from llg_to_fa.converter import llg_to_nfa
from llg_to_fa.dfa import nfa_to_dfa
from llg_to_fa.minimization import minimize_dfa

def test_dfa_conversion_and_minimization():
    grammar_text = """
    S -> S b | A a | eps
    A -> A b | S a
    """
    grammar = parse_llg(grammar_text)
    nfa = llg_to_nfa(grammar)
    dfa = nfa_to_dfa(nfa)
    min_dfa = minimize_dfa(dfa)

    assert dfa.start_state is not None
    assert len(dfa.states) >= 2
    assert len(min_dfa.states) <= len(dfa.states)
