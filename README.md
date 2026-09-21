# LLG → Finite Automaton Converter

<p align="center">
  <strong>Convert Left-Linear Grammars into equivalent finite automata, visualize the transformation, prove the construction, and test strings interactively.</strong>
</p>

<p align="center">
  <a href="https://llg-to-rifxopxv8-yash-dac.vercel.app/" target="_blank">🌐 Live Demo</a> ·
  <a href="https://github.com/1Y20ash/LLG-to-FA">📦 Repository</a>
</p>

---

## 📌 Overview

**LLG → FA Converter** is an educational web application for studying the relationship between **Left-Linear Grammars (LLGs)** and **Finite Automata (FA)**.

The application takes a Left-Linear Grammar, validates its structure, and performs a complete conversion pipeline:

**Left-Linear Grammar → NFA → DFA → Minimized DFA**

It also provides interactive visualization, mathematical proof information, string simulation, and export options so that the conversion can be understood rather than treated as a black-box operation.

### 🌐 Live Application

**[Open LLG → FA Converter](https://llg-to-rifxopxv8-yash-dac.vercel.app/)**

**Live URL:** https://llg-to-rifxopxv8-yash-dac.vercel.app/

---

## ✨ Features

- 🧩 **Left-Linear Grammar input**
  - Enter grammar productions directly in the browser.
  - Supports alternatives and epsilon productions.
  - Includes ready-to-use example presets.

- ✅ **Grammar validation**
  - Checks whether the supplied grammar satisfies the Left-Linear Grammar restrictions.
  - Displays validation errors when the grammar is invalid.

- 🔄 **Automatic conversion pipeline**
  - Left-Linear Grammar → NFA
  - NFA → DFA using subset construction
  - DFA → Minimized DFA

- 📊 **Automaton visualization**
  - Visual state diagrams for the generated automata.
  - Separate views for NFA, DFA, and minimized DFA.

- 📐 **Mathematical explanation**
  - Shows the grammar and automaton construction information.
  - Presents the conversion as a formal transformation rather than only displaying the final graph.

- 🧪 **String simulator**
  - Enter a test string and execute it through the generated automaton.
  - Shows acceptance/rejection and execution details.

- 📤 **Export support**
  - Graphviz DOT representation
  - LaTeX representation
  - JSON representation through the conversion engine
  - CLI output formats for text, DOT, LaTeX, and JSON

- 💻 **CLI support**
  - Use the conversion engine directly from a terminal without opening the web interface.

- 📱 **Responsive / mobile-friendly UI**
  - Bootstrap-based responsive layout.
  - Works across desktop, tablet, and mobile screen sizes.
  - Touch-friendly controls.

- 📲 **Progressive Web App (PWA)**
  - Installable application shell.
  - Web app manifest and service worker.
  - Cached frontend shell for improved repeat loading.

---

## 🧠 How the Conversion Works

For a Left-Linear Grammar:

$$
G = (V, \Sigma, R, S)
$$

the application constructs an equivalent finite automaton.

### 1. Grammar Validation

The grammar is first parsed and checked to ensure that its productions follow the supported Left-Linear form.

Typical productions include:

- $A \rightarrow Bw$
- $A \rightarrow w$
- $A \rightarrow \epsilon$

where $A$ and $B$ are non-terminals and $w$ represents terminal symbols.

### 2. LLG → NFA

The validated grammar is transformed into an NFA.

The construction uses:

- Grammar non-terminals as automaton states.
- An additional start state.
- Grammar terminals as transition symbols.
- Production rules to determine transitions.
- Epsilon productions to represent epsilon transitions where applicable.

### 3. NFA → DFA

The generated NFA is converted into a deterministic finite automaton using **subset construction**.

### 4. DFA Minimization

The DFA is minimized to reduce equivalent states while preserving the accepted language.

The result is:

$$
LLG \equiv NFA \equiv DFA \equiv Minimized\ DFA
$$

---

## 🖥️ Web Application Workflow

The typical workflow is:

1. Open the application.
2. Enter a Left-Linear Grammar or select a preset.
3. Click **Convert**.
4. Review the grammar validation result.
5. Explore the generated **NFA**.
6. Explore the generated **DFA**.
7. Inspect the **Minimized DFA**.
8. Read the mathematical proof/construction.
9. Test strings using the simulator.
10. Export the generated representation when required.

---

## 🧪 Example Grammar

A simple example:

```text
S -> A b | B a
A -> a
B -> b
```

The application parses the grammar, validates it, and generates the corresponding automata.

Another useful preset is:

```text
S -> S b | A a | ε
A -> A b | S a
```

This demonstrates a grammar for strings containing an even number of `a` symbols over the alphabet `{a, b}`.

---

## 🚀 Run Locally

### Prerequisites

- Python 3.10+ recommended
- pip
- Git

### 1. Clone the repository

```bash
git clone https://github.com/1Y20ash/LLG-to-FA.git
cd LLG-to-FA
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\\Scripts\\activate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Flask application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 💻 CLI Usage

The repository also provides a command-line interface.

### Convert a grammar

```bash
python cli.py "S -> A b | B a; A -> a; B -> b"
```

### Simulate a string

```bash
python cli.py "S -> A b | B a; A -> a; B -> b" --test "a b"
```

### Generate Graphviz DOT

```bash
python cli.py "S -> A b | B a; A -> a; B -> b" --format dot -o fa.dot
```

### Generate LaTeX

```bash
python cli.py "S -> A b | B a; A -> a; B -> b" --format latex -o proof.tex
```

### Generate JSON

```bash
python cli.py "S -> A b | B a; A -> a; B -> b" --format json -o result.json
```

### Read a grammar from a file

```bash
python cli.py --file grammar.txt
```

---

## 🧪 Testing

Run the automated test suite with:

```bash
python -m pytest tests/
```

---

## 🏗️ Project Structure

```text
LLG-to-FA/
├── app.py                  # Flask web application and API routes
├── cli.py                  # Command-line interface
├── requirements.txt        # Python dependencies
│
├── llg_to_fa/
│   ├── __init__.py         # Public conversion-engine API
│   ├── grammar.py          # Grammar and production-rule models
│   ├── parser.py           # LLG parser
│   ├── converter.py        # LLG → NFA conversion
│   ├── dfa.py              # NFA → DFA conversion
│   ├── minimization.py     # DFA minimization
│   ├── simulator.py        # Grammar/automaton simulation
│   ├── exporter.py         # DOT, LaTeX and JSON export
│   └── presets.py          # Example grammars
│
├── templates/
│   └── index.html          # Web application interface
│
├── static/
│   ├── css/
│   │   └── style.css       # Application styling and responsive UI
│   ├── js/
│   │   └── app.js          # Frontend interaction and visualization
│   ├── icons/              # PWA icons
│   ├── manifest.json       # PWA manifest
│   └── service-worker.js   # Service worker
│
└── tests/                  # Automated tests
```

---

## 🔌 API Endpoints

The Flask application exposes a small JSON API used by the frontend.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Web application |
| `/api/presets` | GET | Retrieve example grammar presets |
| `/api/convert` | POST | Validate and convert a grammar |
| `/api/simulate` | POST | Simulate an input string |

### Conversion request

```json
{
  "grammar": "S -> A b | B a; A -> a; B -> b"
}
```

### Simulation request

```json
{
  "grammar": "S -> A b | B a; A -> a; B -> b",
  "string": "a b"
}
```

---

## 🛠️ Technology Stack

### Backend

- **Python**
- **Flask**

### Frontend

- **HTML5**
- **CSS3**
- **JavaScript**
- **Bootstrap 5**
- **Tailwind CSS utilities**
- **Font Awesome**
- **Viz.js**

### Computer Science Concepts

- Formal Languages
- Left-Linear Grammars
- Non-deterministic Finite Automata
- Deterministic Finite Automata
- Subset Construction
- DFA Minimization
- Formal Language Simulation
- Graph Representation

### Development & Deployment

- Git / GitHub
- Flask development server
- Vercel deployment
- Progressive Web App technologies

---

## 🎓 Educational Purpose

This project is designed primarily as a **Formal Languages and Automata Theory learning tool**.

Instead of only producing an automaton, it exposes the intermediate stages so students can connect:

**Grammar Rules → Transition Rules → NFA → DFA → Minimized DFA → String Acceptance**

This makes the application useful for:

- Automata Theory practicals
- Formal Languages assignments
- Classroom demonstrations
- Exam preparation
- Understanding grammar-to-automaton conversion
- Experimenting with different Left-Linear Grammars

---

## ⚠️ Scope

The converter is specifically designed for **Left-Linear Grammars** and validates the supplied grammar before conversion.

For learning purposes, users should inspect the generated intermediate automata and proof information rather than relying only on the final minimized DFA.

The PWA service worker improves availability of the frontend application shell; conversion and simulation still depend on the Flask backend being reachable.

---

## 📄 License

No explicit open-source license is currently declared for this repository.

If you intend to distribute or reuse the project publicly, add an appropriate license file.

---

## 👨‍💻 Author

**Yash Chitmalwar**

B.Tech Computer Science & Engineering — Artificial Intelligence & Machine Learning

GitHub: **[1Y20ash](https://github.com/1Y20ash)**

---

<p align="center">
  <strong>LLG → FA</strong><br>
  From Grammar to Automaton — Visualized, Explained, and Simulated.
</p>
