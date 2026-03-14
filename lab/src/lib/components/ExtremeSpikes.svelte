<script>
    import { t } from "../i18n";
    import { onMount, afterUpdate } from "svelte";

    export let engine;
    export let frame = 0;

    let canvasRef;
    let maxPhi = 0;
    let meanPhi = 0;
    let anomalyRatio = 0;
    let status = "NORMAL";

    $: {
        if (engine && engine.phiData && engine.phiData.frames[frame]) {
            analyzeFrame(engine.phiData.frames[frame]);
            if (canvasRef) {
                renderHeatmap(engine.phiData.frames[frame]);
            }
        }
    }

    function analyzeFrame(phiFrame) {
        let max = -Infinity;
        let sum = 0;
        let count = 0;
        for (let y = 0; y < 64; y++) {
            for (let x = 0; x < 64; x++) {
                const val = phiFrame[y][x];
                if (val > max) max = val;
                sum += val;
                count++;
            }
        }
        maxPhi = max;
        meanPhi = sum / count;
        anomalyRatio = meanPhi > 0 ? maxPhi / meanPhi : 0;

        if (anomalyRatio > 200) status = "EXTREME ANOMALY";
        else if (anomalyRatio > 50) status = "HIGH FLUCTUATION";
        else status = "STABLE";
    }

    function renderHeatmap(phiFrame) {
        const ctx = canvasRef.getContext("2d");
        const width = canvasRef.width;
        const height = canvasRef.height;
        const cellW = width / 64;
        const cellH = height / 64;

        ctx.clearRect(0, 0, width, height);

        // Calculate a safe ceiling to prevent total wash-out
        const ceiling = Math.min(maxPhi, meanPhi * 50);

        for (let y = 0; y < 64; y++) {
            for (let x = 0; x < 64; x++) {
                const val = phiFrame[y][x];
                if (val > meanPhi * 2) {
                    // Only draw anomalous pixels to save GPU
                    const intensity = Math.min(
                        1.0,
                        (val - meanPhi) / (ceiling - meanPhi),
                    );
                    ctx.fillStyle = `rgba(0, 255, 255, ${intensity})`;
                    ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
                }
            }
        }
    }
</script>

<div class="spikes-panel">
    <div class="header">
        <h3>{$t('spikes_title')}</h3>
        <p class="subtitle">{$t('spikes_subtitle')}</p>
    </div>

    <div class="split-pane">
        <div class="text-pane">
            <h4>{$t('spikes_live_analysis')}</h4>
            <div class="live-stats">
                <div class="stat-box">
                    <span class="label">{$t('spikes_status')}</span>
                    <strong class={status === "STABLE" ? "safe" : "danger"}
                        >{status}</strong
                    >
                </div>
                <div class="stat-box">
                    <span class="label">{$t('spikes_max_phi')}</span>
                    <strong>{maxPhi.toExponential(2)}</strong>
                </div>
                <div class="stat-box">
                    <span class="label">{$t('spikes_mean_phi')}</span>
                    <strong>{meanPhi.toExponential(2)}</strong>
                </div>
                <div class="stat-box">
                    <span class="label">{$t('spikes_ratio')}</span>
                    <strong>{anomalyRatio.toFixed(1)}x</strong>
                </div>
            </div>

            <p style="margin-top: 15px;">
                {$t('spikes_desc')}
            </p>

            <div class="equation-box">
                <span class="equation-label">{$t('spikes_eq_label')}</span>
                <code>{$t('ex_i_m_k_e_k_c_eff')}</code>
            </div>
        </div>

        <div class="visual-pane">
            <div class="visual-card">
                <h5>{$t('spikes_heatmap_title').replace('{0}', frame)}</h5>
                <canvas
                    bind:this={canvasRef}
                    width="256"
                    height="256"
                    class="heatmap-canvas"
                ></canvas>
                <p class="caption">{$t('spikes_heatmap_cap')}</p>
            </div>
        </div>
    </div>
</div>

<style>
    .spikes-panel {
        padding: 20px;
        color: #fff;
        font-family: var(--font-mono, monospace);
    }
    .header {
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        padding-bottom: 15px;
    }
    h3 {
        margin: 0 0 5px 0;
        font-size: 1.1rem;
        letter-spacing: 2px;
        color: #00ffff;
    }
    .subtitle {
        margin: 0;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.5);
    }
    .split-pane {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }

    h4 {
        color: #00ffff;
        margin-top: 0;
        font-size: 0.9rem;
    }
    .text-pane p {
        font-size: 0.8rem;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 15px;
    }

    .equation-box {
        background: rgba(0, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.3);
        padding: 15px;
        margin: 20px 0;
        text-align: center;
    }
    .equation-label {
        display: block;
        font-size: 0.7rem;
        color: rgba(0, 255, 255, 0.7);
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    .equation-box code {
        font-size: 1rem;
        color: #fff;
    }

    .live-stats {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 15px;
    }
    .stat-box {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stat-box .label {
        font-size: 0.8rem;
        color: #888;
    }
    .stat-box strong {
        font-size: 1rem;
        color: #fff;
        margin-left: 10px;
    }
    .stat-box .safe {
        color: #00ff00;
    }
    .stat-box .danger {
        color: #ff0055;
        animation: pulse 1s infinite alternate;
    }

    .visual-card {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        text-align: center;
    }
    h5 {
        margin: 0 0 10px 0;
        font-size: 0.8rem;
        color: #00ffff;
        letter-spacing: 1px;
    }
    .heatmap-canvas {
        border: 1px solid rgba(0, 255, 255, 0.2);
        width: 100%;
        aspect-ratio: 1/1;
        image-rendering: pixelated;
        margin: 0 auto;
        display: block;
        background: #000;
    }
    .caption {
        font-size: 0.7rem;
        color: #666;
        margin-top: 10px;
    }

    @keyframes pulse {
        0% {
            opacity: 0.8;
        }
        100% {
            opacity: 1;
            text-shadow: 0 0 10px #ff0055;
        }
    }

    @media (max-width: 768px) {
        .split-pane {
            grid-template-columns: 1fr;
        }
    }
</style>
