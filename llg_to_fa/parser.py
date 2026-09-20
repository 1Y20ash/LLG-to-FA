import re
from typing import Set, List, Tuple
from .grammar import LeftLinearGrammar, ProductionRule, EPSILON_SYMBOLS

def tokenize_rhs(rhs_str: str) -> List[str]:
    """Split RHS string into tokens, handling angle bracket non-terminals like <Start>."""
    rhs_str = rhs_str.strip()
    if not rhs_str or rhs_str in EPSILON_SYMBOLS:
        return []
    
    # Check for angle bracket tokens or space-separated tokens
    tokens = []
    pattern = r'<[^>]+>|\S+'
    for match in re.finditer(pattern, rhs_str):
        token = match.group(0)
        tokens.append(token)
    return tokens

def parse_llg(grammar_text: str) -> LeftLinearGrammar:
    """
    Parses a string representation of a Left-Linear Grammar.
    Supports formats like:
      S -> A b | B a | eps
      A -> S a | a
      B -> b
    """
    # Split by newlines and semicolons
    lines = [line.strip() for line in re.split(r'[\n;]', grammar_text)]
    
    raw_rules: List[Tuple[str, str]] = []
    non_terminals: Set[str] = set()
    start_symbol = None

    # Pass 1: Identify all non-terminals from LHS of rules
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        
        # Split by arrow (->, ::=, =>, →)
        parts = re.split(r'->|::=|=>|→', line, maxsplit=1)
        if len(parts) != 2:
            continue
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()

        if not start_symbol:
            start_symbol = lhs
        
        non_terminals.add(lhs)

        # Pipe separated alternatives
        alternatives = [alt.strip() for alt in rhs.split('|')]
        for alt in alternatives:
            raw_rules.append((lhs, alt))

    if not start_symbol:
        raise ValueError("No valid grammar production rules found.")

    # Pass 2: Inspect RHS of rules, collect terminals and build ProductionRule objects
    terminals: Set[str] = set()
    parsed_rules: List[ProductionRule] = []

    for lhs, raw_rhs in raw_rules:
        tokens = tokenize_rhs(raw_rhs)

        if not tokens:
            # Epsilon rule: A -> ε
            parsed_rules.append(ProductionRule(
                lhs=lhs,
                rhs_non_terminal=None,
                rhs_terminal="",
                raw_rhs=raw_rhs
            ))
            continue

        # Check if first token is a non-terminal
        first_token = tokens[0]
        if first_token in non_terminals and len(tokens) > 1:
            rhs_nt = first_token
            term_tokens = tokens[1:]
            rhs_t = "".join(term_tokens)
            for t in term_tokens:
                if t not in EPSILON_SYMBOLS and t not in non_terminals:
                    terminals.add(t)
            parsed_rules.append(ProductionRule(
                lhs=lhs,
                rhs_non_terminal=rhs_nt,
                rhs_terminal=rhs_t,
                raw_rhs=raw_rhs
            ))
        elif first_token in non_terminals and len(tokens) == 1:
            # A -> B (unit rule, equivalent to B ε)
            parsed_rules.append(ProductionRule(
                lhs=lhs,
                rhs_non_terminal=first_token,
                rhs_terminal="",
                raw_rhs=raw_rhs
            ))
        else:
            # A -> w (only terminals)
            rhs_t = "".join(tokens)
            for t in tokens:
                if t not in EPSILON_SYMBOLS and t not in non_terminals:
                    terminals.add(t)
            parsed_rules.append(ProductionRule(
                lhs=lhs,
                rhs_non_terminal=None,
                rhs_terminal=rhs_t,
                raw_rhs=raw_rhs
            ))

    return LeftLinearGrammar(
        start_symbol=start_symbol,
        non_terminals=non_terminals,
        terminals=terminals,
        rules=parsed_rules
    )
