<script lang="ts">
    import * as m from "$lib/paraglide/messages.js";
    import { config } from "$lib/config";
    import { PUBLIC_ENABLE_API_SOLUTIONS } from "$env/static/public";
    import Logo from "$lib/components/Logo.svelte";
</script>

<svelte:head>
    <title>{m.nav_about()} | {m.common_brand()}</title>
</svelte:head>

<div class="about-page">
    <div class="container narrow">
        <span class="label">Corporate Profile</span>
        <div
            class="hero-brand"
            style="display: flex; justify-content: center; margin-bottom: 2rem;"
        >
            <Logo
                width={120}
                height={120}
                color="#00ffff"
                variant="infinity_draw"
            />
        </div>
        <h1 style="text-align: center; width: 100%;">
            About {config.brand.name}
        </h1>
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
        </div>

        <div class="card-grid">
            <div class="contact-card">
                <h2>Legal Entity</h2>
                <p>
                    <strong>Official Name:</strong>
                    <a
                        href="https://or.justice.cz/ias/ui/rejstrik-%24firma?nazev={encodeURIComponent(
                            config.brand.name,
                        )}"
                        target="_blank"
                        rel="noopener noreferrer"
                        title="Official Business Registry"
                    >
                        {config.brand.legalName}
                    </a><br />
                    <strong>IČ:</strong>
                    <a
                        href="https://or.justice.cz/ias/ui/rejstrik-%24firma?ico={config
                            .brand.ic}"
                        target="_blank"
                        rel="noopener noreferrer"
                        title="Official Business Registry by IČ"
                    >
                        {config.brand.ic}
                    </a><br />
                    <strong>Address:</strong>
                    <a
                        href="https://maps.google.com/?q={encodeURIComponent(
                            config.brand.address,
                        )}"
                        target="_blank"
                        rel="noopener noreferrer"
                        title="View on Google Maps"
                    >
                        {config.brand.address}
                    </a><br />
                    <strong>Phone:</strong>
                    <a href="tel:{config.brand.phone.replace(/\s+/g, '')}">
                        {config.brand.phone}
                    </a><br />
                    <strong>Founded:</strong> February 2026<br />
                    <strong>Contact:</strong>
                    <a href="mailto:{config.contact.primary}"
                        >{config.contact.primary}</a
                    >
                </p>
            </div>

            <div class="contact-card">
                <h2>Core Team</h2>
                <div class="team-member">
                    <strong>Tomáš Tříska</strong>
                    <a
                        href={config.academic.orcidUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        class="orcid-link"
                        title="ORCID Profile"
                    >
                        <svg
                            class="w-4 h-4 mr-1 inline-block"
                            viewBox="0 0 256 256"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                fill="currentColor"
                                d="M256,128c0,70.7-57.3,128-128,128C57.3,256,0,198.7,0,128C0,57.3,57.3,0,128,0C198.7,0,256,57.3,256,128z"
                            />
                            <path
                                fill="#fff"
                                d="M86.3,186.2H70.9V79.1h15.4V186.2z M108.9,79.1h41.6c39.6,0,57,28.3,57,53.6c0,27.5-21.5,53.6-56.8,53.6h-41.8V79.1z M124.3,172.4h24.5c34.9,0,41.2-26.5,41.2-41.2c0-19.7-10.7-38.2-41.2-38.2h-24.5V172.4z M88.7,56.8c0,5.5-4.5,10.1-10.1,10.1c-5.6,0-10.1-4.5-10.1-10.1c0-5.6,4.5-10.1,10.1-10.1C84.2,46.7,88.7,51.3,88.7,56.8z"
                            />
                        </svg>
                        <span class="text-xs font-mono"
                            >{config.academic.orcid}</span
                        >
                    </a>
                    <br />
                    <em class="role">Founder, Lead Researcher</em><br />
                    Creator of the Lineum Core simulation engine and primary architecture.
                </div>
                <div class="team-member">
                    <strong>Kateřina Marečková</strong><br />
                    <em class="role">Contributor & Scientific Opposition</em><br
                    />
                    Provided foundational critical opposition, framework design,
                    and hypothesis testing.
                </div>
                <div class="team-member">
                    <strong>Vlastimil Smeták</strong><br />
                    <em class="role">Mathematical & Structural Formulations</em
                    ><br />
                    Contributed structural insights and correlations with the external
                    OEA model.
                </div>
            </div>

            <div class="contact-card highlight">
                <h2>Connect With Us</h2>
                <p>
                    For technical discussions, API integrations, and research
                    inquiries, please reach out via our primary contact
                    endpoint.
                </p>
                <a
                    href="mailto:{config.contact.primary}"
                    class="btn btn-primary inline-btn">Contact Research Team</a
                >
            </div>

            <div class="contact-card col-span-full">
                <h2>Academic References</h2>
                <p>
                    The Lineum methodology is built on transparent, auditable
                    research. Our primary mathematical proofs and theoretical
                    foundations are registered and independently citable via
                    Zenodo.
                </p>
                <div
                    class="mt-4 p-4 bg-slate-900 border border-slate-800 rounded-lg font-mono text-sm leading-relaxed"
                >
                    <span class="text-slate-500">Title:</span>
                    <span class="text-white"
                        >Lineum: reference implementation & evidence bundle</span
                    ><br />
                    <span class="text-slate-500">DOI:</span>
                    <a
                        href={config.academic.zenodoUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        class="text-sky-400 hover:text-sky-300"
                        >10.5281/zenodo.16934359</a
                    ><br />
                    <span class="text-slate-500">License:</span>
                    <span class="text-white">AGPL-3.0</span>
                </div>

                <p class="mt-4 text-xs text-slate-500">
                    To cite the Lineum architecture in published papers, please
                    reference the DOI above. ORCID profiles are linked in the
                    Team section.
                </p>
            </div>
        </div>

        {#if PUBLIC_ENABLE_API_SOLUTIONS === "true"}
            <div class="cta-section">
                <a href="/api-solutions" class="btn btn-primary btn-large">
                    Explore The API Solutions
                </a>
            </div>
        {/if}
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

    .hero-brand {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        margin-bottom: 1rem;
    }

    h1 {
        font-size: 3.5rem;
        margin-bottom: 0;
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

    .cta-section {
        text-align: center;
        background: rgba(126, 184, 255, 0.05);
        padding: 4rem 2rem;
        margin-top: 4rem;
        border-radius: 12px;
        border: 1px solid rgba(126, 184, 255, 0.1);
    }

    .btn-large {
        padding: 1.25rem 3rem;
        font-size: 1.1rem;
        margin-bottom: 0;
    }

    /* Modern Card Layout Extracted from Design rules */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }

    .contact-card {
        background: rgba(10, 15, 25, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.1);
        border-radius: 12px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        transition:
            transform 0.3s ease,
            box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
    }

    .contact-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 255, 255, 0.05);
        border-color: rgba(0, 255, 255, 0.2);
    }

    .contact-card.highlight {
        background: linear-gradient(
            145deg,
            rgba(0, 40, 60, 0.3) 0%,
            rgba(10, 15, 25, 0.4) 100%
        );
        border-color: rgba(0, 255, 255, 0.3);
    }

    .contact-card.col-span-full {
        grid-column: 1 / -1;
    }

    .contact-card h2 {
        font-size: 1.4rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
        color: #fff;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.75rem;
        display: inline-block;
    }

    .contact-card p,
    .team-member {
        font-size: 1rem;
        line-height: 1.7;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 1rem;
    }

    .team-member {
        margin-bottom: 1.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .team-member:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }

    .team-member strong {
        color: #fff;
        font-size: 1.1rem;
    }

    .team-member .role {
        color: var(--accent-color);
        font-size: 0.9rem;
    }

    .contact-card a {
        color: var(--accent-color);
        text-decoration: none;
        transition: opacity 0.2s;
        font-weight: 500;
    }

    .contact-card a:hover {
        opacity: 0.8;
        text-decoration: underline;
    }

    .inline-btn {
        margin-top: auto;
        display: inline-block;
        text-align: center;
        text-decoration: none !important;
    }

    .orcid-link {
        color: #a6ce39 !important;
        margin-left: 8px;
        display: inline-flex;
        align-items: center;
    }
    .orcid-link:hover {
        color: #c0e655 !important;
        text-decoration: none !important;
    }
</style>
