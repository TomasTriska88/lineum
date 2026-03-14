<script>
    import { onMount, onDestroy } from "svelte";
    import { t } from "../i18n";

    let canvas;
    let ctx;
    let ws;

    let isConnected = false;
    let currentStep = 0;
    let maxSteps = 300;
    let currentPhase = "Connecting...";
    let nt = 0;
    let edgeMass = 0;

    let showArtifacts = false;
    let artifactsLoading = false;
    let artifactsData = null;
    let artifactsError = null;

    export let wsUrl = typeof window !== 'undefined' ? `ws://${window.location.host}/api/lab/hydrogen` : "ws://127.0.0.1:8000/api/lab/hydrogen";
    const restUrl = "/api/lab/hydrogen/sweep";

    function connect() {
        if (ws) ws.close();
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            isConnected = true;
            currentPhase = "Initializing Imaginary Time";
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.error) {
                currentPhase = `Error: ${data.error}`;
                return;
            }

            currentStep = data.step;
            maxSteps = data.max_steps;
            currentPhase = data.phase;
            nt = data.n_t;
            if (data.edge_mass !== undefined) edgeMass = data.edge_mass;

            renderGrid(data.dens_flat);
        };

        ws.onclose = () => {
            isConnected = false;
            currentPhase = "Disconnected / Finished";
        };

        ws.onerror = (e) => {
            console.error("Hydrogen WS Error", e);
            currentPhase = "Connection Error";
        };
    }

    async function loadArtifacts() {
        showArtifacts = !showArtifacts;
        if (showArtifacts && !artifactsData) {
            artifactsLoading = true;
            artifactsError = null;
            try {
                const res = await fetch(restUrl);
                if (!res.ok)
                    throw new Error("Failed to generate dynamic sweep");
                artifactsData = await res.json();
            } catch (e) {
                artifactsError = e.message;
            } finally {
                artifactsLoading = false;
            }
        }
    }

    function renderGrid(densFlat) {
        if (!ctx || !densFlat) return;

        const size = Math.sqrt(densFlat.length);
        if (!Number.isInteger(size)) return;

        // Match canvas width/height to array
        if (canvas.width !== size) {
            canvas.width = size;
            canvas.height = size;
        }

        const imgData = ctx.createImageData(size, size);
        const data = imgData.data;

        for (let i = 0; i < densFlat.length; i++) {
            const val = densFlat[i]; // 0.0 to 1.0

            // simple custom magma-like colormap logic
            let r = Math.min(255, val * 300);
            let g = Math.min(255, val * 100);
            let b = Math.min(255, Math.max(0, val * 255 - 100));

            const idx = i * 4;
            data[idx] = r;
            data[idx + 1] = g;
            data[idx + 2] = b;
            data[idx + 3] = 255; // alpha
        }

        ctx.putImageData(imgData, 0, 0);
    }

    onMount(() => {
        ctx = canvas.getContext("2d", { willReadFrequently: true });
        connect();
    });

    onDestroy(() => {
        if (ws) {
            ws.close();
        }
    });
</script>

