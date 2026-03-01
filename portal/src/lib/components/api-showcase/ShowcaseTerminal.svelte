<script lang="ts">
    export let title = "Live Audit Terminal";
    export let badge = "SECURE SHELL";
    export let badgeColorClass = "text-emerald-500";
    export let status: "idle" | "running" | "done" = "idle";

    // Accept either array of strings, or objects with time/color/msg
    export let logs: any[] = [];
    export let emptyText = "Waiting for input...";
    export let primaryColorClass = "text-emerald-400";
</script>

<div
    class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-start gap-4 h-full min-h-[160px] font-mono shadow-inner group transition-all duration-300"
>
    <!-- Header -->
    <div
        class="text-xs text-slate-500 border-b border-slate-800 pb-2 uppercase tracking-widest font-bold flex justify-between"
    >
        <span>{title}</span>
        <span class={badgeColorClass}>{badge}</span>
    </div>

    <!-- Layout Container: Flex column on mobile, Flex row on larger screens if there's a side panel -->
    <div class="flex flex-col md:flex-row gap-6 w-full h-full">
        <!-- Logs Box -->
        <div
            class="flex-1 flex flex-col justify-end text-xs {primaryColorClass} gap-1.5 overflow-hidden h-[120px]"
        >
            {#if logs.length === 0}
                <div class="text-slate-600 opacity-50 animate-pulse">
                    {emptyText}
                </div>
            {:else}
                <!-- Render logs from bottom up visually by rendering array. If array is already ordered correctly, we just iterate it. -->
                {#each logs as log}
                    <div class="animate-fade-in flex gap-3">
                        {#if typeof log === "string"}
                            <span class="break-all">&gt; {log}</span>
                        {:else}
                            {#if log.time}
                                <span class="text-slate-600 shrink-0"
                                    >[{log.time}]</span
                                >
                            {/if}
                            <span
                                class="{log.color ||
                                    primaryColorClass} break-all"
                                >{log.msg}</span
                            >
                        {/if}
                    </div>
                {/each}
            {/if}

            {#if status === "running"}
                <div class="animate-pulse opacity-50 pt-1 text-slate-500">
                    &gt; _
                </div>
            {/if}
        </div>

        <!-- Optional Side Panel (NIST, Metrics, On-Chain steps) -->
        {#if $$slots["side-panel"]}
            <div
                class="w-full md:w-48 lg:w-56 flex flex-col gap-2 justify-end pb-1 border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6"
            >
                <slot name="side-panel"></slot>
            </div>
        {/if}
    </div>

    <!-- Optional full width slot at bottom (metrics) -->
    {#if $$slots["metrics"]}
        <div class="mt-4 pt-4 border-t border-slate-800/50">
            <slot name="metrics"></slot>
        </div>
    {/if}
</div>

<style>
    @keyframes fade-in {
        from {
            opacity: 0;
            transform: translateY(5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .animate-fade-in {
        animation: fade-in 0.15s ease-out forwards;
    }
</style>
