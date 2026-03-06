<script>
    import { onMount, tick } from "svelte";
    import InteractiveChart from "./InteractiveChart.svelte";
    import ConfirmDialog from "./ConfirmDialog.svelte";

    let mode = "validate"; // 'validate' (locked) or 'explore' (unlocked)
    let selectedScenario = "t0";
    let selectedPresetId = null;

    // Exploratory Tuning State
    let exploreConfig = {
        grid_size: 64,
        Z: 1.0,
        eps: 0.1,
        dt: 0.1,
        potential_type: "coulomb", // coulomb, harmonic, double_well, ring
        excited_state: 0, // 0=Ground, 1=P-state, 2=D-state
        physics_mode_psi: "wave_projected_soft",
    };

    const scenarios = [
        // ── Core Validation ──
        {
            id: "t0",
            category: "core_validation",
            name: "Wave Sanity: T0/T1 (Diffusion vs Wave)",
            human: "Check if the Wave Core engine is healthy.",
            scientific: "Unitarity/norm conservation sanity vs diffusion.",
            when: "After any physics/core change.",
            expect: "Energy stays flat and Edge Mass (8 cells) remains near zero.",
        },
        {
            id: "hydro",
            category: "core_validation",
            name: "Hydrogen Validation Mini",
            human: "Can the Core engine sustain the 'atomic cloud' around the nucleus?",
            scientific: "ITP ground state + unitary hold (3D proxy).",
            when: "To confirm bound-state capability.",
            expect: "A stable central blob with no major bleeding to the edges.",
        },
        {
            id: "mu",
            category: "core_validation",
            name: "\u03BC Regression Snapshot",
            human: "Does the structure memory (\u03BC) remain stable in wave mode?",
            scientific:
                "Compare \u03BC dynamics: diffusion vs wave_projected_soft.",
            when: "After any \u03C8 physics change.",
            expect: "Both diffusion and wave modes should deposit structural memory consistently.",
        },
        {
            id: "play",
            category: "core_validation",
            name: "Single-particle Bound-state Analogs",
            human: "Playground for tracing 'single cloud' shapes in a potential.",
            scientific:
                "Single-particle Schr analogs (NOT multi-electron chemistry).",
            when: "For exploration and hypothesis testing.",
            expect: "Depends on your parameters; watch the Energy chart for stability.",
        },
        // ── Reality Alignment Checks ──
        {
            id: "ra1",
            category: "reality_alignment",
            name: "RA-1: Wave Unitarity",
            human: "Does the wave keep its total 'mass'? Nothing should appear or vanish.",
            scientific:
                "N(t) norm conservation over 50 wave_baseline steps (Eq7).",
            when: "After any wave engine change.",
            expect: "Flat N(t) line, unitarity error < 5%.",
        },
        {
            id: "ra2",
            category: "reality_alignment",
            name: "RA-2: Stable Bound State",
            human: "A particle cloud held by a field — does it stay or leak away?",
            scientific:
                "ITP ground state + 30-step wave hold. Edge mass + energy drift.",
            when: "To verify cloud stability.",
            expect: "Central blob survives, edge mass < 10%, drift < 15%.",
        },
        {
            id: "ra3",
            category: "reality_alignment",
            name: "RA-3: Excited State (Two-Lobe)",
            human: "Can we make a 'butterfly' shape — genuinely different from the blob?",
            scientific:
                "Gram\u2013Schmidt P-state + PCA lobe detection + orthogonality.",
            when: "To verify excited-state capability.",
            expect: "Two clear lobes, ortho < 0.05, anisotropy > 0.15.",
        },
        {
            id: "ra4",
            category: "reality_alignment",
            lineum_only: true,
            name: "RA-4: \u03BC Memory Imprint",
            human: "Does the system remember where the particle was? Is the memory stable?",
            scientific:
                "\u03BC field growth + boundedness + spatial correlation (Lineum-only).",
            when: "After \u03BC parameter changes.",
            expect: "\u03BC grows, stays bounded, verdict: stable/saturating/runaway.",
        },
        {
            id: "ra5",
            category: "reality_alignment",
            lineum_only: true,
            name: "RA-5: Driving vs Dephasing",
            human: "Is the system being actively 'pushed' or just decaying?",
            scientific:
                "Linon forcing ON vs OFF: \u0394N comparison (Lineum-only).",
            when: "To verify driving mechanism.",
            expect: "Driven mode gains energy, undriven stays flat.",
        },
        {
            id: "ra6",
            category: "reality_alignment",
            lineum_only: true,
            name: "RA-6: LPF Impact",
            human: "The low-pass filter is a numerical tool — does it change the result?",
            scientific: "wave_projected_soft LPF ON vs OFF (Lineum-only).",
            when: "To understand numerical tool impact.",
            expect: "LPF changes dynamics (expected). Both runs stable.",
        },
    ];

    const particlePresets = [
        {
            id: "h_ground",
            group: "A",
            name: "H-like nucleus (Z=1)",
            human: "Hydrogen-like single-particle core.",
            scientific: "Ground state in Soft Coulomb, Z=1.0.",
            when: "Baseline atomic analog.",
            expect: "Edge Mass (8 cells) should be < 0.05. If high: lower dt or raise eps.",
            config: {
                Z: 1.0,
                eps: 0.1,
                dt: 0.05,
                potential_type: "coulomb",
                excited_state: 0,
                grid_size: 64,
                physics_mode_psi: "wave_projected_soft",
            },
        },
        {
            id: "he_ground",
            group: "A",
            name: "He-like nucleus (Z=2)",
            human: "Helium-like single-particle core (stronger pull).",
            scientific: "Ground state in Soft Coulomb, Z=2.0.",
            when: "Testing tighter gradients.",
            expect: "Edge Mass (8 cells) should be < 0.05. If high: lower dt or raise eps.",
            config: {
                Z: 2.0,
                eps: 0.1,
                dt: 0.02,
                potential_type: "coulomb",
                excited_state: 0,
                grid_size: 64,
                physics_mode_psi: "wave_projected_soft",
            },
        },
        {
            id: "c_ground",
            group: "A",
            name: "Carbon-like nucleus (Z=6) [single-particle analog]",
            human: "Observe a much stronger central pull.",
            scientific:
                "Higher Z potential scaling validation (NOT real chemistry).",
            when: "Testing extreme central forces.",
            expect: "Edge Mass (8 cells) should be < 0.05. Requires very low dt (0.005) or it explodes.",
            config: {
                Z: 6.0,
                eps: 0.1,
                dt: 0.005,
                potential_type: "coulomb",
                excited_state: 0,
                grid_size: 64,
                physics_mode_psi: "wave_projected_soft",
            },
        },
        {
            id: "o_ground",
            group: "A",
            name: "O-like nucleus (Z=8) [single-particle analog]",
            human: "Strongest central pull — oxygen-like single-particle core.",
            scientific:
                "Very deep soft Coulomb well. Extreme gradient test (NOT real chemistry).",
            when: "Stress-testing potential extremes.",
            expect: "Edge Mass (8 cells) < 0.05. Requires ultra-low dt (0.002). FIX: auto-halve dt if leaking.",
            config: {
                Z: 8.0,
                eps: 0.1,
                dt: 0.002,
                potential_type: "coulomb",
                excited_state: 0,
                grid_size: 64,
                physics_mode_psi: "wave_projected_soft",
            },
        },
    ];

    let running = false;
    let errorMsg = null;
    let currentResult = null;
    let history = [];
    let compareResult = null;
    let showDetails = false;
    let maximizedChart = null;

    let systemHealth = { commit_hash: "loading...", tests: "..." };

    let chartConfigs = [];

    let showDeleteConfirm = false;

    $: if (currentResult && currentResult.timeseries_data) {
        chartConfigs = [];
        const td = currentResult.timeseries_data;
        const cmp = compareResult?.timeseries_data;

        function addLine(key, label, color) {
            if (td[key]) {
                const conf = buildChartConfig(
                    label,
                    [key],
                    [label],
                    [color],
                    td,
                    cmp,
                );
                if (conf) chartConfigs.push(conf);
            }
        }
        function addMultiLine(title, keys, labels, colors) {
            if (td[keys[0]]) {
                const conf = buildChartConfig(
                    title,
                    keys,
                    labels,
                    colors,
                    td,
                    cmp,
                );
                if (conf) chartConfigs.push(conf);
            }
        }

        addLine("N_series", "N(t) Norm Conservation", "#00ffff");
        addLine("E", "<E> Energy Conserved", "#00ffff");
        addLine("r", "<r> Distance Spread", "#ff00ff");
        addLine("edge_mass", "Edge Mass (8 cells)", "#ff9900");
        addLine("max_edge", "Max Edge Mass", "#ff3333");
        addLine("mu_max_series", "μ_max Over Time", "#ff9900");

        addMultiLine(
            "N(t): Driven vs Undriven",
            ["N_driven", "N_undriven"],
            ["Driven (Linon ON)", "Undriven (OFF)"],
            ["#00ffff", "#888888"],
        );
        addMultiLine(
            "Energy E(t)",
            ["E_on", "E_off"],
            ["LPF ON", "LPF OFF"],
            ["#00ffff", "#ff6644"],
        );
        addMultiLine(
            "Norm N(t)",
            ["N_on", "N_off"],
            ["LPF ON", "LPF OFF"],
            ["#00ffff", "#ff6644"],
        );
    }

    function buildChartConfig(title, keys, labels, colors, td, cmp) {
        if (!td[keys[0]]) return null;
        const xLabels = td[keys[0]].map((_, i) => i);
        const datasets = [];
        for (let j = 0; j < keys.length; j++) {
            const key = keys[j];
            if (td[key]) {
                datasets.push({
                    label: labels[j],
                    data: td[key],
                    borderColor: colors[j],
                    tension: 0.1,
                });
                if (cmp && cmp[key]) {
                    datasets.push({
                        label: `[CMP] ${labels[j]}`,
                        data: cmp[key],
                        borderColor: "rgba(255, 255, 255, 0.4)",
                        borderDash: [5, 5],
                        tension: 0.1,
                    });
                }
            }
        }
        return {
            title: title,
            type: "line",
            data: { labels: xLabels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Time Step",
                            color: "#888",
                        },
                        ticks: { color: "#666" },
                        grid: { color: "#222" },
                    },
                    y: {
                        title: { display: false },
                        ticks: { color: "#aaa" },
                        grid: { color: "#222" },
                    },
                },
                plugins: {
                    legend: { display: true, labels: { color: "#ccc" } },
                },
            },
        };
    }

    onMount(async () => {
        await fetchHistory();
        await fetchHealth();
    });

    async function fetchHealth() {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/lab/health");
            if (res.ok) systemHealth = await res.json();
        } catch (e) {
            console.error("Health fetch failed:", e);
        }
    }

    async function fetchHistory() {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/lab/history");
            if (res.ok) history = await res.json();
        } catch (e) {
            console.error("History fetch failed:", e);
        }
    }

    function promptClearHistory() {
        showDeleteConfirm = true;
    }

    async function executeClearHistory() {
        showDeleteConfirm = false;
        try {
            const res = await fetch("http://127.0.0.1:8000/api/lab/history", {
                method: "DELETE",
            });
            if (res.ok) {
                history = [];
                currentResult = null;
                compareResult = null;
            }
        } catch (e) {
            console.error("Clear history failed:", e);
        }
    }

    async function fetchRunData(run_id) {
        const res = await fetch(`http://127.0.0.1:8000/api/lab/runs/${run_id}`);
        if (!res.ok) throw new Error("Could not load run data");
        return await res.json();
    }

    async function loadPastRun(run_id) {
        try {
            currentResult = await fetchRunData(run_id);
            compareResult = null;
        } catch (e) {
            errorMsg = e.message;
        }
    }

    async function loadCompareRun(run_id) {
        try {
            compareResult = await fetchRunData(run_id);
        } catch (e) {
            errorMsg = e.message;
        }
    }

    async function executeScenario(isGolden = false) {
        running = true;
        errorMsg = null;
        compareResult = null;

        try {
            let res;
            if (selectedScenario === "play") {
                res = await fetch("http://127.0.0.1:8000/api/lab/playground", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        config: { ...exploreConfig, mode },
                    }),
                });
            } else {
                let url;
                if (selectedScenario === "hydro" || selectedScenario === "t0")
                    url = "http://127.0.0.1:8000/api/lab/hydrogen/sweep";
                else if (selectedScenario === "mu")
                    url = "http://127.0.0.1:8000/api/lab/regression/snapshot";
                else if (selectedScenario === "ra1")
                    url = "http://127.0.0.1:8000/api/lab/ra/unitarity";
                else if (selectedScenario === "ra2")
                    url = "http://127.0.0.1:8000/api/lab/ra/bound-state";
                else if (selectedScenario === "ra3")
                    url = "http://127.0.0.1:8000/api/lab/ra/excited-state";
                else if (selectedScenario === "ra4")
                    url = "http://127.0.0.1:8000/api/lab/ra/mu-memory";
                else if (selectedScenario === "ra5")
                    url = "http://127.0.0.1:8000/api/lab/ra/driving";
                else if (selectedScenario === "ra6")
                    url = "http://127.0.0.1:8000/api/lab/ra/lpf-impact";
                else url = "http://127.0.0.1:8000/api/lab/regression/snapshot";

                if (isGolden) url += "?golden=true";
                res = await fetch(url);
            }

            if (!res.ok) {
                const text = await res.text();
                throw new Error(text);
            }
            currentResult = await res.json();
            await fetchHistory();
        } finally {
            running = false;
            await tick();
            setTimeout(() => {
                document
                    .getElementById("verdict-block")
                    ?.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 50);
        }
    }

    function applyFix() {
        mode = "explore";
        selectedScenario = "play";
        if (exploreConfig.dt > 0.01) {
            exploreConfig.dt = Number((exploreConfig.dt / 2).toFixed(4));
        } else {
            exploreConfig.grid_size = Math.min(
                exploreConfig.grid_size * 2,
                256,
            );
        }
        executeScenario();
    }

    async function runGoldenSuite() {
        if (running) return;
        const suiteIds = ["hydro", "ra1", "ra2", "ra3", "ra4", "ra5", "ra6"];
        for (const scId of suiteIds) {
            selectedScenario = scId;
            try {
                await executeScenario(true);
            } catch (e) {
                console.error("Golden suite failed on", scId, e);
            }
            if (errorMsg) break;
        }
    }

    async function rerunFromManifest(runId) {
        running = true;
        errorMsg = null;
        try {
            const res = await fetch("http://127.0.0.1:8000/api/lab/rerun", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ run_id: runId }),
            });
            if (!res.ok) throw new Error(await res.text());
            currentResult = await res.json();
            await fetchHistory();
        } catch (e) {
            errorMsg = e.message;
        } finally {
            running = false;
        }
    }

    async function autoFix() {
        if (selectedScenario !== "play") return;
        if (
            currentResult &&
            currentResult.ts_metrics &&
            currentResult.ts_metrics.edge_mass
        ) {
            const maxL = Math.max(...currentResult.ts_metrics.edge_mass);
            if (maxL > 0.05) {
                exploreConfig.dt = exploreConfig.dt / 2.0;
                await executeScenario();
            }
        }
    }

    function maximizeChart(title, config) {
        maximizedChart = { title, config };
    }
