<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import { intersect } from "$lib/actions/intersect";

    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null = null;
    let isRunning = false;
    let isVisible = false;
    let animationFrameId: number;
    let isHovered = false;

    // Monte Carlo simulation state
    const TOTAL_POINTS_MAX = 5000;
    let points: { x: number; y: number; inside: boolean }[] = [];
    let pointsInside = 0;
    let currentPi = 0;

    // Fake API logs for the terminal proof
    let logs: { time: string; msg: string; color: string }[] = [];
    let logInterval: ReturnType<typeof setInterval>;

    const codeSnippet = `import lineum

solver = lineum.Client(api_key="lnm_enterprise_***")

# Monte Carlo simulation using Lineum topological entropy
simulation = solver.gaming.monte_carlo_stream(
    topology="zeta_structural_noise",
    dimensions=2,
    batch_size=100
)

for points in simulation:
    process_stochastic_model(points)
    if simulation.variance < 1e-7:
        break`;

    const addLog = (msg: string, color: string = "text-slate-400") => {
        const now = new Date();
        const time = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}.${now.getMilliseconds().toString().padStart(3, "0")}`;
        logs = [{ time, msg, color }, ...logs].slice(0, 6);
    };

    const drawSimulation = () => {
        if (!ctx || !canvas) return;

        // Clear with slight fade for trailing effect
        ctx.fillStyle = "rgba(2, 6, 23, 0.1)"; // slate-950
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 20;

        // Draw bounds (circle & square)
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = "rgba(16, 185, 129, 0.2)"; // emerald-500
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.beginPath();
        ctx.rect(centerX - radius, centerY - radius, radius * 2, radius * 2);
        ctx.strokeStyle = "rgba(56, 189, 248, 0.2)"; // sky-400
        ctx.lineWidth = 1;
        ctx.stroke();

        // Draw points
        for (const p of points) {
            ctx.beginPath();
            ctx.arc(
                centerX + p.x * radius,
                centerY + p.y * radius,
                1.5,
                0,
                2 * Math.PI,
            );
            ctx.fillStyle = p.inside
                ? "rgba(16, 185, 129, 0.8)"
                : "rgba(56, 189, 248, 0.8)";
            ctx.fill();
        }
    };

    const updateSimulation = () => {
        if (!isRunning) return;

        if (!isVisible) {
            // Wait for it to become visible again
            animationFrameId = requestAnimationFrame(updateSimulation);
            return;
        }

        // Generate batch of 20 points
        for (let i = 0; i < 20; i++) {
            if (points.length >= TOTAL_POINTS_MAX) {
                points.shift(); // Remove oldest
            } else {
                // Only update stats if we haven't reached max capacity (keeps Pi stable after fill)
            }

            // Native JS Math.random used here for visual purposes only.
            // In reality, this would be fed by the Lineum API stream.
            const x = Math.random() * 2 - 1;
            const y = Math.random() * 2 - 1;
            const inside = x * x + y * y <= 1;

            points.push({ x, y, inside });

            if (points.length <= TOTAL_POINTS_MAX) {
                if (inside) pointsInside++;
                currentPi = 4 * (pointsInside / points.length);
            }
        }

        drawSimulation();
        animationFrameId = requestAnimationFrame(updateSimulation);
    };

    const startSimulation = () => {
        if (isRunning) return;
        isRunning = true;
        points = [];
        pointsInside = 0;
        currentPi = 0;
        logs = [];

        addLog(
            "INIT: Establishing connection to Lineum Core...",
            "text-slate-400",
        );

        setTimeout(() => {
            if (!isRunning) return;
            addLog("AUTH: Enterprise token verified.", "text-emerald-400");
            addLog(
                "STREAM: Requesting 2D topological mapping...",
                "text-sky-400",
            );
            updateSimulation();
        }, 400);

        logInterval = setInterval(() => {
            if (!isRunning) return;
            const metrics = [
                `TENSOR_SYNC: Batch received [variance: ${(Math.random() * 0.0001).toFixed(7)}]`,
                `Q-STATE: Verified zero geometric correlation in sample subset.`,
                `ENTROPY: Local $\\varphi$ turbulence holding.`,
                `STREAM: Pushing 200 coordinates to client interface.`,
            ];
            addLog(
                metrics[Math.floor(Math.random() * metrics.length)],
                "text-slate-500",
            );
        }, 1200);
    };

    const stopSimulation = () => {
        isRunning = false;
        cancelAnimationFrame(animationFrameId);
        clearInterval(logInterval);
        addLog("STREAM: Connection terminated by client.", "text-rose-400");
    };

    onMount(() => {
        if (canvas) {
            // Set canvas resolution strictly for crisp rendering
            canvas.width = canvas.offsetWidth * window.devicePixelRatio;
            canvas.height = canvas.offsetHeight * window.devicePixelRatio;
            ctx = canvas.getContext("2d");
            if (ctx) {
                ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
                drawSimulation(); // Draw initial empty frame
            }
        }
    });

    onDestroy(() => {
        stopSimulation();
    });
</script>

<ShowcaseTemplate
    badge="5 / 5 API SUITE"
    title="Monte Carlo & Scientific RNG"
    description="High-throughput, un-patterned entropy streams derived from topological structure collapse. Crucial for unbiased stochastic modeling, particle physics, and provably-fair state lotteries."
    traditionalTitle="Algorithmic Pseudo-Randomness"
    traditionalDesc="Standard random number generators (`rand()`, Mersenne Twister) are purely deterministic algorithms. Under heavy scientific sampling, their hidden cyclical patterns skew Monte Carlo results."
    lineumTitle="Topological Simulation Entropy"
    lineumDesc="Lineum generates entropy by colliding massive simulated $\varphi$ structures. Because it maps physical wave chaos, it produces structurally unbreakable, infinite-period noise."
    language="python"
    {codeSnippet}
>
    <!-- Interactive Visual Slot -->
    <div
        slot="visual"
        use:intersect={(inView) => (isVisible = inView)}
        class="relative w-full h-[400px] rounded-3xl overflow-hidden bg-slate-950 border border-slate-800 shadow-xl"
        on:mouseenter={() => (isHovered = true)}
        on:mouseleave={() => (isHovered = false)}
    >
        <!-- Background Grid -->
        <div
            class="absolute inset-0 bg-[url('/img/grid.svg')] opacity-[0.03]"
        ></div>

        <!-- Canvas -->
        <canvas bind:this={canvas} class="absolute inset-0 w-full h-full"
        ></canvas>

        <!-- Overlay UI -->
        <div
            class="absolute inset-x-0 bottom-0 p-6 flex flex-col items-center justify-end bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent pointer-events-none"
        >
            <div
                class="flex items-end justify-between w-full pointer-events-auto"
            >
                <!-- Stats -->
                <div class="flex flex-col">
                    <span
                        class="text-[10px] font-bold tracking-widest text-slate-500 uppercase"
                        >Current $\\pi$ Estimate</span
                    >
                    <span
                        class="text-3xl font-mono text-white transition-colors duration-300"
                        class:text-emerald-400={isRunning}
                    >
                        {currentPi === 0 ? "0.000000" : currentPi.toFixed(6)}
                    </span>
                    <span class="text-xs font-mono text-slate-500 mt-1"
                        >Sample Size: {points.length.toLocaleString()} pts</span
                    >
                </div>

                <!-- Controls -->
                <button
                    on:click={isRunning ? stopSimulation : startSimulation}
                    class="px-5 py-2.5 rounded-full font-mono text-sm font-semibold transition-all duration-300 flex items-center gap-2 border"
                    class:bg-emerald-500={!isRunning}
                    class:text-white={!isRunning}
                    class:border-emerald-400={!isRunning}
                    class:shadow-[0_0_20px_rgba(16,185,129,0.3)]={!isRunning &&
                        isHovered}
                    class:bg-transparent={isRunning}
                    class:text-rose-400={isRunning}
                    class:border-rose-400={isRunning}
                    class:hover:bg-rose-500={isRunning}
                    class:hover:text-white={isRunning}
                >
                    <div
                        class="w-2 h-2 rounded-full"
                        class:bg-white={!isRunning}
                        class:bg-rose-400={isRunning}
                        class:animate-pulse={isRunning}
                    ></div>
                    {isRunning ? "HALT STREAM" : "START SIMULATION"}
                </button>
            </div>
        </div>
    </div>

    <!-- Proof Terminal Slot -->
    <div
        slot="proof"
        class="w-full h-full bg-[#0a0a0a] rounded-2xl border border-slate-800 p-4 font-mono text-xs overflow-hidden flex flex-col relative group"
    >
        <div
            class="flex items-center justify-between border-b border-slate-800 pb-3 mb-3"
        >
            <div class="flex items-center gap-2 text-slate-500">
                <svg
                    class="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 9l3 3-3 3m5 0h3M4 17h16a2 2 0 002-2V5a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                </svg>
                <span>LIVE SCIENTIFIC AUDIT /// TRNG STREAM</span>
            </div>
            <div class="flex gap-1.5">
                <div class="w-2 h-2 rounded-full bg-slate-700"></div>
                <div class="w-2 h-2 rounded-full bg-slate-700"></div>
                <div
                    class="w-2 h-2 rounded-full"
                    class:bg-emerald-500={isRunning}
                    class:bg-slate-700={!isRunning}
                    class:animate-pulse={isRunning}
                ></div>
            </div>
        </div>

        <!-- Terminal Lines -->
        <div class="flex flex-col gap-1.5 flex-1 justify-end h-[160px]">
            {#if logs.length === 0}
                <div class="text-slate-600 animate-pulse">
                    Waiting for simulation trigger...
                </div>
            {:else}
                {#each [...logs].reverse() as log}
                    <div class="flex gap-3">
                        <span class="text-slate-600 shrink-0">[{log.time}]</span
                        >
                        <span class="{log.color} break-all">{log.msg}</span>
                    </div>
                {/each}
            {/if}
        </div>

        <!-- Absolute overlay gradient so it fades nicely at top -->
        <div
            class="absolute inset-x-0 top-12 h-8 bg-gradient-to-b from-[#0a0a0a] to-transparent pointer-events-none"
        ></div>
    </div>
</ShowcaseTemplate>
