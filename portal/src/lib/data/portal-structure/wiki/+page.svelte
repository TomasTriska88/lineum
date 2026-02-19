<script lang="ts">
    import { onMount } from "svelte";
    import { content } from "$lib/content";
    import MarginShards from "$lib/components/MarginShards.svelte";
    import WhitepaperWarningModal from "$lib/components/WhitepaperWarningModal.svelte";
    let { data }: { data: any } = $props();
    let papers = $derived(data.papers as any[]);

    // Warning Modal Logic
    let showWarning = $state(false);

    onMount(() => {
        const ack = sessionStorage.getItem(
            "lineum_whitepaper_warning_acknowledged",
        );
        if (!ack) showWarning = true;
    });

    function handleAck() {
        sessionStorage.setItem(
            "lineum_whitepaper_warning_acknowledged",
            "true",
        );
        showWarning = false;
    }

    // Group papers by category
    const categories = ["Core", "Extension", "Experiment", "Other"];
    let groupedPapers = $derived(
        categories.reduce((acc: any[], cat: string) => {
            const list = papers.filter((p: any) => p.category === cat);
            if (list.length > 0) acc.push({ label: cat, list });
            return acc;
        }, [] as any[]),
    );
</script>

<svelte:head>
    <title>Wiki — Lineum</title>
</svelte:head>

