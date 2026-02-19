<script lang="ts">
    import { scale } from "svelte/transition";

    export let title: string;
    export let subtitle: string;
    export let items: {
        id: string;
        label: string;
        description: string;
        color: string;
    }[];
    export let faq: {
        q: string;
        a: string;
    }[] = [];

    let isOpen = false;
    let containerEl: HTMLDivElement;

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
    aria-label="Visualization Legend"
    bind:this={containerEl}
>
    <div class="trigger-wrapper">
        <button
            class="trigger-icon"
            class:active={isOpen}
            on:click|stopPropagation={toggle}
            aria-label="Toggle legend"
            aria-expanded={isOpen}
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
            aria-modal="false"
            tabindex="-1"
        >
            <header>
                <h3>{title}</h3>
                <p>{subtitle}</p>
            </header>

            <ul class="legend-list">
                {#each items as item}
                    <li class="legend-item">
                        <div class="visual-container">
                            {#if item.id === "psi"}
                                <!-- Linon: Pulsing core -->
                                <div
                                    class="visual-linon"
                                    style="--color: {item.color}"
                                ></div>
                            {:else if item.id === "kappa"}
                                <!-- Safe Zones: Gradient map -->
                                <div class="visual-kappa"></div>
                            {:else if item.id === "phi"}
                                <!-- Trails: Comet tail -->
                                <div
                                    class="visual-phi"
                                    style="--color: {item.color}"
                                ></div>
                            {:else if item.id === "warp"}
                                <!-- Warp: Halo distortion -->
                                <div
                                    class="visual-warp"
                                    style="--color: {item.color}"
                                ></div>
                            {:else if item.id === "tension"}
                                <!-- Tension: Needle indicator -->
                                <div
                                    class="visual-tension"
                                    style="--color: {item.color}"
                                ></div>
                            {:else if item.id === "coupling"}
                                <!-- Bonds: Connected link -->
                                <div
                                    class="visual-coupling"
                                    style="--color: {item.color}"
                                ></div>
                            {/if}
                        </div>
                        <div class="content">
                            <h4>{item.label}</h4>
                            <p>{@html item.description}</p>
                        </div>
                    </li>
                {/each}
            </ul>

            {#if faq && faq.length > 0}
                <div class="faq-section">
                    <header class="faq-header">
                        <h4>Scientific Context (FAQ)</h4>
                    </header>
                    <div class="faq-list">
                        {#each faq as entry}
                            <div class="faq-item">
                                <span class="question">{entry.q}</span>
                                <p class="answer">{@html entry.a}</p>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}
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
        max-width: calc(100vw - 2rem); /* Safety for small screens */

        /* Scrollbar styling */
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 255, 255, 0.2) rgba(0, 0, 0, 0.1);
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

    .legend-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 14px;
    }

    .legend-item {
        display: flex;
        align-items: center; /* Center visuals vertically with title */
        background: rgba(255, 255, 255, 0.02);
        padding: 10px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: background 0.2s ease;
    }

    .legend-item:hover {
        background: rgba(255, 255, 255, 0.07);
    }

    /* Visualization Container */
    .visual-container {
        width: 32px;
        height: 32px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
        margin-right: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        overflow: hidden;
    }

    /* 1. Linon (Emergent Life) - Pulsing Core */
    /* 1. Linon (Emergent Life) - Point Singularity */
    .visual-linon {
        width: 10px;
        height: 10px;
        background: radial-gradient(
            circle,
            #fff 0%,
            var(--color) 40%,
            transparent 80%
        );
        border-radius: 50%;
        box-shadow: 0 0 4px var(--color); /* Sharpened shadow */
        animation: psi-pulse 2s infinite ease-in-out;
        position: relative;
    }

    @keyframes psi-pulse {
        0%,
        100% {
            transform: scale(0.9);
            opacity: 0.8;
        }
        50% {
            transform: scale(1.1);
            opacity: 1;
        }
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }

    /* 2. Safe Zones (κ-Field) - Stability Landscape */
    .visual-kappa {
        width: 100%;
        height: 100%;
        background: #000;
        position: relative;
        overflow: hidden;
        border-radius: 4px;
        box-shadow: inset 0 0 4px rgba(0, 0, 0, 0.5);
    }
    .visual-kappa::before {
        content: "";
        position: absolute;
        inset: -50%;
        background: radial-gradient(
            circle at center,
            transparent 10%,
            #1a3a5a 40%,
            #ff00ff 90%
        );
        animation: kappa-mist 10s infinite alternate ease-in-out;
        opacity: 0.9;
    }

    @keyframes kappa-mist {
        0% {
            opacity: 0.2;
            transform: scale(0.6) rotate(0deg);
            filter: blur(3px);
        }
        50% {
            opacity: 0.6;
            transform: scale(1) rotate(20deg);
            filter: blur(1px);
        }
        100% {
            opacity: 1;
            transform: scale(1.3) rotate(-20deg);
            filter: blur(0px);
            background-color: #ff00ff22;
        }
    }

    /* 3. Ghost Trails (φ-Memory) - Compact Wake */
    .visual-phi {
        width: 10px;
        height: 2px;
        background: linear-gradient(90deg, var(--color) 0%, transparent 100%);
        border-radius: 4px;
        opacity: 0.7;
        filter: blur(0.2px);
        box-shadow: 0 0 2px var(--color);
        animation: comet-tail 2.5s infinite ease-in-out;
    }

    @keyframes comet-tail {
        0%,
        100% {
            transform: scaleX(0.85);
            opacity: 0.6;
        }
        50% {
            transform: scaleX(1.3);
            opacity: 1;
        }
    }

    /* 4. Warp (Space Warp) - Topographic Contour Lines */
    .visual-warp {
        width: 22px;
        height: 20px;
        border: 0.5px solid var(--color);
        border-radius: 64% 36% 27% 73% / 55% 58% 42% 45%;
        position: relative;
        filter: blur(0.3px);
        box-shadow: 0 0 6px var(--color);
        animation:
            warp-morph 12s infinite ease-in-out,
            color-cycle 10s infinite alternate;
        opacity: 0.8;
    }
    /* Inner ring - more irregular and offset */
    .visual-warp::after {
        content: "";
        position: absolute;
        inset: 4.5px;
        border: 0.5px solid var(--color);
        border-radius: 36% 64% 73% 27% / 45% 42% 58% 55%;
        opacity: 0.4;
        animation: warp-morph 9s infinite reverse ease-in-out;
    }

    @keyframes warp-morph {
        0%,
        100% {
            border-radius: 64% 36% 27% 73% / 55% 58% 42% 45%;
            transform: scale(1) rotate(0deg) translate(0, 0);
        }
        33% {
            border-radius: 36% 64% 73% 27% / 45% 42% 58% 55%;
            transform: scale(1.08, 0.92) rotate(12deg) translate(1px, -1px);
        }
        66% {
            border-radius: 45% 55% 36% 64% / 73% 27% 58% 42%;
            transform: scale(0.92, 1.08) rotate(-8deg) translate(-1px, 1px);
        }
    }

    @keyframes color-cycle {
        0% {
            border-color: #ff00ff;
            filter: drop-shadow(0 0 4px #ff00ff);
        }
        100% {
            border-color: #8a2be2;
            filter: drop-shadow(0 0 4px #8a2be2);
        }
    }

    /* 4.5 Tension Vector - Geodetic Needle */
    .visual-tension {
        width: 1px;
        height: 18px;
        background: var(--color);
        box-shadow: 0 0 8px var(--color);
        animation: needle-pulse 1.5s infinite ease-in-out;
        position: relative;
        transform-origin: bottom;
    }
    .visual-tension::before {
        content: "";
        position: absolute;
        bottom: 0;
        left: -1px;
        width: 3px;
        height: 3px;
        background: #fff;
        border-radius: 50%;
    }

    @keyframes needle-pulse {
        0%,
        100% {
            opacity: 0.35;
            transform: scaleY(0.6) translateY(2px);
            filter: blur(0.5px);
        }
        50% {
            opacity: 1;
            transform: scaleY(1.3) translateY(-2px);
            filter: blur(0px);
        }
    }

    /* 4.5 Tension Vector - Geodetic Force (Dashed) */
    .visual-tension {
        width: 1px;
        height: 20px;
        background: repeating-linear-gradient(
            to bottom,
            var(--color) 0,
            var(--color) 4px,
            transparent 4px,
            transparent 8px
        );
        box-shadow: 0 0 8px var(--color);
        animation: force-flow 1.5s infinite linear;
        position: relative;
        transform-origin: bottom;
    }
    .visual-tension::before {
        content: "";
        position: absolute;
        bottom: -1px;
        left: -2px;
        width: 3px;
        height: 3px;
        border-left: 1px solid #fff;
        border-top: 1px solid #fff;
        transform: rotate(45deg);
        opacity: 0.8;
    }

    @keyframes force-flow {
        0% {
            background-position: 0 0;
            opacity: 0.6;
        }
        50% {
            opacity: 1;
        }
        100% {
            background-position: 0 16px;
            opacity: 0.6;
        }
    }

    /* 5. Coupling (Bonds) - Connection Line */
    .visual-coupling {
        width: 20px;
        height: 1px;
        background: var(--color);
        position: relative;
        opacity: 0.6;
        box-shadow: 0 0 6px var(--color);
    }
    .visual-coupling::before,
    .visual-coupling::after {
        content: "";
        position: absolute;
        width: 3px;
        height: 3px;
        background: #fff;
        border-radius: 50%;
        top: -1px;
    }
    .visual-coupling::before {
        left: -2px;
    }
    .visual-coupling::after {
        right: -2px;
    }

    @keyframes pulse {
        0%,
        100% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.3);
            opacity: 0.7;
        }
    }

    .content h4 {
        margin: 0;
        font-size: 0.9rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2px;
    }

    .content p {
        margin: 0;
        font-size: 0.75rem;
        line-height: 1.4;
        color: rgba(255, 255, 255, 0.5);
    }

    /* FAQ Section */
    .faq-section {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .faq-header h4 {
        margin: 0 0 10px;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255, 255, 255, 0.4);
    }

    .faq-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .faq-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .question {
        font-size: 0.8rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.3;
    }

    .answer {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.55);
        line-height: 1.4;
        margin: 0;
    }
</style>
