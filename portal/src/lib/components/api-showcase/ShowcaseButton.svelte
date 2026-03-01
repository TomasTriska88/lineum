<script lang="ts">
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    export let status: "idle" | "running" | "done" = "idle";
    export let idleText = "Start Simulation";
    export let runningText = "Simulating...";
    export let doneText = "Reset";
    export let theme: "sky" | "rose" | "emerald" | "purple" = "sky";
    export let disabled = false;

    const themeMap = {
        sky: {
            bg: "bg-sky-500/10 hover:bg-sky-500/20",
            text: "text-sky-400",
            border: "border-sky-500/30",
            idleDot: "bg-sky-400 animate-pulse",
            runningDot: "bg-slate-400 animate-pulse",
            doneDot: "bg-emerald-400",
        },
        rose: {
            bg: "bg-rose-500/10 hover:bg-rose-500/20",
            text: "text-rose-400",
            border: "border-rose-500/30",
            idleDot: "bg-rose-400 animate-pulse",
            runningDot: "bg-amber-400 animate-pulse",
            doneDot: "bg-emerald-400",
        },
        emerald: {
            bg: "bg-emerald-500/10 hover:bg-emerald-500/20",
            text: "text-emerald-400",
            border: "border-emerald-500/30",
            idleDot: "bg-emerald-400 animate-pulse",
            runningDot: "bg-rose-400 animate-pulse",
            doneDot: "bg-emerald-400",
        },
        purple: {
            bg: "bg-purple-500/10 hover:bg-purple-500/20",
            text: "text-purple-400",
            border: "border-purple-500/30",
            idleDot: "bg-purple-400 animate-pulse",
            runningDot: "bg-amber-400 animate-pulse",
            doneDot: "bg-emerald-400",
        },
    };

    $: styles = themeMap[theme];

    function handleClick() {
        if (!disabled) dispatch("click");
    }
</script>

<button
    on:click={handleClick}
    {disabled}
    class="px-5 py-2.5 {styles.bg} {styles.text} border {styles.border} rounded-full font-bold text-xs tracking-widest uppercase transition-all flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
>
    {#if status === "idle"}
        <span class="w-2 h-2 rounded-full {styles.idleDot}"></span>
        {idleText}
    {:else if status === "running"}
        <span class="w-2 h-2 rounded-full {styles.runningDot}"></span>
        {runningText}
    {:else if status === "done"}
        <span class="w-2 h-2 rounded-full {styles.doneDot}"></span>
        {doneText}
    {/if}
</button>