<div class="wiki-container">
    {#if showWarning}
        <WhitepaperWarningModal onAck={handleAck} />
    {/if}
    <div class="container wrapper">
        <aside class="toc">
            <div class="toc-sticky">
                <h3>Navigation</h3>
                <ul>
                    <li><a href="#whitepapers">Whitepapers</a></li>
                    <li><a href="#glossary">Glossary</a></li>
                    <li><a href="#faq">FAQ</a></li>
                </ul>
            </div>
        </aside>

        <article class="paper">
            <MarginShards
                insights={[
                    {
                        id: "vortex",
                        selector: "#glossary dt:nth-of-type(1)",
                        text: "✨ Lina: Think of Linons like bubbles in water—always moving but keeping their shape. They are the 'atoms' of our simulation.",
                    },
                    {
                        id: "psi",
                        selector: "#glossary dt:nth-of-type(2)",
                        text: "✨ Lina: Psi is the main 'actor' here. It tells us where the action is happening at any given moment.",
                    },
                    {
                        id: "kappa",
                        selector: "#glossary dt:nth-of-type(4)",
                        text: "✨ Lina: Kappa is our tuning map. It's like the terrain that determines how fast a river flows in different places.",
                    },
                    {
                        id: "faq-physics",
                        selector: "#faq details:nth-of-type(1)",
                        text: "✨ Lina: While it looks like physics, Lineum is more like a digital art piece governed by math. We use physics names because they fit the 'vibe'!",
                    },
                ]}
            />
            <section id="whitepapers" class="card">
                <span class="label">DOC // EXPLORE</span>
                <h1>Research & Documentation</h1>
                <p>
                    The conceptual foundations and technical documentation of
                    the Lineum project.
                </p>

                {#each groupedPapers as group}
                    <div class="category-group">
                        <h2 class="cat-label">{group.label}</h2>
                        <div class="papers-list">
                            {#each group.list as paper}
                                <div class="paper-item">
                                    <div class="paper-info">
                                        <h3>{paper.title}</h3>
                                        <p class="version">
                                            {paper.version} • {paper.date}
                                        </p>
                                    </div>
                                    <a href="/wiki/{paper.slug}" class="btn"
                                        >Read Paper &rarr;</a
                                    >
                                </div>
                            {/each}
                        </div>
                    </div>
                {/each}
            </section>

            <section id="glossary" class="card">
                <span class="label">REF // TERMS</span>
                <h2>Glossary</h2>
                <dl class="glossary-list">
                    <div class="g-item">
                        <dt>Linon</dt>
                        <dd>
                            A stable, localized excitation of |ψ|² — a
                            quasi-particle analogue emergent from the Lineum
                            rule.
                        </dd>
                    </div>

                    <div class="g-item">
                        <dt>ψ (psi)</dt>
                        <dd>
                            The primary complex scalar field; |ψ|² = density,
                            arg ψ = phase.
                        </dd>
                    </div>

                    <div class="g-item">
                        <dt>φ (phi)</dt>
                        <dd>
                            The interaction/memory field; accumulates response
                            to |ψ|².
                        </dd>
                    </div>

                    <div class="g-item">
                        <dt>κ (kappa)</dt>
                        <dd>
                            Static spatial tuning map; modulates α and β locally
                            (α_eff = κ·α, β_eff = κ·β).
                        </dd>
                    </div>

                    <div class="g-item">
                        <dt>SBR</dt>
                        <dd>
                            Spectral Balance Ratio — measures dominance of the
                            fundamental tone f₀ over background.
                        </dd>
                    </div>

                    <div class="g-item">
                        <dt>Structural Closure</dt>
                        <dd>
                            Operational consequence of the φ center-trace
                            half-life; φ retains memory after ψ decay.
                        </dd>
                    </div>
                </dl>
            </section>

            <section id="faq" class="card">
                <span class="label">INFO // FAQ</span>
                <h2>Frequently Asked Questions</h2>

                <div class="faq-list">
                    <details>
                        <summary>Is Lineum a physics simulation?</summary>
                        <p>
                            No. Lineum is a minimal discrete coupled-field
                            model. It does not assume physical constants,
                            spacetime metrics, or continuum symmetries. Physics
                            terms used are strictly analogical labels.
                        </p>
                    </details>

                    <details>
                        <summary>What does "validated" mean?</summary>
                        <p>
                            A claim marked [VALIDATED] is enforced by the
                            contract suite with numeric acceptance bands and is
                            traceable to a specific contract key and artifact.
                        </p>
                    </details>

                    <details>
                        <summary>Can I replicate the results?</summary>
                        <p>
                            Yes. The canonical run is fully pinned by the
                            manifest, seed, grid, and Δt. Replication is
                            evaluated by metric tolerances, not bitwise
                            equality.
                        </p>
                    </details>
                </div>
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
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.7));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .category-group {
        margin-top: 3rem;
    }

    .cat-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--accent-color);
        border-bottom: 1px solid rgba(126, 184, 255, 0.2);
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .papers-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .paper-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.25rem 1.5rem;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 8px;
        transition: all 0.2s;
    }

    .paper-item:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
        transform: translateX(4px);
    }

    .paper-info h3 {
        margin: 0;
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
    }

    .paper-info .version {
        margin: 0.25rem 0 0 0;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.3);
        font-family: var(--font-mono, monospace);
    }

    .btn {
        font-size: 0.8rem;
        color: var(--accent-color);
        text-decoration: none;
        font-weight: 500;
    }

    /* --- Glossary & FAQ Styling --- */
    .glossary-list {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1.5rem;
        margin-top: 1rem;
    }

    .g-item dt {
        font-weight: 600;
        color: white;
        font-size: 1rem;
        margin-bottom: 0.4rem;
    }

    .g-item dd {
        margin: 0;
        color: rgba(255, 255, 255, 0.5);
        line-height: 1.6;
        font-size: 0.95rem;
    }

    .faq-list details {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        margin-bottom: 0.75rem;
        overflow: hidden;
    }

    .faq-list summary {
        padding: 1.25rem;
        cursor: pointer;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.85);
        user-select: none;
    }

    .faq-list summary:hover {
        background: rgba(255, 255, 255, 0.03);
    }

    .faq-list p {
        padding: 0.5rem 1.25rem 1.5rem 1.25rem;
        margin: 0;
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.9rem;
        line-height: 1.6;
    }

    @media (max-width: 1024px) {
        .wrapper {
            grid-template-columns: 1fr;
        }
        .toc {
            display: none;
        }
        .paper-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }
    }
</style>
