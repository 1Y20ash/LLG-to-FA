document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const presetSelect = document.getElementById('presetSelect');
    const grammarInput = document.getElementById('grammarInput');
    const convertBtn = document.getElementById('convertBtn');

    const validationBox = document.getElementById('validationBox');
    const symbolsInfo = document.getElementById('symbolsInfo');
    const startSymbolBadge = document.getElementById('startSymbolBadge');
    const nonTerminalsList = document.getElementById('nonTerminalsList');
    const terminalsList = document.getElementById('terminalsList');

    const viewNfaBtn = document.getElementById('viewNfaBtn');
    const viewDfaBtn = document.getElementById('viewDfaBtn');
    const viewMinDfaBtn = document.getElementById('viewMinDfaBtn');
    const faInfoBadge = document.getElementById('faInfoBadge');

    const graphContainer = document.getElementById('graphContainer');
    const graphPlaceholder = document.getElementById('graphPlaceholder');
    const graphSvgOutput = document.getElementById('graphSvgOutput');

    const mathGrammarDef = document.getElementById('mathGrammarDef');
    const mathConversionRulesTable = document.getElementById('mathConversionRulesTable');
    const powersetTableHeader = document.getElementById('powersetTableHeader');
    const powersetTableBody = document.getElementById('powersetTableBody');

    const simInputString = document.getElementById('simInputString');
    const simRunBtn = document.getElementById('simRunBtn');
    const simStatusBanner = document.getElementById('simStatusBanner');
    const simStatusBadge = document.getElementById('simStatusBadge');
    const simStatusText = document.getElementById('simStatusText');
    const simPlaybackControls = document.getElementById('simPlaybackControls');
    const simPrevBtn = document.getElementById('simPrevBtn');
    const simNextBtn = document.getElementById('simNextBtn');
    const simStepCounter = document.getElementById('simStepCounter');
    const simFaTraceList = document.getElementById('simFaTraceList');
    const simDerivationList = document.getElementById('simDerivationList');

    const exportDotCode = document.getElementById('exportDotCode');
    const exportLatexCode = document.getElementById('exportLatexCode');

    // Global Conversion State
    let currentData = null;
    let currentFaType = 'nfa'; // 'nfa' | 'dfa' | 'min_dfa'
    let currentSimulation = null;
    let currentSimStep = 0;

    const viz = new Viz();

    // 1. Fetch & Load Presets
    async function loadPresets() {
        try {
            const res = await fetch('/api/presets');
            const json = await res.json();
            if (json.success) {
                json.presets.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name;
                    opt.dataset.grammar = p.grammar;
                    opt.dataset.test = p.test_strings[0] || "";
                    presetSelect.appendChild(opt);
                });
            }
        } catch (err) {
            console.error("Failed to load presets:", err);
        }
    }

    presetSelect.addEventListener('change', (e) => {
        const selected = presetSelect.options[presetSelect.selectedIndex];
        if (selected && selected.dataset.grammar) {
            grammarInput.value = selected.dataset.grammar;
            if (selected.dataset.test) {
                simInputString.value = selected.dataset.test;
            }
            convertGrammar();
        }
    });

    // 2. Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('active', 'border-indigo-500', 'text-indigo-400', 'bg-slate-800');
                b.classList.add('text-slate-400');
            });
            btn.classList.add('active', 'border-indigo-500', 'text-indigo-400', 'bg-slate-800');
            btn.classList.remove('text-slate-400');

            const targetTab = btn.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.add('hidden'));
            document.getElementById(targetTab).classList.remove('hidden');
        });
    });

    // 3. FA Type Switching
    function setFaType(type) {
        currentFaType = type;
        [viewNfaBtn, viewDfaBtn, viewMinDfaBtn].forEach(b => b.classList.remove('active', 'bg-indigo-600', 'text-white'));
        [viewNfaBtn, viewDfaBtn, viewMinDfaBtn].forEach(b => b.classList.add('bg-slate-700', 'text-slate-300'));

        if (type === 'nfa') {
            viewNfaBtn.classList.add('active', 'bg-indigo-600', 'text-white');
            viewNfaBtn.classList.remove('bg-slate-700', 'text-slate-300');
        } else if (type === 'dfa') {
            viewDfaBtn.classList.add('active', 'bg-indigo-600', 'text-white');
            viewDfaBtn.classList.remove('bg-slate-700', 'text-slate-300');
        } else if (type === 'min_dfa') {
            viewMinDfaBtn.classList.add('active', 'bg-indigo-600', 'text-white');
            viewMinDfaBtn.classList.remove('bg-slate-700', 'text-slate-300');
        }

        renderCurrentGraph();
    }

    viewNfaBtn.addEventListener('click', () => setFaType('nfa'));
    viewDfaBtn.addEventListener('click', () => setFaType('dfa'));
    viewMinDfaBtn.addEventListener('click', () => setFaType('min_dfa'));

    // 4. Render Current Graph with Viz.js
    async function renderCurrentGraph() {
        if (!currentData || !currentData.dot) return;

        let dotString = currentData.dot.nfa;
        let infoText = "";

        if (currentFaType === 'dfa') {
            dotString = currentData.dot.dfa;
            infoText = `DFA: ${currentData.dfa.states.length} states`;
        } else if (currentFaType === 'min_dfa') {
            dotString = currentData.dot.min_dfa;
            infoText = `Minimized DFA: ${currentData.min_dfa.states.length} states`;
        } else {
            infoText = `NFA: ${currentData.nfa.states.length} states`;
        }

        faInfoBadge.textContent = infoText;

        try {
            const svgElement = await viz.renderSVGElement(dotString);
            graphPlaceholder.classList.add('hidden');
            graphSvgOutput.classList.remove('hidden');
            graphSvgOutput.innerHTML = '';
            graphSvgOutput.appendChild(svgElement);
        } catch (err) {
            console.error("Viz rendering error:", err);
            graphSvgOutput.innerHTML = `<p class="text-rose-400 text-xs">Failed to render Graphviz SVG: ${err.message}</p>`;
        }
    }

    // 5. Convert Grammar API Call
    async function convertGrammar() {
        const text = grammarInput.value.trim();
        if (!text) return;

        validationBox.className = "p-3 rounded-lg border text-xs bg-slate-900 border-slate-700 text-slate-400";
        validationBox.textContent = "Converting Left-Linear Grammar...";
        validationBox.classList.remove('hidden');

        try {
            const res = await fetch('/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ grammar: text })
            });

            const json = await res.json();

            if (!json.success) {
                validationBox.className = "p-3 rounded-lg border text-xs bg-rose-950/80 border-rose-800 text-rose-300";
                if (json.errors && json.errors.length > 0) {
                    validationBox.innerHTML = `<strong>Invalid Left-Linear Grammar:</strong><ul class="list-disc ms-4 mt-1 space-y-1">${json.errors.map(e => `<li>${e}</li>`).join('')}</ul>`;
                } else {
                    validationBox.textContent = json.error || "Grammar conversion failed.";
                }
                symbolsInfo.classList.add('hidden');
                return;
            }

            // Success
            currentData = json;

            validationBox.className = "p-3 rounded-lg border text-xs bg-emerald-950/80 border-emerald-800 text-emerald-300 flex items-center space-x-2";
            validationBox.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400"></i> <span>Valid Left-Linear Grammar successfully restructured!</span>`;

            // Render Metadata
            startSymbolBadge.textContent = json.grammar.start_symbol;
            
            nonTerminalsList.innerHTML = json.grammar.non_terminals.map(nt => 
                `<span class="bg-indigo-950 text-indigo-300 border border-indigo-800 px-2 py-0.5 rounded font-mono">${nt}</span>`
            ).join('');

            terminalsList.innerHTML = json.grammar.terminals.map(t => 
                `<span class="bg-amber-950 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-mono">${t}</span>`
            ).join('');

            symbolsInfo.classList.remove('hidden');

            // Render Graphs
            renderCurrentGraph();

            // Populate Math Proof Tables
            renderMathProof(json);

            // Populate Export Boxes
            exportDotCode.value = json.dot.nfa;
            exportLatexCode.value = json.latex;

            // Auto run simulation if string input present
            if (simInputString.value.trim()) {
                simulateString();
            }

        } catch (err) {
            validationBox.className = "p-3 rounded-lg border text-xs bg-rose-950/80 border-rose-800 text-rose-300";
            validationBox.textContent = "Server connection error: " + err.message;
        }
    }

    convertBtn.addEventListener('click', convertGrammar);

    // 6. Render Mathematical Proof Tables
    function renderMathProof(json) {
        const g = json.grammar;
        mathGrammarDef.innerHTML = `
            G = (V, &Sigma;, R, S)<br>
            V = { ${g.non_terminals.join(', ')} }<br>
            &Sigma; = { ${g.terminals.join(', ')} }<br>
            S = ${g.start_symbol}<br>
            R = { ${g.rules.map(r => r.str).join(' ; ')} }
        `;

        // Step 2 table: Conversion rules
        mathConversionRulesTable.innerHTML = '';
        json.nfa.conversion_steps.forEach(step => {
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-950/40";
            tr.innerHTML = `
                <td class="p-2 text-amber-300 font-bold">${step.rule}</td>
                <td class="p-2 text-slate-400">${step.type === 'non_terminal_prefix' ? 'A &rarr; B w' : 'A &rarr; w'}</td>
                <td class="p-2 text-emerald-400">${step.added_transitions.join('<br>')}</td>
            `;
            mathConversionRulesTable.appendChild(tr);
        });

        // Step 3 table: Powerset Construction
        powersetTableHeader.innerHTML = `
            <th class="p-2">DFA State</th>
            <th class="p-2">NFA Subsets</th>
            ${json.dfa.alphabet.map(sym => `<th class="p-2">&delta;('${sym}')</th>`).join('')}
            <th class="p-2">Status</th>
        `;

        powersetTableBody.innerHTML = '';
        json.dfa.subset_table.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-950/40";
            const transTds = json.dfa.alphabet.map(sym => `<td class="p-2 text-indigo-300">${row.transitions[sym] || '&empty;'}</td>`).join('');
            const statusBadge = row.is_final 
                ? `<span class="bg-emerald-950 text-emerald-300 border border-emerald-800 px-1.5 py-0.5 rounded text-[10px]">ACCEPTING</span>`
                : `<span class="text-slate-500 text-[10px]">Normal</span>`;

            tr.innerHTML = `
                <td class="p-2 font-bold text-amber-400">${row.dfa_state}</td>
                <td class="p-2 text-slate-300">{${row.nfa_subsets.join(', ')}}</td>
                ${transTds}
                <td class="p-2">${statusBadge}</td>
            `;
            powersetTableBody.appendChild(tr);
        });
    }

    // 7. String Simulation API Call
    async function simulateString() {
        const text = grammarInput.value.trim();
        const inputStr = simInputString.value.trim();
        if (!text) return;

        try {
            const res = await fetch('/api/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ grammar: text, string: inputStr })
            });

            const json = await res.json();
            if (!json.success) {
                simStatusBanner.className = "p-4 rounded-xl border bg-rose-950/80 border-rose-800 text-rose-300 text-xs";
                simStatusBanner.textContent = json.error;
                simStatusBanner.classList.remove('hidden');
                return;
            }

            currentSimulation = json.simulation;
            currentSimStep = 0;

            renderSimulationBanner();
            renderSimulationStep();
            simPlaybackControls.classList.remove('hidden');

        } catch (err) {
            console.error("Simulation error:", err);
        }
    }

    const simInsertEpsBtn = document.getElementById('simInsertEpsBtn');
    if (simInsertEpsBtn) {
        simInsertEpsBtn.addEventListener('click', () => {
            simInputString.value = "ε";
            simulateString();
        });
    }

    simRunBtn.addEventListener('click', simulateString);

    function renderSimulationBanner() {
        if (!currentSimulation) return;
        simStatusBanner.classList.remove('hidden');

        if (currentSimulation.is_accepted) {
            simStatusBanner.className = "p-4 rounded-xl border bg-emerald-950/80 border-emerald-800 text-emerald-300 flex items-center justify-between";
            simStatusBadge.className = "px-3 py-1 rounded-full text-xs font-bold font-mono bg-emerald-800 text-emerald-100";
            simStatusBadge.textContent = "ACCEPTED";
        } else {
            simStatusBanner.className = "p-4 rounded-xl border bg-rose-950/80 border-rose-800 text-rose-300 flex items-center justify-between";
            simStatusBadge.className = "px-3 py-1 rounded-full text-xs font-bold font-mono bg-rose-800 text-rose-100";
            simStatusBadge.textContent = "REJECTED";
        }

        simStatusText.textContent = currentSimulation.explanation;
    }

    function renderSimulationStep() {
        if (!currentSimulation || !currentSimulation.steps) return;
        const totalSteps = currentSimulation.steps.length;
        const step = currentSimulation.steps[currentSimStep];

        simStepCounter.textContent = `Step ${currentSimStep} / ${totalSteps - 1}`;

        // Render FA Trace
        simFaTraceList.innerHTML = '';
        currentSimulation.steps.forEach((s, idx) => {
            const div = document.createElement('div');
            const isActive = idx === currentSimStep;
            div.className = `p-2.5 rounded border transition-all ${
                isActive 
                    ? 'bg-indigo-950 border-indigo-500 text-indigo-200 shadow-md ring-1 ring-indigo-500' 
                    : 'bg-slate-950 border-slate-800 text-slate-400 opacity-60'
            }`;
            div.innerHTML = `
                <div class="flex justify-between items-center mb-1">
                    <span class="font-bold text-amber-400">Step ${s.step_index}: read '${s.symbol_consumed || '&epsilon;'}'</span>
                    <span class="text-[10px] text-slate-500">Consumed: "${s.consumed_prefix}"</span>
                </div>
                <div class="text-[11px] text-emerald-400">Active NFA States: {${s.active_nfa_states.join(', ')}}</div>
            `;
            simFaTraceList.appendChild(div);
        });

        // Render Grammar Derivation
        simDerivationList.innerHTML = '';
        if (currentSimulation.derivation_path && currentSimulation.derivation_path.length > 0) {
            currentSimulation.derivation_path.forEach((form, idx) => {
                const div = document.createElement('div');
                div.className = "p-2 rounded bg-slate-950 border border-slate-800 text-slate-300 flex items-center space-x-2";
                div.innerHTML = `
                    <span class="text-slate-500 text-[10px]">#${idx}:</span>
                    <span class="font-bold text-amber-300">${form}</span>
                `;
                simDerivationList.appendChild(div);
            });
        } else {
            simDerivationList.innerHTML = `<p class="text-slate-500 text-xs italic">No left-derivation path available for rejected string.</p>`;
        }
    }

    simPrevBtn.addEventListener('click', () => {
        if (currentSimStep > 0) {
            currentSimStep--;
            renderSimulationStep();
        }
    });

    simNextBtn.addEventListener('click', () => {
        if (currentSimulation && currentSimStep < currentSimulation.steps.length - 1) {
            currentSimStep++;
            renderSimulationStep();
        }
    });

    // 8. Copy to Clipboard Buttons
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const targetEl = document.getElementById(targetId);
            if (targetEl) {
                targetEl.select();
                navigator.clipboard.writeText(targetEl.value);
                const originalText = btn.innerHTML;
                btn.innerHTML = `<i class="fa-solid fa-check me-1 text-emerald-400"></i> Copied!`;
                setTimeout(() => btn.innerHTML = originalText, 1500);
            }
        });
    });

    // Initialize Default View
    loadPresets();
    grammarInput.value = "S -> S b | A a | eps\nA -> A b | S a";
    simInputString.value = "a b a";
    convertGrammar();
});
