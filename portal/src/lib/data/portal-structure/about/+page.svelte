<script lang="ts">
    import { t } from "$lib/i18n";
    import { config } from "$lib/config";
</script>

<svelte:head>
    <title>{$t("nav.about")} | {$t("common.brand")}</title>
</svelte:head>

<div class="about-page">
    <div class="container narrow">
        <span class="label">Corporate Profile</span>
        <h1>About {config.brand.name}</h1>
        <p class="subtitle">
            Exploring the continuous nature of discrete computation.
        </p>

        <div class="content-block">
            <h2>Our Mission</h2>
            <p>
                Lineum is an independent research initiative dedicated to
                discovering the fundamental rules of emergent stable excitations
                within continuous wave fields. Our goal is to build
                hardware-less computation logic directly into the fabric of
                simulated physics.
            </p>

            <h2>Legal Entity</h2>
            <p>
                <strong>Official Name:</strong>
                {config.brand.legalName}<br />
                <strong>Founded:</strong> February 2026<br />
                <strong>Contact:</strong>
                <a href="mailto:{config.contact.primary}"
                    >{config.contact.primary}</a
                >
            </p>

            <h2>Connect With Us</h2>
            <p>
                For technical discussions, API integrations, and research
                inquiries, please reach out via our primary contact endpoint. We
                do not use third-party tracking or host non-essential telemetry.
            </p>
        </div>

        <div class="cta-section">
            <a href="/api-solutions" class="btn btn-primary btn-large">
                Explore The API Solutions
            </a>
        </div>
    </div>
</div>

<style>
    .about-page {
        padding-top: 8rem;
        padding-bottom: 8rem;
        min-height: 100vh;
    }

    .narrow {
        max-width: 800px;
    }

    .label {
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        color: var(--accent-color);
        margin-bottom: 1rem;
        display: block;
    }

    h1 {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }

    .subtitle {
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 3rem;
    }

    .content-block {
        background: rgba(255, 255, 255, 0.02);
        padding: 3rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 4rem;
    }

    .content-block h2 {
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: white;
    }

    .content-block h2:first-child {
        margin-top: 0;
    }

    .content-block p {
        font-size: 1.1rem;
        line-height: 1.8;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 1.5rem;
    }

    .content-block a {
        color: var(--accent-color);
        text-decoration: none;
    }

    .cta-section {
        text-align: center;
        background: rgba(126, 184, 255, 0.05);
        padding: 4rem 2rem;
        border-radius: 12px;
        border: 1px solid rgba(126, 184, 255, 0.1);
    }

    .btn-large {
        padding: 1.25rem 3rem;
        font-size: 1.1rem;
        margin-bottom: 0;
    }
</style>
