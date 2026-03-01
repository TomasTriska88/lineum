<script lang="ts">
    import ResonanceDeck from "$lib/components/ResonanceDeck.svelte";
    import CookieBanner from "$lib/components/CookieBanner.svelte";
    import { hudActive } from "$lib/stores/hudStore";
    import WikiWarning from "$lib/components/WikiWarning.svelte";
</script>

<WikiWarning />

<slot />
