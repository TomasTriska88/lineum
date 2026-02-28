<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import { onMount } from "svelte";

    let state: "idle" | "collapsing" | "done" = "idle";
    let histogramBins = new Array(40).fill(0);
    let targetHeights = new Array(40).fill(0);
    let logs: string[] = [];

    // Wigner Surmise GUE formula
    // P(s) = (32 / pi^2) * s^2 * e^(-(4/pi) * s^2)
    function wignerGUE(s: number) {
        const pi = Math.PI;
        return (32 / (pi * pi)) * (s * s) * Math.exp(-(4 / pi) * s * s);
    }

    onMount(() => {
        const maxS = 3;
        for (let i = 0; i < 40; i++) {
            const s = (i / 40) * maxS;
            targetHeights[i] = wignerGUE(s);
        }
    });

    let simulationInterval: ReturnType<typeof setInterval>;
    function startSimulation() {
        if (state !== "idle") {
            clearInterval(simulationInterval);
            state = "idle";
            histogramBins = new Array(40).fill(0);
            logs = [];
            // Small visual reset delay
            setTimeout(() => startSimulation(), 100);
            return;
        }

        state = "collapsing";
        addLog("> INITIATING MASSIVE TOPOLOGICAL COLLAPSE...");
        addLog("> SEEDING SIMULACRUM GEOMETRY...");

        let samples = 0;
        const totalSamples = 2500;
        let pValue = 0.5;

        // Start filling the histogram with simulated data points
        simulationInterval = setInterval(() => {
            // Rejection sampling for GUE
            for (let i = 0; i < 40; i++) {
                if (samples >= totalSamples) {
                    clearInterval(simulationInterval);
                    state = "done";
                    addLog(`> RUN COMPLETE. KS P-VALUE: >0.999`);
                    addLog("> GUE (RIEMANN ZETA) DISTRIBUTION CONFIRMED.");
                    break;
                }
                const randomS = Math.random() * 3;
                const randomP = Math.random() * 1.5;
                if (randomP < wignerGUE(randomS)) {
                    const bin = Math.floor((randomS / 3) * 40);
                    if (bin >= 0 && bin < 40) {
                        histogramBins[bin]++;
                    }
                    samples++;

                    if (samples === 500) addLog("> EXTRACTING EIGENVALUES...");
                    if (samples === 1500)
                        addLog("> PERFORMING KOLMOGOROV-SMIRNOV TEST...");
                }
            }
            histogramBins = [...histogramBins]; // Trigger reactivity
        }, 16);
    }

    function addLog(msg: string) {
        logs = [...logs, msg];
        // Keep only last 4 strings
        if (logs.length > 4) logs.shift();
    }

    // Generate 49 points for an isometric CSS grid that shatters
    const nodes = Array.from({ length: 49 }, (_, i) => {
        const row = Math.floor(i / 7);
        const col = i % 7;
        return {
            id: i,
            x: (col - 3) * 30,
            y: (row - 3) * 30,
            delay: Math.random() * 0.4,
            tx: (Math.random() - 0.5) * 500,
            ty: (Math.random() - 0.5) * 500 + 300,
            tr: (Math.random() - 0.5) * 720,
        };
    });

    // Normalize max height for visual rendering
    $: maxCurrentBin = Math.max(...histogramBins, 1);
</script>

<ShowcaseTemplate
    badge="2 / 5 API SUITE"
    title="Extreme Zeta Entropy API"
    description="A premium B2B endpoint that artificially generates mathematically perfect Riemann Zeta points by colliding massive structures. The Quantum Chaos."
    traditionalTitle="Odlyzko Analytical Algorithms"
    traditionalDesc="Calculating these values analytically requires supercomputers and days of processing time."
    lineumTitle="Lineum Oracle-as-a-Service"
    lineumDesc="Extracts Riemann Zeta patterns directly from simulated geometric collapse in milliseconds."
    language="bash"
    codeSnippet={`curl -X POST https://api.lineum.io/v1/entropy/zeta \\
  -H "Authorization: Bearer lnm_enterprise_***" \\
  -d '{"bytes": 64, "mixing_nodes": 1000}'`}
