<script lang="ts">
    import { fade, fly } from "svelte/transition";
    import { portal } from "$lib/actions/portal";
    import { createEventDispatcher } from "svelte";

    export let title: string;
    export let variant: "info" | "danger" = "info";
    export let confirmLabel = "Confirm";
    export let cancelLabel = "Cancel";
    export let showCancel = true;

    const dispatch = createEventDispatcher();

    function handleConfirm() {
        dispatch("confirm");
    }

    function handleCancel() {
        dispatch("cancel");
    }
</script>

<div class="dialog-backdrop" use:portal transition:fade={{ duration: 200 }}>
    <div
        class="dialog-window {variant}"
        transition:fly={{ y: 20, duration: 300 }}
    >
        <div class="dialog-header">
            {#if variant === "danger"}
                <span class="icon">⚠️</span>
            {:else}
                <span class="icon">ℹ️</span>
            {/if}
            <h2>{title}</h2>
        </div>

        <div class="dialog-content">
            <slot />
        </div>

        <div class="dialog-actions">
            {#if showCancel}
                <button class="btn btn-cancel" on:click={handleCancel}
                    >{cancelLabel}</button
                >
            {/if}
            <button class="btn btn-confirm" on:click={handleConfirm}
                >{confirmLabel}</button
            >
        </div>
    </div>
</div>

<style>
    .dialog-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(12px);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }

    .dialog-window {
        background: rgba(10, 10, 14, 0.95);
        border: 1px solid rgba(124, 58, 237, 0.3); /* Default accent violet */
        box-shadow:
            0 0 0 1px rgba(0, 0, 0, 0.5),
            0 20px 50px rgba(0, 0, 0, 0.7),
            0 0 30px rgba(124, 58, 237, 0.1);
        max-width: 480px;
        width: 100%;
        border-radius: 16px;
        overflow: hidden;
        font-family: var(--font-sans, sans-serif);
    }

    .dialog-window.danger {
        border-color: rgba(255, 69, 58, 0.4);
        box-shadow:
            0 0 0 1px rgba(0, 0, 0, 0.5),
            0 20px 50px rgba(0, 0, 0, 0.7),
            0 0 30px rgba(255, 69, 58, 0.15);
    }

    .dialog-header {
        background: rgba(255, 255, 255, 0.03);
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .danger .dialog-header {
        background: rgba(255, 69, 58, 0.08);
        border-bottom-color: rgba(255, 69, 58, 0.15);
    }

    h2 {
        font-size: 1rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #fff;
        font-family: var(--font-mono, monospace);
    }

    .danger h2 {
        color: #ff453a;
        text-shadow: 0 0 10px rgba(255, 69, 58, 0.4);
    }

    .icon {
        font-size: 1.25rem;
        filter: grayscale(0.2);
    }

    .dialog-content {
        padding: 2rem 1.5rem;
        color: #ccc;
        font-size: 0.95rem;
        line-height: 1.7;
    }

    .dialog-actions {
        padding: 1.25rem 1.5rem;
        background: rgba(0, 0, 0, 0.2);
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }

    .btn {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        font-size: 0.8rem;
        border: 1px solid transparent;
        transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
        font-family: var(--font-mono, monospace);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .btn-cancel {
        background: transparent;
        color: #888;
        border-color: rgba(255, 255, 255, 0.1);
    }

    .btn-cancel:hover {
        color: #fff;
        border-color: rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.05);
    }

    .btn-confirm {
        background: var(--accent-color, #7c3aed);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
    }

    .danger .btn-confirm {
        background: rgba(255, 69, 58, 0.1);
        color: #ff453a;
        border-color: rgba(255, 69, 58, 0.5);
        box-shadow: 0 0 15px rgba(255, 69, 58, 0.1);
    }

    .danger .btn-confirm:hover {
        background: rgba(255, 69, 58, 0.2);
        box-shadow: 0 0 25px rgba(255, 69, 58, 0.3);
        transform: translateY(-1px);
    }

    .info .btn-confirm:hover {
        filter: brightness(1.2);
        box-shadow: 0 0 25px rgba(124, 58, 237, 0.5);
        transform: translateY(-1px);
    }
</style>
