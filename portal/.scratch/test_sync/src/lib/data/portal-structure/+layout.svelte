<script lang="ts">
    import { ParaglideJS } from "@inlang/paraglide-sveltekit";
    import { i18n } from "$lib/i18n";

    import "../app.css";
    import ResonanceDeck from "$lib/components/ResonanceDeck.svelte";
    import CookieBanner from "$lib/components/CookieBanner.svelte";
    import Navigation from "$lib/components/Navigation.svelte";
    import { hudActive } from "$lib/stores/hudStore";
    import * as m from "$lib/paraglide/messages.js";
</script>

<svelte:head>
    <meta property="og:title" content={m.meta_title()} />
    <meta property="og:description" content={m.meta_description()} />
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

<ParaglideJS {i18n}>
    <Navigation />

    <div class="grid-bg"></div>

    <main class:hud-pushed={$hudActive}>
        <slot />
    </main>

    <ResonanceDeck active={$hudActive} />
    <CookieBanner />
</ParaglideJS>

<style>
    main {
        position: relative;
        z-index: 1;
        padding-top: var(--nav-height, 80px);
        transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    main.hud-pushed {
        transform: translateY(-20px);
    }

    @media (max-width: 768px) {
        main {
            padding-top: var(
                --nav-height,
                80px
            ); /* Standard padding is enough now */
        }
    }
</style>