</script>

<div class="system-health-bar">
    <span class="commit"
        >🛡️ System Health &rsaquo; Build: <strong
            >{systemHealth.commit_hash}</strong
        ></span
    >
    <span class="status-pass"
        >Golden tests last run: <strong>{systemHealth.tests}</strong></span
    >
    {#if systemHealth.loaded_modules}
        <span
            class="loaded-paths"
            title="routing_backend: {systemHealth.loaded_modules
                .routing_backend}&#10;validation_core: {systemHealth
                .loaded_modules.validation_core}"
        >
            Running from: <strong
                >{systemHealth.loaded_modules.routing_backend}</strong
            >
        </span>
    {/if}
</div>

<div class="dashboard layout">
    <aside class="sidebar-left">
        <div class="sidebar-scroll">
            <div class="mode-switcher">
                <button
                    class:active={mode === "validate"}
                    class="val-btn"
                    on:click={() => (mode = "validate")}
                >
                    🔒 VALIDATE<small>Safe Presets</small>
                </button>
                <button
                    class:active={mode === "explore"}
                    class="exp-btn"
                    on:click={() => (mode = "explore")}
                >
                    ⚡ EXPLORE<small>Unlocked</small>
                </button>
            </div>

            {#if mode === "explore"}
                <div class="warning-banner border-explore">
                    <span class="badge badge-explore">Exploratory</span>
                    <p><strong>Sandbox — you might break stability.</strong></p>
                    <p class="sci">
                        Free params + warnings, not validation-grade.
                    </p>
                </div>
            {:else}
                <div class="warning-banner border-validate">
                    <span class="badge">Validation-grade</span>
                    <p>
                        <strong>Technical check — reproducible results.</strong>
                    </p>
                    <p class="sci">
                        Locked presets + manifest + validation-grade.
                    </p>
                </div>
            {/if}

            <div class="scenario-list">
                <div class="scenario-header-row">
                    <h3>Core Validation</h3>
                    {#if mode === "validate"}
                        <button
                            class="golden-suite-btn"
                            on:click={runGoldenSuite}
                            disabled={running}
                        >
                            🌟 RUN GOLDEN SUITE
                        </button>
                    {/if}
                </div>
                {#each scenarios.filter((s) => s.category === "core_validation") as sc}
                    <div
                        class="scenario-card"
                        class:active={selectedScenario === sc.id}
                        on:click={() => (selectedScenario = sc.id)}
                        role="button"
                        tabindex="0"
                    >
                        <strong>{sc.name}</strong>
                        <div class="dual-desc">
                            <p class="human">{sc.human}</p>
                            <p class="scientific">{sc.scientific}</p>
                            <p class="when"><em>When:</em> {sc.when}</p>
                            <p class="expect"><em>Expect:</em> {sc.expect}</p>
                        </div>
                    </div>
                {/each}

                <h3 class="ra-header">Reality Alignment Checks</h3>
                {#each scenarios.filter((s) => s.category === "reality_alignment") as sc}
                    <div
                        class="scenario-card ra-card"
                        class:active={selectedScenario === sc.id}
                        on:click={() => (selectedScenario = sc.id)}
                        role="button"
                        tabindex="0"
                    >
                        <div class="scenario-title-row">
                            <strong>{sc.name}</strong>
                            {#if sc.lineum_only}
                                <span class="lineum-badge">LINEUM-ONLY</span>
                            {/if}
                        </div>
                        <div class="dual-desc">
                            <p class="human">{sc.human}</p>
                            <p class="scientific">{sc.scientific}</p>
                            <p class="when"><em>When:</em> {sc.when}</p>
                            <p class="expect"><em>Expect:</em> {sc.expect}</p>
                        </div>
                    </div>
                {/each}
            </div>

            {#if selectedScenario === "play"}
                <div class="preset-panel">
                    <h3>Particle Presets</h3>
                    <div class="preset-buttons">
                        {#each particlePresets as p}
                            <button
                                class="p-btn"
                                class:active={selectedPresetId === p.id}
                                on:click={() => {
                                    selectedPresetId = p.id;
                                    if (mode === "explore")
                                        exploreConfig = { ...p.config };
                                }}
                            >
                                {p.name.split(" ")[0]}
                                <small>Z={p.config.Z}</small>
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}

            {#if mode === "explore" && selectedScenario === "play"}
                <div class="tuning-panel">
                    <h3>Advanced V(r) Analog Tuning</h3>
                    <label
                        >Z (Charge) <input
                            type="number"
                            step="0.5"
                            bind:value={exploreConfig.Z}
                        /></label
                    >
                    <label
                        >ε (Epsilon) <input
                            type="number"
                            step="0.05"
                            bind:value={exploreConfig.eps}
                        /></label
                    >
                    <label
                        >dt (Time Step) <input
                            type="number"
                            step="0.01"
                            bind:value={exploreConfig.dt}
                        /></label
                    >
                    <label
                        >Potential V(r):
                        <select bind:value={exploreConfig.potential_type}>
                            <option value="coulomb">Soft Coulomb</option>
                            <option value="harmonic">Harmonic r^2</option>
                            <option value="double_well">Double Well</option>
                            <option value="ring">Ring Potential</option>
                        </select>
                    </label>
                    <label
                        >Excitation
                        <select bind:value={exploreConfig.excited_state}>
                            <option value={0}>0 (Ground / S-like)</option>
                            <option value={1}>1 (First Node / P-like)</option>
                            <option value={2}>2 (Cross Node / D-like)</option>
                        </select>
                    </label>
                </div>
            {/if}
        </div>
        <div class="sidebar-footer">
            <button
                class="mega-run"
                disabled={running}
                on:click={executeScenario}
            >
                {running ? "EXECUTING MATH CORE..." : "RUN SCENARIO"}
            </button>
        </div>
    </aside>

    <main class="content-center">
        {#if errorMsg}
            <div class="error-msg">❌ {errorMsg}</div>
        {/if}

        {#if !currentResult && !running}
            <div class="empty-state">
                <div class="welcome-box">
                    <h2>Lineum Validation Core</h2>
                    <p class="human-lead">
                        Verify that the digital universe is stable and behaves
                        according to the rules of physics.
                    </p>
                    <div class="dual-desc-box">
                        <div class="desc-row">
                            <span class="mode-pill validate">VALIDATE Mode</span
                            >
                            <div class="text">
                                <strong
                                    >Technical check over reproducible results.</strong
                                >
                                <span class="sci"
                                    >Executes locked presets against a
                                    predefined manifest of wave-dynamics
                                    expectations.</span
                                >
                            </div>
                        </div>
                        <div class="desc-row">
                            <span class="mode-pill explore">EXPLORE Mode</span>
                            <div class="text">
                                <strong
                                    >Sandbox for hunting phenomena — you might
                                    break stability.</strong
                                >
                                <span class="sci"
                                    >Unlocks parameters for single-particle
                                    Schrödinger analogs. Not validation-grade.</span
                                >
                            </div>
                        </div>
                    </div>
                    <p class="call-to-action">
                        Select a scenario from the left panel and click <strong
                            >RUN SCENARIO</strong
                        >.
                    </p>
                </div>
            </div>
        {/if}

        {#if currentResult}
            <div class="results-header" id="verdict-block">
                <div class="header-main">
                    <h2>Run Complete: {currentResult.manifest.run_id}</h2>
                    <span class="git-badge">{currentResult.manifest.git}</span>
                </div>
                <div class="header-actions">
                    <button
                        class="jump-btn"
                        on:click={() =>
                            document
                                .getElementById("visuals-section")
                                ?.scrollIntoView({ behavior: "smooth" })}
                    >
                        ⬇️ Jump to Results
                    </button>
                    <button
                        class="toggle-details"
                        on:click={() => (showDetails = !showDetails)}
                    >
                        {showDetails
                            ? "Hide Details"
                            : "Show Scientific Details"}
                    </button>
                    <a
                        class="export-btn"
                        href={`http://127.0.0.1:8000/api/lab/runs/${currentResult.manifest.run_id}/export`}
                        download
                    >
                        📥 Export Data Package (.zip)
                    </a>
                </div>
            </div>

            {#if currentResult.expectation_results && currentResult.expectation_results.length > 0}
                <div
                    class="pass-fail-panel"
                    class:verdict-pass={currentResult.overall_pass === true}
                    class:verdict-fail={currentResult.overall_pass === false}
                >
                    <div class="verdict-header">
                        {#if currentResult.overall_pass === true}
                            <span class="verdict-icon">✅</span>
                            <span class="verdict-text"
                                >PASS — All expectations met</span
                            >
                        {:else}
                            <span class="verdict-icon">❌</span>
                            <span class="verdict-text"
                                >FAIL — Some expectations not met</span
                            >
                            <button class="fix-btn" on:click={applyFix}
                                >🔨 Auto-Fix Params</button
                            >
                        {/if}
                        <span class="verdict-mode"
                            >{mode === "validate"
                                ? "🔒 VALIDATE"
                                : "⚡ EXPLORE"}</span
                        >
                    </div>
                    <div class="expectation-checklist">
                        {#each currentResult.expectation_results as exp}
                            <div
                                class="exp-row"
                                class:exp-pass={exp.passed}
                                class:exp-fail={!exp.passed}
                            >
                                <span class="exp-icon"
                                    >{exp.passed ? "✅" : "❌"}</span
                                >
                                <span class="exp-labels">
                                    <span class="exp-human"
                                        >{exp.human_label || exp.label}</span
                                    >
                                    <span class="exp-scientific"
                                        >{exp.label}</span
                                    >
                                </span>
                                <span class="exp-values">
                                    {exp.measured !== null &&
                                    exp.measured !== undefined
                                        ? typeof exp.measured === "number"
                                            ? exp.measured.toFixed(6)
                                            : exp.measured
                                        : "N/A"}
                                    <span class="exp-op">{exp.op}</span>
                                    {exp.expected}
                                </span>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}

            {#if currentResult.timeseries_data && currentResult.timeseries_data.edge_mass}
                {@const lastL =
                    currentResult.timeseries_data.edge_mass[
                        currentResult.timeseries_data.edge_mass.length - 1
                    ]}
                {@const maxL = Math.max(
                    ...currentResult.timeseries_data.edge_mass,
                )}
                <div
                    class="status-banner"
                    class:pass={maxL < 0.05}
                    class:warn={maxL >= 0.05 && maxL < 0.2}
                    class:fail={maxL >= 0.2}
                >
                    <div class="status-icon">
                        {#if maxL < 0.05}✅ Stable cloud
                        {:else if maxL < 0.2}⚠️ Leaking edge
                        {:else}❌ Chaotic (Unstable)
                        {/if}
                    </div>
                    <div class="status-text">
                        Max Edge Mass (8 cells): {maxL.toFixed(3)} | Final: {lastL.toFixed(
                            3,
                        )}
                    </div>
                    {#if maxL >= 0.05 && mode === "explore"}
                        <button class="autofix-btn" on:click={autoFix}
                            >🔨 Auto FIX (Drop dt)</button
                        >
                    {/if}
                </div>
            {/if}

            <div
                class="visuals-grid"
                id="visuals-section"
                class:side-by-side={showDetails}
            >
                <div class="run-col">
                    <h3>Simulation Output</h3>
                    {#if currentResult.image_b64}
                        <img
                            src={`data:image/png;base64,${currentResult.image_b64}`}
                            alt="Validation Mathplot"
                        />
                    {/if}
                </div>
                {#if compareResult && showDetails}
                    <div class="run-col">
                        <h3>
                            Comparison Base: {compareResult.manifest.run_id
                                .split("_")
                                .slice(1, 3)
                                .join("_")}
                        </h3>
                        {#if compareResult.image_b64}
                            <img
                                src={`data:image/png;base64,${compareResult.image_b64}`}
                                alt="Compare plot"
                            />
                        {/if}
                    </div>
                {/if}
            </div>

            {#if chartConfigs.length > 0}
                <div class="metrics-dashboard">
                    {#each chartConfigs as conf, i}
                        {#if showDetails || (!currentResult.image_b64 && i === 0)}
                            <div
                                class="metric-card"
                                on:click={() => maximizeChart(conf.title, conf)}
                                role="button"
                                tabindex="0"
                            >
                                <InteractiveChart
                                    config={conf}
                                    title={conf.title}
                                />
                            </div>
                        {/if}
                    {/each}
                </div>
            {/if}

            {#if showDetails}
                <div class="details-section">
                    <pre class="manifest-code">{JSON.stringify(
                            currentResult.manifest,
                            null,
                            2,
                        )}</pre>
                </div>
            {/if}

            {#if compareResult}
                <div class="compare-panel">
                    <h3>
                        📊 Compare: {currentResult.manifest.run_id} vs {compareResult
                            .manifest?.run_id}
                    </h3>

                    {#if currentResult.results && compareResult.results}
                        {@const a =
                            currentResult.results[
                                currentResult.results.length - 1
                            ]}
                        {@const b =
                            compareResult.results?.[
                                compareResult.results?.length - 1
                            ]}
                        {#if a && b}
                            <div class="delta-metrics">
                                <h4>Δ Metrics</h4>
                                <table class="delta-table">
                                    <thead
                                        ><tr
                                            ><th>Metric</th><th>Current</th><th
                                                >Compare</th
                                            ><th>Δ</th></tr
                                        ></thead
                                    >
                                    <tbody>
                                        {#if a.E !== undefined && b.E !== undefined}
                                            <tr>
                                                <td>Energy E</td>
                                                <td>{a.E?.toFixed(4)}</td>
                                                <td>{b.E?.toFixed(4)}</td>
                                                <td
                                                    class:delta-pos={a.E - b.E >
                                                        0}
                                                    class:delta-neg={a.E - b.E <
                                                        0}
                                                    >{a.E - b.E > 0
                                                        ? "+"
                                                        : ""}{(
                                                        a.E - b.E
                                                    ).toFixed(4)}</td
                                                >
                                            </tr>
                                        {/if}
                                        {#if a.r !== undefined && b.r !== undefined}
                                            <tr>
                                                <td>⟨r⟩</td>
                                                <td>{a.r?.toFixed(4)}</td>
                                                <td>{b.r?.toFixed(4)}</td>
                                                <td
                                                    class:delta-pos={a.r - b.r >
                                                        0}
                                                    class:delta-neg={a.r - b.r <
                                                        0}
                                                    >{a.r - b.r > 0
                                                        ? "+"
                                                        : ""}{(
                                                        a.r - b.r
                                                    ).toFixed(4)}</td
                                                >
                                            </tr>
                                        {/if}
                                        {#if a.edge_mass_cells !== undefined && b.edge_mass_cells !== undefined}
                                            <tr>
                                                <td>Edge Mass</td>
                                                <td
                                                    >{a.edge_mass_cells?.toFixed(
                                                        6,
                                                    )}</td
                                                >
                                                <td
                                                    >{b.edge_mass_cells?.toFixed(
                                                        6,
                                                    )}</td
                                                >
                                                <td
                                                    class:delta-pos={a.edge_mass_cells -
                                                        b.edge_mass_cells >
                                                        0}
                                                    class:delta-neg={a.edge_mass_cells -
                                                        b.edge_mass_cells <
                                                        0}
                                                    >{a.edge_mass_cells -
                                                        b.edge_mass_cells >
                                                    0
                                                        ? "+"
                                                        : ""}{(
                                                        a.edge_mass_cells -
                                                        b.edge_mass_cells
                                                    ).toFixed(6)}</td
                                                >
                                            </tr>
                                        {/if}
                                        {#if a.drift_dE !== undefined && b.drift_dE !== undefined}
                                            <tr>
                                                <td>Drift ΔE/E</td>
                                                <td>{a.drift_dE?.toFixed(4)}</td
                                                >
                                                <td>{b.drift_dE?.toFixed(4)}</td
                                                >
                                                <td
                                                    class:delta-pos={a.drift_dE -
                                                        b.drift_dE >
                                                        0}
                                                    class:delta-neg={a.drift_dE -
                                                        b.drift_dE <
                                                        0}
                                                    >{a.drift_dE - b.drift_dE >
                                                    0
                                                        ? "+"
                                                        : ""}{(
                                                        a.drift_dE - b.drift_dE
                                                    ).toFixed(4)}</td
                                                >
                                            </tr>
                                        {/if}
                                    </tbody>
                                </table>
                            </div>
                        {/if}
                    {/if}

                    <div class="diff-manifest">
                        <h4>Diff Manifest</h4>
                        <div class="diff-grid">
                            {#if currentResult.manifest?.config && compareResult.manifest?.config}
                                {@const mc = currentResult.manifest.config}
                                {@const mb = compareResult.manifest.config}
                                {@const allKeys = [
                                    ...new Set([
                                        ...Object.keys(mc),
                                        ...Object.keys(mb),
                                    ]),
                                ]}
                                {#each allKeys as key}
                                    {@const vc = JSON.stringify(mc[key])}
                                    {@const vb = JSON.stringify(mb[key])}
                                    <div
                                        class="diff-row"
                                        class:diff-changed={vc !== vb}
                                    >
                                        <span class="diff-key">{key}</span>
                                        <span class="diff-val">{vc ?? "—"}</span
                                        >
                                        <span class="diff-arrow"
                                            >{vc !== vb ? "≠" : "="}</span
                                        >
                                        <span class="diff-val">{vb ?? "—"}</span
                                        >
                                    </div>
                                {/each}
                            {/if}
                        </div>
                    </div>
                    <button
                        class="close-compare"
                        on:click={() => (compareResult = null)}
                        >✕ Close Compare</button
                    >
                </div>
            {/if}
        {/if}
    </main>

    <aside class="sidebar-right">
        <div class="hist-header">
            <h3>Run History DB</h3>
            <button
                class="clear-db-btn"
                on:click={promptClearHistory}
                title="Clear All History">🗑️ Clear</button
            >
        </div>
        <div class="hist-list">
            {#each history as run}
                <div
                    class="hist-card"
                    class:hist-active={currentResult?.manifest?.run_id ===
                        run.run_id}
                >
                    <div class="hist-stamp">
                        {typeof run.timestamp === "number"
                            ? new Date(run.timestamp * 1000)
                                  .toISOString()
                                  .replace("T", " ")
                                  .substring(0, 16)
                            : (run.timestamp || "")
                                  .replace("T", " ")
                                  .substring(0, 16)}
                    </div>
                    <div class="hist-badges">
                        {#if run.manifest?.is_golden}<span
                                class="golden-badge"
                                title="Part of the Golden validation suite"
                                >GOLDEN</span
                            >{/if}
                        {#if run.manifest?.mode === "explore"}<span
                                class="b-exp">EXP</span
                            >{:else}<span class="b-val">VAL</span>{/if}
                        {#if run.overall_pass === true}<span class="b-pass"
                                >PASS</span
                            >
                        {:else if run.overall_pass === false}<span
                                class="b-fail">FAIL</span
                            >
                        {/if}
                    </div>
                    <strong>{run.scenario}</strong>
                    <div class="hist-p">
                        {#if run.manifest?.config?.Z}Z={run.manifest.config
                                .Z}{/if}
                        {#if run.manifest?.config?.dt}dt={run.manifest.config
                                .dt}{/if}
                        {#if run.manifest?.config?.physics_mode_psi}| {run
                                .manifest.config.physics_mode_psi}{/if}
                    </div>
                    <div class="hist-actions">
                        <button on:click={() => loadPastRun(run.run_id)}
                            >Load</button
                        >
                        <button
                            class="rerun-btn"
                            on:click={() => rerunFromManifest(run.run_id)}
                            >Rerun</button
                        >
                        {#if currentResult && currentResult.manifest.run_id !== run.run_id}
                            <button
                                class="cmp-btn"
                                on:click={() => loadCompareRun(run.run_id)}
                                >Diff</button
                            >
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    </aside>

    {#if maximizedChart}
        <div
            class="modal-backdrop"
            on:click={() => (maximizedChart = null)}
            role="button"
            tabindex="0"
        >
            <div
                class="modal-content"
                on:click|stopPropagation
                role="dialog"
                tabindex="-1"
            >
                <div class="modal-header">
                    <h2>{maximizedChart.title}</h2>
                    <button
                        class="close-modal"
                        aria-label="Close"
                        on:click={() => (maximizedChart = null)}>✕</button
                    >
                </div>
                <div class="modal-body">
                    <InteractiveChart
                        config={JSON.parse(
                            JSON.stringify(maximizedChart.config),
                        )}
                        title={maximizedChart.title}
                        showMax={false}
                    />
                </div>
            </div>
        </div>
    {/if}

    <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Clear Run History"
        message="Are you sure you want to delete all run data? This action permanently destroys all tracked validation runs and cannot be undone."
        confirmText="Yes, delete everything"
        cancelText="Cancel"
        on:confirm={executeClearHistory}
        on:cancel={() => (showDeleteConfirm = false)}
    />
</div>

<style>
    .layout {
        display: grid;
        grid-template-columns: 320px 1fr 280px;
        gap: 0;
        height: 100%;
        min-height: calc(100vh - 150px);
        background: #080808;
        position: relative;
    }
    .help-fab {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0ff, #06c);
        color: #000;
        font-size: 1.4rem;
        font-weight: 800;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.3);
        z-index: 100;
        transition: transform 0.2s;
    }
    .help-fab:hover {
        transform: scale(1.15);
    }
    .help-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.75);
        z-index: 200;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .help-panel {
        background: #111;
        border: 1px solid #0ff3;
        border-radius: 12px;
        width: min(800px, 90vw);
        max-height: 80vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 8px 40px rgba(0, 255, 255, 0.15);
    }
    .help-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid #222;
    }
    .help-header h2 {
        color: #0ff;
        font-size: 1.1rem;
        margin: 0;
    }
    .help-body {
        overflow-y: auto;
        padding: 20px;
    }
    .help-md {
        color: #ccc;
        font-family: "Inter", sans-serif;
        font-size: 0.82rem;
        line-height: 1.7;
        white-space: pre-wrap;
        word-break: break-word;
        margin: 0;
    }

    aside,
    main {
        padding: 20px;
        overflow-y: auto;
    }

    .sidebar-left {
        background: #111;
        border-right: 1px solid #333;
        padding: 0;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .sidebar-scroll {
        padding: 20px;
        flex: 1;
        overflow-y: auto;
    }
    .sidebar-footer {
        padding: 0;
        background: #00ffff;
        flex-shrink: 0;
        position: sticky;
        bottom: 0;
        z-index: 10;
        box-shadow: 0 -5px 15px rgba(0, 0, 0, 0.5);
    }

    .sidebar-right {
        background: #111;
        border-left: 1px solid #333;
    }

    .mode-switcher {
        display: flex;
        gap: 5px;
        margin-bottom: 20px;
    }
    .mode-switcher button {
        flex: 1;
        padding: 10px;
        border: 1px solid #333;
        background: #1a1a1a;
        color: #888;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .mode-switcher button small {
        font-size: 0.65rem;
        opacity: 0.7;
    }
    .mode-switcher button.active.val-btn {
        background: rgba(0, 255, 100, 0.1);
        border-color: #0f6;
        color: #0f6;
    }
    .mode-switcher button.active.exp-btn {
        background: rgba(255, 150, 0, 0.1);
        border-color: #f90;
        color: #f90;
    }

    .warning-banner {
        background: rgba(0, 0, 0, 0.3);
        padding: 10px;
        font-size: 0.8rem;
        margin-bottom: 20px;
        position: relative;
    }
    .border-explore {
        border: 1px solid #f60;
    }
    .border-validate {
        border: 1px solid #0f6;
    }
    .badge-explore {
        background: #f60;
        color: #fff;
    }
    .badge {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #0f6;
        color: #000;
        padding: 2px 6px;
        font-size: 0.65rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .warning-banner p {
        margin: 0 0 4px 0;
    }
    .warning-banner .sci {
        font-family: monospace;
        color: #888;
    }

    .scenario-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 30px;
    }
    .ra-header {
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid #333;
        color: #f90;
    }
    .scenario-title-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .lineum-badge {
        font-size: 0.55rem;
        background: rgba(255, 150, 0, 0.15);
        color: #f90;
        padding: 1px 5px;
        border-radius: 3px;
        border: 1px solid #f903;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .ra-card.active {
        border-color: #f90;
        background: rgba(255, 150, 0, 0.05);
    }
    .ra-card strong {
        color: #f90;
    }
    .scenario-card {
        padding: 12px;
        border: 1px solid #333;
        background: #151515;
        cursor: pointer;
        transition: 0.2s;
    }
    .scenario-card:hover {
        border-color: #666;
    }
    .scenario-card.active {
        border-color: #0ff;
        background: rgba(0, 255, 255, 0.05);
    }
    .scenario-card strong {
        color: #0ff;
        display: block;
        margin-bottom: 4px;
        font-size: 0.9rem;
    }
    .dual-desc {
        margin-top: 5px;
    }
    .dual-desc p {
        margin: 0;
        font-size: 0.75rem;
        line-height: 1.3;
    }
    .dual-desc .human {
        color: #ccc;
        margin-bottom: 2px;
    }
    .dual-desc .scientific {
        color: #888;
        font-family: monospace;
        font-size: 0.7rem;
        margin-bottom: 2px;
    }
    .dual-desc .when {
        color: #55a;
        font-style: italic;
    }
    .dual-desc .expect {
        color: #aa5;
        margin-top: 4px;
        font-style: italic;
        font-weight: bold;
    }

    .preset-panel h3,
    .tuning-panel h3 {
        color: #888;
        font-size: 0.8rem;
        text-transform: uppercase;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
        margin-top: 20px;
    }
    .preset-buttons {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .p-btn {
        background: #222;
        border: 1px solid #444;
        color: #ccc;
        padding: 6px;
        cursor: pointer;
        text-align: left;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .p-btn:hover {
        background: #333;
    }
    .p-btn.active {
        border-color: #0ff;
        background: rgba(0, 255, 255, 0.1);
        color: #0ff;
    }
    .p-btn small {
        font-size: 0.7rem;
        color: #888;
    }

    .tuning-panel {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    .tuning-panel label {
        display: flex;
        flex-direction: column;
        font-size: 0.85rem;
        color: #ccc;
        gap: 5px;
    }
    .tuning-panel input,
    .tuning-panel select {
        background: #000;
        color: #fff;
        border: 1px solid #444;
        padding: 6px;
        outline: none;
    }
    .tuning-panel input:focus,
    .tuning-panel select:focus {
        border-color: #0ff;
    }

    .mega-run {
        width: 100%;
        padding: 20px;
        background: transparent;
        font-size: 1.1rem;
        font-weight: bold;
        letter-spacing: 2px;
        color: #000;
        border: none;
        cursor: pointer;
    }
    .mega-run:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    .mega-run:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .results-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    .header-main {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .results-header h2 {
        margin: 0;
        color: #fff;
    }
    .git-badge {
        background: #333;
        padding: 4px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.8rem;
    }
    .header-actions {
        display: flex;
        gap: 10px;
    }
    .toggle-details {
        background: transparent;
        color: #aaa;
        border: 1px solid #555;
        padding: 8px 15px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: 0.2s;
    }
    .toggle-details:hover {
        background: #333;
        color: #fff;
    }
    .export-btn {
        background: #00ffff;
        color: #000;
        padding: 8px 15px;
        text-decoration: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9rem;
        transition: 0.2s;
    }
    .export-btn:hover {
        background: #fff;
        transform: scale(1.02);
    }

    .status-banner {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .status-banner.pass {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #0f0;
        color: #0f0;
    }
    .status-banner.warn {
        background: rgba(255, 200, 0, 0.1);
        border: 1px solid #fc0;
        color: #fc0;
    }
    .status-banner.fail {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid #f00;
        color: #f00;
    }
    .autofix-btn {
        background: #fc0;
        color: #000;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
    }
    .autofix-btn:hover {
        background: #fff;
    }

    .visuals-grid {
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin-bottom: 30px;
    }
    .visuals-grid.side-by-side {
        flex-direction: row;
    }
    .run-col {
        flex: 1;
        background: #111;
        border: 1px solid #333;
        padding: 15px;
    }
    .run-col img {
        max-width: 100%;
        border: 1px solid #222;
    }

    .metrics-dashboard {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: #151515;
        border: 1px solid #333;
        padding: 15px;
        height: 250px;
        cursor: pointer;
        transition: 0.2s;
    }
    .metric-card:hover {
        border-color: #0ff;
        transform: translateY(-2px);
    }

    .manifest-code {
        background: #000;
        color: #0f0;
        padding: 15px;
        font-family: monospace;
        font-size: 0.8rem;
        overflow-x: auto;
        border: 1px solid #333;
    }

    .hist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .hist-header h3 {
        margin: 0;
        color: #fff;
        font-size: 1.1rem;
    }
    .clear-db-btn {
        background: transparent;
        color: #ff4444;
        border: 1px solid #ff4444;
        padding: 4px 8px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8rem;
    }
    .clear-db-btn:hover {
        background: rgba(255, 0, 0, 0.1);
    }

    .charts-section {
        display: flex;
        flex-direction: column;
        gap: 30px;
    }

    /* ── Empty State ─────────────────────────────────── */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 400px;
        text-align: center;
        gap: 10px;
        color: #ccc;
        opacity: 0.5;
    }

    .empty-state h2 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 400;
        color: #00ffff;
        letter-spacing: 0.1rem;
    }

    .empty-state p {
        margin: 0;
        font-size: 0.8rem;
        color: #888;
    }
    .hist-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .hist-card {
        background: #1a1a1a;
        border: 1px solid #333;
        padding: 10px;
    }
    .hist-card.hist-active {
        border-color: #0ff;
    }
    .hist-stamp {
        color: #888;
        font-size: 0.75rem;
        margin-bottom: 5px;
    }
    .hist-badges span {
        display: inline-block;
        padding: 2px 4px;
        border-radius: 2px;
        font-size: 0.65rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .b-exp {
        background: #f90;
        color: #000;
    }
    .b-val {
        background: #0f6;
        color: #000;
    }
    .hist-card strong {
        display: block;
        color: #ccc;
        margin-bottom: 5px;
    }
    .hist-p {
        font-family: monospace;
        color: #0ff;
        margin-bottom: 10px;
    }
    .hist-actions {
        display: flex;
        gap: 5px;
    }
    .hist-actions button {
        flex: 1;
        background: #333;
        color: #fff;
        border: 1px solid #555;
        cursor: pointer;
        padding: 4px;
    }
    .hist-actions button:hover {
        background: #555;
    }
    .cmp-btn {
        border-color: #f0f !important;
        color: #f0f !important;
    }
    .cmp-btn:hover {
        background: rgba(255, 0, 255, 0.1) !important;
    }
    .rerun-btn {
        border-color: #0af !important;
        color: #0af !important;
    }
    .rerun-btn:hover {
        background: rgba(0, 170, 255, 0.1) !important;
    }

    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 40px;
    }
    .modal-content {
        background: #111;
        border: 1px solid #333;
        width: 100%;
        max-width: 1200px;
        height: 90vh;
        display: flex;
        flex-direction: column;
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        border-bottom: 1px solid #333;
    }
    .modal-header h2 {
        margin: 0;
        color: #fff;
    }
    .close-modal {
        background: none;
        border: none;
        color: #aaa;
        font-size: 1.5rem;
        cursor: pointer;
    }
    .close-modal:hover {
        color: #fff;
    }
    .modal-body {
        flex: 1;
        padding: 20px;
        min-height: 0;
    }
    .error-msg {
        background: rgba(255, 0, 0, 0.1);
        border-left: 3px solid #f00;
        color: #faa;
        padding: 15px;
        margin-bottom: 20px;
    }

    /* ═══ P3: PASS/FAIL Verdict Panel ═══ */
    .pass-fail-panel {
        border: 2px solid #555;
        padding: 16px;
        margin-bottom: 20px;
        background: rgba(0, 0, 0, 0.4);
    }
    .pass-fail-panel.verdict-pass {
        border-color: #0f6;
        background: rgba(0, 255, 100, 0.05);
    }
    .pass-fail-panel.verdict-fail {
        border-color: #f44;
        background: rgba(255, 50, 50, 0.05);
    }
    .verdict-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .verdict-icon {
        font-size: 1.4rem;
    }
    .verdict-text {
        flex: 1;
    }
    .verdict-pass .verdict-text {
        color: #0f6;
    }
    .verdict-fail .verdict-text {
        color: #f44;
    }
    .verdict-mode {
        font-size: 0.7rem;
        padding: 3px 8px;
        border: 1px solid #555;
        background: rgba(255, 255, 255, 0.05);
        color: #aaa;
    }
    .expectation-checklist {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .exp-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        font-size: 0.78rem;
        border-left: 3px solid #555;
        background: rgba(255, 255, 255, 0.02);
    }
    .exp-row.exp-pass {
        border-left-color: #0f6;
        background: rgba(0, 255, 100, 0.04);
    }
    .exp-row.exp-fail {
        border-left-color: #f44;
        background: rgba(255, 50, 50, 0.06);
    }
    .exp-icon {
        flex-shrink: 0;
    }
    .exp-labels {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 1px;
    }
    .exp-human {
        color: #eee;
        font-size: 0.78rem;
    }
    .exp-scientific {
        color: #777;
        font-size: 0.62rem;
        font-family: "Courier New", monospace;
    }
    .exp-values {
        font-family: "Courier New", monospace;
        color: #0ff;
        font-size: 0.72rem;
        white-space: nowrap;
    }
    .exp-op {
        color: #888;
        margin: 0 3px;
    }

    /* History PASS/FAIL badges */
    .b-pass {
        background: rgba(0, 255, 80, 0.2);
        color: #0f6;
        font-size: 0.6rem;
        padding: 1px 5px;
        border: 1px solid #0f6;
        margin-left: 4px;
    }
    .b-fail {
        background: rgba(255, 50, 50, 0.2);
        color: #f44;
        font-size: 0.6rem;
        padding: 1px 5px;
        border: 1px solid #f44;
        margin-left: 4px;
    }

    /* ═══ P7: Compare Panel ═══ */
    .compare-panel {
        border: 2px solid #f0f;
        background: rgba(255, 0, 255, 0.03);
        padding: 16px;
        margin-top: 20px;
    }
    .compare-panel h3 {
        color: #f0f;
        margin: 0 0 12px 0;
        font-size: 0.95rem;
    }
    .compare-panel h4 {
        color: #aaa;
        margin: 8px 0 6px 0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .delta-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.75rem;
        margin-bottom: 12px;
    }
    .delta-table th {
        text-align: left;
        color: #888;
        padding: 4px 8px;
        border-bottom: 1px solid #333;
    }
    .delta-table td {
        padding: 4px 8px;
        color: #ccc;
        font-family: "Courier New", monospace;
    }
    .delta-pos {
        color: #f44;
    }
    .delta-neg {
        color: #0f6;
    }
    .diff-grid {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .diff-row {
        display: grid;
        grid-template-columns: 120px 1fr 30px 1fr;
        gap: 6px;
        padding: 3px 8px;
        font-size: 0.72rem;
        font-family: "Courier New", monospace;
        background: rgba(255, 255, 255, 0.02);
    }
    .diff-row.diff-changed {
        background: rgba(255, 200, 0, 0.08);
        border-left: 2px solid #fc0;
    }
    .diff-key {
        color: #0ff;
    }
    .diff-val {
        color: #ccc;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .diff-arrow {
        color: #888;
        text-align: center;
    }
    .diff-changed .diff-arrow {
        color: #fc0;
        font-weight: bold;
    }
    .close-compare {
        margin-top: 10px;
        background: #222;
        color: #f0f;
        border: 1px solid #f0f;
        padding: 6px 16px;
        cursor: pointer;
    }
    .close-compare:hover {
        background: rgba(255, 0, 255, 0.1);
    }

    /* ═══ Layman Empty State ═══ */
    .empty-state {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        padding: 20px;
    }
    .welcome-box {
        background: #111;
        border: 1px solid #333;
        padding: 40px;
        max-width: 600px;
        text-align: center;
        border-radius: 8px;
    }
    .welcome-box h2 {
        color: #0ff;
        margin: 0 0 10px 0;
        font-size: 1.8rem;
        letter-spacing: 2px;
    }
    .human-lead {
        color: #ddd;
        font-size: 1.1rem;
        margin-bottom: 30px;
        line-height: 1.4;
    }
    .dual-desc-box {
        display: flex;
        flex-direction: column;
        gap: 20px;
        text-align: left;
        margin-bottom: 30px;
        background: #0a0a0a;
        padding: 20px;
        border: 1px solid #222;
        border-radius: 6px;
    }
    .desc-row {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .desc-row .mode-pill {
        display: inline-block;
        padding: 4px 8px;
        font-size: 0.75rem;
        font-weight: bold;
        border-radius: 4px;
        width: max-content;
    }
    .desc-row .mode-pill.validate {
        background: #0f6;
        color: #000;
    }
    .desc-row .mode-pill.explore {
        background: #f60;
        color: #fff;
    }
    .desc-row .text strong {
        display: block;
        color: #ccc;
        font-size: 0.95rem;
        margin-bottom: 4px;
    }
    .desc-row .text .sci {
        display: block;
        color: #777;
        font-size: 0.8rem;
        font-family: monospace;
    }
    .call-to-action {
        color: #0ff;
        font-weight: bold;
        font-size: 1.05rem;
    }

    @media (max-width: 768px) {
        .layout {
            display: flex;
            flex-direction: column;
            height: auto;
        }
        .sidebar-right {
            display: none;
        }
    }

    .system-health-bar {
        background-color: #0b111a;
        border-bottom: 1px solid #1a2332;
        padding: 6px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: monospace;
        font-size: 0.85em;
        color: #8892b0;
    }
    .system-health-bar strong {
        color: #fff;
    }
    .system-health-bar .status-pass {
        color: #0f6;
    }
    .system-health-bar .loaded-paths {
        margin-left: auto;
        color: #888;
        font-family: monospace;
        background: #111;
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px dotted #333;
        max-width: 400px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        cursor: help;
    }
    .system-health-bar .loaded-paths strong {
        color: #aaa;
    }

    .scenario-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .scenario-header-row h3 {
        margin: 0;
    }
    .golden-suite-btn {
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255, 215, 0, 0.5);
        color: #ffd700;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        font-size: 0.8rem;
        transition: all 0.2s;
    }
    .golden-suite-btn:hover:not(:disabled) {
        background: rgba(255, 215, 0, 0.2);
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    .golden-suite-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .golden-badge {
        background: rgba(255, 215, 0, 0.1);
        color: #ffd700;
        border: 1px solid #ffd700;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 0.65rem;
        font-weight: bold;
    }
</style>
