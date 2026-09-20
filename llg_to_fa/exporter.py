import json
from typing import Union, Dict, Set, List, Optional
from .grammar import LeftLinearGrammar
from .converter import NFA
from .dfa import DFA
from .minimization import MinimizedDFA

def to_dot(fa: Union[NFA, DFA, MinimizedDFA], title: str = "Finite Automaton") -> str:
    """Generates Graphviz DOT representation of an NFA, DFA, or Minimized DFA."""
    dot_lines = [
        f'digraph "{title}" {{',
        '  rankdir=LR;',
        '  fontname="Helvetica,Arial,sans-serif";',
        '  node [fontname="Helvetica,Arial,sans-serif", fontsize=12];',
        '  edge [fontname="Helvetica,Arial,sans-serif", fontsize=10];',
        ''
    ]

    final_states = set(fa.final_states)
    all_states = set(fa.states)
    start_state = fa.start_state

    # Invisible start arrow
    dot_lines.append('  __start__ [shape=none, label="", width=0, height=0];')

    # Group transitions by (src, dst) pair for clean multi-symbol edge labels
    grouped_edges: Dict[tuple, List[str]] = {}

    if isinstance(fa, NFA):
        for src, sym_map in fa.transitions.items():
            for symbol, targets in sym_map.items():
                for dst in targets:
                    key = (src, dst)
                    if key not in grouped_edges:
                        grouped_edges[key] = []
                    grouped_edges[key].append(symbol)
    else:
        for src, sym_map in fa.transitions.items():
            for symbol, dst in sym_map.items():
                key = (src, dst)
                if key not in grouped_edges:
                    grouped_edges[key] = []
                grouped_edges[key].append(symbol)

    # Style final states with double circle
    if final_states:
        fs_str = " ".join(f'"{s}"' for s in sorted(list(final_states)))
        dot_lines.append(f'  node [shape=doublecircle, style=filled, fillcolor="#e0f2fe", color="#0284c7"]; {fs_str};')

    # Style normal states
    normal_states = all_states - final_states
    if normal_states:
        ns_str = " ".join(f'"{s}"' for s in sorted(list(normal_states)))
        dot_lines.append(f'  node [shape=circle, style=filled, fillcolor="#f8fafc", color="#64748b"]; {ns_str};')

    dot_lines.append(f'  __start__ -> "{start_state}";')

    # Add edges
    for (src, dst), symbols in sorted(grouped_edges.items()):
        label = ", ".join(sorted(symbols))
        dot_lines.append(f'  "{src}" -> "{dst}" [label="{label}"];')

    dot_lines.append('}')
    return "\n".join(dot_lines)

def to_latex(grammar: LeftLinearGrammar, nfa: NFA, dfa: Optional[DFA] = None) -> str:
    """Generates formal mathematical LaTeX document for the LLG to FA conversion."""
    v_str = "\\{" + ", ".join(sorted(list(grammar.non_terminals))) + "\\}"
    sigma_str = "\\{" + ", ".join(sorted(list(grammar.terminals))) + "\\}"
    
    rules_latex = []
    for r in grammar.rules:
        rhs = r.raw_rhs if r.raw_rhs else "\\varepsilon"
        rules_latex.append(f"{r.lhs} \\to {rhs}")
    rules_str = ", \\quad ".join(rules_latex)

    q_nfa = "\\{" + ", ".join(sorted(list(nfa.states))) + "\\}"
    f_nfa = "\\{" + ", ".join(sorted(list(nfa.final_states))) + "\\}"

    lines = [
        "% Left-Linear Grammar to Finite Automaton Transformation",
        "\\documentclass{article}",
        "\\usepackage{amsmath, amssymb}",
        "\\begin{document}",
        "",
        "\\section*{1. Left-Linear Grammar Definition}",
        "Let $G = (V, \\Sigma, R, S)$ be the context-free left-linear grammar:",
        "\\begin{itemize}",
        f"  \\item $V = {v_str}$",
        f"  \\item $\\Sigma = {sigma_str}$",
        f"  \\item $S = {grammar.start_symbol}$",
        f"  \\item Production Rules $R$: ${rules_str}$",
        "\\end{itemize}",
        "",
        "\\section*{2. Converted NFA 5-Tuple}",
        "The equivalent Non-deterministic Finite Automaton $M = (Q_N, \\Sigma, \\delta_N, q_{\\text{start}}, F_N)$ is defined as:",
        "\\begin{itemize}",
        f"  \\item $Q_N = {q_nfa}$",
        f"  \\item Start State $= {nfa.start_state}$",
        f"  \\item Accepting States $F_N = {f_nfa}$",
        "\\end{itemize}",
        "",
        "\\subsection*{Transition Table $\\delta_N$}",
        "\\begin{table}[h]",
        "\\centering",
        "\\begin{tabular}{|c|c|c|}",
        "\\hline",
        "State & Symbol & Next State(s) \\\\",
        "\\hline"
    ]

    for src, sym_map in sorted(nfa.transitions.items()):
        for sym, targets in sorted(sym_map.items()):
            target_str = "\\{" + ", ".join(sorted(list(targets))) + "\\}"
            lines.append(f"{src} & ${sym}$ & ${target_str}$ \\\\")

    lines.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{table}",
        "",
        "\\end{document}"
    ])

    return "\n".join(lines)

def to_json_export(grammar: LeftLinearGrammar, nfa: NFA, dfa: DFA, min_dfa: MinimizedDFA) -> str:
    """Exports complete transformation data as JSON."""
    data = {
        "grammar": grammar.to_dict(),
        "nfa": nfa.to_dict(),
        "dfa": dfa.to_dict(),
        "minimized_dfa": min_dfa.to_dict(),
        "dot": {
            "nfa": to_dot(nfa, "NFA"),
            "dfa": to_dot(dfa, "DFA"),
            "minimized_dfa": to_dot(min_dfa, "Minimized DFA")
        }
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
