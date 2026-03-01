<script lang="ts">
    import { onMount } from "svelte";
    import Dialog from "$lib/components/ui/Dialog.svelte";
    import { hudActive, isChatOpen } from "$lib/stores/hudStore";
    import * as m from "$lib/paraglide/messages.js";

    let showWarning = $state(false);

    onMount(() => {
        const hasAcknowledged = sessionStorage.getItem("wiki_warning_ack");
        if (!hasAcknowledged) {
            showWarning = true;
        }
    });

    function handleAcknowledge() {
        sessionStorage.setItem("wiki_warning_ack", "true");
        showWarning = false;
    }

    function handleAskLina() {
        sessionStorage.setItem("wiki_warning_ack", "true");
        showWarning = false;
        $hudActive = true;
        $isChatOpen = true;
    }
</script>

{#if showWarning}
    <Dialog title={m.whitepaper_warning_title()}>
        <div class="warning-text">
            <p>{@html m.whitepaper_warning_paragraphs_0()}</p>
            <p>{@html m.whitepaper_warning_paragraphs_1()}</p>
            <p>{@html m.whitepaper_warning_paragraphs_2()}</p>
            <p>{@html m.whitepaper_warning_paragraphs_3()}</p>
        </div>

        <svelte:fragment slot="actions">
            <button class="btn btn-ask-lina" onclick={handleAskLina}>
                ✨ Ask Lina Instead
            </button>
            <button class="btn btn-confirm" onclick={handleAcknowledge}>
                {m.whitepaper_warning_ack_label()}
            </button>
        </svelte:fragment>
    </Dialog>
{/if}

<style>
    .warning-text {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .warning-text p {
        margin: 0;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.8);
    }

    .btn-ask-lina {
        background: transparent;
        color: var(--accent-color, #7eb8ff);
        border: 1px solid rgba(126, 184, 255, 0.3);
    }

    .btn-ask-lina:hover {
        background: rgba(126, 184, 255, 0.1);
        border-color: rgba(126, 184, 255, 0.6);
    }

    .btn-confirm {
        background: var(--accent-color, #7eb8ff);
        color: #0a0a0f;
    }

    .btn-confirm:hover {
        filter: brightness(1.2);
    }
</style>