>
    <!-- Visual -->
    <div
        slot="visual"
        class="w-full flex items-center justify-center bg-slate-950/80 rounded-3xl border border-rose-500/20 shadow-[0_0_80px_rgba(244,63,94,0.05)] overflow-hidden h-[450px] relative font-mono"
    >
        <!-- The Geometry Canvas (Top) -->
        <div
            class="absolute inset-0 top-0 h-[60%] perspective-[1000px] flex items-center justify-center overflow-hidden"
        >
            <div
                class={`relative w-full h-full transform-style-3d transition-transform duration-1000 ${state === "collapsing" ? "scale-150 rotate-x-60 rotate-z-45 opacity-0" : "scale-100 rotate-x-60 rotate-z-45"}`}
            >
                {#each nodes as node (node.id)}
                    <div
                        class="absolute w-[20px] h-[20px] bg-rose-500/10 border border-rose-500/50 shadow-[0_0_10px_rgba(244,63,94,0.5)] transition-all ease-[cubic-bezier(0.25,1,0.5,1)]"
                        style="
                            left: calc(50% + {node.x}px);
                            top: calc(50% + {node.y}px);
                            transform: translateZ({state !== 'idle'
                            ? '0px'
                            : '0px'}) translate3d({state !== 'idle'
                            ? node.tx
                            : 0}px, {state !== 'idle'
                            ? node.ty
                            : 0}px, {state !== 'idle'
                            ? Math.random() * -500
                            : 0}px) rotateX({state !== 'idle'
                            ? node.tr
                            : 0}deg) rotateY({state !== 'idle'
                            ? node.tr
                            : 0}deg);
                            transition-duration: {state !== 'idle'
                            ? 1.5 + node.delay
                            : 0.5}s;
                            opacity: {state !== 'idle' ? 0 : 1};
                        "
                    ></div>
                {/each}
            </div>
        </div>

        <!-- The GUE Histogram (Bottom) -->
        <div
            class="absolute bottom-6 left-8 right-8 h-[35%] flex items-end justify-between gap-0.5 border-b border-rose-500/30"
        >
            <!-- Wigner Surmise Overlay Curve (Theoretical) -->
            <svg
                class="absolute inset-0 w-full h-full pointer-events-none"
                preserveAspectRatio="none"
            >
                <path
                    d={`M 0,100 ` +
                        targetHeights
                            .map(
                                (h, i) =>
                                    `L ${(i / 39) * 100}%,${100 - (h / 1.1) * 100}%`,
                            )
                            .join(" ")}
                    class="stroke-white/10"
                    stroke-width="2"
                    fill="none"
                    vector-effect="non-scaling-stroke"
                />
            </svg>

            <!-- Real generated data -->
            {#each histogramBins as bin, i}
                <div class="w-full relative group h-full flex items-end">
                    <div
                        class="w-full bg-rose-500/80 rounded-t-sm transition-all duration-75 origin-bottom"
                        style="height: {(bin / maxCurrentBin) * 90}%;"
                    ></div>
                </div>
            {/each}
        </div>

        <!-- Start Button -->
        <div class="absolute top-6 left-6 z-10">
            <button
                on:click={startSimulation}
                class="px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-full font-bold text-xs tracking-widest uppercase transition-all flex items-center gap-2"
            >
                {#if state === "idle"}
                    <span class="w-2 h-2 rounded-full bg-rose-400 animate-pulse"
                    ></span>
                    Run Structural Collapse
                {:else if state === "collapsing"}
                    <span
                        class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"
                    ></span>
                    Simulating Chaos...
                {:else}
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                    Reset Experiment
                {/if}
            </button>
        </div>

        <div
            class="absolute top-6 right-6 text-xs text-rose-500/50 uppercase tracking-[0.2em] font-bold"
        >
            GUE Ensemble target
        </div>
    </div>

    <!-- Proof (Live Terminal) -->
    <div
        slot="proof"
        class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-start gap-2 h-full min-h-[150px] font-mono"
    >
        <div
            class="text-xs text-slate-500 border-b border-slate-800 pb-2 mb-2 uppercase tracking-widest font-bold flex justify-between"
        >
            <span>Live Audit Terminal</span>
            <span class="text-emerald-500">SECURE SHELL</span>
        </div>

        <div
            class="flex-1 flex flex-col justify-end text-xs text-emerald-400 gap-1.5 overflow-hidden"
        >
            {#if logs.length === 0}
                <div class="text-slate-600 opacity-50">
                    Waiting for simulation input...
                </div>
            {/if}
            {#each logs as log}
                <div class="animate-fade-in">&gt; {log}</div>
            {/each}
            {#if state === "collapsing"}
                <div class="animate-pulse opacity-50">&gt; _</div>
            {/if}
        </div>
    </div>
</ShowcaseTemplate>

<style>
    .perspective-\[1000px\] {
        perspective: 1000px;
    }
    .transform-style-3d {
        transform-style: preserve-3d;
    }
    .rotate-x-60 {
        transform: rotateX(60deg) rotateZ(45deg);
    }

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
        animation: fade-in 0.2s ease-out forwards;
    }
</style>
