<script>
    import { onMount } from "svelte";
    import { TopographyEngine } from "./lib/engines/TopographyEngine";
    import ZetaScanner from "./lib/components/ZetaScanner.svelte";
    import TidalAnalyzer from "./lib/components/TidalAnalyzer.svelte";
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
    let activeTab = "stats"; // "scanner" | "stats" | "tidal"

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

    onMount(async () => {
        const res = await fetch("/data/manifest.json");
        manifest = await res.json();
        if (manifest.length > 0) {
            // Default to the first (latest) run in manifest
            await loadRun(manifest[0].run_id);
        }
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

            loading = false;
        } catch (e) {
            console.error("Failed to load run:", runId, e);
        }
    }
</script>

<main>
    {#if loading}
        <div class="loader">
            <div class="spinner"></div>
            <p>{$t("loading")}</p>
        </div>
    {/if}

    <div class="canvas-container" bind:this={container}></div>
    <div class="overlay">
        <div class="header-section">
            <div class="header-top">
                <h1>{$t("simulakrum")}</h1>
                <div class="header-controls">
                    {#if manifest.length > 0}
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
                    <button class="lang-btn" on:click={toggleLanguage}>
                        {$locale === "cs" ? "EN" : "CZ"}
                    </button>
                </div>
            </div>
            <p class="subtitle">{$t("sub_title")}</p>
        </div>

        {#if frame >= 391}
            <div class="central-alert-system">
                <div class="event-marker">{$t("alert_birth")}</div>
            </div>
        {/if}

        <div class="side-panel side-panel-left">
            <div class="panel-tabs">
                <button
                    class="tab-btn"
                    class:active={activeTab === "stats"}
                    on:click={() => (activeTab = "stats")}
                >
                    {$t("tab_stats")}
                </button>
                <button
                    class="tab-btn"
                    class:active={activeTab === "scanner"}
                    on:click={() => (activeTab = "scanner")}
                >
                    {$t("tab_scanner")}
                </button>
                <button
                    class="tab-btn"
                    class:active={activeTab === "tidal"}
                    on:click={() => (activeTab = "tidal")}
                >
                    Tidal
                </button>
            </div>

            <div class="tab-content">
                {#if activeTab === "stats"}
                    <div class="stats-panel">
                        <div class="stat">
                            <span class="label">{$t("label_mode")}</span>
                            <span class="value">{$t("val_mode")}</span>
                        </div>
                        <div class="stat">
                            <span class="label">{$t("label_metric")}</span>
                            <span class="value">{$t("val_metric")}</span>
                        </div>
                        <div class="stat">
                            <span class="label">{$t("label_frame")}</span>
                            <span class="value">{frame} / {totalFrames}</span>
                        </div>
                        <div class="stat">
                            <span class="label">{$t("label_source")}</span>
                            <span class="value"
                                >{metadata?.run_tag || "Audit"}</span
                            >
                        </div>
                        <div class="stat">
                            <span class="label">{$t("label_status")}</span>
                            <span class="value"
                                >{frame >= (metadata?.birth_frame || 391)
                                    ? $t("status_born")
                                    : $t("status_init")}</span
                            >
                            {#if metadata && frame < metadata.birth_frame}
                                <button
                                    class="jump-btn"
                                    on:click={() =>
                                        engine.jumpToFrame(
                                            metadata.birth_frame,
                                        )}
                                >
                                    {$t("btn_jump")} [{metadata.birth_frame}]
                                </button>
                            {/if}
                        </div>
                        <div class="stat speed-control">
                            <span class="label">{$t("label_speed")}</span>
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
                            <span class="label">{$t("label_phi")}</span>
                            <button
                                class="toggle-btn {showSpiral ? 'active' : ''}"
                                on:click={() => (showSpiral = !showSpiral)}
                            >
                                {showSpiral ? $t("on") : $t("off")}
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
                    <TidalAnalyzer {dataRoot} />
                {/if}
            </div>
        </div>

        <div class="side-panel side-panel-right">
            <div class="guide-panel">
                <h3>{$t("guide_title")}</h3>
                <div class="guide-item">
                    <strong>{$t("guide_watch_title")}</strong>
                    {$t("guide_watch_desc")}
                </div>
                <div class="guide-item">
                    <strong>{$t("guide_linons_title")}</strong>
                    {$t("guide_linons_desc")}
                </div>
                <div class="guide-item">
                    <strong>{$t("guide_topo_title")}</strong>
                    {$t("guide_topo_desc")}
                </div>
                <div class="guide-item">
                    <strong>{$t("guide_zeta_title")}</strong>
                    {$t("guide_zeta_desc")}
                </div>
                <div class="guide-item">
                    <strong>{$t("guide_grid_title")}</strong>
                    {$t("guide_grid_desc")}
                </div>
            </div>
        </div>
    </div>
</main>

<style>
    main {
        width: 100vw;
        height: 100vh;
        background: #050505;
        position: relative;
        overflow: hidden;
    }

    .canvas-container {
        width: 100%;
        height: 100%;
    }

    .overlay {
        position: absolute;
        inset: 32px;
        pointer-events: none;
        z-index: 100;
        display: grid;
        grid-template-columns: 400px 1fr 400px;
        grid-template-rows: auto 1fr;
        gap: 20px;
    }

    .header-section {
        grid-column: 1 / 4;
        pointer-events: all;
    }

    .header-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
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

    .lang-btn {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.4);
        color: #00ffff;
        padding: 4px 10px;
        cursor: pointer;
        font-size: 0.7rem;
        font-weight: bold;
        transition: all 0.2s;
    }

    .lang-btn:hover {
        background: rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }

    .central-alert-system {
        grid-column: 2;
        grid-row: 1;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        pointer-events: none;
    }

    .side-panel {
        pointer-events: all;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .side-panel-left {
        grid-column: 1;
        grid-row: 2;
    }

    .side-panel-right {
        grid-column: 3;
        grid-row: 2;
    }

    h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 200;
        letter-spacing: 0.5rem;
        color: #fff;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
    }

    .subtitle {
        margin: 0;
        font-size: 0.8rem;
        letter-spacing: 0.1rem;
        color: #00ffff;
        opacity: 0.7;
        margin-top: 8px;
        text-transform: uppercase;
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
        transition: all 0.2s;
    }

    .tab-btn.active {
        background: rgba(0, 255, 255, 0.2);
        color: #00ffff;
        box-shadow: inset 0 -2px 0 #00ffff;
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

    .event-marker {
        background: rgba(255, 170, 0, 0.3);
        color: #fff;
        padding: 10px 20px;
        font-size: 0.8rem;
        font-weight: bold;
        border: 2px solid #ffaa00;
        text-align: center;
        animation:
            blink 1s infinite,
            pulse-alert 2s infinite;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(255, 170, 0, 0.4);
        pointer-events: all;
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
</style>
