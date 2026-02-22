<script>
    import "../app.css";
    import ResonanceDeck from "$lib/components/ResonanceDeck.svelte";
    import CookieBanner from "$lib/components/CookieBanner.svelte";
    import { hudActive } from "$lib/stores/hudStore";
    import { page } from "$app/stores"; // For closing menu on nav

    let menuOpen = false;

    function toggleMenu() {
        menuOpen = !menuOpen;
    }

    // Close menu when navigating
    $: if ($page.url.pathname) {
        menuOpen = false;
    }
</script>

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
            <a href="/wiki">Wiki</a>
            <a href="/wiki#faq">FAQ</a>
            <a href="https://simulacrum.lineum.io" target="simulacrum"
                >Simulacrum</a
            >
            <a href="/api-solutions" style="color: #38bdf8; font-weight: bold;"
                >API Solutions</a
            >
            <a href="/#scientist">For Scientists</a>
            <a href="/support" class="nav-cta">Support</a>
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
