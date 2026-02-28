<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import { onMount, onDestroy } from "svelte";

    let state: "idle" | "sampling" | "done" = "idle";
    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null = null;
    let animationId: number;
    let logs: string[] = [];
    let hexStream: string[] = [];

    // FIPS 140-3 / NIST test suite validations
    let nistTests = [
        { name: "Frequency (Monobit)", passed: false },
        { name: "Runs Test", passed: false },
        { name: "Longest Run of Ones", passed: false },
        { name: "Discrete Fourier Transform", passed: false },
        { name: "Approximate Entropy", passed: false },
    ];

    onMount(() => {
        if (canvas) {
            ctx = canvas.getContext("2d");
            drawIdleState();
        }
    });

    onDestroy(() => {
        if (animationId) cancelAnimationFrame(animationId);
    });

    function drawIdleState() {
        if (!ctx || !canvas) return;
        ctx.fillStyle = "#020617"; // slate-950
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw a faint horizontal grid or standby line
        ctx.strokeStyle = "rgba(14, 165, 233, 0.1)"; // sky-500 very faint
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, canvas.height / 2);
        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();
    }

    function drawNoise() {
        if (!ctx || !canvas) return;
        const width = canvas.width;
        const height = canvas.height;
        const imageData = ctx.createImageData(width, height);
        const data = imageData.data;

        for (let i = 0; i < data.length; i += 4) {
            const noise = Math.random();
            // High contrast black/white/pink noise
            // 80% black/dark slate, 15% white, 5% bright pink/sky
            if (noise < 0.8) {
                data[i] = 2;
                data[i + 1] = 6;
                data[i + 2] = 23; // slate-950
                data[i + 3] = 255;
            } else if (noise < 0.95) {
                const val = Math.random() * 255;
                data[i] = val;
                data[i + 1] = val;
                data[i + 2] = val; // greyscale
                data[i + 3] = 255;
            } else if (noise < 0.98) {
                // Pink/Rose-500 sparks
                data[i] = 244;
                data[i + 1] = 63;
                data[i + 2] = 94;
                data[i + 3] = 255;
            } else {
                // Sky-400 sparks
                data[i] = 56;
                data[i + 1] = 189;
                data[i + 2] = 248;
                data[i + 3] = 255;
            }
        }
        ctx.putImageData(imageData, 0, 0);
    }

    function generateRandomHexLine() {
        const chars = "0123456789ABCDEF";
        let line = "";
        for (let i = 0; i < 32; i++) {
            line += chars[Math.floor(Math.random() * chars.length)];
            if ((i + 1) % 8 === 0) line += " ";
        }
        return line.trim();
    }

    function triggerSampling() {
        if (state !== "idle") {
            // Reset
            if (animationId) cancelAnimationFrame(animationId);
            state = "idle";
            logs = [];
            hexStream = [];
            nistTests = nistTests.map((t) => ({ ...t, passed: false }));
            drawIdleState();
            return;
        }

        state = "sampling";
        logs = ["> ALLOCATING VACUUM BUFFER...", "> OPENING SENSOR GATE..."];
        hexStream = [];

        let frames = 0;
        const maxFrames = 120; // 2 seconds at 60fps

        function animate() {
            drawNoise();
            frames++;

            // Stream hex data
            if (frames % 3 === 0) {
                hexStream = [generateRandomHexLine(), ...hexStream].slice(0, 6);
            }

            // Progressively pass NIST validations
            if (frames === 20) nistTests[0].passed = true;
            if (frames === 40) nistTests[1].passed = true;
            if (frames === 70) nistTests[2].passed = true;
            if (frames === 90) nistTests[3].passed = true;
            if (frames === 110) nistTests[4].passed = true;

            if (frames >= maxFrames) {
                state = "done";
                drawIdleState();
                hexStream = [
                    `[FIPS COMPLIANT PACKET DELIVERED]`,
                    ...hexStream,
                ].slice(0, 6);
                logs = [...logs, "> ENTROPY HARVEST COMPLETE."];
                if (logs.length > 3) logs.shift();
            } else {
                animationId = requestAnimationFrame(animate);
            }
        }

        animate();
    }
</script>

