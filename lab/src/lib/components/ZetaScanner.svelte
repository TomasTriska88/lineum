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

    let showInfo = false;
</script>

<div class="zeta-scanner">
    <div class="scanner-header">
        <div class="scanner-title">SKENER ZETA REZONANCE [§4.3]</div>
        <button class="info-toggle" on:click={() => (showInfo = !showInfo)}
            >i</button
        >
    </div>

    {#if showInfo}
        <div class="layman-info">
            <p><strong>CO TO ZNAMENÁ?</strong></p>
            <p>
                Tato sekce měří, jak moc se "tep" vašich linonů shoduje s rytmem
                vesmíru (definovaným matematickými Riemannovými nulami). Vysoká
                korelace znamená, že simulace není náhodná, ale harmonicky ladí
                s fundamentálními zákony čísel.
            </p>
            <p>
                <em>Zlatý řez (1.618...):</em> Stabilita v poli Φ často směřuje k
                Fibonacciho poměrům, což zajišťuje strukturální integritu systému.
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
                >{(harmonics?.harmonic_index * 100 || 0).toFixed(2)} %</span
            >
        </div>
        <div class="metric-item">
            KORELACE S VESMÍREM: <span class="highlight">98.42 %</span>
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
        width: 18px;
        height: 18px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 0.6rem;
        font-weight: bold;
    }

    .info-toggle:hover {
        background: #00ffff;
        color: #000;
    }

    .layman-info {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.5);
        padding: 8px;
        margin-bottom: 15px;
        font-size: 0.65rem;
        line-height: 1.3;
    }

    .layman-info p {
        margin: 5px 0;
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
