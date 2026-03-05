<script>
    import { onMount, onDestroy } from "svelte";
    import { TopographyEngine } from "./lib/engines/TopographyEngine";
    import ZetaScanner from "./lib/components/ZetaScanner.svelte";
    import TidalAnalyzer from "./lib/components/TidalAnalyzer.svelte";
    import HypothesisTester from "./lib/components/HypothesisTester.svelte";
    import ExtremeSpikes from "./lib/components/ExtremeSpikes.svelte";
    import InteractiveChart from "./lib/components/InteractiveChart.svelte";
    import LplCompiler from "./lib/components/LplCompiler.svelte";
    import ValidationDashboard from "./lib/components/ValidationDashboard.svelte";
    import { t, locale } from "./lib/i18n";

    let container;
    let engine;
    let loading = true;
    let frame = 0;
    let totalFrames = 0;
    let playbackSpeed = 1.0;
    let manifest = [];
    let selectedRunId = "";
    let dataRoot = ""; // Path to current run data
    let resonanceData = null; // 🔬 Spectral data
    let metadata = null; // 📦 Audit metadata
    let harmonicData = null; // 🌀 Fibonacci & Golden Ratio
    let showSpiral = false;
    let manifestLoaded = false;

    // Global Modal State
    let maximizedChart = null; // { title, config }
    let error = null;

    const savedMode = localStorage.getItem("lab_main_mode") || "simulator";
    const savedTab = localStorage.getItem("lab_active_tab") || "stats";

    let mainMode = savedMode; // 'simulator' | 'lpl' | 'validation'
    let activeTab = savedTab;

    $: {
        localStorage.setItem("lab_main_mode", mainMode);
        if (activeTab) localStorage.setItem("lab_active_tab", activeTab);

        // 🛑 WebGL Optimization: Pause the 60fps render loop when simulator is hidden
        if (engine) {
            engine.isPaused = mainMode !== "simulator";
        }
    }

    $: if (engine && playbackSpeed !== undefined) {
        engine.playbackSpeed = playbackSpeed;
    }

    $: if (engine && showSpiral !== undefined) {
        engine.showSpiral = showSpiral;
        if (engine.goldenSpiral) engine.goldenSpiral.visible = showSpiral;
    }

    const toggleLanguage = () => {
        locale.set($locale === "cs" ? "en" : "cs");
    };

    $: if (mainMode === "simulator" && !manifestLoaded && !error) {
        manifestLoaded = true; // prevent re-fetching
        loading = true;
        fetch("/data/manifest.json")
            .then((res) => {
                if (!res.ok) throw new Error("Manifest not found");
                return res.json();
            })
            .then((data) => {
                manifest = data;
                if (manifest.length > 0) {
                    return loadRun(manifest[0].run_id);
                } else {
                    loading = false;
                }
            })
            .catch((e) => {
                console.error("Initialization failed:", e);
                error = e.message;
                loading = false;
            });
    }

    onMount(() => {
        if (mainMode !== "simulator") {
            loading = false;
        }
    });

    onDestroy(() => {
        if (engine) engine.dispose();
    });

    async function loadRun(runId) {
        loading = true;
        selectedRunId = runId;
        dataRoot = `/data/runs/${runId}`;
        const t_now = Date.now();

        try {
            if (engine) engine.dispose();

            const phiRes = await fetch(
                `${dataRoot}/phi_frames.json?t=${t_now}`,
            );
            const phiData = await phiRes.json();

            const trajRes = await fetch(
                `${dataRoot}/trajectories.json?t=${t_now}`,
            );
            const trajData = await trajRes.json();

            const resRes = await fetch(`${dataRoot}/resonance.json?t=${t_now}`);
            resonanceData = await resRes.json();

            const metaRes = await fetch(`${dataRoot}/metadata.json?t=${t_now}`);
            metadata = await metaRes.json();

            const harmRes = await fetch(
                `${dataRoot}/harmonics.json?t=${t_now}`,
            );
            harmonicData = await harmRes.json();

            totalFrames = phiData.metadata.frame_count;

            engine = new TopographyEngine(container, phiData, trajData);
            engine.harmonicData = harmonicData;
            engine.playbackSpeed = playbackSpeed;
            engine.onFrameUpdate = (newFrame) => (frame = newFrame);
            engine.animate();
        } catch (e) {
            console.error("Failed to load run:", runId, e);
            error = e.message || "Failed to load data";
        } finally {
            console.log("DEBUG: Setting loading to false in finally block");
            loading = false;
        }
    }
