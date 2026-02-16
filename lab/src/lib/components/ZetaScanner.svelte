<script>
    export let frame = 0;
    export let data = null;
    export let harmonics = null;

    let zetaZeros = [14.13, 21.02, 25.01, 30.42, 32.93];
    let evolution = [];

    $: if (data) {
        zetaZeros = data.zeta_zeros;
        evolution = data.phi_evolution;
    }

    // Normalized current value
    $: currentVal = evolution[frame] || 0;

    // Per-frame harmonic data
    $: h_score = harmonics?.frame_harmonics?.[frame] || 0.5;
    $: c_score = harmonics?.frame_correlation?.[frame] || 0.5;

    // 📈 Cumulative Statistics (History up to current frame)
    $: historyHarmonics = harmonics?.frame_harmonics?.slice(0, frame + 1) || [];
    $: historyCorrelation =
        harmonics?.frame_correlation?.slice(0, frame + 1) || [];

    $: avgHarmony =
        historyHarmonics.length > 0
            ? historyHarmonics.reduce((a, b) => a + b, 0) /
              historyHarmonics.length
            : 0.5;
    $: avgCorrelation =
        historyCorrelation.length > 0
            ? historyCorrelation.reduce((a, b) => a + b, 0) /
              historyCorrelation.length
            : 0.5;

    $: harmonyPercent = h_score * 100;
    $: harmonyStatus =
        harmonyPercent > 80
            ? "ABSOLUTNÍ"
            : harmonyPercent > 50
              ? "VYSOKÁ"
              : "LADĚNÍ...";

    $: harmonyInsight =
        harmonyPercent > 80
            ? "Dosáhli jsme matematické dokonalosti Zlatého řezu."
            : harmonyPercent > 50
              ? "Strukturální řád se plynule upevňuje."
              : "Probíhá formování fundamentální geometrie.";

    $: correlationPercent = c_score * 100;

    // 🌌 Revolutionary Logic: Sliding Window for "Discovery"
    // We look at the last 15 frames. If they average > 80%, it's a fundamental discovery.
    $: recentCorrelation = historyCorrelation.slice(-15);
    $: windowAvg =
        recentCorrelation.length > 0
            ? recentCorrelation.reduce((a, b) => a + b, 0) /
              recentCorrelation.length
            : 0;

    $: isFundamentalDiscovery = windowAvg > 0.8 && frame > 10;

    $: discoveryStatus = isFundamentalDiscovery
        ? "ZÁSADNÍ OBJEV"
        : correlationPercent > 60
          ? "Vysoká shoda"
          : "Hledání řádu";

    $: cosmicConclusion = isFundamentalDiscovery
        ? "🌟 POTVRZENO: Tato konfigurace vykazuje geometrickou shodu s fundamentálním kódem našeho vesmíru."
        : avgCorrelation > 0.6
          ? "Systém vykazuje známky rezonance s Riemannovými nulami."
          : "Probíhá ladění frekvencí pro dosažení kosmické shody.";

    let showInfo = false;
</script>

