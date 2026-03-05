<script>
    import { onMount, onDestroy } from "svelte";

    let canvasDiff;
    let canvasWave;
    let ctxDiff;
    let ctxWave;
    let ws;

    let isConnected = false;
    let currentStep = 0;
    let maxSteps = 1000;
    let phaseText = "Connecting...";

    // Metrics
    let diffMaxMu = 0;
    let waveMaxMu = 0;
    let diffN = 0;
    let waveN = 0;

    let showArtifacts = false;
    let artifactsLoading = false;
    let artifactsData = null;
    let artifactsError = null;

    export let wsUrl = "ws://localhost:8000/api/lab/regression";
    const restUrl = "http://localhost:8000/api/lab/regression/snapshot";

    async function loadArtifacts() {
        showArtifacts = !showArtifacts;
        if (showArtifacts && !artifactsData) {
            artifactsLoading = true;
            artifactsError = null;
            try {
                const res = await fetch(restUrl);
                if (!res.ok)
                    throw new Error("Failed to generate dynamic snapshot");
                artifactsData = await res.json();
            } catch (e) {
                artifactsError = e.message;
            } finally {
                artifactsLoading = false;
            }
        }
    }

    function connect() {
        if (ws) ws.close();
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            isConnected = true;
            phaseText = "Stress-Testing Mu Memory";
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.error) {
                phaseText = `Error: ${data.error}`;
                return;
            }

            currentStep = data.step;
            maxSteps = data.max_steps;
            diffMaxMu = data.diff_max_mu;
            waveMaxMu = data.wave_max_mu;
            diffN = data.diff_n;
            waveN = data.wave_n;

            renderGrid(ctxDiff, data.diff_mu, data.diff_psi);
            renderGrid(ctxWave, data.wave_mu, data.wave_psi);

            if (currentStep >= maxSteps - 1) {
                phaseText = "Test Complete (Stable)";
            }
        };

        ws.onclose = () => {
            isConnected = false;
            // Only overwrite if it wasn't a clean finish
            if (!phaseText.includes("Complete")) {
                phaseText = "Disconnected";
            }
        };

        ws.onerror = (e) => {
            console.error("Regression WS Error", e);
            phaseText = "Connection Error";
        };
    }

    function renderGrid(ctx, muFlat, psiFlat) {
        if (!ctx || !muFlat) return;

        const size = Math.sqrt(muFlat.length);
        if (!Number.isInteger(size)) return;

        if (ctx.canvas.width !== size) {
            ctx.canvas.width = size;
            ctx.canvas.height = size;
        }

        const imgData = ctx.createImageData(size, size);
        const data = imgData.data;

        for (let i = 0; i < muFlat.length; i++) {
            const m = muFlat[i]; // The structural memory (0..1 normalized)
            const p = psiFlat[i]; // The active energy pulse (0..1 normalized)

            // Base Inferno colormap for Mu
            let r = Math.min(255, m * 255 + p * 100); // Red grows with memory, spiked by energy
            let g = Math.min(255, (m > 0.5 ? (m - 0.5) * 510 : 0) + p * 255); // Yellow/white highlights
            let b = Math.min(
                255,
                (m < 0.2 ? m * 1275 : Math.max(0, 255 - (m - 0.2) * 500)) +
                    p * 255,
            ); // Purple base

            if (m === 0 && p === 0) {
                r = 0;
                g = 0;
                b = 0;
            }

            const idx = i * 4;
            data[idx] = r;
            data[idx + 1] = g;
            data[idx + 2] = b;
            data[idx + 3] = 255;
        }

        ctx.putImageData(imgData, 0, 0);
    }

    onMount(() => {
        ctxDiff = canvasDiff.getContext("2d", { willReadFrequently: true });
        ctxWave = canvasWave.getContext("2d", { willReadFrequently: true });
        connect();
    });

    onDestroy(() => {
        if (ws) ws.close();
    });
</script>

