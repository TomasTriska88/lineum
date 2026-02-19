<script lang="ts">
    import FieldShader from "$lib/components/FieldShader.svelte";
    import Legend from "$lib/components/Legend.svelte";
    import MarginShards from "$lib/components/MarginShards.svelte";
    import { content } from "$lib/content";
</script>

<svelte:head>
    <title>Lineum | Discrete Field Dynamics</title>
    <meta
        name="description"
        content="Official portal for the Lineum project. Discover the emergence of stable localized excitations in discrete field models."
    />
</svelte:head>

<section class="hero">
    <div class="shader-overlay">
        <FieldShader />
    </div>

    <div class="hero-content container">
        <div class="logo">
            <span class="logo-symbol">{content.hero.symbol}</span>
            <span class="logo-text">Lineum</span>
            <Legend
                title={content.legend.title}
                subtitle={content.legend.subtitle}
                items={content.legend.items}
                faq={content.legend.faq}
            />
        </div>
        <h1>{content.hero.title}</h1>
        <p>
            {content.hero.subtitle}
        </p>
        <div class="cta-group">
            <a href="/wiki" class="btn btn-primary">{content.hero.cta_wiki}</a>
            <a href="#evidence" class="btn btn-outline"
                >{content.hero.cta_audit}</a
            >
        </div>
    </div>
</section>

<section id="layman" class="info-section">
    <div class="container">
        <MarginShards
            insights={[
                {
                    id: "hero-dynamic",
                    selector: ".hero-content h1",
                    text: "✨ Lina: This simulation represents our 'Version 1' resonance. It's the most stable field we've achieved so far.",
                },
                {
                    id: "layman-vibe",
                    selector: "#layman h2",
                    text: "✨ Lina: Don't worry about the math! Think of Lineum like a musical instrument. We're just learning how to play the strings of reality.",
                },
                {
                    id: "scientist-data",
                    selector: "#scientist h2",
                    text: "✨ Lina: For my fellow researchers—every data point here is cross-validated against the [VALIDATED] contract suite.",
                },
            ]}
        />

        <div
            class="text-block"
            style="text-align: center; margin-bottom: 4rem;"
        >
            <span class="label">{content.sections.layman.label}</span>
            <h2>{content.sections.layman.title}</h2>
            <p style="margin: 0 auto 2rem; max-width: 800px;">
                {content.sections.layman.p1}
            </p>
        </div>
    </div>
</section>

<section id="scientist" class="info-section alternate">
    <div class="container">
        <span class="label">{content.sections.scientist.label}</span>
        <h2>{content.sections.scientist.title}</h2>
        <div class="scientific-grid">
            <div class="card">
                <h3>{content.sections.scientist.whitepaper.title}</h3>
                <p>{content.sections.scientist.whitepaper.desc}</p>
                <a href="/wiki">{content.sections.scientist.whitepaper.link}</a>
            </div>
            <div class="card">
                <h3>{content.sections.scientist.zenodo.title}</h3>
                <p>{content.sections.scientist.zenodo.desc}</p>
                <a
                    href="https://doi.org/10.5281/zenodo.16934359"
                    target="_blank">{content.sections.scientist.zenodo.link}</a
                >
            </div>
            <div class="card">
                <h3>{content.sections.scientist.simulacrum.title}</h3>
                <p>{content.sections.scientist.simulacrum.desc}</p>
                <a href="https://simulacrum.lineum.io" target="simulacrum"
                    >{content.sections.scientist.simulacrum.link}</a
                >
            </div>
        </div>
    </div>
</section>

<footer class="container">
    <div class="footer-content">
        <p>{content.footer.copy}</p>
        <div class="footer-links">
            <a href="/support">{content.footer.support}</a>
            <a href="/privacy">{content.footer.privacy}</a>
            <a
                href="https://github.com/TomasTriska88/lineum-private"
                target="_blank">{content.footer.github}</a
            >
        </div>
    </div>
</footer>

<style>
    .hero {
        height: 100vh;
        display: flex;
        align-items: center;
        position: relative;
        overflow: visible;
        margin-top: -64px;
        padding-top: 64px;
    }

    .shader-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
    }

    .hero-content {
        position: relative;
        z-index: 2;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .logo-symbol {
        font-size: 4rem;
        font-family: serif;
        background: linear-gradient(
            135deg,
            var(--accent-violet),
            var(--accent-cyan)
        );
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(124, 58, 237, 0.4));
    }

    .logo-text {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        color: white;
    }

    h1 {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        color: white;
    }

    p {
        font-size: 1.25rem;
        color: #aaa;
        max-width: 600px;
        margin-bottom: 2.5rem;
    }

    .cta-group {
        display: flex;
        gap: 1.5rem;
    }

    .btn {
        padding: 1rem 2rem;
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 0.1em;
        transition: all 0.3s;
    }

    .btn-primary {
        background-color: var(--accent-color);
        color: white;
    }

    .btn-outline {
        border: 1px solid var(--accent-color);
        color: var(--accent-color);
    }

    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    }

    .info-section {
        padding: 8rem 0;
    }

    .info-section.alternate {
        background: rgba(255, 255, 255, 0.02);
    }

    .label {
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        color: var(--accent-color);
        margin-bottom: 1rem;
        display: block;
    }

    h2 {
        font-size: 3rem;
        margin-bottom: 2rem;
    }

    .scientific-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        margin-top: 4rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.03);
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: border-color 0.3s;
    }

    .card:hover {
        border-color: var(--accent-color);
    }

    .card h3 {
        margin-bottom: 1rem;
    }

    .card p {
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    footer {
        padding: 4rem 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 4rem;
    }

    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #555;
        font-size: 0.9rem;
    }

    .footer-links {
        display: flex;
        gap: 2rem;
    }

    @media (max-width: 768px) {
        .logo-text {
            font-size: 3rem;
        }
        .scientific-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
