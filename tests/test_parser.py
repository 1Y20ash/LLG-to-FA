import pytest
from llg_to_fa.parser import parse_llg
from llg_to_fa.grammar import LeftLinearGrammar

def test_parse_valid_llg():
    grammar_text = """
    # Sample LLG
    S -> A b | B a | eps
    A -> S a | a
    B -> b
    """
    grammar = parse_llg(grammar_text)

    assert grammar.start_symbol == "S"
    assert grammar.non_terminals == {"S", "A", "B"}
    assert grammar.terminals == {"a", "b"}
    
    is_valid, errors = grammar.validate_left_linear()
    assert is_valid
    assert len(errors) == 0

def test_parse_invalid_right_linear():
    # Right-linear rule A -> a S has non-terminal at end
    grammar_text = """
    S -> a S | b
    """
    grammar = parse_llg(grammar_text)
    is_valid, errors = grammar.validate_left_linear()
    assert not is_valid
    assert any("MUST be the FIRST symbol" in err for err in errors)

def test_parse_multiple_non_terminals():
    # Context-free rule A -> B C
    grammar_text = """
    S -> A B
    A -> a
    B -> b
    """
    grammar = parse_llg(grammar_text)
    is_valid, errors = grammar.validate_left_linear()
    assert not is_valid
    assert any("multiple non-terminals" in err for err in errors)