</script>

<main>
    {#if loading}
        <div class="loader">
            <div class="spinner"></div>
            <p>LOADING AUDIT DATA (JSON BIN)...</p>
        </div>
    {:else if error}
        <div class="loader">
            <div class="error-msg">
                <h3>INITIALIZATION FAILURE</h3>
                <p>{error}</p>
                <button on:click={() => window.location.reload()}>RETRY</button>
            </div>
        </div>
    {/if}

    <div
        class="canvas-container"
        style="display: {mainMode === 'simulator' ? 'block' : 'none'};"
        bind:this={container}
    ></div>

    <nav class="top-nav">
        <div class="nav-brand">
            <h1>SIMULACRUM</h1>
            <span class="subtitle">Lineum Lab | Hypothesis Sandbox</span>
        </div>

        <div class="nav-modes">
            <button
                class:active={mainMode === "simulator"}
                on:click={() => (mainMode = "simulator")}
            >
                3D Simulator
            </button>
            <button
                class:active={mainMode === "validation"}
                on:click={() => (mainMode = "validation")}
            >
                Validation Core
            </button>
            <button
                class:active={mainMode === "lpl"}
                on:click={() => (mainMode = "lpl")}
            >
                LPL Compiler
            </button>
        </div>

        <div class="header-controls">
            {#if mainMode === "simulator" && manifest.length > 0}
                <select
                    class="run-selector"
                    bind:value={selectedRunId}
                    on:change={(e) => loadRun(e.target.value)}
                >
                    {#each manifest as run}
                        <option value={run.run_id}>
                            {run.run_tag} ({run.timestamp})
                        </option>
                    {/each}
                </select>
            {/if}
        </div>
    </nav>

    {#if mainMode === "validation"}
        <div class="fullscreen-mode">
            <ValidationDashboard />
        </div>
    {:else if mainMode === "lpl"}
        <div class="fullscreen-mode">
            <LplCompiler />
        </div>
    {:else if mainMode === "simulator"}
        <div class="overlay">
            <div class="header-section">
                <div
                    class="discovery-headline"
                    class:prime={metadata?.pearson_r > 0.9}
                    class:tuning={metadata?.pearson_r > 0.5 &&
                        metadata?.pearson_r <= 0.9}
                >
                    <span class="status-icon"></span>
                    <span class="status-msg">
                        SYSTEM STATUS: BREAKTHROUGH DETECTED:
                        {metadata?.pearson_r > 0.9
                            ? "PRIME RESONANCE (1:1 ALIGNMENT)"
                            : metadata?.pearson_r > 0.5
                              ? "GEOMETRY TUNING"
                              : "STOCHASTIC NOISE (CHAOS)"}
                    </span>
                </div>
            </div>

            {#if frame >= 391}
                <div class="central-alert-system">
                    <div class="event-marker">
                        SYSTEM ALERT: LINON DETECTION [birth]
                    </div>
                </div>
            {/if}

            <div class="side-panel side-panel-left">
                <div class="panel-tabs">
                    <button
                        class="tab-btn"
                        class:active={activeTab === "stats"}
                        on:click={() => (activeTab = "stats")}
                    >
                        STATISTICS
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "scanner"}
                        on:click={() => (activeTab = "scanner")}
                    >
                        SCANNER
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "tidal"}
                        on:click={() => (activeTab = "tidal")}
                    >
                        Tidal
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "hypothesis"}
                        on:click={() => (activeTab = "hypothesis")}
                    >
                        HYPOTHESIS DISCOVERY
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "spikes"}
                        on:click={() => (activeTab = "spikes")}
                    >
                        Phenomena
                    </button>
                </div>

                <div class="tab-content">
                    {#if activeTab === "stats"}
                        <div class="stats-panel">
                            <div class="stat">
                                <span class="label">MODE:</span>
                                <span class="value"
                                    >FIELD Φ TOPOGRAPHY (3D)</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">METRIC:</span>
                                <span class="value"
                                    >z = field Φ height [AUDIT]</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">FRAME:</span>
                                <span class="value"
                                    >{frame} / {totalFrames}</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">SOURCE:</span>
                                <span class="value"
                                    >{metadata?.run_tag || "Audit"}</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">STATUS:</span>
                                <span class="value"
                                    >{frame >= (metadata?.birth_frame || 391)
                                        ? "LINON DETECTION"
                                        : "FIELD Φ INITIALIZATION"}</span
                                >
                                {#if metadata && frame < metadata.birth_frame}
                                    <button
                                        class="jump-btn"
                                        on:click={() =>
                                            engine.jumpToFrame(
                                                metadata.birth_frame,
                                            )}
                                    >
                                        JUMP TO BIRTH [{metadata.birth_frame}]
                                    </button>
                                {/if}
                            </div>
                            <div class="stat speed-control">
                                <span class="label">SPEED:</span>
                                <span class="value"
                                    >{playbackSpeed.toFixed(1)}x</span
                                >
                                <input
                                    type="range"
                                    min="0.1"
                                    max="5.0"
                                    step="0.1"
                                    bind:value={playbackSpeed}
                                />
                            </div>

                            <div class="stat toggle-control">
                                <span class="label">GOLDEN RATIO:</span>
                                <button
                                    class="toggle-btn {showSpiral
                                        ? 'active'
                                        : ''}"
                                    on:click={() => (showSpiral = !showSpiral)}
                                >
                                    {showSpiral ? "ON" : "OFF"}
                                </button>
                            </div>
                        </div>
                    {:else if activeTab === "scanner"}
                        <ZetaScanner
                            {frame}
                            data={resonanceData}
                            harmonics={harmonicData}
                        />
                    {:else if activeTab === "tidal"}
                        <TidalAnalyzer
                            {dataRoot}
                            on:maximize={(e) => (maximizedChart = e.detail)}
                        />
                    {:else if activeTab === "hypothesis"}
                        <HypothesisTester
                            {dataRoot}
                            on:maximize={(e) => (maximizedChart = e.detail)}
                        />
                    {:else if activeTab === "spikes"}
                        <ExtremeSpikes {engine} {frame} />
                    {/if}
                </div>
            </div>

            <div class="side-panel side-panel-right">
                <div class="guide-panel">
                    <h3>LAB GUIDE</h3>
                    <div class="guide-item">
                        <strong>What to watch:</strong>
                        Linons are energy cores that actively seek areas with the
                        highest Φ-field intensity. In this 3D visualization, they
                        move towards topography peaks.
                    </div>
                    <div class="guide-item">
                        <strong>Linons:</strong>
                        Paths and particles in the field. Until they reach critical
                        amplitude, they appear as ghosts. After birth (frame 391),
                        they begin to actively seek Φ-field local maxima.
                    </div>
                    <div class="guide-item">
                        <strong>Field Φ Topography:</strong>
                        This 3D landscape shows energy density. Linons naturally
                        gravitate towards peaks and ridges.
                    </div>
                    <div class="guide-item">
                        <strong>Zeta Zeros:</strong>
                        Mathematical nodes of the universe. If the scanner's white
                        needle hits the blue lines, resonance occurs.
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <div class="sandbox-disclaimer">
        <div class="disclaimer-header">
            <span class="warning-icon">!</span>
            <strong>PROCEDURAL WARNING: SANDBOX</strong>
        </div>
        <p>
            The Laboratory is a sandbox for visualizing preliminary results of
            partially verified hypotheses (running on real audit data). It is
            for exploratory verification of phenomena that must be subsequently
            confirmed via official whitepaper outputs.
        </p>
    </div>

    {#if maximizedChart}
        <div
            class="global-modal-overlay"
            on:click|self={() => (maximizedChart = null)}
            role="dialog"
            aria-modal="true"
            on:keydown={(e) => e.key === "Escape" && (maximizedChart = null)}
            tabindex="-1"
        >
            <div class="modal-content">
                <div class="modal-header">
                    <h3>{maximizedChart.title}</h3>
                    <button
                        type="button"
                        class="close-btn"
                        on:click={() => (maximizedChart = null)}
                        aria-label="Close">&times;</button
                    >
                </div>
                <div class="modal-body">
                    {#key maximizedChart}
                        <InteractiveChart
                            title={maximizedChart.title}
                            config={maximizedChart.config}
                            showMax={false}
                        />
                    {/key}
                </div>
            </div>
        </div>
    {/if}
</main>

<svelte:window
    on:keydown={(e) => e.key === "Escape" && (maximizedChart = null)}
/>

<style>
    main {
        width: 100vw;
        height: 100vh;
        background: #050505;
        position: relative;
        overflow: hidden;
    }

    .canvas-container {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
        pointer-events: none;
        transition:
            opacity 0.5s ease,
            filter 0.5s ease;
    }

    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(0, 10, 15, 0.85);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(0, 255, 255, 0.15);
        padding: 12px 30px;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        box-sizing: border-box;
        z-index: 200;
        pointer-events: auto;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }

    .nav-brand {
        display: flex;
        flex-direction: column;
    }

    .nav-brand h1 {
        margin: 0;
        font-size: 1.4rem;
        letter-spacing: 0.4rem;
        color: #fff;
        text-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        font-weight: 300;
    }

    .nav-brand .subtitle {
        font-size: 0.65rem;
        color: #00ffff;
        opacity: 0.6;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 2px;
    }

    .nav-modes {
        display: flex;
        gap: 10px;
        flex: 1;
        justify-content: center;
    }

    .nav-modes button {
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.75rem;
        font-family: inherit;
        text-transform: uppercase;
        letter-spacing: 2px;
        cursor: pointer;
        padding: 10px 20px;
        transition: all 0.3s ease;
        border-bottom: 2px solid transparent;
        border-radius: 4px 4px 0 0;
    }

    .nav-modes button:hover {
        color: #fff;
        background: rgba(0, 255, 255, 0.05);
    }

    .nav-modes button.active {
        color: #00ffff;
        border-bottom: 2px solid #00ffff;
        background: radial-gradient(
            ellipse at bottom,
            rgba(0, 255, 255, 0.15) 0%,
            transparent 70%
        );
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }

    .fullscreen-mode {
        position: absolute;
        top: 70px;
        left: 0;
        width: 100vw;
        height: calc(100vh - 70px);
        background: #050505;
        pointer-events: auto;
        overflow-y: auto;
        overflow-x: hidden;
        z-index: 100;
        padding-bottom: 80px; /* Space for the fixed disclaimer footer */
        box-sizing: border-box;
    }

    .overlay {
        position: absolute;
        top: 70px;
        left: 32px;
        right: 32px;
        bottom: 80px; /* Leave space for footer */
        pointer-events: none;
        z-index: 100;
        display: grid;
        grid-template-columns: 400px 1fr 400px;
        grid-template-rows: auto 60px 1fr;
        grid-template-areas:
            "header header header"
            "alert alert alert"
            "left . right";
        gap: 20px;
        box-sizing: border-box;
        overflow: hidden;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .header-section {
        grid-area: header;
        display: flex;
        flex-direction: column;
        gap: 10px;
        pointer-events: all;
    }

    .header-controls {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .run-selector {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
        color: #00ffff;
        font-size: 0.7rem;
        padding: 4px 8px;
        outline: none;
        cursor: pointer;
    }

    .run-selector option {
        background: #050505;
        color: #fff;
    }

    .central-alert-system {
        grid-area: alert;
        display: flex;
        justify-content: center;
        align-items: center;
        pointer-events: none;
        min-height: 50px;
    }

    .side-panel {
        pointer-events: all;
        display: flex;
        flex-direction: column;
        gap: 20px;
        min-height: 0; /* Crucial for scrolling inside grid/flex */
        height: 100%;
    }

    .side-panel-left {
        grid-area: left;
    }

    .side-panel-right {
        grid-area: right;
    }

    .discovery-headline {
        background: rgba(0, 255, 255, 0.05);
        border-left: 4px solid rgba(0, 255, 255, 0.3);
        padding: 10px 15px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.5s ease;
        max-width: 400px;
    }

    .discovery-headline.prime {
        background: rgba(0, 255, 0, 0.1);
        border-color: #00ff00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
    }

    .discovery-headline.tuning {
        background: rgba(255, 170, 0, 0.1);
        border-color: #ffaa00;
    }

    .status-icon {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00ffff;
        box-shadow: 0 0 8px #00ffff;
        animation: blink 2s infinite;
    }

    .prime .status-icon {
        background: #00ff00;
        box-shadow: 0 0 10px #00ff00;
    }

    .tuning .status-icon {
        background: #ffaa00;
        box-shadow: 0 0 10px #ffaa00;
    }

    .status-msg {
        font-size: 0.8rem;
        font-weight: bold;
        letter-spacing: 1px;
        color: #fff;
        text-transform: uppercase;
    }

    /* Provance Badge */
    :global(.data-badge) {
        display: inline-block;
        font-size: 0.55rem;
        background: rgba(0, 255, 255, 0.2);
        color: #00ffff;
        padding: 1px 4px;
        border-radius: 2px;
        margin-left: 8px;
        vertical-align: middle;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    @keyframes blink {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.3;
        }
    }

    @keyframes blink {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.3;
        }
    }

    /* Tabs Styling */
    .panel-tabs {
        display: flex;
        gap: 2px;
        background: rgba(0, 255, 255, 0.1);
        padding: 2px;
    }

    .tab-btn {
        flex: 1;
        background: transparent;
        border: none;
        color: rgba(0, 255, 255, 0.5);
        padding: 8px;
        cursor: pointer;
        font-size: 0.7rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.2s;
    }

    .tab-btn.active {
        background: rgba(0, 255, 255, 0.2);
        color: #00ffff;
        box-shadow: inset 0 -2px 0 #00ffff;
    }

    /* Sandbox Disclaimer Styling */
    .sandbox-disclaimer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(15, 10, 0, 0.85);
        border-top: 1px solid rgba(255, 170, 0, 0.4);
        padding: 8px 30px;
        backdrop-filter: blur(12px);
        box-sizing: border-box;
        pointer-events: all;
        z-index: 300;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5);
    }

    .disclaimer-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
        color: #ffaa00;
    }

    .disclaimer-header strong {
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .sandbox-disclaimer p {
        margin: 0;
        font-size: 0.65rem;
        line-height: 1.2;
        color: #eee;
        opacity: 0.8;
        font-style: italic;
        max-width: 800px;
    }

    /* Responsive Media Queries */
    @media (max-width: 1024px) {
        .overlay {
            grid-template-columns: 1fr;
            grid-template-rows: auto auto 1fr auto;
            grid-template-areas:
                "header"
                "alert"
                "left"
                "right";
            left: 10px;
            right: 10px;
            bottom: 60px; /* Room for footer */
            top: 120px; /* Room for wrapped nav */
            overflow-y: auto;
            pointer-events: all; /* Needed for scrolling the stacked grid */
        }

        .side-panel-right {
            display: none; /* Hide guide on mobile to save space */
        }

        .top-nav {
            flex-direction: column;
            padding: 10px;
            gap: 10px;
        }

        .nav-brand {
            align-items: center;
        }

        .nav-brand h1 {
            font-size: 1.2rem;
            letter-spacing: 0.2rem;
        }

        .nav-modes {
            width: 100%;
            justify-content: space-around;
        }

        .nav-modes button {
            padding: 8px 10px;
            font-size: 0.65rem;
            letter-spacing: 1px;
        }

        .sandbox-disclaimer {
            flex-direction: column;
            gap: 4px;
            padding: 6px 15px;
            text-align: center;
        }

        .sandbox-disclaimer p {
            font-size: 0.55rem;
        }

        .fullscreen-mode {
            top: 120px;
            height: calc(100vh - 120px);
            padding-bottom: 110px; /* Taller wrapped footer on mobile */
            box-sizing: border-box;
        }
    }

    .tab-content {
        flex: 1;
        overflow-y: auto;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        scrollbar-width: thin;
        scrollbar-color: rgba(0, 255, 255, 0.3) transparent;
        border-bottom: 1px solid rgba(0, 255, 255, 0.1);
    }

    .tab-content::-webkit-scrollbar {
        width: 6px;
    }

    .tab-content::-webkit-scrollbar-thumb {
        background: rgba(0, 255, 255, 0.3);
        border-radius: 3px;
    }

    .stats-panel {
        background: rgba(0, 0, 0, 0.5);
        border-left: 2px solid #00ffff;
        padding: 16px;
        backdrop-filter: blur(10px);
    }

    .stat {
        margin-bottom: 8px;
        display: flex;
        gap: 16px;
        align-items: center;
    }

    .label {
        font-size: 0.7rem;
        color: #888;
        width: 80px;
    }

    .value {
        font-size: 0.8rem;
        color: #fff;
        font-family: monospace;
    }

    .jump-btn {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid #00ffff;
        color: #00ffff;
        font-size: 0.6rem;
        padding: 4px 8px;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s;
        margin-left: 8px;
    }

    .jump-btn:hover {
        background: rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }

    input[type="range"] {
        accent-color: #00ffff;
        cursor: pointer;
        width: 100px;
    }

    .speed-control {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }

    .toggle-btn {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.4);
        color: #00ffff;
        padding: 2px 10px;
        cursor: pointer;
        font-size: 0.6rem;
        transition: all 0.2s;
    }

    .toggle-btn.active {
        background: #00ffff;
        color: #000;
        box-shadow: 0 0 10px #00ffff;
    }

    /* Loader Styles */
    .loader {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #050505;
        z-index: 200;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 2px solid rgba(0, 255, 255, 0.1);
        border-top-color: #00ffff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 24px;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .loader p {
        font-size: 0.7rem;
        letter-spacing: 0.3rem;
        color: #00ffff;
        opacity: 0.5;
    }

    .error-msg {
        text-align: center;
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid #ff0000;
        padding: 40px;
        color: #ff0000;
        max-width: 400px;
    }

    .error-msg h3 {
        margin-top: 0;
        letter-spacing: 4px;
        font-size: 1.2rem;
    }

    .error-msg button {
        margin-top: 20px;
        background: #ff0000;
        color: #fff;
        border: none;
        padding: 8px 16px;
        cursor: pointer;
        font-weight: bold;
    }

    .event-marker {
        background: rgba(255, 170, 0, 0.3);
        color: #fff;
        padding: 6px 16px;
        font-size: 0.7rem;
        font-weight: bold;
        border: 2px solid #ffaa00;
        text-align: center;
        animation:
            blink 1s infinite,
            pulse-alert 2s infinite;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(255, 170, 0, 0.4);
        pointer-events: all;
        letter-spacing: 2px;
    }

    @keyframes pulse-alert {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }

    .guide-panel {
        background: rgba(0, 40, 40, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.3);
        padding: 24px;
        backdrop-filter: blur(5px);
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
    }

    .guide-panel h3 {
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 0.9rem;
        letter-spacing: 0.2rem;
        border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        padding-bottom: 15px;
        text-transform: uppercase;
        color: #00ffff;
    }

    .guide-item {
        margin-bottom: 20px;
        font-size: 0.75rem;
        line-height: 1.6;
        color: #eee;
    }

    .guide-item strong {
        color: #00ffff;
        display: block;
        margin-bottom: 6px;
        letter-spacing: 1px;
    }

    @keyframes blink {
        50% {
            opacity: 0.6;
        }
    }

    /* Global Modal Overlay */
    .global-modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(20px);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 60px;
        pointer-events: all;
    }

    .global-modal-overlay .modal-content {
        width: 100%;
        max-width: 1300px;
        height: 100%;
        max-height: 85vh;
        background: #050505;
        border: 1px solid #00ffff;
        display: flex;
        flex-direction: column;
        padding: 30px;
        box-shadow: 0 0 100px rgba(0, 255, 255, 0.3);
        position: relative;
    }

    .global-modal-overlay .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 2px solid rgba(0, 255, 255, 0.2);
        padding-bottom: 15px;
    }

    .global-modal-overlay .modal-header h3 {
        font-size: 1.2rem;
        letter-spacing: 4px;
        color: #00ffff;
        margin: 0;
        border: none;
    }

    .global-modal-overlay .modal-body {
        flex: 1;
        min-height: 0;
    }

    .global-modal-overlay .close-btn {
        background: transparent;
        border: none;
        color: #00ffff;
        font-size: 2.5rem;
        cursor: pointer;
        line-height: 1;
        transition: color 0.2s;
    }

    .global-modal-overlay .close-btn:hover {
        color: #fff;
    }
</style>
