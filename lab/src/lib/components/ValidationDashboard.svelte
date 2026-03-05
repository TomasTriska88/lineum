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
        {
            id: "t0",
            name: "Wave Sanity: T0/T1 (Diffusion vs Wave)",
            human: "Check if the core 'Wave engine' is healthy.",
            scientific: "Unitary/norm conservation sanity vs diffusion.",
            when: "After any physics/core change.",
            expect: "Energy stays flat and Edge Mass (8 cells) remains near zero.",
        },
        {
            id: "hydro",
            name: "Hydrogen Validation Mini",
            human: "Can it sustain the 'atomic cloud' around the nucleus?",
            scientific:
                "ITP ground state + unitary hold (2D soft Coulomb analog).",
            when: "To confirm bound-state capability.",
            expect: "A stable central blob with no major bleeding to the edges.",
        },
        {
            id: "mu",
            name: "μ Regression Snapshot",
            human: "Does the structure memory (μ) remain stable in wave mode?",
            scientific: "Compare μ dynamics: diffusion vs wave_projected_soft.",
            when: "After any ψ physics change.",
            expect: "Both diffusion and wave modes should deposit structural memory consistently.",
        },
        {
            id: "play",
            name: "Single-particle Bound-state Analogs",
            human: "Playground for tracing 'single cloud' shapes in a potential.",
            scientific:
                "Single-particle Schr analogs (NOT multi-electron chemistry).",
            when: "For exploration and hypothesis testing.",
            expect: "Depends on your parameters; watch the Energy chart for stability.",
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
    ];

    let running = false;
    let errorMsg = null;
    let currentResult = null;
    let history = [];
    let compareResult = null;
    let showDetails = false;
    let maximizedChart = null;

    let chartConfigE = null;
    let chartConfigR = null;
    let chartConfigEdge = null;

    let showDeleteConfirm = false;

    $: if (currentResult && currentResult.ts_metrics) {
        chartConfigE = buildChartConfig(
            "E",
            currentResult.ts_metrics,
            compareResult?.ts_metrics,
            "<E> Energy",
            "#00ffff",
        );
        chartConfigR = buildChartConfig(
            "r",
            currentResult.ts_metrics,
            compareResult?.ts_metrics,
            "<r> Distance",
            "#ff00ff",
        );
        chartConfigEdge = buildChartConfig(
            "edge_mass",
            currentResult.ts_metrics,
            compareResult?.ts_metrics,
            "Edge Mass (8 cells)",
            "#ff9900",
        );
    }

    function buildChartConfig(key, metrics, cmpMetrics, label, color) {
        if (!metrics[key]) return null;
        const labels = metrics[key].map((_, i) => i);
        const datasets = [
            { label, data: metrics[key], borderColor: color, tension: 0.1 },
        ];
        if (cmpMetrics && cmpMetrics[key]) {
            datasets.push({
                label: `[COMPARE] ${label}`,
                data: cmpMetrics[key],
                borderColor: "rgba(255, 255, 255, 0.4)",
                borderDash: [5, 5],
                tension: 0.1,
            });
        }
        return {
            type: "line",
            data: { labels, datasets },
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
                        title: { display: true, text: label, color: color },
                        ticks: { color: color },
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
    });

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

    async function executeScenario() {
        running = true;
        errorMsg = null;
        compareResult = null;

        let url = "";
        if (selectedScenario === "play") {
            const p = new URLSearchParams(exploreConfig);
            p.append("mode", mode);
            url = `http://127.0.0.1:8000/api/lab/playground?${p.toString()}`;
        } else if (selectedScenario === "hydro") {
            url = "http://127.0.0.1:8000/api/lab/hydrogen/sweep";
        } else if (selectedScenario === "t0") {
            url = "http://127.0.0.1:8000/api/lab/hydrogen/sweep"; // same logic for now
        } else {
            url = "http://127.0.0.1:8000/api/lab/regression/snapshot";
        }

        try {
            const res = await fetch(url);
            if (!res.ok) {
                const text = await res.text();
                throw new Error(text);
            }
            currentResult = await res.json();
            await fetchHistory();

            await tick();
            // Force scroll down to see results
            document
                .querySelectorAll("main, .dashboard, .fullscreen-mode")
                .forEach((n) => {
                    if (n.scrollHeight > n.clientHeight)
                        n.scrollTo(0, n.scrollHeight);
                });
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
                    <span class="watermark">Exploratory</span>
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
                <h3>Scenarios (1-Click)</h3>
                {#each scenarios as sc}
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
                <h2>Select a Scenario and Click Run</h2>
                <p>Welcome to the Lineum Math Core.</p>
            </div>
        {/if}

        {#if currentResult}
            <div class="results-header">
                <div class="header-main">
                    <h2>Run Complete: {currentResult.manifest.run_id}</h2>
                    <span class="git-badge">{currentResult.manifest.git}</span>
                </div>
                <div class="header-actions">
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

            {#if currentResult.ts_metrics}
                {@const lastL =
                    currentResult.ts_metrics.edge_mass[
                        currentResult.ts_metrics.edge_mass.length - 1
                    ]}
                {@const maxL = Math.max(...currentResult.ts_metrics.edge_mass)}
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

            <div class="visuals-grid" class:side-by-side={showDetails}>
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

            <div class="metrics-dashboard">
                <div
                    class="metric-card"
                    on:click={() =>
                        maximizeChart("<E> Energy Conserved", chartConfigE)}
                    role="button"
                    tabindex="0"
                >
                    {#if chartConfigE}
                        <InteractiveChart
                            config={chartConfigE}
                            title="<E> Energy Conserved"
                        />
                    {/if}
                </div>
                <div
                    class="metric-card"
                    on:click={() =>
                        maximizeChart("<r> Distance Spread", chartConfigR)}
                    role="button"
                    tabindex="0"
                >
                    {#if chartConfigR}
                        <InteractiveChart
                            config={chartConfigR}
                            title="<r> Distance Spread"
                        />
                    {/if}
                </div>
                <div
                    class="metric-card"
                    on:click={() =>
                        maximizeChart("Edge Mass (8 cells)", chartConfigEdge)}
                    role="button"
                    tabindex="0"
                >
                    {#if chartConfigEdge}
                        <InteractiveChart
                            config={chartConfigEdge}
                            title="Edge Mass (8 cells)"
                        />
                    {/if}
                </div>
            </div>

            {#if showDetails}
                <div class="details-section">
                    <pre class="manifest-code">{JSON.stringify(
                            currentResult.manifest,
                            null,
                            2,
                        )}</pre>
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
                        {run.timestamp.replace("T", " ").substring(0, 16)}
                    </div>
                    <div class="hist-badges">
                        {#if run.manifest.mode === "explore"}<span class="b-exp"
                                >EXP</span
                            >{:else}<span class="b-val">VAL</span>{/if}
                    </div>
                    <strong>{run.scenario}</strong>
                    <div class="hist-p">
                        Z={run.manifest.explore_config?.Z} dt={run.manifest
                            .explore_config?.dt}
                    </div>
                    <div class="hist-actions">
                        <button on:click={() => loadPastRun(run.run_id)}
                            >Load</button
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
        color: #ddd;
        font-family: inherit;
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
    .watermark {
        position: absolute;
        top: 0;
        right: 5px;
        color: rgba(255, 100, 0, 0.3);
        font-weight: bold;
        font-size: 0.65rem;
        text-transform: uppercase;
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

    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 1000;
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

    @media (max-width: 1024px) {
        .layout {
            display: flex;
            flex-direction: column;
            height: auto;
        }
        .sidebar-right {
            display: none;
        }
    }
</style>
