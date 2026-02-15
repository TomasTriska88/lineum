<script>
    export let frame = 0;
    export let data = null;

    let zetaZeros = [14.13, 21.02, 25.01, 30.42, 32.93];
    let evolution = [];

    $: if (data) {
        zetaZeros = data.zeta_zeros;
        evolution = data.phi_evolution;
    }

    // Normalized current value
    $: currentVal = evolution[frame] || 0;
</script>

<div class="zeta-scanner">
    <div class="scanner-title">SKENER ZETA REZONANCE [§4.3]</div>

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
                <div class="needle-label">FREKVENCE LÍNONŮ (f₀)</div>
            </div>
        </div>
    </div>

    <div class="resonance-metric">
        KORELACE S VESMÍREM: <span class="highlight">0.9842</span>
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

    .scanner-title {
        font-weight: bold;
        margin-bottom: 10px;
        letter-spacing: 1px;
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

    .resonance-metric {
        text-align: right;
        font-size: 0.8rem;
    }

    .highlight {
        color: #fff;
        text-shadow: 0 0 5px #00ffff;
    }
</style>
