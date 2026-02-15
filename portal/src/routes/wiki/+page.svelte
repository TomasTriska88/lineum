<script lang="ts">
    import { content } from "$lib/content";
</script>

<svelte:head>
    <title>Wiki — Lineum</title>
</svelte:head>

<div class="wiki-container">
    <div class="container wrapper">
        <aside class="toc">
            <div class="toc-sticky">
                <h3>Navigation</h3>
                <ul>
                    <li><a href="#whitepaper">Whitepaper</a></li>
                    <li><a href="#glossary">Glossary</a></li>
                    <li><a href="#faq">FAQ</a></li>
                </ul>
            </div>
        </aside>

        <article class="paper">
            <section id="whitepaper" class="card">
                <span class="label">DOC // CORE</span>
                <h1>Lineum Core Whitepaper</h1>
                <p class="version">v1.0.18-core &bull; 2026-02-15</p>
                <p>
                    The canonical whitepaper describing the Lineum model, its
                    discrete coupled-field update rule, and the full evidence
                    bundle for the pinned canonical run
                    <code>spec6_false_s41</code>.
                </p>
                <div class="meta-grid">
                    <div class="meta-item">
                        <span class="meta-key">Equation</span>
                        <span class="meta-val">Eq-4 (κ static)</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-key">Scope</span>
                        <span class="meta-val">2D, periodic BCs, 128×128</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-key">Seed</span>
                        <span class="meta-val">41</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-key">DOI</span>
                        <span class="meta-val">10.5281/zenodo.16934359</span>
                    </div>
                </div>
                <a
                    href="https://github.com/TomasTriska88/lineum-private/blob/main/whitepapers/lineum-core.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="btn"
                >
                    Read Full Whitepaper &rarr;
                </a>
            </section>

            <section id="glossary" class="card">
                <span class="label">REF // TERMS</span>
                <h2>Glossary</h2>
                <dl>
                    <dt>Linon</dt>
                    <dd>
                        A stable, localized excitation of |ψ|² — a
                        quasi-particle analogue emergent from the Lineum rule. <em
                            >Not</em
                        > a fundamental particle.
                    </dd>

                    <dt>ψ (psi)</dt>
                    <dd>
                        The primary complex scalar field; |ψ|² = density, arg ψ
                        = phase.
                    </dd>

                    <dt>φ (phi)</dt>
                    <dd>
                        The interaction/memory field; accumulates response to
                        |ψ|².
                    </dd>

                    <dt>κ (kappa)</dt>
                    <dd>
                        Static spatial tuning map; modulates α and β locally
                        (α_eff = κ·α, β_eff = κ·β).
                    </dd>

                    <dt>SBR</dt>
                    <dd>
                        Spectral Balance Ratio — measures dominance of the
                        fundamental tone f₀ over background.
                    </dd>

                    <dt>Structural Closure</dt>
                    <dd>
                        Operational consequence of the φ center-trace half-life;
                        φ retains memory after ψ decay.
                    </dd>
                </dl>
            </section>

            <section id="faq" class="card">
                <span class="label">INFO // FAQ</span>
                <h2>Frequently Asked Questions</h2>

                <details>
                    <summary>Is Lineum a physics simulation?</summary>
                    <p>
                        No. Lineum is a minimal discrete coupled-field model. It
                        does not assume physical constants, spacetime metrics,
                        or continuum symmetries. Physics terms used are strictly
                        analogical labels.
                    </p>
                </details>

                <details>
                    <summary>What does "validated" mean?</summary>
                    <p>
                        A claim marked [VALIDATED] is enforced by the contract
                        suite with numeric acceptance bands and is traceable to
                        a specific contract key and artifact.
                    </p>
                </details>

                <details>
                    <summary>Can I replicate the results?</summary>
                    <p>
                        Yes. The canonical run is fully pinned by the manifest,
                        seed, grid, and Δt. Replication is evaluated by metric
                        tolerances, not bitwise equality.
                    </p>
                </details>
            </section>
        </article>
    </div>
</div>

<style>
    .wiki-container {
        padding-top: 6rem;
        background: var(--bg-primary, #0a0a0f);
        color: var(--text-primary, #e0e0e8);
        min-height: 100vh;
    }

    .wrapper {
        display: grid;
        grid-template-columns: 220px 1fr;
        gap: 3rem;
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    /* --- TOC --- */
    .toc-sticky {
        position: sticky;
        top: 8rem;
    }

    .toc h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 1.5rem;
        color: rgba(255, 255, 255, 0.35);
        font-family: var(--font-mono, "JetBrains Mono", monospace);
    }

    .toc ul {
        list-style: none;
        padding: 0;
    }

    .toc li {
        margin-bottom: 0.75rem;
    }

    .toc a {
        color: rgba(255, 255, 255, 0.45);
        font-size: 0.85rem;
        text-decoration: none;
        transition: color 0.2s;
        font-family: var(--font-mono, monospace);
    }

    .toc a:hover {
        color: var(--accent-color, #7eb8ff);
    }

    /* --- Cards --- */
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
    }

    .label {
        font-family: var(--font-mono, monospace);
        font-size: 0.65rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.25);
        display: block;
        margin-bottom: 1rem;
    }

    h1 {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.7));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h2 {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: rgba(255, 255, 255, 0.9);
    }

    .version {
        font-family: var(--font-mono, monospace);
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.35);
        margin-bottom: 1.5rem;
    }

    p {
        line-height: 1.7;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 1.5rem;
    }

    code {
        background: rgba(255, 255, 255, 0.06);
        padding: 0.15rem 0.4rem;
        border-radius: 3px;
        font-size: 0.85em;
        font-family: var(--font-mono, monospace);
        color: rgba(255, 255, 255, 0.7);
    }

    /* --- Meta Grid --- */
    .meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin-bottom: 2rem;
    }

    .meta-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .meta-key {
        font-family: var(--font-mono, monospace);
        font-size: 0.65rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.25);
    }

    .meta-val {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
    }

    /* --- Button --- */
    .btn {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px;
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.25s;
        background: rgba(255, 255, 255, 0.04);
    }

    .btn:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
        color: #fff;
    }

    /* --- Glossary --- */
    dl {
        margin: 0;
    }

    dt {
        font-weight: 600;
        color: rgba(255, 255, 255, 0.85);
        margin-top: 1.25rem;
        font-size: 1rem;
    }

    dt:first-of-type {
        margin-top: 0;
    }

    dd {
        margin-left: 0;
        padding-left: 1rem;
        border-left: 2px solid rgba(255, 255, 255, 0.06);
        color: rgba(255, 255, 255, 0.55);
        line-height: 1.6;
        margin-top: 0.3rem;
        margin-bottom: 0.75rem;
    }

    /* --- FAQ --- */
    details {
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding: 1rem 0;
    }

    details:last-child {
        border-bottom: none;
    }

    summary {
        cursor: pointer;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.8);
        list-style: none;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    summary::before {
        content: "+";
        font-family: var(--font-mono, monospace);
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.3);
        transition: transform 0.2s;
    }

    details[open] summary::before {
        content: "−";
        color: var(--accent-color, #7eb8ff);
    }

    details p {
        margin-top: 0.75rem;
        padding-left: 1.65rem;
    }

    @media (max-width: 1024px) {
        .wrapper {
            grid-template-columns: 1fr;
        }
        .toc {
            display: none;
        }
    }
</style>
