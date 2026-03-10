<script lang="ts">
    import { page } from "$app/stores";
    import { dev } from "$app/environment";
    import * as m from "$lib/paraglide/messages.js";
    import { languageTag } from "$lib/paraglide/runtime.js";
    import { i18n, pathnames } from "$lib/i18n";
    import {
        PUBLIC_SIMULACRUM_URL,
        PUBLIC_ENABLE_API_SOLUTIONS,
    } from "$env/static/public";
    import Logo from "$lib/components/Logo.svelte";

    let menuOpen = false;
    let docsOpen = false;
    let devToolsOpen = false;
    let currentLang = languageTag();

    function toggleMenu() {
        menuOpen = !menuOpen;
    }

    function toggleDocs(e: Event) {
        e.preventDefault();
        docsOpen = !docsOpen;
    }

    function toggleDevTools(e: Event) {
        e.preventDefault();
        devToolsOpen = !devToolsOpen;
    }

    // Close menu when navigating and reactively update language
    $: if ($page.url.pathname) {
        menuOpen = false;
        docsOpen = false;
        devToolsOpen = false;
        currentLang = languageTag();
    }

    // Language handling
    const langs = [
        { code: "en", label: "English", abbr: "EN" },
        { code: "cs", label: "Čeština", abbr: "CZ" },
        { code: "de", label: "Deutsch", abbr: "DE" },
        { code: "ja", label: "日本語", abbr: "JA" },
    ];

    function getResolvedCanonicalPath(currentPath: string) {
        // First trim the temporary language prefix (/cs/api-reseni -> /api-reseni)
        let p = currentPath;
        const prefixes = ["/cs", "/de", "/ja", "/en"];
        for (const pre of prefixes) {
            if (p === pre) p = "/";
            else if (p.startsWith(pre + "/")) p = p.slice(pre.length);
        }

        // Reverse map the translated path to its SvelteKit base (e.g., /api-reseni -> /api-solutions)
        for (const [canonical, translations] of Object.entries(pathnames)) {
            if ((Object.values(translations) as string[]).includes(p))
                return canonical;
        }

        return p;
    }
</script>

