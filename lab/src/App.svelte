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

    $: if (engine && playbackSpeed !== undefined) {
        engine.playbackSpeed = playbackSpeed;
    }

    onMount(async () => {
        // Load audit data
        const phiRes = await fetch("/data/phi_audit_frames.json");
        const phiData = await phiRes.json();

        const trajRes = await fetch("/data/trajectories_audit.json");
        const trajData = await trajRes.json();

        const resRes = await fetch("/data/resonance_audit.json");
        resonanceData = await resRes.json();

        totalFrames = phiData.metadata.frame_count;

        engine = new TopographyEngine(container, phiData, trajData);

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
            <p>OBNOVOVÁNÍ DAT AUDITU...</p>
        </div>
    {/if}

    <div class="canvas-container" bind:this={container}></div>
    <div class="overlay">
        <h1>SIMULAKRUM</h1>
        <p class="subtitle">Laboratoř Lineum Core | Pískoviště hypotéz</p>

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
            <div class="stat speed-control">
                <span class="label">RYCHLOST:</span>
                <span class="value">{playbackSpeed.toFixed(1)}x</span>
                <input
                    type="range"
                    min="0.1"
                    max="5.0"
                    step="0.1"
                    bind:value={playbackSpeed}
                />
            </div>

            {#if resonanceData}
                <ZetaScanner {frame} data={resonanceData} />
            {/if}

            {#if frame >= 4 && frame <= 15}
                <div class="event-marker">DETEKVÁN POČÁTEČNÍ RÁZ [§5.1]</div>
            {/if}
        </div>

        <div class="guide-panel">
            <h3>PRŮVODCE LABEM</h3>
            <div class="guide-item">
                <strong>Vlákna (Chapadla):</strong> Dráhy, po kterých se pohybují
                částice v poli. Sledují "jímky" (prohlubně) v paměti prostoru.
            </div>
            <div class="guide-item">
                <strong>Jímky v poli Φ:</strong> Tato 3D krajina ukazuje "hustotu"
                paměti. Línony se přirozeně stahují tam, kde je pole hlubší.
            </div>
            <div class="guide-item">
                <strong>Zeta Nuly:</strong> "Matematické uzly" vesmíru. Pokud se
                bílá ryska spektrálního skeneru trefí do modrých čar (Zeta), dochází
                k rezonanci a stabilizaci částic.
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
        top: 32px;
        left: 32px;
        pointer-events: none;
        z-index: 10;
        max-width: 400px;
    }

    .overlay * {
        pointer-events: all; /* Ensure slider etc. works */
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

    .stats-panel {
        margin-top: 40px;
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

    input[type="range"] {
        accent-color: #00ffff;
        cursor: pointer;
        width: 100px;
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
        z-index: 100;
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
        margin-top: 10px;
        background: rgba(255, 0, 0, 0.3);
        color: #ffaa00;
        padding: 5px;
        font-size: 0.7rem;
        border: 1px solid #ffaa00;
        text-align: center;
        animation: blink 1s infinite;
    }

    .guide-panel {
        margin-top: 40px;
        background: rgba(0, 40, 40, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 20px;
        backdrop-filter: blur(5px);
    }

    .guide-panel h3 {
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 0.9rem;
        letter-spacing: 0.1rem;
        border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        padding-bottom: 10px;
    }

    .guide-item {
        margin-bottom: 15px;
        font-size: 0.75rem;
        line-height: 1.4;
        color: #ddd;
    }

    .guide-item strong {
        color: #00ffff;
        display: block;
        margin-bottom: 4px;
    }

    @keyframes blink {
        50% {
            opacity: 0.5;
        }
    }
</style>
