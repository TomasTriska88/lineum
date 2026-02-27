<script lang="ts">
    import FieldShader from "$lib/components/FieldShader.svelte";
    import Legend from "$lib/components/Legend.svelte";
    import MarginShards from "$lib/components/MarginShards.svelte";
    import LogoCloud from "$lib/components/LogoCloud.svelte";
    import * as m from "$lib/paraglide/messages.js";
    import { PUBLIC_SIMULACRUM_URL } from "$env/static/public";

    $: legendItems = [
        {
            id: "psi",
            color: "#00ffff",
            label: m.legend_items_psi_label(),
            description: m.legend_items_psi_description(),
        },
        {
            id: "kappa",
            color: "#1a3a5a",
            label: m.legend_items_kappa_label(),
            description: m.legend_items_kappa_description(),
        },
        {
            id: "phi",
            color: "#8a2be2",
            label: m.legend_items_phi_label(),
            description: m.legend_items_phi_description(),
        },
        {
            id: "warp",
            color: "#ff00ff",
            colorAlt: "#8a2be2",
            label: m.legend_items_warp_label(),
            description: m.legend_items_warp_description(),
        },
    ];
</script>

<svelte:head>
    <title>{m.meta_title()}</title>
    <meta name="description" content={m.meta_description()} />
</svelte:head>

<section class="hero">
    <div class="shader-overlay">
        <FieldShader />
    </div>

    <div class="hero-content container">
        <div class="logo">
            <span class="logo-symbol">{m.hero_symbol()}</span>
            <span class="logo-text">Lineum</span>
            <div class="equation-inline">
                <span class="math-symbol"
                    >∂<sub>t</sub><span style="color: var(--accent-cyan)"
                        >ψ</span
                    >
                    = ∇²<span style="color: var(--accent-cyan)">ψ</span> +
                    <span style="color: var(--accent-violet)">φ</span><span
                        style="color: var(--accent-cyan)">ψ</span
                    >
                    + ∇<span style="color: var(--accent-violet)">φ</span></span
                >
            </div>
            <Legend
                title={m.legend_title()}
                subtitle={m.legend_subtitle()}
                items={legendItems}
                faq={[
                    { q: m.legend_faq_0_q(), a: m.legend_faq_0_a() },
                    { q: m.legend_faq_1_q(), a: m.legend_faq_1_a() },
                    { q: m.legend_faq_2_q(), a: m.legend_faq_2_a() },
                ]}
            />
        </div>
        <h1>
            {@html m.hero_title_full({
                highlight_span:
                    "<span class='text-gradient-multi animate-breathe'>",
                highlight_span_end: "</span>",
            })}
        </h1>

        <p>
            {m.hero_subtitle()}
        </p>
        <div class="cta-group">
            <a href="/wiki" class="btn btn-primary">{m.hero_cta_wiki()}</a>
            <a
                href="/api-solutions"
                class="btn btn-outline"
                style="border-color: #38bdf8; color: #38bdf8;">{m.nav_api()}</a
            >
            <a href="#scientist" class="btn btn-outline">{m.hero_cta_audit()}</a
            >
        </div>
    </div>
</section>

<div class="container">
    <LogoCloud />
</div>

<section id="layman" class="info-section">
    <div class="container">
        <MarginShards
            insights={[
                {
                    id: "hero-dynamic",
                    selector: ".hero-content h1",
                    text: m.sections_layman_p1(),
                },
                {
                    id: "layman-vibe",
                    selector: "#layman h2",
                    text: m.hero_subtitle(),
                },
                {
                    id: "scientist-data",
                    selector: "#scientist h2",
                    text: `✨ ${m.sections_scientist_whitepaper_desc()}`,
                },
            ]}
        />

        <div
            class="text-block"
            style="text-align: center; margin-bottom: 4rem;"
        >
            <span class="label">{m.sections_layman_label()}</span>
            <h2>{m.sections_layman_title()}</h2>
            <p style="margin: 0 auto 2rem; max-width: 800px;">
                {m.sections_layman_p1()}
            </p>
        </div>
    </div>
</section>

