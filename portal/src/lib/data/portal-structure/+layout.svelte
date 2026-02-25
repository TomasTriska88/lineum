<script>
    import "../app.css";
    import ResonanceDeck from "$lib/components/ResonanceDeck.svelte";
    import CookieBanner from "$lib/components/CookieBanner.svelte";
    import { hudActive } from "$lib/stores/hudStore";
    import { page } from "$app/stores"; // For closing menu on nav
    import { dev } from "$app/environment";
    import { t, locale } from "$lib/i18n";

    const SIMULACRUM_URL = dev
        ? "http://localhost:5174"
        : "https://simulacrum.lineum.io";

    let menuOpen = false;

    function toggleMenu() {
        menuOpen = !menuOpen;
    }

    // Close menu when navigating
    $: if ($page.url.pathname) {
        menuOpen = false;
    }

    // Language handling
    const langs = [
        { code: "en", label: "English" },
        { code: "cs", label: "Čeština" },
        { code: "de", label: "Deutsch" },
        { code: "ja", label: "日本語" },
    ];

    function changeLang(code) {
        locale.set(code);
    }
</script>

<svelte:head>
    <meta property="og:title" content={$t("meta.title")} />
    <meta property="og:description" content={$t("meta.description")} />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://lineum.io" />
    <meta property="og:image" content="https://lineum.io/social-preview.png" />
    <meta name="twitter:card" content="summary_large_image" />

    <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "Lineum Field Engine",
            "operatingSystem": "Any",
            "applicationCategory": "Systema Software",
            "description": "Continuous space particle dynamics simulator and API.",
            "offers": {
                "@type": "Offer",
                "price": "0"
            }
        }
    </script>
</svelte:head>

<nav>
    <div class="container nav-content">
        <a href="/" class="nav-logo">Lineum</a>

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
            <a href="/">{$t("nav.portal")}</a>
            <a href={SIMULACRUM_URL} target="simulacrum">{$t("nav.lab")}</a>
            <a href="/api-solutions" style="color: #38bdf8; font-weight: bold;"
                >{$t("nav.api")}</a
            >
            <a href="/#scientist" data-sveltekit-reload
                >{$t("sections.scientist.label")}</a
            >
            <a href="/wiki#faq" data-sveltekit-reload>FAQ</a>
            <a href="/support" class="nav-cta">{$t("nav.support")}</a>

            <div class="lang-switcher">
                {#each langs as lang}
                    <button
                        class="lang-btn"
                        class:active={$locale === lang.code}
                        on:click={() => changeLang(lang.code)}
                        title={lang.label}
                    >
                        {lang.code.toUpperCase()}
                    </button>
                {/each}
            </div>
        </div>
    </div>
</nav>

<div class="grid-bg"></div>

<main class:hud-pushed={$hudActive}>
    <slot />
</main>

<ResonanceDeck active={$hudActive} />
<CookieBanner />

<style>
    nav {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        padding: 1.5rem 0;
        z-index: 100;
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
        font-weight: 700;
        font-size: 1.2rem;
        letter-spacing: -0.05em;
        color: white;
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
    }

    .nav-links a:hover {
        color: white;
    }

    .nav-cta {
        background: var(--accent-color);
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }

    .lang-switcher {
        display: flex;
        gap: 0.2rem;
        background: rgba(255, 255, 255, 0.03);
        padding: 0.3rem 0.4rem;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        align-items: center;
    }

    .lang-btn {
        background: transparent;
        border: none;
        color: #666;
        font-size: 0.75rem;
        font-weight: 700;
        cursor: pointer;
        padding: 0.3rem 0.5rem;
        border-radius: 4px;
        transition: all 0.2s ease;
    }

    .lang-btn:hover {
        color: white;
        background: rgba(255, 255, 255, 0.05);
    }

    .lang-btn.active {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
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

    main {
        position: relative;
        z-index: 1;
        padding-top: var(--nav-height, 80px);
        transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    main.hud-pushed {
        transform: translateY(-20px);
    }

    main {
        position: relative;
        z-index: 1;
        padding-top: 80px;
        transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    main.hud-pushed {
        transform: translateY(-20px);
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
            padding: 2rem;
            gap: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            align-items: center;
        }

        .nav-links.mobile-open {
            display: flex;
        }

        .nav-links a {
            font-size: 1.2rem; /* Balanced size */
            padding: 0.5rem 0; /* Maintain touch target height */
            width: 100%; /* Full width for easier clicking */
            text-align: center;
        }

        .mobile-toggle {
            display: block; /* Visible on mobile */
        }

        main {
            padding-top: var(
                --nav-height,
                80px
            ); /* Standard padding is enough now */
        }
    }

    @media (min-width: 769px) {
        .mobile-toggle {
            display: none;
        }
    }
</style>
