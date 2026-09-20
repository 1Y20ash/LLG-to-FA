from flask import Flask, render_template, request, jsonify
from llg_to_fa import (
    parse_llg, llg_to_nfa, nfa_to_dfa, minimize_dfa,
    simulate_llg_and_fa, to_dot, to_latex, to_json_export
)
from llg_to_fa.presets import PRESETS, get_preset_by_id

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/presets', methods=['GET'])
def get_presets():
    return jsonify({"success": True, "presets": PRESETS})

@app.route('/api/convert', methods=['POST'])
def convert_llg():
    data = request.get_json() or {}
    grammar_text = data.get("grammar", "").strip()

    if not grammar_text:
        return jsonify({"success": False, "error": "Grammar text cannot be empty."}), 400

    try:
        grammar = parse_llg(grammar_text)
        is_valid, errors = grammar.validate_left_linear()

        if not is_valid:
            return jsonify({
                "success": False,
                "is_left_linear": False,
                "errors": errors,
                "grammar": grammar.to_dict()
            }), 400

        nfa = llg_to_nfa(grammar)
        dfa = nfa_to_dfa(nfa)
        min_dfa = minimize_dfa(dfa)

        return jsonify({
            "success": True,
            "is_left_linear": True,
            "grammar": grammar.to_dict(),
            "nfa": nfa.to_dict(),
            "dfa": dfa.to_dict(),
            "min_dfa": min_dfa.to_dict(),
            "dot": {
                "nfa": to_dot(nfa, "Converted NFA"),
                "dfa": to_dot(dfa, "Converted DFA"),
                "min_dfa": to_dot(min_dfa, "Minimized DFA")
            },
            "latex": to_latex(grammar, nfa, dfa)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/simulate', methods=['POST'])
def simulate_string():
    data = request.get_json() or {}
    grammar_text = data.get("grammar", "").strip()
    input_string = data.get("string", "").strip()

    if not grammar_text:
        return jsonify({"success": False, "error": "Grammar text cannot be empty."}), 400

    try:
        grammar = parse_llg(grammar_text)
        is_valid, errors = grammar.validate_left_linear()
        if not is_valid:
            return jsonify({"success": False, "error": f"Grammar is not Left-Linear: {'; '.join(errors)}"}), 400

        nfa = llg_to_nfa(grammar)
        dfa = nfa_to_dfa(nfa)

        # Handle space-separated terminal symbols or continuous string
        sim_res = simulate_llg_and_fa(grammar, nfa, dfa, input_string)
        return jsonify({
            "success": True,
            "simulation": sim_res.to_dict()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
