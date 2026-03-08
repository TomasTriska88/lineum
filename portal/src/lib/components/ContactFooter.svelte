<script>
    import config from "../data/project/lineum-config.json";
</script>

<div class="contact-footer" aria-label="Contact Information" translate="no">
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
    </div>
    <div class="contact-row">
        <a href="mailto:{config.contact.primary}" class="contact-link"
            >{config.contact.primary}</a
        >
        <span class="separator">•</span>
        <a
            href="tel:{config.brand.phone.replace(/\s+/g, '')}"
            class="contact-link">{config.brand.phone}</a
        >
    </div>
</div>

<style>
    .contact-footer {
        position: fixed;
        bottom: 12px;
        right: 120px; /* Leave space for version HUD */
        font-family: var(--font-mono, monospace);
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.5);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
        background: rgba(10, 10, 12, 0.7);
        padding: 6px 12px;
        border-radius: 6px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition:
            opacity 0.2s ease,
            transform 0.2s ease;
    }

    .contact-footer:hover {
        color: rgba(255, 255, 255, 0.8);
        background: rgba(15, 15, 20, 0.85);
        border-color: rgba(255, 255, 255, 0.15);
    }

    .contact-row {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .contact-link {
        color: inherit;
        text-decoration: none;
        transition: color 0.15s ease;
    }

    .contact-link:hover {
        color: #38bdf8; /* Brand accent color */
    }

    .separator {
        opacity: 0.3;
        font-size: 0.8em;
    }

    @media (max-width: 768px) {
        .contact-footer {
            flex-direction: column;
            align-items: flex-end;
            right: 12px;
            bottom: 36px; /* Above the version HUD if stacked */
            padding: 8px 10px;
            font-size: 0.65rem;
            gap: 6px;
        }

        .contact-row {
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 6px;
        }

        .separator {
            display: none;
        }
    }
</style>
