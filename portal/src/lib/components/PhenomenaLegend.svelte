<script lang="ts">
    import { fade, scale } from "svelte/transition";

    let isOpen = false;

    const phenomena = [
        {
            id: "psi",
            label: "ψ Phase Colors",
            description:
                "The rotating hue in linon cores represents the complex phase angle arg(ψ).",
            color: "#00d2ff",
        },
        {
            id: "kappa",
            label: "Stability Islands",
            description:
                "Voronoi geometry showing regions of localized stability in the κ map substrate.",
            color: "#1a3a5a",
        },
        {
            id: "phi",
            label: "Field Memory",
            description:
                'The "Return Echo" (trailing ghosts) visualizes the persistence of the interaction field φ.',
            color: "#8a2be2",
        },
        {
            id: "warp",
            label: "Field Curvature",
            description:
                "Topological warping of the background represents the singular nature of vortex clusters.",
            color: "#ff00ff",
        },
        {
            id: "coupling",
            label: "Interaction Filaments",
            description:
                "Lines of tension between linons representing non-linear interaction coupling.",
            color: "#ff007f",
        },
    ];
</script>

<div
    class="legend-container"
    role="region"
    aria-label="Physics Legend"
    on:mouseenter={() => (isOpen = true)}
    on:mouseleave={() => (isOpen = false)}
>
    <div class="trigger-icon" class:active={isOpen}>
        <!-- Fallback SVG since I can't be sure about lucide-svelte -->
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
        >
            <circle cx="12" cy="12" r="10" /><path d="M12 16v-4" /><path
                d="M12 8h.01"
            />
        </svg>
    </div>

    {#if isOpen}
        <div
            class="legend-card"
            transition:scale={{ duration: 200, start: 0.9 }}
        >
            <header>
                <h3>Physics Reference</h3>
                <p>Emergent phenomena in Lineum</p>
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
        position: absolute;
        bottom: 24px;
        right: 24px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
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
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    .trigger-icon:hover,
    .trigger-icon.active {
        background: rgba(255, 255, 255, 0.08);
        color: #fff;
        border-color: rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
    }

    .legend-card {
        width: 320px;
        background: rgba(10, 10, 18, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
        transform-origin: bottom right;
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
