<script lang="ts">
    import { fade } from "svelte/transition";
</script>

<svelte:head>
    <title>Extreme Spikes | Lineum Lab</title>
</svelte:head>

<div class="lab-container">
    <div class="header">
        <span class="label">LAB // SHOWCASE</span>
        <h1>Extreme Spikes (White Holes)</h1>
        <p class="subtitle">
            Visualizing geometric anomalies and localized "Big Bangs" in the
            Lineum φ field.
        </p>
    </div>

    <div class="split-pane">
        <div class="text-pane card">
            <h2>The Mathematics of a White Hole</h2>
            <p>
                In an extremely low-noise Lineum simulation environment (like
                Seed 9 and Seed 35), phase resonance occasionally creates an
                immense, highly concentrated localized fluctuation in the ψ
                field.
            </p>
            <p>
                As this massive density digs a rapid, impossibly dense tension
                well into the φ fabric, the geometric shear forces it to
                violently "unwind", creating a massive release of energy that
                mimics an Astrophysical Jet or a Localized Big Bang.
            </p>

            <div class="equation-box">
                <span class="equation-label">The Information Equivalence</span>
                <code>I = m / k_φ = E / (k_φ · c_eff²)</code>
            </div>

            <p>
                This equation demonstrates that Energy (E), Mass (m), and
                Information (I) are perfectly equivalent. The White Hole is a
                geometric unwinding of dense Information back into free-flowing
                Energy phase ripples.
            </p>

            <div class="audit-badge">
                <div class="badge-icon">✓</div>
                <div class="badge-text">
                    <strong>Reproducible Proof</strong>
                    <span
                        >Data originates from canon Audit Run <span
                            class="highlight">Spec6_True</span
                        >.</span
                    >
                </div>
            </div>
        </div>

        <div class="visual-pane">
            <div class="visual-card card" transition:fade>
                <h3>Seed 9: The Primary Anomaly</h3>
                <div class="img-wrapper">
                    <img
                        src="/assets/lab/seed_9_extreme_phi.gif"
                        alt="3D Animation of Phi Spike in Seed 9"
                    />
                </div>
                <p class="caption">
                    Amplitude density overload causing a critical φ inversion.
                </p>
            </div>

            <div class="visual-card card" transition:fade>
                <h3>Seed 35: The Secondary Anomaly</h3>
                <div class="img-wrapper">
                    <img
                        src="/assets/lab/seed_35_extreme_phi.gif"
                        alt="3D Animation of Phi Spike in Seed 35"
                    />
                </div>
                <p class="caption">
                    A geometric jet eruption following extreme phase clustering.
                </p>
            </div>
        </div>
    </div>
</div>

<style>
    .lab-container {
        padding: 6rem 2rem 4rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
        color: rgba(255, 255, 255, 0.9);
    }
    .header {
        margin-bottom: 3rem;
        text-align: center;
    }
    .label {
        font-family: var(--font-mono, monospace);
        font-size: 0.75rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--accent-color, #7eb8ff);
        display: block;
        margin-bottom: 1rem;
    }
    h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.6));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.6);
        max-width: 600px;
        margin: 0 auto;
    }

    .split-pane {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 2.5rem;
        backdrop-filter: blur(12px);
    }

    .text-pane h2 {
        font-size: 1.5rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
        color: #fff;
    }

    .text-pane p {
        line-height: 1.7;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 1.5rem;
    }

    .equation-box {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(126, 184, 255, 0.2);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: inset 0 0 20px rgba(126, 184, 255, 0.05);
    }

    .equation-label {
        display: block;
        font-family: var(--font-mono, monospace);
        font-size: 0.75rem;
        color: rgba(126, 184, 255, 0.7);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .equation-box code {
        font-size: 1.4rem;
        color: #fff;
        font-family: "JetBrains Mono", "Fira Code", monospace;
    }

    .audit-badge {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(46, 160, 67, 0.1);
        border: 1px solid rgba(46, 160, 67, 0.3);
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 3rem;
    }

    .badge-icon {
        background: #3fb950;
        color: #000;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-weight: bold;
        flex-shrink: 0;
    }

    .badge-text strong {
        display: block;
        color: #3fb950;
        margin-bottom: 0.25rem;
    }

    .badge-text span {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.6);
    }

    .highlight {
        color: #fff !important;
        font-family: var(--font-mono, monospace);
        background: rgba(255, 255, 255, 0.1);
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
    }

    .visual-pane {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .visual-card {
        padding: 1.5rem;
    }

    .visual-card h3 {
        font-size: 1.1rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
        color: rgba(255, 255, 255, 0.9);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.75rem;
    }

    .img-wrapper {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: #000;
        position: relative;
    }

    /* Subtle glowing back-drop for images */
    .img-wrapper::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        box-shadow: inset 0 0 30px rgba(126, 184, 255, 0.1);
        pointer-events: none;
    }

    .visual-card img {
        width: 100%;
        height: auto;
        display: block;
        mix-blend-mode: screen;
        transform: scale(1.02);
    }

    .caption {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.4);
        margin-top: 1rem;
        text-align: center;
        font-family: var(--font-mono, monospace);
    }

    @media (max-width: 900px) {
        .split-pane {
            grid-template-columns: 1fr;
        }
    }
</style>