<div class="lab-container">
    <div class="lab-header">
        <h2>Mu Memory Substrate Regression Test</h2>
        <div class="status-indicator">
            <div class="dot" class:connected={isConnected}></div>
            {phaseText} | Step: {currentStep} / {maxSteps}
        </div>
        <button on:click={connect}>Restart Test</button>
    </div>

    <div class="lab-content">
        <div class="split-view">
            <div class="view-panel">
                <h3>Diffusion Kanon (Thermodynamic)</h3>
                <div class="render-box">
                    <canvas bind:this={canvasDiff} class="pixel-canvas"
                    ></canvas>
                </div>
                <div class="stats-mini">
                    <div>N(t): {diffN.toExponential(2)}</div>
                    <div class:warning={diffMaxMu >= 9.9}>
                        Max Mu: {diffMaxMu.toFixed(2)}
                    </div>
                </div>
            </div>

            <div class="view-panel">
                <h3>Wave Projected Soft (Quantum Acoustic)</h3>
                <div class="render-box">
                    <canvas bind:this={canvasWave} class="pixel-canvas"
                    ></canvas>
                </div>
                <div class="stats-mini">
                    <div>N(t): {waveN.toExponential(2)}</div>
                    <div class:warning={waveMaxMu >= 9.9}>
                        Max Mu: {waveMaxMu.toFixed(2)}
                    </div>
                </div>
            </div>
        </div>

        <div class="info-footer">
            <strong>Regression Goal:</strong> Verify that the new Wave physics engine
            carves persistent identity ($\mu$) into the topography without causing
            mathematical saturation blowouts (NaN) compared to the stable canonical
            diffusion matrix. Bright yellow indicates fully saturated `mu_cap` (10.0).
        </div>
    </div>

    <div class="artifacts-toggle">
        <button on:click={loadArtifacts}>
            {showArtifacts
                ? "Hide Raw Data & Scripts"
                : "Generate Dynamic Validation Artifacts"}
        </button>
    </div>

    {#if showArtifacts}
        <div class="artifacts-panel">
            {#if artifactsLoading}
                <div class="loader-txt">
                    Spinning up Eq-7 Cores to generate real-time metrics...
                </div>
            {:else if artifactsError}
                <div class="error-txt">
                    Error computing dynamic snapshot: {artifactsError}
                </div>
            {:else if artifactsData}
                <div class="artifact-section">
                    <h3>1. Real-Time Render Output (Matplotlib)</h3>
                    <p>
                        Side-by-side comparison of Diffusion (Kanon) vs Wave
                        Projected Soft generated perfectly on-demand from live
                        Engine.
                    </p>
                    <img
                        src={`data:image/png;base64,${artifactsData.image_b64}`}
                        alt="Mu Regression Output"
                        class="artifact-img"
                    />
                </div>

                <div class="artifact-section">
                    <h3>2. Core Executable Script (`run_mu_regression.py`)</h3>
                    <pre><code
                            >{`# 1:1 Validated Logic
from lineum_core.math import Eq4Config, step_eq4

def run_regression_scene(mode_name, config_kwargs):
    size = 128
    
    psi[30:35, 30:35] = 1.0 + 1j
    psi[90:95, 90:95] = 1.0 - 1j
    kappa[60:68, 40:88] = 0.0 # obstacle
    
    cfg = Eq4Config(**config_kwargs)
    
    for step in range(1000):
        # Continuous driving
        state["psi"][30:35, 30:35] += (0.1 + 0.1j) * cfg.dt
        state["psi"][90:95, 90:95] += (0.1 - 0.1j) * cfg.dt
        state = step_eq4(state, cfg)
        
    return state["psi"], state["mu"]
    
# Diffusion Configuration
diff_kwargs = { "dt": 0.1, "physics_mode_psi": "diffusion", "use_mode_coupling": True, "use_mu": True }

# Wave Projected Soft Configuration
wave_kwargs = { "dt": 0.1, "physics_mode_psi": "wave_projected_soft", "wave_lpf_enabled": True, "use_mode_coupling": True, "use_mu": True }
`}</code
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
        flex-direction: column;
        gap: 20px;
        flex: 1;
        min-height: 0;
    }

    .split-view {
        display: flex;
        gap: 20px;
        flex: 1;
        min-height: 0;
    }

    .view-panel {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 10px;
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.1);
        padding: 15px;
    }

    h3 {
        margin: 0;
        font-size: 0.9rem;
        text-align: center;
        color: #88ff88;
        letter-spacing: 1px;
    }

    .render-box {
        flex: 1;
        background: #000;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
        overflow: hidden;
    }

    .pixel-canvas {
        width: 100%;
        height: auto;
        aspect-ratio: 1/1;
        image-rendering: pixelated;
        max-width: 500px;
    }

    .stats-mini {
        display: flex;
        justify-content: space-between;
        font-family: monospace;
        font-size: 0.85rem;
        color: #aaa;
        padding: 0 10px;
    }

    .warning {
        color: #ffaa00;
        font-weight: bold;
    }

    .info-footer {
        background: rgba(0, 255, 0, 0.05);
        border-left: 2px solid #00ff00;
        padding: 10px 15px;
        font-size: 0.8rem;
        color: #ccc;
        line-height: 1.4;
    }

    .info-footer strong {
        color: #00ff00;
        margin-right: 5px;
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
</style>
