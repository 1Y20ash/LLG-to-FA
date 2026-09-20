from dataclasses import dataclass, field
from typing import Optional, Set, List, Dict

EPSILON_SYMBOLS = {'ε', 'eps', 'epsilon', 'lambda', 'λ', '^', 'e', ''}

@dataclass
class ProductionRule:
    lhs: str
    rhs_non_terminal: Optional[str]  # B in A -> B w, or None in A -> w
    rhs_terminal: str                # w in A -> B w or A -> w (can be empty string for ε)
    raw_rhs: str                     # Original string representation

    def __str__(self) -> str:
        if self.rhs_non_terminal and self.rhs_terminal:
            return f"{self.lhs} -> {self.rhs_non_terminal} {self.rhs_terminal}"
        elif self.rhs_non_terminal:
            return f"{self.lhs} -> {self.rhs_non_terminal}"
        elif self.rhs_terminal:
            return f"{self.lhs} -> {self.rhs_terminal}"
        else:
            return f"{self.lhs} -> ε"

    def to_dict(self) -> dict:
        return {
            "lhs": self.lhs,
            "rhs_non_terminal": self.rhs_non_terminal,
            "rhs_terminal": self.rhs_terminal if self.rhs_terminal != "" else "ε",
            "raw_rhs": self.raw_rhs,
            "str": str(self)
        }

@dataclass
class LeftLinearGrammar:
    start_symbol: str
    non_terminals: Set[str] = field(default_factory=set)
    terminals: Set[str] = field(default_factory=set)
    rules: List[ProductionRule] = field(default_factory=list)

    def is_terminal_symbol(self, sym: str) -> bool:
        return sym not in self.non_terminals and sym not in EPSILON_SYMBOLS

    def validate_left_linear(self) -> tuple[bool, List[str]]:
        """
        Validates if the grammar strictly satisfies Left-Linear Grammar rules:
        - A -> B w (where A, B in V, w in Σ*)
        - A -> w   (where A in V, w in Σ*)
        Returns (is_valid, list_of_error_messages)
        """
        errors = []
        for rule in self.rules:
            tokens = rule.raw_rhs.strip().split()
            if not tokens:
                continue

            non_eps_tokens = [t for t in tokens if t not in EPSILON_SYMBOLS]
            if not non_eps_tokens:
                continue

            nt_positions = [i for i, t in enumerate(tokens) if t in self.non_terminals]

            if len(nt_positions) > 1:
                errors.append(
                    f"Rule '{rule.lhs} -> {rule.raw_rhs}' contains multiple non-terminals. "
                    f"Left-Linear rules allow at most one non-terminal."
                )
            elif len(nt_positions) == 1:
                pos = nt_positions[0]
                if pos != 0:
                    errors.append(
                        f"Rule '{rule.lhs} -> {rule.raw_rhs}' has non-terminal '{tokens[pos]}' at position {pos+1}. "
                        f"In a Left-Linear Grammar, the non-terminal MUST be the FIRST symbol on the RHS (e.g., A -> B w)."
                    )
        
        return (len(errors) == 0, errors)

    def to_dict(self) -> dict:
        is_valid, errors = self.validate_left_linear()
        return {
            "start_symbol": self.start_symbol,
            "non_terminals": sorted(list(self.non_terminals)),
            "terminals": sorted(list(self.terminals)),
            "rules": [r.to_dict() for r in self.rules],
            "is_left_linear": is_valid,
            "validation_errors": errors
        }
