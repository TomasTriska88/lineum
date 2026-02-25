<script>
    import { t } from "$lib/i18n";
</script>

<div class="demo-container">
    <div class="header">
        <h2>FLUID GEOMETRY COMPRESSION</h2>
        <p>
            Lossless neural topography mapping. Compress petabytes of spatial
            point-cloud data by finding the unique fluid equilibrium equation
            that recreates the shape.
        </p>
    </div>

    <div class="workspace">
        <div class="panel controls-panel">
            <h3>SPATIAL MESH</h3>
            <p class="desc">
                Select a 3D point-cloud or volumetric dataset. The solver will
                collapse the discrete nodes into a continuous field formula.
            </p>

            <div class="file-drop">
                <svg
                    class="w-6 h-6 text-sky-500 mb-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                </svg>
                <span>DROP .OBJ OR .LAS</span>
            </div>

            <button class="generate-btn" disabled> INITIATE COLLAPSE </button>
            <div class="coming-soon">
                <span class="pulse"></span>
                <span>AWAITING GPU ALLOCATION</span>
            </div>

            <div class="stats mt-4">
                <div class="stat">
                    <span class="label">TARGET RATIO:</span>
                    <span class="val">1 : 14,000</span>
                </div>
                <div class="stat">
                    <span class="label">EQUATION COMPLEXITY:</span>
                    <span class="val">O(1)</span>
                </div>
            </div>
        </div>

        <div class="panel visual-panel relative group">
            <div
                class="absolute inset-0 bg-[url('/noise.png')] opacity-10 mix-blend-overlay"
            ></div>
            <div
                class="flex flex-col items-center justify-center h-full opacity-50 relative z-10"
            >
                <svg
                    class="w-16 h-16 text-sky-500 mb-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                    />
                </svg>
                <div class="font-mono text-sky-400 tracking-widest text-sm">
                    COMPRESSION CORE OFFLINE
                </div>
            </div>
        </div>

        <div class="panel terminal-panel relative">
            <h4>WAVEFORM FORMULA</h4>
            <div class="terminal flex items-center justify-center opacity-50">
                <div
                    class="text-sky-500/50 font-mono text-xs text-center border border-sky-500/20 p-4 rounded bg-sky-500/5"
                >
                    Φ(x,y,z) = ∫ ∇² AWAITING DATA...
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .demo-container {
        padding: 40px;
        color: #fff;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
        font-family: var(--font-mono, monospace);
    }

    .header h2 {
        margin: 0 0 10px 0;
        font-weight: bold;
        letter-spacing: 4px;
        color: #0ea5e9; /* sky-500 */
        text-shadow: 0 0 10px rgba(14, 165, 233, 0.4);
        font-family: var(--font-sans, sans-serif);
    }

    .header p {
        margin: 0;
        font-size: 0.9rem;
        color: #aaa;
        margin-bottom: 20px;
        max-width: 600px;
    }

    .workspace {
        display: flex;
        gap: 30px;
        flex: 1;
        align-items: stretch;
    }

    .panel {
        background: rgba(0, 5, 10, 0.8);
        border: 1px solid rgba(14, 165, 233, 0.3);
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.05);
        padding: 25px;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
    }

    .controls-panel {
        width: 300px;
    }

    .visual-panel {
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.5);
        flex: 1.5;
        border: 1px dashed rgba(14, 165, 233, 0.3);
    }

    .terminal-panel {
        flex: 1;
    }

    h3 {
        margin: 0 0 10px 0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #888;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 5px;
    }

    h4 {
        margin: 0 0 15px 0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #0ea5e9;
        background: rgba(14, 165, 233, 0.1);
        padding: 4px 10px;
        border-left: 3px solid #0ea5e9;
    }

    .desc {
        color: #bbb;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    .file-drop {
        background: rgba(0, 0, 0, 0.5);
        border: 1px dashed rgba(14, 165, 233, 0.5);
        color: #0ea5e9;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        letter-spacing: 1px;
        opacity: 0.5;
        margin-bottom: 15px;
    }

    .generate-btn {
        background: rgba(14, 165, 233, 0.2);
        color: #0ea5e9;
        font-weight: bold;
        text-align: center;
        letter-spacing: 1px;
        padding: 15px;
        border: 1px solid rgba(14, 165, 233, 0.5);
        cursor: not-allowed;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .coming-soon {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        color: #0ea5e9;
        font-size: 0.7rem;
        font-weight: bold;
        letter-spacing: 1px;
        opacity: 0.8;
    }

    .pulse {
        width: 6px;
        height: 6px;
        background-color: #0ea5e9;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.5;
            transform: scale(1.5);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }

    .stats {
        margin-top: auto;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .stat {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
    }

    .stat .label {
        color: #888;
    }
    .stat .val {
        color: #fff;
    }

    .terminal {
        flex: 1;
        background: #000;
        border: 1px solid #111;
    }

    @media (max-width: 1024px) {
        .workspace {
            flex-direction: column;
        }
        .controls-panel {
            width: 100%;
        }
        .visual-panel,
        .terminal-panel {
            min-height: 300px;
        }
    }
</style>
