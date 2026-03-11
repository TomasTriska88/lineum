<script>
    export let buttonMode;
    export let currentMode;
    export let text;
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    
    function handleClick() {
        dispatch('select', buttonMode);
    }
</script>

<button
    class:active={currentMode === buttonMode}
    on:click={handleClick}
>
    {text}
</button>

<style>
    button {
        background: transparent;
        border: 1px solid transparent;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 6px 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        border-radius: 4px;
    }

    button:hover {
        color: #00ffff;
        background: rgba(0, 255, 255, 0.05);
    }

    button.active {
        color: #00ffff;
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.1);
    }
</style>
