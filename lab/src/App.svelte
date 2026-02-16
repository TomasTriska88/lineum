<script>
    import { onMount } from "svelte";
    import { TopographyEngine } from "./lib/engines/TopographyEngine";
    import ZetaScanner from "./lib/components/ZetaScanner.svelte";

    let container;
    let engine;
    let loading = true;
    let frame = 0;
    let totalFrames = 0;
    let playbackSpeed = 1.0;
    let resonanceData = null; // 🔬 Spectral data
    let metadata = null; // 📦 Audit metadata
    let harmonicData = null; // 🌀 Fibonacci & Golden Ratio
    let showSpiral = false;
    let activeTab = "scanner"; // "scanner" | "stats"

    $: if (engine && playbackSpeed !== undefined) {
        engine.playbackSpeed = playbackSpeed;
    }

    $: if (engine && showSpiral !== undefined) {
        engine.showSpiral = showSpiral;
        if (engine.goldenSpiral) engine.goldenSpiral.visible = showSpiral;
    }

    onMount(async () => {
        // Load audit data with cache-busting
        const t = Date.now();
        const phiRes = await fetch(`/data/phi_frames.json?t=${t}`);
        const phiData = await phiRes.json();

        const trajRes = await fetch(`/data/trajectories.json?t=${t}`);
        const trajData = await trajRes.json();

        const resRes = await fetch(`/data/resonance.json?t=${t}`);
        resonanceData = await resRes.json();

        const metaRes = await fetch(`/data/metadata.json?t=${t}`);
        metadata = await metaRes.json();

        const harmRes = await fetch(`/data/harmonics.json?t=${t}`);
        harmonicData = await harmRes.json();

        totalFrames = phiData.metadata.frame_count;

        engine = new TopographyEngine(container, phiData, trajData);
        engine.harmonicData = harmonicData;
        engine.playbackSpeed = playbackSpeed;

        // 📡 Hook into engine's frame updates instead of polling
        engine.onFrameUpdate = (newFrame) => {
            frame = newFrame;
        };

        engine.animate();

        loading = false;

        return () => {
            engine.dispose();
        };
    });
</script>

<main>
    {#if loading}
        <div class="loader">
            <div class="spinner"></div>
            <p>NAČÍTÁNÍ AUDITNÍCH DAT (JSON BIN)...</p>
        </div>
    {/if}

    <div class="canvas-container" bind:this={container}></div>
    <div class="overlay">
        <div class="header-section">
            <h1>SIMULAKRUM</h1>
            <p class="subtitle">Laboratoř Lineum Core | Pískoviště hypotéz</p>
        </div>

        {#if frame >= 391}
            <div class="central-alert-system">
                <div class="event-marker">
                    SYSTEM ALERT: DETEKCE LINONŮ [zrození]
                </div>
            </div>
        {/if}

        <div class="side-panel side-panel-left">
            <div class="panel-tabs">
                <button
                    class="tab-btn"
                    class:active={activeTab === "scanner"}
                    on:click={() => (activeTab = "scanner")}
                >
                    SKENER
                </button>
                <button
                    class="tab-btn"
                    class:active={activeTab === "stats"}
                    on:click={() => (activeTab = "stats")}
                >
                    STATISTIKY
                </button>
            </div>

            <div class="tab-content">
                {#if activeTab === "scanner"}
                    <ZetaScanner
                        {frame}
                        data={resonanceData}
                        harmonics={harmonicData}
                    />
                {:else}
                    <div class="stats-panel">
                        <div class="stat">
                            <span class="label">REŽIM:</span>
                            <span class="value">TOPOGRAFIE POLE Φ (3D)</span>
                        </div>
                        <div class="stat">
                            <span class="label">METRIKA:</span>
                            <span class="value">z = výška pole Φ [AUDIT]</span>
                        </div>
                        <div class="stat">
                            <span class="label">SNÍMEK:</span>
                            <span class="value">{frame} / {totalFrames}</span>
                        </div>
                        <div class="stat">
                            <span class="label">ZDROJ:</span>
                            <span class="value"
                                >{metadata?.run_tag || "Audit"}</span
                            >
                        </div>
                        <div class="stat">
                            <span class="label">STAV:</span>
                            <span class="value"
                                >{frame >= (metadata?.birth_frame || 391)
                                    ? "DETEKCE LINONŮ"
                                    : "ZÁBĚH POLE Φ"}</span
                            >
                            {#if metadata && frame < metadata.birth_frame}
                                <button
                                    class="jump-btn"
                                    on:click={() =>
                                        engine.jumpToFrame(
                                            metadata.birth_frame,
                                        )}
                                >
                                    SKOČIT NA ZROZENÍ [{metadata.birth_frame}]
                                </button>
                            {/if}
                        </div>
                        <div class="stat speed-control">
                            <span class="label">RYCHLOST:</span>
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
                            <span class="label">ZLATÝ ŘEZ:</span>
                            <button
                                class="toggle-btn {showSpiral ? 'active' : ''}"
                                on:click={() => (showSpiral = !showSpiral)}
                            >
                                {showSpiral ? "ON" : "OFF"}
                            </button>
                        </div>
                    </div>
                {/if}
            </div>
        </div>

        <div class="side-panel side-panel-right">
            <div class="guide-panel">
                <h3>PRŮVODCE LABEM</h3>
                <div class="guide-item">
                    <strong>Co sledovat:</strong> Linony jsou energetická jádra,
                    která se aktivně snaží najít oblasti s nejvyšší intenzitou pole
                    Φ. V této 3D vizualizaci se pohybují k "vrcholům" topografie.
                </div>
                <div class="guide-item">
                    <strong>Linony:</strong> Dráhy a částice v poli. Dokud nedosáhnou
                    kritické amplitudy, vidíte je jako "duchy". Po zrození (snímek
                    391) aktivně vyhledávají maxima pole Φ.
                </div>
                <div class="guide-item">
                    <strong>Topografie pole Φ:</strong> Tato 3D krajina ukazuje energetickou
                    hustotu. Linony se přirozeně stahují na vrcholky a hřebeny.
                </div>
                <div class="guide-item">
                    <strong>Zeta Nuly:</strong> "Matematické uzly" vesmíru. Pokud
                    se bílá ryska skeneru trefí do modrých čar, dochází k rezonanci.
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