<div class="lab-container">
    <div class="lab-header">
        <h2>{$t('hydro_title')}</h2>
        <div class="status-indicator">
            <div class="dot" class:connected={isConnected}></div>
            {currentPhase}
        </div>
        <button on:click={connect}>{$t('hydro_restart')}</button>
    </div>

    <div class="lab-content">
        <div class="render-box">
            <canvas bind:this={canvas} class="pixel-canvas"></canvas>
        </div>

        <div class="metrics-panel">
            <h3>{$t('hydro_telemetry')}</h3>
            <div class="metric">
                <span class="label">{$t('hydro_step')}</span>
                <span class="value">{currentStep} / {maxSteps}</span>
            </div>
            <div class="metric">
                <span class="label">{$t('hydro_mass_t')}</span>
                <span class="value">{nt.toExponential(2)}</span>
            </div>
            {#if edgeMass > 0}
                <div class="metric">
                    <span class="label">{$t('hydro_edge_mass')}</span>
                    <span class="value">{edgeMass.toExponential(4)}</span>
                </div>
            {/if}

            <div class="disclaimer">
                <strong>{$t('hydro_log_density')}</strong>
                {$t('hydro_log_desc')}
            </div>
        </div>
    </div>

    <div class="artifacts-toggle">
        <button on:click={loadArtifacts}>
            {showArtifacts
                ? $t('hydro_btn_hide')
                : $t('hydro_btn_gen')}
        </button>
    </div>

    {#if showArtifacts}
        <div class="artifacts-panel">
            {#if artifactsLoading}
                <div class="loader-txt">
                    {$t('hydro_spin_up')}
                </div>
            {:else if artifactsError}
                <div class="error-txt">
                    {$t('hydro_error_sweep')} {artifactsError}
                </div>
            {:else if artifactsData}
                <div class="artifact-section">
                    <h3>{$t('hydro_sweep_res')}</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>{$t('hydro_grid')}</th><th>Z</th><th>{$t('hydro_eps')}</th><th
                                    >{$t('hydro_e_start')}</th
                                ><th>{$t('hydro_e_end')}</th><th>{$t('hydro_de_drift')}</th><th
                                    >&lt;r&gt;</th
                                ><th>&lt;r²&gt;</th><th>{$t('hydro_edge_mass')}</th><th
                                    >{$t('hydro_max_edge')}</th
                                >
                            </tr>
                        </thead>
                        <tbody>
                            {#each artifactsData.results as r}
                                <tr>
                                    <td>{r.grid}</td><td>{r.Z}</td><td
                                        >{r.eps}</td
                                    >
                                    <td>{r.E.toExponential(4)}</td><td
                                        >{r.E_end.toExponential(4)}</td
                                    >
                                    <td>{r.drift_dE.toExponential(4)}</td>
                                    <td>{r.r.toFixed(4)}</td><td
                                        >{r.r2.toFixed(4)}</td
                                    >
                                    <td>{r.edge_mass.toExponential(4)}</td><td
                                        >{r.max_edge.toExponential(4)}</td
                                    >
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>

                <div class="artifact-section">
                    <h3>{$t('hydro_rt_render')}</h3>
                    <p>
                        {$t('hydro_rt_desc')}
                    </p>
                    <img
                        src={`data:image/png;base64,${artifactsData.image_b64}`}
                        alt="Log Orbital Output"
                        class="artifact-img"
                    />
                </div>

                <div class="artifact-section">
                    <h3>
                        {$t('hydro_core_script')}
                    </h3>
                    <pre><code
                            >{`# 1:1 Validated Logic
from lineum_core.math import CoreConfig, step_core

def run_experiment(grid_size, Z, eps):
    size = grid_size
    V = -Z / np.sqrt(R**2 + eps**2)
    phi_pot = np.clip(-V * 100, 0, 1000)
    
    cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    # Phase A: Imaginary time cooling
    for _ in range(300):
        state = step_core(state, cfg_itp)
        N_curr = np.sum(np.abs(state["psi"])**2)
        state["psi"] = state["psi"] / np.sqrt(N_curr)
        
    cfg_wave = CoreConfig(dt=0.1, physics_mode_psi="wave_baseline", use_mode_coupling=False)
    # Phase B: Unitary wave propagation (Sanity check)
    for _ in range(50):
        state = step_core(state, cfg_wave)
        
    return metrics`}</code
                        ></pre>
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    .lab-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 20px;
        color: #fff;
        height: 100%;
        box-sizing: border-box;
    }

    .lab-header {
        display: flex;
        align-items: center;
        gap: 20px;
        border-bottom: 1px solid rgba(0, 255, 255, 0.2);
        padding-bottom: 10px;
    }

    h2 {
        margin: 0;
        font-size: 1.2rem;
        color: #00ffff;
        font-weight: normal;
    }

    .status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: monospace;
        font-size: 0.9rem;
        color: #aaa;
        flex: 1;
    }

    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: red;
        box-shadow: 0 0 5px red;
    }

    .dot.connected {
        background: #00ff00;
        box-shadow: 0 0 8px #00ff00;
    }

    button {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid #00ffff;
        color: #00ffff;
        padding: 6px 14px;
        cursor: pointer;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    button:hover {
        background: rgba(0, 255, 255, 0.3);
    }

    .lab-content {
        display: flex;
        gap: 20px;
        flex: 1;
        min-height: 0;
    }

    .render-box {
        flex: 1;
        background: #000;
        border: 1px solid rgba(0, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
    }

    .pixel-canvas {
        width: 100%;
        height: auto;
        aspect-ratio: 1/1;
        image-rendering: pixelated; /* sharp pixels */
        max-width: 600px;
    }

    .metrics-panel {
        width: 300px;
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    h3 {
        margin: 0 0 10px 0;
        font-size: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 5px;
    }

    .metric {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }

    .label {
        color: #888;
        font-size: 0.8rem;
    }

    .value {
        font-family: monospace;
        font-size: 1.1rem;
        color: #00ffff;
    }

    .disclaimer {
        margin-top: auto;
        font-size: 0.75rem;
        color: #aaa;
        line-height: 1.4;
        background: rgba(255, 170, 0, 0.1);
        border-left: 2px solid #ffaa00;
        padding: 10px;
    }
    .disclaimer strong {
        color: #ffaa00;
        display: block;
        margin-bottom: 5px;
    }

    .loader-txt {
        color: #0ff;
        font-family: monospace;
        animation: pulse 1s infinite alternate;
        padding: 20px;
        text-align: center;
    }

    @keyframes pulse {
        from {
            opacity: 0.5;
            text-shadow: 0 0 5px #0ff;
        }
        to {
            opacity: 1;
            text-shadow: 0 0 20px #0ff;
        }
    }

    .error-txt {
        color: #f00;
        font-family: monospace;
        padding: 20px;
        text-align: center;
    }

    .artifacts-toggle {
        display: flex;
        justify-content: center;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed rgba(0, 255, 255, 0.2);
    }

    .artifacts-panel {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 20px;
        background: rgba(0, 5, 10, 0.8);
        border: 1px solid rgba(0, 255, 255, 0.3);
        margin-top: 10px;
        max-height: 500px;
        overflow-y: auto;
    }

    .artifact-section {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .artifact-section h3 {
        color: #00ffff;
        margin: 0;
        font-size: 1rem;
        border-bottom: 1px solid rgba(0, 255, 255, 0.2);
        padding-bottom: 5px;
    }

    .artifact-img {
        max-width: 100%;
        height: auto;
        border: 1px solid #444;
    }

    pre {
        background: #000;
        padding: 15px;
        color: #0f0;
        font-family: monospace;
        font-size: 0.8rem;
        border-left: 3px solid #00ffff;
        overflow-x: auto;
        white-space: pre-wrap;
    }

    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-family: monospace;
        font-size: 0.8rem;
    }

    .data-table th,
    .data-table td {
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 6px 10px;
        text-align: right;
    }

    .data-table th {
        background: rgba(0, 255, 255, 0.1);
        color: #00ffff;
    }
</style>
