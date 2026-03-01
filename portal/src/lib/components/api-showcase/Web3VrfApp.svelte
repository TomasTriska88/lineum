<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import ShowcaseButton from "./ShowcaseButton.svelte";
    import ShowcaseTerminal from "./ShowcaseTerminal.svelte";
    import { intersect } from "$lib/actions/intersect";

    let state: "idle" | "running" | "delivering" | "done" = "idle";
    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null = null;
    let animationId: number;
    let isVisible = false;

    // Proof Section Logs
    let logs: string[] = [];
    let validationSteps = [
        { name: "Gas Fee Deposited", status: "pending" }, // pending, running, pass
        { name: "Quantum Sample Acquired", status: "pending" },
        { name: "zk-SNARK Payload Gen", status: "pending" },
        { name: "On-Chain Verification", status: "pending" },
    ];

    // Animation state
    let particles: {
        x: number;
        y: number;
        speed: number;
        size: number;
        opacity: number;
    }[] = [];
    let time = 0;

    onMount(() => {
        if (canvas) {
            ctx = canvas.getContext("2d");
            // Initialize some background floating data
            for (let i = 0; i < 50; i++) {
                particles.push({
                    x: Math.random() * 800,
                    y: Math.random() * 300,
                    speed: 0.1 + Math.random() * 0.5,
                    size: Math.random() * 2,
                    opacity: 0.1 + Math.random() * 0.3,
                });
            }
            drawCanvas();
        }
    });

    onDestroy(() => {
        if (typeof window !== "undefined" && animationId)
            cancelAnimationFrame(animationId);
    });

    function drawCanvas() {
        if (!ctx || !canvas) return;
        const width = canvas.width;
        const height = canvas.height;

        // Clear frame
        ctx.fillStyle = "#020617"; // slate-950
        ctx.fillRect(0, 0, width, height);

        time += 0.05;

        // Background grid (blockchain metaphor)
        ctx.strokeStyle = "rgba(56, 189, 248, 0.05)"; // sky-500
        ctx.lineWidth = 1;
        for (let x = 0; x < width; x += 40) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        for (let y = 0; y < height; y += 40) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }

        // Floating ambient nodes
        particles.forEach((p) => {
            p.x -= p.speed;
            if (p.x < 0) p.x = width;
            ctx!.fillStyle = `rgba(56, 189, 248, ${p.opacity})`;
            ctx!.beginPath();
            ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx!.fill();
        });

        // The Smart Contract target block (right side)
        const blockX = width - 120;
        const blockY = height / 2 - 40;

        ctx.lineWidth = 2;
        if (state === "done") {
            ctx.strokeStyle = "rgba(16, 185, 129, 0.8)"; // emerald-500
            ctx.fillStyle = "rgba(16, 185, 129, 0.1)";
        } else if (state === "running") {
            ctx.strokeStyle = "rgba(56, 189, 248, 0.8)"; // sky-500
            ctx.fillStyle = "rgba(56, 189, 248, 0.1)";
        } else {
            ctx.strokeStyle = "rgba(71, 85, 105, 0.5)"; // slate-600
            ctx.fillStyle = "rgba(15, 23, 42, 0.8)"; // slate-900
        }

        ctx.beginPath();
        ctx.roundRect(blockX, blockY, 80, 80, 8);
        ctx.fill();
        ctx.stroke();

        // Target Block interior logic lines
        ctx.strokeStyle =
            state === "done"
                ? "rgba(16, 185, 129, 0.4)"
                : "rgba(71, 85, 105, 0.3)";
        ctx.beginPath();
        ctx.moveTo(blockX + 20, blockY + 30);
        ctx.lineTo(blockX + 60, blockY + 30);
        ctx.moveTo(blockX + 20, blockY + 50);
        ctx.lineTo(blockX + 40, blockY + 50);
        ctx.stroke();

        // Lineum Source Node (left side)
        const sourceX = 40;
        const sourceY = height / 2;

        ctx.beginPath();
        ctx.arc(sourceX, sourceY, 15, 0, Math.PI * 2);
        if (state === "delivering") {
            ctx.fillStyle = "rgba(244, 63, 94, 0.8)"; // rose-500 glowing
            ctx.shadowColor = "rgba(244, 63, 94, 0.5)";
            ctx.shadowBlur = 20;
        } else {
            ctx.fillStyle = "rgba(56, 189, 248, 0.5)"; // sky back to normal
            ctx.shadowBlur = 0;
        }
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        // The Tunnel / Payload
        if (state === "running") {
            // Signal going right to left
            const progress = (time % 2) / 2;
            ctx.fillStyle = "rgba(56, 189, 248, 0.8)";
            ctx.beginPath();
            ctx.arc(
                blockX - progress * (blockX - sourceX),
                sourceY,
                4,
                0,
                Math.PI * 2,
            );
            ctx.fill();
        } else if (state === "delivering") {
            // Quantum payload firing left to right
            const progress = Math.min((time % 2) * 2, 1); // faster

            // Laser beam effect
            const gradient = ctx.createLinearGradient(
                sourceX,
                sourceY,
                blockX,
                sourceY,
            );
            gradient.addColorStop(0, "rgba(244, 63, 94, 0.0)");
            gradient.addColorStop(progress, "rgba(244, 63, 94, 0.8)");
            gradient.addColorStop(progress + 0.01, "rgba(244, 63, 94, 0.0)");

            ctx.lineWidth = 4;
            ctx.strokeStyle = gradient;
            ctx.beginPath();
            ctx.moveTo(sourceX + 15, sourceY);
            ctx.lineTo(blockX, sourceY);
            ctx.stroke();

            // Sizzle particles along the beam
            if (progress < 0.95) {
                for (let i = 0; i < 3; i++) {
                    ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
                    ctx.beginPath();
                    ctx.arc(
                        sourceX +
                            progress * (blockX - sourceX) +
                            (Math.random() * 10 - 5),
                        sourceY + (Math.random() * 20 - 10),
                        Math.random() * 2,
                        0,
                        Math.PI * 2,
                    );
                    ctx.fill();
                }
            }
        } else if (state === "done") {
            // Success ripple
            const rippleSize = (time % 2) * 40;
            ctx.strokeStyle = `rgba(16, 185, 129, ${1 - rippleSize / 80})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(blockX + 40, blockY + 40, 40 + rippleSize, 0, Math.PI * 2);
            ctx.stroke();
        }

        if (isVisible) {
            animationId = requestAnimationFrame(drawCanvas);
        }
    }

    // Trigger visual cycle when visibility changes to catch up if needed
    $: if (isVisible && !animationId) {
        drawCanvas();
    }

    function generateTxHash() {
        return (
            "0x" +
            Array.from({ length: 40 }, () =>
                Math.floor(Math.random() * 16).toString(16),
            ).join("")
        );
    }

    function runSimulation() {
        if (state === "done") {
            // Manual Reset
            state = "idle";
            validationSteps = validationSteps.map((s) => ({
                ...s,
                status: "pending",
            }));
            logs = [];
            time = 0;
            return;
        }

        if (state !== "idle") return;

        // Start
        state = "running";
        time = 0;
        validationSteps = validationSteps.map((s) => ({
            ...s,
            status: "pending",
        }));
        logs = [
            `> TXN INITIATED: ${generateTxHash().substring(0, 16)}...`,
            `> CALLING LINEUM_VRF.sol...`,
        ];

        let sequence = 0;

        const simInterval = setInterval(() => {
            sequence++;

            if (sequence === 1) {
                validationSteps[0].status = "pass";
                validationSteps[1].status = "running";
                logs = [...logs, `> PRE-PAYING GAS ESTIMATE... OK`];
            } else if (sequence === 3) {
                state = "delivering";
                validationSteps[1].status = "pass";
                validationSteps[2].status = "running";
                logs = [...logs, `> VACUUM ENTROPY HARVESTED`];
                if (logs.length > 5) logs.shift();
            } else if (sequence === 5) {
                validationSteps[2].status = "pass";
                validationSteps[3].status = "running";
                logs = [...logs, `> GENERATING ZK-SNARK PROOF...`];
                if (logs.length > 5) logs.shift();
            } else if (sequence === 7) {
                state = "done";
                time = 0; // reset for ripple
                validationSteps[3].status = "pass";
                logs = [
                    ...logs,
                    `> ON-CHAIN VERIFICATION PASSED`,
                    `> [SUCCESS] RANDOMNESS INJECTED`,
                ];
                if (logs.length > 5) logs.shift();
                clearInterval(simInterval);
            }
        }, 600);
    }
</script>

<ShowcaseTemplate
    badge="5 / 7 API SUITE"
    title="Web3 VRF API"
    description="Deliver cryptographically verifiable, truly unpredictable quantum randomness directly to your smart contracts. Un-gameable on-chain entropy powered by Lineum's fluid vacuum simulation."
    traditionalTitle="Traditional On-Chain Randomness"
    traditionalDesc="Predictable block hashes or easily manipulated off-chain data sources. Prone to MEV attacks and validator front-running."
    lineumTitle="Lineum ZK-VRF"
    lineumDesc="Quantum chaotic measurements locked with zero-knowledge proofs. Guaranteed unpredictable, instantly verifiable."
    language="Solidity"
    codeSnippet={`import "@lineum/contracts/LineumVRF.sol";

contract LootBox is LineumVRFConsumer {
    function openBox(uint256 boxId) public {
        // Request mathematically pure entropy
        uint256 requestId = requestRandomness();
        boxOwners[requestId] = msg.sender;
    }

    function fulfillRandomness(uint256 id, uint256 randomWord) internal override {
        // Un-gameable result delivered on-chain
        uint256 winningItem = randomWord % 100;
        mintItem(boxOwners[id], winningItem);
    }
}`}
>
    <!-- Visual -->
    <div
        slot="visual"
        use:intersect={(inView) => (isVisible = inView)}
        class="w-full flex items-center justify-center p-8 bg-slate-950/80 rounded-3xl border border-sky-500/20 shadow-[0_0_80px_rgba(56,189,248,0.05)] overflow-hidden h-[450px] relative font-mono"
    >
        <!-- Canvas Container -->
        <div
            class="absolute inset-0 top-0 h-[65%] w-full bg-black/50 border-b border-sky-500/30 overflow-hidden flex items-center justify-center"
        >
            <canvas
                bind:this={canvas}
                width="800"
                height="300"
                class="w-full h-full object-cover mix-blend-screen"
            ></canvas>

            <!-- Contextual Overlay Labels -->
            <div
                class="absolute top-4 left-6 text-[10px] sm:text-xs text-rose-500 font-bold tracking-widest uppercase opacity-70"
            >
                Lineum
            </div>
            <div
                class="absolute top-4 right-6 text-[10px] sm:text-xs text-sky-500 font-bold tracking-widest uppercase opacity-70 text-right"
            >
                Target Contract
            </div>
        </div>

        <!-- Controls -->
        <div
            class="absolute bottom-6 left-8 right-8 h-[30%] flex items-end justify-center"
        >
            <ShowcaseButton
                status={state === "delivering" ? "running" : state}
                theme="purple"
                disabled={state === "delivering" || state === "running"}
                idleText="Generate VRF Proof"
                runningText={state === "running"
                    ? "Broadcasting TXN..."
                    : "VRF Payload Incoming..."}
                doneText="New VRF Hash"
                on:click={runSimulation}
            />
        </div>
    </div>

    <!-- Proof (Cryptographic Verification) -->
    <ShowcaseTerminal
        slot="proof"
        title="Live Cryptographic Audit"
        badge="ZK-SNARK"
        badgeColorClass="text-sky-500"
        primaryColorClass="text-sky-400"
        {logs}
        status={state === "delivering" ? "running" : state}
    >
        <div slot="side-panel">
            <div
                class="text-[10px] text-slate-500 uppercase tracking-wider mb-2"
            >
                On-Chain Consensus
            </div>
            {#each validationSteps as step}
                <div class="flex items-center justify-between text-[10px] mb-2">
                    <span
                        class={step.status === "pass"
                            ? "text-slate-300"
                            : "text-slate-600"}>{step.name}</span
                    >
                    {#if step.status === "pass"}
                        <span class="text-emerald-400 font-bold ml-2">PASS</span
                        >
                    {:else if step.status === "running"}
                        <span
                            class="text-sky-400 animate-pulse ml-2 text-[8px] tracking-widest"
                            >AWAIT</span
                        >
                    {:else}
                        <span class="text-slate-700 ml-2 text-[8px] uppercase"
                            >PEND</span
                        >
                    {/if}
                </div>
            {/each}
        </div>
    </ShowcaseTerminal>
</ShowcaseTemplate>

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
</style>
