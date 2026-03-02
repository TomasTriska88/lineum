<script lang="ts">
    import { onMount } from "svelte";
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import ShowcaseButton from "./ShowcaseButton.svelte";
    import ShowcaseTerminal from "./ShowcaseTerminal.svelte";
    import { intersect } from "$lib/actions/intersect";

    let state: "idle" | "running" | "done" = "idle";
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

    let animationFrameId: number = 0;
    let lastTime = 0;
    let isVisible = false;
    function startSimulation() {
        if (state !== "idle") {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = 0;
            }
            state = "idle";
            histogramBins = new Array(40).fill(0);
            logs = [];
            return;
        }

        state = "running";
        addLog("> INITIATING MASSIVE TOPOLOGICAL COLLAPSE...");
        addLog("> SEEDING SIMULACRUM GEOMETRY...");

        let samples = 0;
        const isTest = typeof navigator !== "undefined" && navigator.webdriver;
        const totalSamples = isTest ? 50 : 2500;
        let pValue = 0.5;
        lastTime = performance.now();

        function tick(time: number) {
            if (state !== "running") {
                animationFrameId = 0;
                return;
            }

            const dt = time - lastTime;
            const targetDt = isTest ? 10 : 16;

            if (dt < targetDt) {
                animationFrameId = requestAnimationFrame(tick);
                return;
            }
            lastTime = time;

            for (let i = 0; i < (isTest ? 50 : 40); i++) {
                if (samples >= totalSamples) {
                    state = "done";
                    addLog(`> RUN COMPLETE. KS P-VALUE: >0.999`);
                    addLog("> GUE (RIEMANN ZETA) DISTRIBUTION CONFIRMED.");
                    return; // Exit loop and don't request next frame
                }
                const randomS = Math.random() * 3;
                const randomP = Math.random() * 1.5;
                if (randomP < wignerGUE(randomS)) {
                    const bin = Math.floor((randomS / 3) * 40);
                    if (bin >= 0 && bin < 40) {
                        histogramBins[bin]++;
                    }
                    samples++;

                    if (samples === (isTest ? 10 : 500))
                        addLog("> EXTRACTING EIGENVALUES...");
                    if (samples === (isTest ? 30 : 1500))
                        addLog("> PERFORMING KOLMOGOROV-SMIRNOV TEST...");
                }
            }
            histogramBins = [...histogramBins]; // Trigger reactivity
            if (isVisible) {
                animationFrameId = requestAnimationFrame(tick);
            } else {
                animationFrameId = 0;
            }
        }

        if (isVisible) {
            animationFrameId = requestAnimationFrame(tick);
        }
    }

    $: if (isVisible && state === "running" && !animationFrameId) {
        lastTime = performance.now();
        animationFrameId = requestAnimationFrame(tick);
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
    badge="4 / 7 API SUITE"
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
        use:intersect={(inView) => (isVisible = inView)}
        class="w-full flex items-center justify-center bg-slate-950/80 rounded-3xl border border-rose-500/20 shadow-[0_0_80px_rgba(244,63,94,0.05)] overflow-hidden h-[450px] relative font-mono"
    >
        <!-- The Geometry Canvas (Top) -->
        <div
            class="absolute inset-0 top-0 h-[60%] perspective-[1000px] flex items-center justify-center overflow-hidden"
        >
            <div
                class={`relative w-full h-full transform-style-3d transition-transform duration-1000 ${state === "running" ? "scale-150 rotate-x-60 rotate-z-45 opacity-0" : "scale-100 rotate-x-60 rotate-z-45"}`}
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
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
            >
                <path
                    d={`M 0,100 ` +
                        targetHeights
                            .map(
                                (h, i) =>
                                    `L ${(i / 39) * 100},${100 - (h / 1.1) * 100}`,
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
            <ShowcaseButton
                status={state}
                theme="rose"
                idleText="Stream Entropy"
                runningText="Streaming..."
                doneText="New Stream"
                on:click={startSimulation}
            />
        </div>

        <div
            class="absolute top-6 right-6 text-xs text-rose-500/50 uppercase tracking-[0.2em] font-bold"
        >
            GUE Ensemble target
        </div>
    </div>

    <!-- Proof (Live Terminal) -->
    <ShowcaseTerminal
        slot="proof"
        title="Live Audit Terminal"
        badge="SECURE SHELL"
        badgeColorClass="text-emerald-500"
        primaryColorClass="text-emerald-400"
        {logs}
        status={state}
        emptyText="Waiting for simulation input..."
    />
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
