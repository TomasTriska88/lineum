<script lang="ts">
    import FieldShader from "$lib/components/FieldShader.svelte";
    import Legend from "$lib/components/Legend.svelte";
    import MarginShards from "$lib/components/MarginShards.svelte";
    import LogoCloud from "$lib/components/LogoCloud.svelte";
    import { t } from "$lib/i18n";
    import { dev } from "$app/environment";

    const SIMULACRUM_URL = dev
        ? "http://localhost:5174"
        : "https://simulacrum.lineum.io";

    $: legendItems = [
        {
            id: "psi",
            color: "#00ffff",
            ...(typeof $t("legend.items.psi") === "object"
                ? $t("legend.items.psi")
                : {}),
        },
        {
            id: "kappa",
            color: "#1a3a5a",
            ...(typeof $t("legend.items.kappa") === "object"
                ? $t("legend.items.kappa")
                : {}),
        },
        {
            id: "phi",
            color: "#8a2be2",
            ...(typeof $t("legend.items.phi") === "object"
                ? $t("legend.items.phi")
                : {}),
        },
        {
            id: "warp",
            color: "#ff00ff",
            colorAlt: "#8a2be2",
            ...(typeof $t("legend.items.warp") === "object"
                ? $t("legend.items.warp")
                : {}),
        },
    ];
</script>

<svelte:head>
    <title>{$t("meta.title")}</title>
    <meta name="description" content={$t("meta.description")} />
</svelte:head>

<section class="hero">
    <div class="shader-overlay">
        <FieldShader />
    </div>

    <div class="hero-content container">
        <div class="logo">
            <span class="logo-symbol">{$t("hero.symbol")}</span>
            <span class="logo-text">Lineum</span>
            <Legend
                title={$t("legend.title")}
                subtitle={$t("legend.subtitle")}
                items={legendItems}
                faq={$t("legend.faq")}
            />
        </div>
        <h1>
            {$t("hero.title_prefix")}
            <span class="text-gradient-multi animate-breathe">
                {$t("hero.title_highlight")}
            </span>
        </h1>
        <p>
            {$t("hero.subtitle")}
        </p>
        <div class="cta-group">
            <a href="/wiki" class="btn btn-primary">{$t("hero.cta_wiki")}</a>
            <a
                href="/api-solutions"
                class="btn btn-outline"
                style="border-color: #38bdf8; color: #38bdf8;"
                >{$t("nav.api")}</a
            >
            <a href="#scientist" class="btn btn-outline"
                >{$t("hero.cta_audit")}</a
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
                    text: $t("sections.layman.p1"),
                },
                {
                    id: "layman-vibe",
                    selector: "#layman h2",
                    text: $t("hero.subtitle"),
                },
                {
                    id: "scientist-data",
                    selector: "#scientist h2",
                    text: `✨ ${$t("sections.scientist.whitepaper.desc")}`,
                },
            ]}
        />

        <div
            class="text-block"
            style="text-align: center; margin-bottom: 4rem;"
        >
            <span class="label">{$t("sections.layman.label")}</span>
            <h2>{$t("sections.layman.title")}</h2>
            <p style="margin: 0 auto 2rem; max-width: 800px;">
                {$t("sections.layman.p1")}
            </p>
        </div>
    </div>
</section>

<section id="scientist" class="info-section alternate">
    <div class="container">
        <span class="label">{$t("sections.scientist.label")}</span>
        <h2>{$t("sections.scientist.title")}</h2>
        <div class="scientific-grid">
            <div class="card">
                <h3>{$t("sections.scientist.whitepaper.title")}</h3>
                <p>{$t("sections.scientist.whitepaper.desc")}</p>
                <a href="/wiki">{$t("sections.scientist.whitepaper.link")}</a>
            </div>
            <div class="card">
                <h3>{$t("sections.scientist.zenodo.title")}</h3>
                <p>{$t("sections.scientist.zenodo.desc")}</p>
                <a
                    href="https://doi.org/10.5281/zenodo.16934359"
                    target="_blank">{$t("sections.scientist.zenodo.link")}</a
                >
            </div>
            <div class="card">
                <h3>{$t("sections.scientist.simulacrum.title")}</h3>
                <p>{$t("sections.scientist.simulacrum.desc")}</p>
                <a href={SIMULACRUM_URL} target="simulacrum"
                    >{$t("sections.scientist.simulacrum.link")}</a
                >
            </div>
            <div class="card">
                <h3>{$t("sections.scientist.referencePack.title")}</h3>
                <p>{$t("sections.scientist.referencePack.desc")}</p>
                <a
                    href="https://github.com/TomasTriska88/lineum-private/releases"
                    target="_blank"
                    >{$t("sections.scientist.referencePack.link")}</a
                >
            </div>
        </div>
    </div>
</section>

<footer class="container">
    <div class="footer-content">
        <div class="footer-info">
            <p>{$t("footer.copy")}</p>
            <!-- <div class="operator-info">
                Operator info removed temporarily until dynamic translations for config are ready
            </div> -->
        </div>
        <div class="footer-links">
            <a href="/support">{$t("footer.support")}</a>
            <a href="/privacy">{$t("footer.privacy")}</a>
            <a
                href="https://github.com/TomasTriska88/lineum-private"
                target="_blank">{$t("footer.github")}</a
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
