import pytest
from llg_to_fa.parser import parse_llg
from llg_to_fa.converter import llg_to_nfa
from llg_to_fa.dfa import nfa_to_dfa
from llg_to_fa.simulator import simulate_llg_and_fa

def test_even_as_equivalence():
    # Language: even number of 'a's
    grammar_text = """
    S -> S b | A a | eps
    A -> A b | S a
    """
    grammar = parse_llg(grammar_text)
    nfa = llg_to_nfa(grammar)
    dfa = nfa_to_dfa(nfa)

    accepted_samples = ["", "bb", "aa", "aba", "aabb", "abab"]
    rejected_samples = ["a", "ab", "aaa", "ba", "aaba", "ababa"]

    for s in accepted_samples:
        res = simulate_llg_and_fa(grammar, nfa, dfa, s)
        assert res.is_accepted, f"Expected '{s}' to be accepted"

    for s in rejected_samples:
        res = simulate_llg_and_fa(grammar, nfa, dfa, s)
        assert not res.is_accepted, f"Expected '{s}' to be rejected"

def test_ends_with_ab_equivalence():
    # Language: ends with 'ab'
    grammar_text = """
    S -> A b
    A -> B a
    B -> B a | B b | eps
    """
    grammar = parse_llg(grammar_text)
    nfa = llg_to_nfa(grammar)
    dfa = nfa_to_dfa(nfa)

    accepted_samples = ["ab", "aab", "bbab", "babab"]
    rejected_samples = ["", "a", "b", "ba", "aba", "bb"]

    for s in accepted_samples:
        res = simulate_llg_and_fa(grammar, nfa, dfa, s)
        assert res.is_accepted, f"Expected '{s}' to be accepted"

    for s in rejected_samples:
        res = simulate_llg_and_fa(grammar, nfa, dfa, s)
        assert not res.is_accepted, f"Expected '{s}' to be rejected"

def test_epsilon_simulation_keywords():
    grammar_text = """
    S -> S b | A a | eps
    A -> A b | S a
    """
    grammar = parse_llg(grammar_text)
    nfa = llg_to_nfa(grammar)
    dfa = nfa_to_dfa(nfa)

    for eps_symbol in ["", "eps", "epsilon", "lambda", "λ", "ε"]:
        res = simulate_llg_and_fa(grammar, nfa, dfa, eps_symbol)
        assert res.is_accepted, f"Expected epsilon representation '{eps_symbol}' to be accepted"