<section id="scientist" class="info-section alternate">
    <div class="container">
        <span class="label">{m.sections_scientist_label()}</span>
        <h2>{m.sections_scientist_title()}</h2>

        <div class="equation-system-block">
            <div class="eq-line">
                <span class="math-term">∂<sub>t</sub>ψ</span> = ∇²ψ + φψ + ∇φ
            </div>
            <div class="eq-line">
                <span class="math-term">∂<sub>t</sub>φ</span> = α(|ψ|² - φ) + β∇²φ
            </div>
            <div class="eq-caption">
                The Continuous PDE Limit. A fully deterministic, coupled
                oscillator network with emergent gravity and memory. No
                predefined metric. No background spacetime.
            </div>
        </div>

        <div class="scientific-grid">
            <div class="card">
                <h3>{m.sections_scientist_whitepaper_title()}</h3>
                <p>{m.sections_scientist_whitepaper_desc()}</p>
                <a href="/wiki">{m.sections_scientist_whitepaper_link()}</a>
            </div>
            <div class="card">
                <h3>{m.sections_scientist_zenodo_title()}</h3>
                <p>{m.sections_scientist_zenodo_desc()}</p>
                <a
                    href="https://doi.org/10.5281/zenodo.16934359"
                    target="_blank">{m.sections_scientist_zenodo_link()}</a
                >
            </div>
            <div class="card">
                <h3>{m.sections_scientist_simulacrum_title()}</h3>
                <p>{m.sections_scientist_simulacrum_desc()}</p>
                <a href={PUBLIC_SIMULACRUM_URL} target="simulacrum"
                    >{m.sections_scientist_simulacrum_link()}</a
                >
            </div>
            <div class="card">
                <h3>{m.sections_scientist_referencePack_title()}</h3>
                <p>{m.sections_scientist_referencePack_desc()}</p>
                <a
                    href="https://github.com/TomasTriska88/lineum-private/releases"
                    target="_blank"
                    >{m.sections_scientist_referencePack_link()}</a
                >
            </div>
        </div>
    </div>
</section>

<footer class="container">
    <div class="footer-content">
        <div class="footer-info">
            <p>{m.footer_copy()}</p>
            <!-- <div class="operator-info">
                Operator info removed temporarily until dynamic translations for config are ready
            </div> -->
        </div>
        <div class="footer-links">
            <a href="/support">{m.footer_support()}</a>
            <a href="/privacy">{m.footer_privacy()}</a>
            <a
                href="https://github.com/TomasTriska88/lineum-private"
                target="_blank">{m.footer_github()}</a
            >
        </div>
    </div>
</footer>

<style>
    :global(:root) {
        --nav-height: 0px;
    }
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
    }

    p {
        font-size: 1.25rem;
        color: #aaa;
        max-width: 600px;
        margin-bottom: 2.5rem;
    }

    .equation-inline {
        margin-left: auto;
        margin-right: 1rem;
        opacity: 0.8;
        display: flex;
        align-items: center;
        background: rgba(0, 0, 0, 0.3);
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .equation-inline .math-symbol {
        font-family: var(--font-mono);
        font-size: 1rem;
        letter-spacing: 0.05em;
        color: #ffffff;
        text-shadow:
            0 0 10px rgba(124, 58, 237, 0.3),
            0 0 10px rgba(56, 189, 248, 0.3);
    }

    .equation-system-block {
        background: rgba(0, 0, 0, 0.3);
        border-left: 3px solid var(--accent-color);
        padding: 2.5rem;
        margin: 3rem 0 4rem 0;
        border-radius: 0 8px 8px 0;
        font-family: "Courier New", Courier, monospace;
    }

    .eq-line {
        font-size: 1.8rem;
        color: #e0e0e0;
        margin-bottom: 0.5rem;
        letter-spacing: 0.05em;
    }

    .eq-line .math-term {
        color: #fff;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
    }

    .eq-caption {
        font-family:
            system-ui,
            -apple-system,
            sans-serif;
        font-size: 0.9rem;
        color: #888;
        margin-top: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
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
        .hero {
            flex-direction: column;
            justify-content: center;
            text-align: center;
            padding-top: 120px; /* Offset for taller nav */
            height: auto;
            min-height: 100vh;
        }

        .hero-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .logo {
            flex-direction: column;
            gap: 0.5rem;
        }

        .logo-symbol {
            font-size: 3rem;
        }

        .logo-text {
            font-size: 2rem;
        }

        h1 {
            font-size: 2.5rem;
        }

        .cta-group {
            flex-direction: column;
            width: 100%;
            gap: 1rem;
        }

        .cta-group .btn {
            width: 100%;
            text-align: center;
        }

        .scientific-grid {
            grid-template-columns: 1fr;
        }

        .footer-content {
            flex-direction: column;
            gap: 2rem;
            text-align: center;
        }

        .footer-links {
            flex-direction: column;
            gap: 1rem;
        }
    }
</style>