<div class="zeta-scanner">
    <div class="scanner-header">
        <div class="scanner-title">SKENER ZETA REZONANCE [§4.3]</div>
        <button
            type="button"
            class="info-toggle"
            on:click|stopPropagation={() => (showInfo = !showInfo)}
        >
            {showInfo ? "×" : "i"}
        </button>
    </div>

    <!-- 🌐 Layman Insights: Now permanent and condensed -->
    <div class="permanent-insights">
        <div class="insight-item">
            <span class="label">STAV Φ:</span>
            <span
                class="value"
                style="color: {harmonyPercent > 30 ? '#00ffff' : '#ffaa00'}"
            >
                {harmonyStatus} ({harmonyPercent.toFixed(1)}%)
            </span>
            <div class="sub-label">{harmonyInsight}</div>
            <div class="cumulative-label">
                Celkový průměr: {(avgHarmony * 100).toFixed(1)}%
            </div>
        </div>
        <div class="insight-item">
            <span class="label">KORELACE:</span>
            <span class="value" class:discovery={isFundamentalDiscovery}>
                {discoveryStatus} ({correlationPercent.toFixed(1)}%)
            </span>
            <div
                class="sub-label conclusion-text"
                class:revolutionary={isFundamentalDiscovery}
            >
                {cosmicConclusion}
            </div>
            <div class="cumulative-label">
                Stabilita shody (posledních 15 sn.): {(windowAvg * 100).toFixed(
                    1,
                )}%
            </div>
        </div>
    </div>

    {#if showInfo}
        <div class="layman-info">
            <p><strong>CO TO ZNAMENÁ?</strong></p>
            <p>
                Tato sekce měří, jak moc se "tep" vašich linonů shoduje s rytmem
                našeho vesmíru.
            </p>
            <p>
                <em>Zlatý řez (1.618...):</em> Stabilita v poli Φ často směřuje k
                Fibonacciho poměrům.
            </p>
        </div>
    {/if}

    <div class="spectral-display">
        <div class="axis-label">INTENZITA REZONANCE [NORMOVÁNO]</div>

        <div class="spectrum-container">
            <!-- 🪐 Zeta Zero Background Markers -->
            {#each zetaZeros as zero}
                <div class="zeta-line" style="left: {(zero / 40) * 100}%">
                    <span class="zeta-label">ζ={zero.toFixed(2)}</span>
                </div>
            {/each}

            <!-- 🧪 Audit Data Resonance Needle -->
            <div
                class="resonance-needle"
                style="left: {(currentVal / 40) * 100}%"
            >
                <div class="needle-glow"></div>
                <div class="needle-label">FREKVENCE LINONŮ (f₀)</div>
            </div>
        </div>
    </div>

    <div class="metrics-row">
        <div class="metric-item">
            HARMONIE Φ: <span class="highlight"
                >{harmonyPercent.toFixed(2)} %</span
            >
        </div>
        <div class="metric-item">
            KORELACE S NAŠÍM VESMÍREM: <span class="highlight"
                >{correlationPercent.toFixed(2)} %</span
            >
        </div>
    </div>
</div>

<style>
    .zeta-scanner {
        margin-top: 15px;
        padding: 10px;
        border: 1px solid rgba(0, 255, 255, 0.3);
        background: rgba(0, 20, 20, 0.5);
        color: #00ffff;
        font-family: "Courier New", Courier, monospace;
        font-size: 0.7rem;
        position: relative; /* ⚓ Base for absolute children */
    }

    .scanner-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .scanner-title {
        font-weight: bold;
        letter-spacing: 1px;
    }

    .info-toggle {
        background: rgba(0, 255, 255, 0.2);
        border: 1px solid #00ffff;
        color: #00ffff;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 0.7rem;
        font-weight: bold;
        transition: all 0.2s;
        z-index: 110;
        pointer-events: all;
    }

    .info-toggle:hover {
        background: #00ffff;
        color: #000;
    }

    .layman-info {
        position: absolute;
        top: 35px;
        left: 10px;
        right: 10px;
        background: rgba(0, 20, 20, 0.95);
        border: 1px solid rgba(0, 255, 255, 0.8);
        padding: 12px;
        font-size: 0.65rem;
        line-height: 1.3;
        z-index: 105;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(5px);
    }

    .layman-info p {
        margin: 5px 0;
    }

    .permanent-insights {
        display: flex;
        gap: 10px;
        margin-bottom: 12px;
        background: rgba(0, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.1);
        padding: 8px;
    }

    .insight-item {
        flex: 1;
        font-size: 0.65rem;
    }

    .insight-item .label {
        opacity: 0.6;
        margin-right: 5px;
    }

    .insight-item .value {
        font-weight: bold;
    }

    .insight-item .sub-label {
        font-size: 0.55rem;
        opacity: 0.8;
        margin-top: 2px;
        font-style: italic;
        transition: all 0.5s ease;
    }

    .conclusion-text.revolutionary {
        color: #fff;
        text-shadow: 0 0 10px rgba(0, 255, 255, 1);
        font-weight: bold;
        opacity: 1;
        font-style: normal;
        background: rgba(0, 255, 255, 0.15);
        padding: 4px 6px;
        border-radius: 4px;
        font-size: 0.65rem;
        border: 1px solid rgba(0, 255, 255, 0.3);
        margin-top: 5px;
    }

    .value.discovery {
        color: #fff;
        text-shadow: 0 0 5px #ffaa00;
        animation: pulse-discovery 2s infinite;
    }

    @keyframes pulse-discovery {
        0% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
        100% {
            opacity: 1;
        }
    }

    .cumulative-label {
        font-size: 0.5rem;
        opacity: 0.5;
        margin-top: 4px;
        border-top: 1px dotted rgba(0, 255, 255, 0.2);
        padding-top: 2px;
    }

    .spectral-display {
        position: relative;
        height: 60px;
        border-bottom: 1px solid #00ffff;
        margin-bottom: 15px;
    }

    .axis-label {
        font-size: 0.5rem;
        opacity: 0.6;
        position: absolute;
        top: -12px;
    }

    .spectrum-container {
        position: relative;
        width: 100%;
        height: 100%;
        overflow: visible;
    }

    .zeta-line {
        position: absolute;
        bottom: 0;
        width: 1px;
        height: 100%;
        background: rgba(0, 255, 255, 0.2);
        transition: left 0.3s;
    }

    .zeta-label {
        position: absolute;
        top: -15px;
        left: -10px;
        font-size: 0.5rem;
        white-space: nowrap;
        opacity: 0.4;
    }

    .resonance-needle {
        position: absolute;
        bottom: 0;
        width: 2px;
        height: 100%;
        background: #fff;
        box-shadow: 0 0 10px #fff;
        transition: left 0.1s linear;
        z-index: 5;
    }

    .needle-glow {
        position: absolute;
        top: 0;
        left: -15px;
        width: 32px;
        height: 100%;
        background: radial-gradient(
            circle,
            rgba(255, 255, 255, 0.2) 0%,
            transparent 70%
        );
    }

    .needle-label {
        position: absolute;
        bottom: -15px;
        left: -20px;
        font-size: 0.5rem;
        font-weight: bold;
        white-space: nowrap;
    }

    .metrics-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
    }

    .highlight {
        color: #fff;
        text-shadow: 0 0 5px #00ffff;
    }
</style>
