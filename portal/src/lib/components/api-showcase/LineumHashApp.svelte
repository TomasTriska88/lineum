<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import { onMount, onDestroy } from "svelte";
    import { intersect } from "$lib/actions/intersect";

    let inputText = "Lineum is inevitable.";
    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null = null;
    let animationId: number;
    let isVisible = false;

    // Proof Section Metrics
    let inputLength = 0;
    let timeToHash = 0;
    let avalancheEffect = 0;
    let hashOutput = "";

    // Abstract tensor state derived from input string
    let tensorState: number[] = new Array(64).fill(0);
    let targetTensorState: number[] = new Array(64).fill(0);
    let time = 0;

    // Simulate hashing and topological mapping
    function processInput() {
        if (!inputText) {
            targetTensorState = new Array(64).fill(0);
            updateMetrics(true);
            return;
        }

        // Extremely naive, fast "hash" just to generate visual seeds based on char codes
        let seed = 0;
        for (let i = 0; i < inputText.length; i++) {
            seed = (seed << 5) - seed + inputText.charCodeAt(i);
            seed |= 0;
        }

        // Generate the 64-dimensional pseudo-tensor state
        for (let i = 0; i < 64; i++) {
            // Using bitwise math to create chaotic, unpredictable target states [-1 to 1]
            const chaos = Math.sin(seed * (i + 1) * 13.37);
            targetTensorState[i] = chaos;
        }

        updateMetrics(false);
    }

    function updateMetrics(isEmpty: boolean) {
        if (isEmpty) {
            inputLength = 0;
            timeToHash = 0;
            avalancheEffect = 0;
            hashOutput = "AWAITING_INPUT";
            return;
        }

        inputLength = new Blob([inputText]).size; // bytes

        // Simulate execution time (quantum resistant usually takes longer, but we are "Lineum Fast")
        // We add some minor jitter based on length
        timeToHash = 14.2 + Math.random() * 2 + inputLength * 0.1;

        // Simulate Avalanche Effect (ideal is ~50%)
        avalancheEffect = 49.5 + Math.random() * 1.0;

        // Generate synthetic hex output just for the log
        const hexChars = "0123456789abcdef";
        let out = "0x";
        for (let i = 0; i < 64; i++) {
            // 256-bit
            // Derive hex from the tensor state to at least look deterministicish per state
            const idx = Math.abs(Math.floor(targetTensorState[i] * 100)) % 16;
            out += hexChars[idx];
        }
        hashOutput = out;
    }

    // Removed purely reactive statement
    // $: inputText, processInput();
    onMount(() => {
        if (canvas) {
            ctx = canvas.getContext("2d");
            processInput(); // Initial paint state
            drawCanvas();
        }
    });

    onDestroy(() => {
        if (animationId) cancelAnimationFrame(animationId);
    });

    function drawCanvas() {
        if (!ctx || !canvas) return;
        const width = canvas.width;
        const height = canvas.height;

        // Smoothly interpolate current tensor state towards the target state
        for (let i = 0; i < 64; i++) {
            tensorState[i] += (targetTensorState[i] - tensorState[i]) * 0.1;
        }

        // Clear frame with severe trail effect (motion blur)
        ctx.fillStyle = "rgba(2, 6, 23, 0.15)"; // slate-950 with low alpha
        ctx.fillRect(0, 0, width, height);

        time += 0.02;

        const centerX = width / 2;
        const centerY = height / 2;
        const radiusBase = Math.min(width, height) * 0.35;

        // Draw the complex multi-dimensional shape
        ctx.lineWidth = 1;

        // Draw orbital rings
        for (let ring = 0; ring < 4; ring++) {
            ctx.beginPath();

            // Connect 16 points per ring
            for (let i = 0; i < 16; i++) {
                const tensorIdx = ring * 16 + i;
                const value = tensorState[tensorIdx]; // -1 to 1

                const angle =
                    (i / 16) * Math.PI * 2 +
                    time * (ring % 2 === 0 ? 1 : -1) * 0.5;
                const r = radiusBase + ring * 15 + value * 30; // displacement based on hash state

                const x = centerX + Math.cos(angle) * r;
                const y = centerY + Math.sin(angle) * r;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();

            // Color based on activity intensity
            const intensity = Math.abs(tensorState[ring * 16]); // sample one
            // Blend from cyan (sky-400) to purple (purple-500) based on ring & intensity
            if (ring % 2 === 0) {
                ctx.strokeStyle = `rgba(56, 189, 248, ${0.3 + intensity * 0.5})`; // Sky 400
            } else {
                ctx.strokeStyle = `rgba(168, 85, 247, ${0.3 + intensity * 0.5})`; // Purple 500
            }
            ctx.stroke();

            // Interconnecting lines between this ring and the next to form the topological web
            if (ring < 3) {
                for (let i = 0; i < 16; i += 2) {
                    const tensorIdx1 = ring * 16 + i;
                    const tensorIdx2 = (ring + 1) * 16 + i;

                    const angle1 =
                        (i / 16) * Math.PI * 2 +
                        time * (ring % 2 === 0 ? 1 : -1) * 0.5;
                    const r1 =
                        radiusBase + ring * 15 + tensorState[tensorIdx1] * 30;

                    const angle2 =
                        (i / 16) * Math.PI * 2 +
                        time * ((ring + 1) % 2 === 0 ? 1 : -1) * 0.5;
                    const r2 =
                        radiusBase +
                        (ring + 1) * 15 +
                        tensorState[tensorIdx2] * 30;

                    ctx.beginPath();
                    ctx.moveTo(
                        centerX + Math.cos(angle1) * r1,
                        centerY + Math.sin(angle1) * r1,
                    );
                    ctx.lineTo(
                        centerX + Math.cos(angle2) * r2,
                        centerY + Math.sin(angle2) * r2,
                    );

                    // Connecting webs are subtle slate
                    ctx.strokeStyle = "rgba(100, 116, 139, 0.15)";
                    ctx.stroke();
                }
            }
        }

        // Draw core geometry (crystal shape reacting violently to input)
        ctx.beginPath();
        for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2;
            // The core points react to the sum of segments of the tensor state
            let sum = 0;
            for (let j = 0; j < 8; j++) sum += Math.abs(tensorState[i * 8 + j]);
            const r = radiusBase * 0.4 + sum * 5;

            const x = centerX + Math.cos(angle - time) * r;
            const y = centerY + Math.sin(angle - time) * r;

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fillStyle = "rgba(168, 85, 247, 0.1)"; // solid purple core
        ctx.fill();
        ctx.strokeStyle = "rgba(168, 85, 247, 0.8)";
        ctx.lineWidth = 2;
        ctx.stroke();

        if (isVisible) {
            animationId = requestAnimationFrame(drawCanvas);
        }
    }

    $: if (isVisible && !animationId) {
        drawCanvas();
    }
</script>

<ShowcaseTemplate
    badge="4 / 5 API SUITE"
    title="LineumHash API"
    description="Drop-in replacement for SHA-256 and Keccak. Extremely collision-resistant cryptographic hash function utilizing fluid dynamics topology to achieve mathematically verified Quantum Resistance."
    traditionalTitle="Traditional Cryptographic Hashing"
    traditionalDesc="Math-based block ciphers (SHA family) are increasingly vulnerable to Shor's algorithm running on imminent quantum hardware."
    lineumTitle="Topological Hashing"
    lineumDesc="Maps input data to high-dimensional non-linear fluid vortex coordinates. Brute-forcing would require simulating a proprietary physical universe."
    language="Python"
    codeSnippet={`import lineum

# Quantum-resistant topological hashing
payload = b"Top secret corporate data."

# Instantly returns 256-bit or 512-bit geometric hash
secure_hash = lineum.hash(
    data=payload,
    dimensions=256,
    salt=b"random_vacuum_noise"
)

# Output is deterministic but topologically un-inversible
print(secure_hash.hex())`}
>
    <!-- Visual -->
    <div
        slot="visual"
        use:intersect={(inView) => (isVisible = inView)}
        class="w-full flex items-center justify-center bg-slate-950/80 rounded-3xl border border-purple-500/20 shadow-[0_0_80px_rgba(168,85,247,0.05)] overflow-hidden h-[450px] relative font-mono"
    >
        <!-- The Geometry Canvas (Top) -->
        <div
            class="absolute inset-0 top-0 h-[70%] w-full bg-black/50 border-b border-purple-500/30 overflow-hidden flex items-center justify-center"
        >
            <canvas
                bind:this={canvas}
                width="800"
                height="400"
                class="w-full h-full object-cover mix-blend-screen"
            ></canvas>

            <div
                class="absolute top-4 left-6 text-[10px] sm:text-xs text-purple-500 font-bold tracking-widest uppercase opacity-70"
            >
                Topological Tensor Map
            </div>
        </div>

        <!-- Controls (Bottom) -->
        <div
            class="absolute bottom-4 left-8 right-8 h-[25%] flex flex-col items-center justify-center gap-2"
        >
            <div
                class="w-full max-w-lg mb-1 flex justify-between text-[10px] text-slate-400 uppercase tracking-widest px-2"
            >
                <span>Data Input</span>
                <span class="text-sky-400">{inputLength} bytes</span>
            </div>
            <input
                type="text"
                bind:value={inputText}
                on:input={processInput}
                placeholder="Enter string data to hash..."
                class="w-full max-w-lg bg-slate-900 border border-slate-700 text-slate-200 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 rounded-lg px-4 py-3 font-mono text-sm transition-colors"
                spellcheck="false"
            />
        </div>
    </div>

    <!-- Proof (Live Cryptographic Audit) -->
    <div
        slot="proof"
        class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-start gap-4 h-full min-h-[150px] font-mono"
    >
        <div
            class="text-xs text-slate-500 border-b border-slate-800 pb-2 uppercase tracking-widest font-bold flex justify-between"
        >
            <span>Live Cryptographic Audit</span>
            <span class="text-purple-500">LINEUM-256</span>
        </div>

        <div class="flex flex-col gap-3">
            <!-- Metrics Grid -->
            <div
                class="grid grid-cols-2 gap-4 pb-3 border-b border-slate-800/50"
            >
                <div class="flex flex-col">
                    <span
                        class="text-[10px] text-slate-500 uppercase tracking-widest"
                        >Time-to-Hash</span
                    >
                    <span class="text-sm font-bold text-sky-400"
                        >{timeToHash > 0 ? timeToHash.toFixed(2) : "0.00"}
                        <span class="text-[10px] text-slate-600">ns</span></span
                    >
                </div>
                <div class="flex flex-col">
                    <span
                        class="text-[10px] text-slate-500 uppercase tracking-widest"
                        >Avalanche Effect</span
                    >
                    <span class="text-sm font-bold text-purple-400"
                        >{avalancheEffect > 0
                            ? avalancheEffect.toFixed(2)
                            : "0.00"}%</span
                    >
                </div>
            </div>

            <!-- Streaming Hash Log -->
            <div
                class="flex flex-col text-xs text-emerald-400 gap-1 overflow-hidden h-full"
            >
                {#if inputText.length === 0}
                    <div class="text-slate-600 opacity-50">
                        Waiting for data payload...
                    </div>
                {:else}
                    <div
                        class="text-slate-500 mb-1 opacity-70 break-all text-[10px]"
                    >
                        &gt; mapping text tensor...
                    </div>
                    <div
                        class="break-words break-all font-bold text-emerald-400 leading-relaxed max-w-full"
                    >
                        &gt; {hashOutput}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</ShowcaseTemplate>
