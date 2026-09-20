import argparse
import sys
import io

# Ensure UTF-8 output encoding for Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from llg_to_fa import (
    parse_llg, llg_to_nfa, nfa_to_dfa, minimize_dfa,
    simulate_llg_and_fa, to_dot, to_latex, to_json_export
)

def main():
    parser = argparse.ArgumentParser(
        description="Left-Linear Grammar (LLG) to Finite Automaton (FA) Restructuring Engine"
    )
    parser.add_argument("grammar", type=str, nargs="?", help="Grammar text or path to grammar file")
    parser.add_argument("--file", "-f", type=str, help="Path to input grammar file")
    parser.add_argument("--format", choices=["text", "dot", "latex", "json"], default="text", help="Output format")
    parser.add_argument("--test", "-t", type=str, help="Input string to simulate and test for acceptance")
    parser.add_argument("--output", "-o", type=str, help="Save output to specified file")

    args = parser.parse_args()

    grammar_str = ""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                grammar_str = f.read()
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    elif args.grammar:
        grammar_str = args.grammar
    else:
        # Read from stdin if piped
        if not sys.stdin.isatty():
            grammar_str = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(0)

    try:
        grammar = parse_llg(grammar_str)
        is_valid, errors = grammar.validate_left_linear()
        if not is_valid:
            print("ERROR: Grammar is not Left-Linear:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)

        nfa = llg_to_nfa(grammar)
        dfa = nfa_to_dfa(nfa)
        min_dfa = minimize_dfa(dfa)

        output_content = ""

        if args.test is not None:
            # Strip quotes or spaces
            test_str = args.test.strip()
            sim_res = simulate_llg_and_fa(grammar, nfa, dfa, test_str)
            output_content += f"=== Simulation for string: '{test_str}' ===\n"
            output_content += f"Status: {'ACCEPTED' if sim_res.is_accepted else 'REJECTED'}\n"
            output_content += f"Explanation: {sim_res.explanation}\n\n"
            output_content += "Step-by-step execution trace:\n"
            for step in sim_res.steps:
                consumed = step.consumed_prefix if step.consumed_prefix else "(start)"
                output_content += f"  Step {step.step_index}: read '{step.symbol_consumed or 'ε'}' -> consumed '{consumed}' -> NFA states {step.active_nfa_states} | Derivation: {step.grammar_derivation_step}\n"

        elif args.format == "dot":
            output_content = to_dot(nfa, "Converted NFA")
        elif args.format == "latex":
            output_content = to_latex(grammar, nfa, dfa)
        elif args.format == "json":
            output_content = to_json_export(grammar, nfa, dfa, min_dfa)
        else:
            # Text summary
            output_content += "=== Left-Linear Grammar ===\n"
            output_content += f"Start Symbol: {grammar.start_symbol}\n"
            output_content += f"Non-Terminals: {sorted(list(grammar.non_terminals))}\n"
            output_content += f"Terminals: {sorted(list(grammar.terminals))}\n"
            output_content += "Rules:\n"
            for r in grammar.rules:
                output_content += f"  - {r}\n"

            output_content += "\n=== Converted NFA (5-Tuple) ===\n"
            output_content += f"States Q: {sorted(list(nfa.states))}\n"
            output_content += f"Start State: {nfa.start_state}\n"
            output_content += f"Accepting States F: {sorted(list(nfa.final_states))}\n"
            output_content += "Transitions δ:\n"
            for src, sym_map in sorted(nfa.transitions.items()):
                for sym, targets in sorted(sym_map.items()):
                    output_content += f"  δ({src}, {sym}) = {sorted(list(targets))}\n"

            output_content += "\n=== Converted DFA ===\n"
            output_content += f"DFA States: {dfa.states}\n"
            output_content += f"DFA Start: {dfa.start_state}\n"
            output_content += f"DFA Final: {dfa.final_states}\n"

            output_content += "\n=== Minimized DFA ===\n"
            output_content += f"Minimized States: {min_dfa.states}\n"

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_content)
            print(f"Saved output to '{args.output}'")
        else:
            print(output_content)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