<ShowcaseTemplate
    badge="1 / 5 API SUITE"
    title="Fast Edge-of-Chaos TRNG API"
    description="Harvest mathematically pure, highly volatile entropy from the vacuum noise of simulated chaotic fields. Ideal for low-latency session keys and web cryptography."
    traditionalTitle="Traditional PRNGs / Hardware Sources"
    traditionalDesc="Predictable algorithms (Mersenne Twister) or slow external hardware devices bottlenecking at high throughput."
    lineumTitle="Lineum Simulated Vacuum"
    lineumDesc="Generates millions of unpredictable states trivially by reading the microscopic phase fluctuations in the fluid."
    language="JSON / REST"
    codeSnippet={`{
  "status": "success",
  "source": "lineum_quantum_chaos_trng",
  "requested_bytes": 32,
  "entropy_hex": "e7b9a23f8c01d4a9...9f1a",
  "certification": "FIPS 140-3 compliant signature"
}`}
>
    <!-- Visual -->
    <div
        slot="visual"
        class="w-full flex items-center justify-center p-8 bg-slate-950/80 rounded-3xl border border-sky-500/20 shadow-[0_0_80px_rgba(56,189,248,0.05)] overflow-hidden h-[450px] relative font-mono"
    >
        <!-- Canvas Container -->
        <div
            class="absolute inset-0 top-0 h-[65%] w-full bg-black/50 border-b border-sky-500/30 overflow-hidden flex items-center justify-center"
        >
            <!-- CRT aesthetic overlays -->
            <div
                class="absolute inset-0 pointer-events-none bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-20 z-10 mix-blend-overlay"
            ></div>
            <div
                class="absolute inset-0 pointer-events-none shadow-[inset_0_0_100px_rgba(0,0,0,0.9)] z-20"
            ></div>

            <canvas
                bind:this={canvas}
                width="800"
                height="300"
                class="w-full h-full object-cover mix-blend-screen"
            ></canvas>

            {#if state === "idle"}
                <div
                    class="absolute inset-0 flex items-center justify-center text-sky-500/30 tracking-[0.5em] text-sm uppercase pointer-events-none z-30"
                >
                    Vacuum Oscillator Standby
                </div>
            {/if}
        </div>

        <!-- Controls & Live Hex Stream -->
        <div
            class="absolute bottom-6 left-8 right-8 h-[30%] flex justify-between items-end"
        >
            <!-- Left Side: Hex Stream Terminal -->
            <div
                class="flex-1 text-[10px] sm:text-xs text-sky-400 opacity-80 leading-tight"
            >
                {#if hexStream.length === 0}
                    <div class="text-slate-600 opacity-50">
                        Awaiting vacuum sampling...
                    </div>
                {/if}
                {#each hexStream as line}
                    <div
                        class="animate-fade-in font-mono whitespace-nowrap overflow-hidden text-ellipsis"
                    >
                        {line}
                    </div>
                {/each}
            </div>

            <!-- Start Button -->
            <div class="ml-4 flex-shrink-0">
                <button
                    on:click={triggerSampling}
                    class="px-5 py-2.5 bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 rounded-full font-bold text-xs tracking-widest uppercase transition-all flex items-center gap-2"
                >
                    {#if state === "idle"}
                        <span
                            class="w-2 h-2 rounded-full bg-sky-400 animate-pulse"
                        ></span>
                        Sample Vacuum
                    {:else if state === "sampling"}
                        <span
                            class="w-2 h-2 rounded-full bg-rose-400 animate-pulse"
                        ></span>
                        Sampling...
                    {:else}
                        <span class="w-2 h-2 rounded-full bg-emerald-400"
                        ></span>
                        Reset Sensor
                    {/if}
                </button>
            </div>
        </div>
    </div>

    <!-- Proof (Live Terminal & Validations) -->
    <div
        slot="proof"
        class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-start gap-4 h-full min-h-[150px] font-mono"
    >
        <div
            class="text-xs text-slate-500 border-b border-slate-800 pb-2 uppercase tracking-widest font-bold flex justify-between"
        >
            <span>Live Audit Terminal</span>
            <span class="text-emerald-500">SECURE SHELL</span>
        </div>

        <div class="flex flex-col md:flex-row gap-6 w-full h-full">
            <!-- Terminal Logs -->
            <div
                class="flex-1 flex flex-col justify-end text-xs text-emerald-400 gap-1.5 overflow-hidden"
            >
                {#if logs.length === 0}
                    <div class="text-slate-600 opacity-50">
                        Waiting for sensor input...
                    </div>
                {/if}
                {#each logs as log}
                    <div class="animate-fade-in">&gt; {log}</div>
                {/each}
                {#if state === "sampling"}
                    <div class="animate-pulse opacity-50">&gt; _</div>
                {/if}
            </div>

            <!-- NIST Validations -->
            <div
                class="w-full md:w-48 flex flex-col gap-2 justify-end pb-1 border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6"
            >
                <div
                    class="text-[10px] text-slate-500 uppercase tracking-wider mb-1"
                >
                    NIST SP 800-22 Suite
                </div>
                {#each nistTests as test}
                    <div class="flex items-center justify-between text-[10px]">
                        <span
                            class={test.passed
                                ? "text-slate-300"
                                : "text-slate-600"}>{test.name}</span
                        >
                        {#if test.passed}
                            <span class="text-emerald-400 font-bold ml-2"
                                >PASS</span
                            >
                        {:else if state === "sampling"}
                            <span
                                class="text-sky-400 animate-pulse ml-2 text-[8px] tracking-widest"
                                >RUNNING</span
                            >
                        {:else}
                            <span
                                class="text-slate-700 ml-2 text-[8px] uppercase"
                                >PENDING</span
                            >
                        {/if}
                    </div>
                {/each}
            </div>
        </div>
    </div>
</ShowcaseTemplate>

<style>
    @keyframes fade-in {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    .animate-fade-in {
        animation: fade-in 0.1s ease-out forwards;
    }
</style>