<nav>
    <div class="container nav-content">
        <a href="/" class="nav-logo">
            <Logo
                width={28}
                height={28}
                color="#00ffff"
                variant="infinity_draw"
            />
            Lineum&trade;
        </a>

        <button
            class="mobile-toggle"
            on:click={toggleMenu}
            aria-label="Toggle Menu"
        >
            {#if menuOpen}
                ✕
            {:else}
                ☰
            {/if}
        </button>

        <div class="nav-links" class:mobile-open={menuOpen}>
            {#if PUBLIC_ENABLE_API_SOLUTIONS === "true"}
                <a
                    href="/api-solutions"
                    style="color: #38bdf8; font-weight: bold;"
                >
                    {m.nav_api()}
                    <span
                        style="font-size: 0.6rem; vertical-align: super; opacity: 0.8;"
                        >{m.badge_early_access()}</span
                    >
                </a>
            {/if}

            <a href={PUBLIC_SIMULACRUM_URL} target="simulacrum">{m.nav_lab()}</a
            >
            <a href="/#scientist">{m.sections_scientist_label()}</a>

            <div class="dropdown" role="menu" tabindex="0">
                <button class="dropdown-toggle" on:click={toggleDocs}>
                    Ecosystem <span class="caret">▼</span>
                </button>
                <div
                    class="dropdown-menu mega-menu"
                    class:mobile-open={docsOpen}
                >
                    <div class="menu-section">
                        <span class="menu-label">The Project</span>
                        <a href="/about">{m.nav_about()}</a>
                        <a href="/brand">{m.nav_brand()}</a>
                        <a href="/codex">{m.nav_codex()}</a>
                        <a href="/wiki#faq">{m.nav_faq()}</a>
                    </div>
                    <div class="menu-section">
                        <span class="menu-label">Developers</span>
                        {#if PUBLIC_ENABLE_API_SOLUTIONS === "true"}
                            <a href="/engraving" style="color: #ffaa00;"
                                >{m.nav_engraving()}
                                <span
                                    style="font-size: 0.6rem; vertical-align: super;"
                                    >{m.badge_beta()}</span
                                ></a
                            >
                        {/if}
                        <a href="/explorer">Explorer</a>
                        <a href="/journal">Memory Journal</a>
                        <a href="http://127.0.0.1:8000/redoc" target="_blank"
                            >API Redoc</a
                        >
                    </div>
                </div>
            </div>

            <div class="spacer" style="margin-left: auto;"></div>

            <a href="/support" class="nav-cta">{m.nav_support()}</a>

            <div class="dropdown lang-dropdown" role="menu" tabindex="0">
                <button
                    class="dropdown-toggle lang-toggle"
                    on:click={toggleDevTools}
                >
                    {langs.find((l) => l.code === currentLang)?.abbr ||
                        currentLang.toUpperCase()} <span class="caret">▼</span>
                </button>
                <div
                    class="dropdown-menu"
                    class:mobile-open={devToolsOpen}
                    style="min-width: max-content;"
                >
                    {#each langs as lang}
                        <a
                            href={getResolvedCanonicalPath($page.url.pathname)}
                            hreflang={lang.code}
                            data-sveltekit-reload
                            class="lang-btn"
                            class:active={currentLang === lang.code}
                        >
                            {lang.label} ({lang.abbr})
                        </a>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</nav>

<style>
    nav {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        padding: 1.5rem 0;
        z-index: 9999;
        background: rgba(5, 5, 5, 0.8);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .nav-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 700;
        font-size: 1.2rem;
        letter-spacing: -0.05em;
        color: white;
        text-decoration: none;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .nav-links a {
        font-size: 0.9rem;
        font-weight: 500;
        color: #aaa;
        text-decoration: none;
    }

    .nav-links a:hover {
        color: white;
    }

    /* Dropdown CSS */
    :global(.dropdown) {
        position: relative;
    }
    :global(.dropdown-toggle) {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        background: none;
        border: none;
        color: white;
        font-size: 1rem;
        cursor: pointer;
        padding: 0.5rem 0;
    }
    :global(.caret) {
        font-size: 0.6rem;
        transition: transform 0.2s;
    }
    :global(.dropdown:hover .caret) {
        transform: rotate(180deg);
    }
    :global(.dropdown-menu) {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        min-width: 150px;
        background: rgba(10, 10, 15, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem 0;
        flex-direction: column;
        backdrop-filter: blur(10px);
        z-index: 1000;
        box-shadow:
            0 10px 40px rgba(0, 0, 0, 0.5),
            0 1px 3px rgba(255, 255, 255, 0.05) inset;
        transition:
            opacity 0.2s ease,
            transform 0.2s ease;
        opacity: 0;
        transform: translateY(5px);
        pointer-events: none;
    }
    :global(.mega-menu) {
        min-width: 480px;
        flex-direction: row;
        gap: 2rem;
        padding: 1.25rem;
    }
    :global(.menu-section) {
        display: flex;
        flex-direction: column;
        flex: 1;
        gap: 0.15rem;
    }
    :global(.menu-label) {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #777;
        padding: 0 0.6rem 0.4rem 0.6rem;
        font-weight: 700;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 0.4rem;
    }
    :global(.dropdown:hover .dropdown-menu) {
        display: flex;
        opacity: 1;
        transform: translateY(0);
        pointer-events: auto;
    }
    :global(.dropdown-menu.mobile-open) {
        display: flex;
        opacity: 1;
        transform: translateY(0);
        pointer-events: auto;
    }
    :global(.dropdown-menu a) {
        padding: 0.4rem 0.6rem;
        width: 100%;
        box-sizing: border-box;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #bbb;
        transition: all 0.2s ease;
    }
    :global(.dropdown-menu a:hover) {
        background: rgba(255, 255, 255, 0.08);
        color: white;
        transform: translateX(2px);
    }

    .nav-cta {
        background: var(--accent-color);
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Language specific overrides */
    :global(.lang-dropdown .dropdown-toggle) {
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.3rem 0.6rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    :global(.lang-dropdown .dropdown-menu) {
        left: auto;
        right: 0;
    }
    :global(.lang-dropdown a) {
        white-space: nowrap;
        padding-right: 1.5rem;
    }
    :global(.lang-dropdown a.active) {
        background: rgba(255, 255, 255, 0.1);
        color: var(--accent-cyan);
    }

    .mobile-toggle {
        display: none; /* Hidden by default */
        background: transparent;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
        z-index: 101;
    }

    @media (max-width: 768px) {
        nav {
            padding: 1rem 0;
            background: rgba(5, 5, 5, 0.95); /* More opaque on mobile */
        }

        .nav-content {
            /* Keep row for logo + hamburger */
            flex-direction: row;
            justify-content: space-between;
        }

        /* Hide desktop links by default */
        .nav-links {
            display: none;
            position: fixed;
            top: 60px; /* Below nav */
            left: 0;
            width: 100%;
            height: calc(100vh - 60px);
            background: #0a0a0f;
            flex-direction: column;
            justify-content: flex-start;
            padding: 1.5rem 2rem 4rem;
            gap: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            align-items: center;
            overflow-y: auto;
        }

        .nav-links.mobile-open {
            display: flex;
        }

        .nav-links a,
        :global(.dropdown-toggle) {
            font-size: 1.2rem; /* Balanced size */
            padding: 0.5rem 0; /* Maintain touch target height */
            width: 100%; /* Full width for easier clicking */
            text-align: center;
            justify-content: center;
        }

        :global(.dropdown-menu) {
            position: relative;
            background: transparent;
            border: none;
            padding: 0;
            box-shadow: none;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            width: 100%;
        }

        :global(.mega-menu) {
            min-width: 100%;
            flex-direction: column;
            gap: 0;
            padding: 0;
        }

        :global(.menu-section) {
            margin-bottom: 1rem;
        }

        :global(.menu-label) {
            padding-left: 0;
            background: transparent;
        }

        .mobile-toggle {
            display: block; /* Visible on mobile */
        }
    }

    @media (min-width: 769px) {
        .mobile-toggle {
            display: none;
        }
    }
</style>
