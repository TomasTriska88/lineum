<script lang="ts">
    import { onMount } from "svelte";
    import { content } from "$lib/content";
    import Dialog from "$lib/components/ui/Dialog.svelte";

    export let onAck: () => void;

    let mounted = false;

    onMount(() => {
        mounted = true;
    });
</script>

{#if mounted}
    <Dialog
        title={content.whitepaper_warning.title}
        variant="danger"
        confirmLabel={content.whitepaper_warning.ack_label}
        showCancel={false}
        onconfirm={onAck}
    >
        {#each content.whitepaper_warning.paragraphs as p}
            <p>{@html p}</p>
        {/each}
    </Dialog>
{/if}

<style>
    p {
        margin-bottom: 1rem;
    }
    p:last-child {
        margin-bottom: 0;
    }
</style>
