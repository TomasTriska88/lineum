<script lang="ts">
    import { onMount } from "svelte";
    import { content } from "$lib/content";
    import Dialog from "$lib/components/ui/Dialog.svelte";
    import { isChatOpen } from "$lib/stores/hudStore";

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

        <svelte:fragment slot="actions">
            <button class="btn-secondary" onclick={onAck}>
                {content.whitepaper_warning.ack_label}
            </button>
            <button
                class="btn-lina"
                onclick={() => {
                    $isChatOpen = true;
                    onAck();
                }}
            >
                ✨ Ask Lina Instead
            </button>
        </svelte:fragment>
    </Dialog>
{/if}

<style>
    p {
        margin-bottom: 1rem;
    }
    p:last-child {
        margin-bottom: 0;
    }

    .btn-secondary {
        background: transparent;
        color: #888;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        font-size: 0.8rem;
        font-family: var(--font-mono, monospace);
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.2s;
    }

    .btn-secondary:hover {
        color: #fff;
        border-color: rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.05);
    }

    .btn-lina {
        background: var(--accent-color, #7eb8ff);
        color: #000;
        border: 1px solid var(--accent-color, #7eb8ff);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        font-size: 0.8rem;
        font-family: var(--font-mono, monospace);
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.2s;
        box-shadow: 0 0 15px rgba(126, 184, 255, 0.3);
    }

    .btn-lina:hover {
        background: #fff;
        color: var(--accent-color, #7eb8ff);
        box-shadow: 0 0 25px rgba(126, 184, 255, 0.5);
        transform: translateY(-1px);
    }
</style>
