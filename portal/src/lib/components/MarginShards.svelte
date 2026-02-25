<script lang="ts">
    import { fade, scale } from "svelte/transition";
    import { onMount } from "svelte";
    import { t } from "$lib/i18n";

    export let insights: { id: string; selector: string; text: string }[] = [];

    let activeInsight: string | null = null;
    let positions: { [key: string]: { top: number; side: "left" | "right" } } =
        {};

    onMount(() => {
        const updatePositions = () => {
            insights.forEach((insight, index) => {
                const el = document.querySelector(insight.selector);
                if (el) {
                    const rect = el.getBoundingClientRect();
                    const scrollTop =
                        window.pageYOffset ||
                        document.documentElement.scrollTop;
                    positions[insight.id] = {
                        top: rect.top + scrollTop + rect.height / 2 - 15,
                        side: index % 2 === 0 ? "left" : "right",
                    };
                }
            });
            positions = { ...positions };
        };

        updatePositions();
        window.addEventListener("resize", updatePositions);
        return () => window.removeEventListener("resize", updatePositions);
    });

    function showInsight(id: string) {
        activeInsight = activeInsight === id ? null : id;
    }
</script>

<div class="shards-container">
    {#each insights as insight}
        {#if positions[insight.id]}
            <button
                class="shard-trigger {positions[insight.id].side}"
                style="top: {positions[insight.id].top}px"
                on:click={() => showInsight(insight.id)}
                type="button"
                aria-label="Toggle explorer insight"
            >
                <div class="shard-sparkle">✨</div>

                {#if activeInsight === insight.id}
                    <div
                        class="insight-popover {positions[insight.id].side}"
                        in:scale={{ duration: 300, start: 0.8 }}
                    >
                        <div class="popover-header">
                            {$t("lina.insight_header")}
                        </div>
                        <div class="popover-content">{insight.text}</div>
                    </div>
                {/if}
            </button>
        {/if}
    {/each}
</div>

<style>
    .shards-container {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 100;
    }

    .shard-trigger {
        position: absolute;
        width: 30px;
        height: 30px;
        pointer-events: auto;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        background: none;
        border: none;
        padding: 0;
    }

    .shard-trigger.left {
        left: 2rem;
    }
    .shard-trigger.right {
        right: 2rem;
    }

    .shard-sparkle {
        font-size: 20px;
        line-height: 1;
        color: #0070f3;
        filter: drop-shadow(0 0 5px rgba(0, 112, 243, 0.5));
        animation: pulse-sparkle 2s infinite ease-in-out;
        user-select: none;
    }

    @keyframes pulse-sparkle {
        0%,
        100% {
            filter: drop-shadow(0 0 5px rgba(0, 112, 243, 0.5)) brightness(1);
            transform: scale(1);
        }
        50% {
            filter: drop-shadow(0 0 15px rgba(0, 112, 243, 0.8)) brightness(1.5);
            transform: scale(1.2);
        }
    }

    .insight-popover {
        position: absolute;
        width: 280px;
        background: rgba(15, 15, 15, 0.95);
        backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
        z-index: 1000;
        text-align: left;
    }

    .insight-popover.left {
        left: 45px;
        top: 0;
    }
    .insight-popover.right {
        right: 45px;
        top: 0;
    }

    .popover-header {
        font-size: 0.6rem;
        font-weight: 800;
        color: #0070f3;
        letter-spacing: 0.15em;
        margin-bottom: 0.5rem;
    }

    .popover-content {
        color: #eee;
        font-size: 0.85rem;
        line-height: 1.6;
    }

    @media (max-width: 1200px) {
        .shard-trigger {
            display: none;
        }
    }
</style>
