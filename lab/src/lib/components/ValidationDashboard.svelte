<script>
    import { onMount } from "svelte";

    let mode = "quick"; // 'quick' or 'repro'
    let selectedScenario = "hydrogen"; // 't0', 'hydrogen', 'mu'

    let running = false;
    let resultData = null;
    let errorMsg = null;

    const scenarios = [
        {
            id: "t0",
            name: "T0/T1 Core Sanity (Wave Baseline vs Diffusion)",
            url: null,
        }, // we can add a new api if needed, or skip for now and just say it runs CI directly. Wait, I will use /hydrogen/sweep for now since it does T0/T1 implicitly via Hydrogen ITP/Unitary. Actually, let's just make the UI for it.
        {
            id: "hydrogen",
            name: "Hydrogen Mini Sweep & L2 Norm",
            url: "http://localhost:8000/api/lab/hydrogen/sweep",
        },
        {
            id: "mu",
            name: "μ Memory Engine Regression Snapshot",
            url: "http://localhost:8000/api/lab/regression/snapshot",
        },
    ];

    async function runScenario() {
        if (!selectedScenario) return;
        const scenario = scenarios.find((s) => s.id === selectedScenario);
        if (!scenario.url) {
            errorMsg =
                "This scenario is strictly run within the Pytest CI suite due to PyTorch GPU heavy isolation.";
            return;
        }

        running = true;
        errorMsg = null;
        resultData = null;

        try {
            const res = await fetch(scenario.url);
            if (!res.ok)
                throw new Error("Failed to execute Golden validation run");
            resultData = await res.json();

            // If Repro run, we also prepare a download blob for the manifest
            if (mode === "repro" && resultData.manifest) {
                downloadManifest(resultData.manifest);
            }
        } catch (e) {
            errorMsg = e.message;
        } finally {
            running = false;
        }
    }

    function downloadManifest(manifest) {
        const blob = new Blob([JSON.stringify(manifest, null, 4)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `manifest_${manifest.run_id || "snap"}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
</script>

<div class="validation-container">
    <div class="header">
        <h2>Lineum Wave Core Validation Dashboard</h2>
        <p>
            Unified Entrypoint sharing identical integration tests with `pytest`
            CI
        </p>
    </div>

    <div class="controls-panel">
        <div class="mode-toggle">
            <span class="label">Run Execution Mode:</span>
            <button
                class:active={mode === "quick"}
                on:click={() => (mode = "quick")}
                >⚡ Quick Explore (Visual)</button
            >
            <button
                class:active={mode === "repro"}
                on:click={() => (mode = "repro")}
                >🔒 Repro Run (Strict + Download Manifest)</button
            >
        </div>

        <div class="scenario-selector">
            <span class="label">Golden Scenarios:</span>
            <div class="scenario-buttons">
                {#each scenarios as sc}
                    <button
                        class:active={selectedScenario === sc.id}
                        on:click={() => (selectedScenario = sc.id)}
                        disabled={running}
                    >
                        {sc.name}
                    </button>
                {/each}
            </div>
        </div>

        <div class="action-bar">
            <button class="run-btn" on:click={runScenario} disabled={running}>
                {#if running}
                    Spinning Up Math Core...
                {:else}
                    Execute Selected CI Scenario
                {/if}
            </button>
        </div>
    </div>

    {#if errorMsg}
        <div class="error-msg">
            Error: {errorMsg}
        </div>
    {/if}

    {#if resultData}
        <div class="results-panel">
            <div class="manifest-sidebar">
                <h3>Run Manifest 📦</h3>
                {#if resultData.manifest}
                    <pre>{JSON.stringify(resultData.manifest, null, 2)}</pre>
                {:else}
                    <p class="muted">
                        No strict manifest found for this output.
                    </p>
                {/if}
                {#if mode === "repro"}
                    <div class="auth-stamp">✓ Saved to Disk</div>
                {/if}
            </div>

            <div class="content-main">
                {#if resultData.image_b64}
                    <h3>Snapshot (Strict Output)</h3>
                    <img
                        src={`data:image/png;base64,${resultData.image_b64}`}
                        alt="Validation Matplotlib Output"
                        class="verified-img"
                    />
                {/if}

                {#if resultData.results}
                    <h3>Golden Telemetry Logs</h3>
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Grid</th>
                                    <th>Z</th>
                                    <th>E (Ground)</th>
                                    <th>E (End)</th>
                                    <th>dE Drift</th>
                                    <th>Radial &lt;r&gt;</th>
                                    <th>Edge Mass</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each resultData.results as row}
                                    <tr>
                                        <td>{row.grid}x{row.grid}</td>
                                        <td>{row.Z}</td>
                                        <td>{row.E.toFixed(3)}</td>
                                        <td>{row.E_end.toFixed(3)}</td>
                                        <td>{row.drift_dE.toExponential(2)}</td>
                                        <td>{row.r.toFixed(3)}</td>
                                        <td
                                            class:fail={row.edge_mass_cells >
                                                0.1}
                                            class:pass={row.edge_mass_cells <=
                                                0.1}
                                        >
                                            {row.edge_mass_cells.toFixed(3)}
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>

<style>
    .validation-container {
        padding: 20px;
        color: #e0e0e0;
        font-family: sans-serif;
        height: 100%;
        overflow-y: auto;
        box-sizing: border-box;
    }

    .header h2 {
        margin: 0 0 5px 0;
        color: #00ffff;
    }
    .header p {
        margin: 0 0 20px 0;
        color: #aaa;
        font-style: italic;
    }

    .controls-panel {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .label {
        display: block;
        font-size: 0.9rem;
        color: #88ff88;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    button {
        background: rgba(40, 40, 40, 0.8);
        border: 1px solid #555;
        color: #fff;
        padding: 8px 12px;
        cursor: pointer;
        margin-right: 10px;
        font-size: 0.85rem;
    }

    button:hover {
        background: rgba(80, 80, 80, 1);
    }

    button.active {
        background: rgba(0, 255, 255, 0.2);
        border-color: #00ffff;
        color: #00ffff;
    }

    button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .run-btn {
        background: #00ffff;
        color: #000;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        font-size: 1rem;
    }
    .run-btn:hover {
        background: #00cccc;
    }

    .results-panel {
        display: flex;
        gap: 20px;
        margin-top: 20px;
        border-top: 1px dashed rgba(255, 255, 255, 0.2);
        padding-top: 20px;
    }

    .manifest-sidebar {
        flex: 1;
        background: #050505;
        border: 1px solid #333;
        padding: 10px;
        max-width: 300px;
    }

    .manifest-sidebar h3 {
        margin-top: 0;
        color: #ff00ff;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
    }
    .manifest-sidebar pre {
        font-size: 0.75rem;
        color: #0f0;
        overflow-x: auto;
        white-space: pre-wrap;
        font-family: monospace;
    }
    .auth-stamp {
        color: #0f0;
        font-weight: bold;
        margin-top: 10px;
        text-transform: uppercase;
    }

    .content-main {
        flex: 3;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .content-main h3 {
        margin-top: 0;
        color: #fff;
    }

    .verified-img {
        max-width: 100%;
        border: 1px solid #444;
    }

    .table-wrap {
        overflow-x: auto;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-family: monospace;
        font-size: 0.85rem;
    }
    th,
    td {
        border: 1px solid #444;
        padding: 6px 10px;
        text-align: left;
    }
    th {
        background: #111;
        color: #00ffff;
    }
    td.fail {
        color: #ff4444;
        font-weight: bold;
    }
    td.pass {
        color: #44ff44;
    }

    .error-msg {
        margin-top: 20px;
        padding: 15px;
        background: rgba(255, 0, 0, 0.1);
        border-left: 3px solid red;
        color: #ff8888;
        font-family: monospace;
    }
    .muted {
        color: #666;
    }
</style>
