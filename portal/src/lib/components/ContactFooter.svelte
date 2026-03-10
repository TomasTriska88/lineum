<script>
    import config from "../data/project/lineum-config.json";
    import pkg from "../../../../package.json";
    import * as m from "$lib/paraglide/messages.js";

    // @ts-ignore
    const commitHash =
        typeof __GIT_HASH__ !== "undefined" ? __GIT_HASH__ : "dev";
</script>

<footer class="contact-footer" aria-label="Footer" translate="no">
    <div class="container footer-container">
        <div class="footer-top">
            <div class="footer-info">
                <p>{m.footer_copy()}</p>
            </div>
            <div class="footer-links">
                <a href="/support">{m.footer_support()}</a>
                <a href="/privacy">{m.footer_privacy()}</a>
                <a
                    href="https://github.com/TomasTriska88/lineum-core/tree/{commitHash}"
                    target="_blank"
                    style="color: var(--accent-cyan);"
                    >Source (AGPLv3) - Commit: {commitHash}</a
                >
                <a
                    href="https://github.com/TomasTriska88/lineum-private"
                    target="_blank">{m.footer_github()}</a
                >
            </div>
        </div>

        <div class="footer-bottom">
            <div class="contact-row">
                <a
                    href="https://or.justice.cz/ias/ui/rejstrik-%24firma?nazev={encodeURIComponent(
                        config.brand.name,
                    )}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="contact-link company"
                    title="Official Business Registry"
                >
                    {config.brand.name}
                </a>
                <span class="separator">|</span>
                <a
                    href="https://maps.google.com/?q={encodeURIComponent(
                        config.brand.address,
                    )}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="contact-link address"
                    title="View on Google Maps"
                >
                    {config.brand.address}
                </a>
                <span class="separator desktop-only">•</span>
                <a href="mailto:{config.contact.primary}" class="contact-link"
                    >{config.contact.primary}</a
                >
                <span class="separator">•</span>
                <a
                    href="tel:{config.brand.phone.replace(/\s+/g, '')}"
                    class="contact-link">{config.brand.phone}</a
                >
                <span class="separator desktop-only">•</span>
                <span class="version-hud">v{pkg.version}</span>
            </div>
        </div>
    </div>
</footer>

<style>
    .contact-footer {
        padding: 4rem 2rem 2rem;
        background: var(--bg-primary, #0a0a0f);
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: auto;
        width: 100%;
        color: rgba(255, 255, 255, 0.5);
    }

    .footer-container {
        display: flex;
        flex-direction: column;
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .footer-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
    }

    .footer-links {
        display: flex;
        gap: 2rem;
    }

    .footer-links a {
        color: inherit;
        text-decoration: none;
        transition: color 0.2s;
    }

    .footer-links a:hover {
        color: white;
    }

    .footer-bottom {
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 2rem;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: var(--font-mono, monospace);
        font-size: 0.75rem;
    }

    .contact-row {
        display: flex;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
        justify-content: center;
    }

    .contact-link {
        color: rgba(255, 255, 255, 0.4);
        text-decoration: none;
        transition: color 0.15s ease;
    }

    .contact-link.company {
        color: rgba(255, 255, 255, 0.6);
        font-weight: 600;
    }

    .contact-link:hover {
        color: #38bdf8;
    }

    .separator {
        opacity: 0.3;
        font-size: 0.8em;
    }

    .version-hud {
        color: rgba(255, 255, 255, 0.25);
    }

    @media (max-width: 768px) {
        .footer-top {
            flex-direction: column;
            gap: 2rem;
            text-align: center;
        }

        .footer-links {
            flex-direction: column;
            gap: 1.5rem;
        }

        .contact-row {
            gap: 8px;
            font-size: 0.65rem;
        }

        .desktop-only {
            display: none;
        }

        .contact-link.address {
            display: none;
        }
    }
</style>
