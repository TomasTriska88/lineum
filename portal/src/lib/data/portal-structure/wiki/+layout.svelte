<script lang="ts">
    import { onMount } from "svelte";
    import WhitepaperWarningModal from "$lib/components/WhitepaperWarningModal.svelte";

    let showWarning = false;

    onMount(() => {
        const ack = sessionStorage.getItem(
            "lineum_whitepaper_warning_acknowledged",
        );
        console.log("Wiki Layout Mounted. Ack:", ack);
        // FORCE SHOW FOR DEBUG
        showWarning = true;
        /*
        if (!ack) {
            console.log("Showing warning modal");
            showWarning = true;
        }
        */
    });

    function handleAck() {
        sessionStorage.setItem(
            "lineum_whitepaper_warning_acknowledged",
            "true",
        );
        showWarning = false;
    }
</script>

<div
    style="position:fixed; top:100px; left:0; z-index:999999; background:red; color:white; padding: 10px;"
>
    DEBUG LAYOUT ACTIVE
</div>
{#if showWarning}
    <WhitepaperWarningModal onAck={handleAck} />
{/if}

<slot />
