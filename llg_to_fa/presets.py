PRESETS = [
    {
        "id": "even_as",
        "name": "Even number of 'a's",
        "description": "Left-Linear Grammar for binary strings over {a, b} containing an even count of 'a's.",
        "grammar": "S -> S b | A a | ε\nA -> A b | S a",
        "test_strings": ["b b", "a a", "a b a", "a a b b", "a b a b a"]
    },
    {
        "id": "ends_with_ab",
        "name": "Strings ending with 'ab'",
        "description": "Left-Linear Grammar generating strings over {a, b} that end with 'ab'.",
        "grammar": "S -> A b\nA -> B a\nB -> B a | B b | ε",
        "test_strings": ["a b", "a a a b", "b b a b", "a b a", "b b"]
    },
    {
        "id": "binary_mod_3",
        "name": "Binary numbers divisible by 3",
        "description": "Left-Linear Grammar generating binary numbers (from right to left) divisible by 3.",
        "grammar": "S -> S 0 | A 1 | ε\nA -> B 0 | S 1\nB -> A 0 | B 1",
        "test_strings": ["0", "1 1", "1 1 0", "1 0 0 1", "1 0 1"]
    },
    {
        "id": "simple_identifier",
        "name": "Variable identifiers",
        "description": "Strings starting with a letter ('a' or 'b') followed by letters or digits.",
        "grammar": "S -> S a | S b | S 0 | S 1 | a | b",
        "test_strings": ["a", "b 0 1", "a b 0 a", "0 a"]
    }
]

def get_preset_by_id(preset_id: str):
    for p in PRESETS:
        if p["id"] == preset_id:
            return p
    return None
