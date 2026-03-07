<script>
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    export let isOpen = false;
    export let title = "Confirm Action";
    export let message = "Are you sure you want to proceed?";
    export let confirmText = "Confirm";
    export let cancelText = "Cancel";

    function onConfirm() {
        isOpen = false;
        dispatch("confirm");
    }

    function onCancel() {
        isOpen = false;
        dispatch("cancel");
    }
</script>

{#if isOpen}
    <div class="modal-backdrop">
        <div class="confirm-dialog" role="dialog" aria-modal="true">
            <div class="dialog-header">
                <h3>{title}</h3>
            </div>
            <div class="dialog-body">
                <p>{message}</p>
            </div>
            <div class="dialog-actions">
                <button class="cancel-btn" on:click={onCancel}
                    >{cancelText}</button
                >
                <button class="confirm-btn" on:click={onConfirm}
                    >{confirmText}</button
                >
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.85);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        backdrop-filter: blur(8px);
    }
    .confirm-dialog {
        background: #0d0d0d;
        border: 1px solid #ff4444;
        max-width: 450px;
        width: 90%;
        color: #fff;
        box-shadow:
            0 10px 40px rgba(0, 0, 0, 0.8),
            0 0 20px rgba(255, 68, 68, 0.2);
        display: flex;
        flex-direction: column;
        animation: slide-up 0.2s ease-out;
    }
    @keyframes slide-up {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .dialog-header {
        padding: 16px 20px;
        border-bottom: 1px solid rgba(255, 68, 68, 0.2);
        background: rgba(255, 0, 0, 0.05);
    }
    .dialog-header h3 {
        margin: 0;
        color: #ff4444;
        letter-spacing: 2px;
        font-size: 1.1rem;
        text-transform: uppercase;
    }
    .dialog-body {
        padding: 20px;
    }
    .dialog-body p {
        margin: 0;
        color: #ddd;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .dialog-actions {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        padding: 16px 20px;
        background: #050505;
        border-top: 1px solid #222;
    }
    .dialog-actions button {
        padding: 8px 16px;
        cursor: pointer;
        border: none;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.8rem;
        transition: 0.2s;
    }
    .cancel-btn {
        background: transparent;
        color: #aaa;
        border: 1px solid #555 !important;
    }
    .cancel-btn:hover {
        background: #222;
        color: #fff;
        border-color: #888 !important;
    }
    .confirm-btn {
        background: #ff0000;
        color: #fff;
    }
    .confirm-btn:hover {
        background: #ff4444;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
    }
</style>
