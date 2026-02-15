<script lang="ts">
    import { scale } from "svelte/transition";
    import { content } from "$lib/content";

    let isOpen = false;
    let containerEl: HTMLDivElement;

    const phenomena = content.legend.items;

    function toggle() {
        isOpen = !isOpen;
    }

    function handleClickOutside(e: MouseEvent) {
        if (isOpen && containerEl && !containerEl.contains(e.target as Node)) {
            isOpen = false;
        }
    }
</script>

<svelte:window on:click={handleClickOutside} />

<div
    class="legend-container"
    role="region"
    aria-label="Physics Legend"
    bind:this={containerEl}
>
    <div class="trigger-wrapper">
        <button
            class="trigger-icon"
            class:active={isOpen}
            on:click|stopPropagation={toggle}
            aria-label="Toggle legend"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
            >
                <circle cx="12" cy="12" r="10" /><path d="M12 16v-4" /><path
                    d="M12 8h.01"
                />
            </svg>
        </button>
    </div>

    {#if isOpen}
        <div
            class="legend-card"
            transition:scale={{ duration: 200, start: 0.9 }}
            on:click|stopPropagation
            on:keydown|stopPropagation
            role="dialog"
        >
            <header>
                <h3>{content.legend.title}</h3>
                <p>{content.legend.subtitle}</p>
            </header>

            <ul class="phenomena-list">
                {#each phenomena as item}
                    <li class="phenomena-item">
                        <div
                            class="dot"
                            style="background-color: {item.color}"
                        ></div>
                        <div class="content">
                            <h4>{item.label}</h4>
                            <p>{item.description}</p>
                        </div>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
</div>

<style>
    .legend-container {
        position: relative;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        margin-left: auto;
    }

    .trigger-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
    }

    .trigger-icon {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: rgba(15, 15, 25, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        cursor: pointer;
        padding: 0;
    }

    .trigger-icon:hover,
    .trigger-icon.active {
        background: rgba(255, 255, 255, 0.08);
        color: #fff;
        border-color: rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
    }

    .legend-card {
        position: absolute;
        top: 100%;
        right: 0;
        width: 320px;
        max-height: calc(100vh - 250px);
        overflow-y: auto;
        background: rgba(10, 10, 18, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-top: 12px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
        transform-origin: top right;
    }

    header {
        margin-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 12px;
    }

    header h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #fff;
        letter-spacing: 0.5px;
    }

    header p {
        margin: 4px 0 0;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.5);
    }

    .phenomena-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 14px;
    }

    .phenomena-item {
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-top: 6px;
        flex-shrink: 0;
        box-shadow: 0 0 10px currentColor;
    }

    .content h4 {
        margin: 0;
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 600;
    }

    .content p {
        margin: 2px 0 0;
        font-size: 0.75rem;
        line-height: 1.4;
        color: rgba(255, 255, 255, 0.5);
    }
</style>
