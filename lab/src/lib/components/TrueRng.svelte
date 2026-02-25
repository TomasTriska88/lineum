<script>
    import { onMount } from "svelte";

    let canvas;
    let ctx;
    let isGenerating = false;
    let hexStream = [];
    let error = null;
    let animationId = null;

    // Simulate boiling pot while waiting
    let noiseGrid = [];
    const GRID_SIZE = 64;

    const generateNoiseGrid = () => {
        noiseGrid = [];
        for (let y = 0; y < GRID_SIZE; y++) {
            const row = [];
            for (let x = 0; x < GRID_SIZE; x++) {
                row.push(Math.random());
            }
            noiseGrid.push(row);
        }
    };

    const drawGrid = (gridData) => {
        if (!ctx) return;
        const cellSize = canvas.width / GRID_SIZE;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let y = 0; y < GRID_SIZE; y++) {
            for (let x = 0; x < GRID_SIZE; x++) {
                const val = gridData[y]?.[x] || 0;
                // Dark background with intense red/pink chaotic waves
                const intensity = Math.floor(val * 255);
                ctx.fillStyle = `rgb(${intensity}, ${Math.floor(intensity * 0.2)}, ${Math.floor(intensity * 0.5)})`;
                ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    };

    const animateBoiling = () => {
        if (!isGenerating) return;
        generateNoiseGrid();
        // Smooth out the noise slightly for a "fluid" look
        for (let i = 0; i < 3; i++) {
            for (let y = 1; y < GRID_SIZE - 1; y++) {
                for (let x = 1; x < GRID_SIZE - 1; x++) {
                    noiseGrid[y][x] =
                        (noiseGrid[y][x] +
                            noiseGrid[y - 1][x] +
                            noiseGrid[y + 1][x] +
                            noiseGrid[y][x - 1] +
                            noiseGrid[y][x + 1]) /
                        5;
                }
            }
        }
        drawGrid(noiseGrid);
        animationId = requestAnimationFrame(animateBoiling);
    };

    onMount(() => {
        ctx = canvas.getContext("2d");
        generateNoiseGrid();
        drawGrid(noiseGrid);
    });

    const generateEntropy = async () => {
        isGenerating = true;
        error = null;
        if (!animationId) animateBoiling();

        try {
            // Target the SvelteKit proxy on the portal (assuming portal runs on 5173 in dev)
            const res = await fetch("http://localhost:5173/api/v1/rng", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resolution: GRID_SIZE,
                    pump_cycles: 1500,
                }),
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || "RNG Pipeline failed.");
            }

            const data = await res.json();

            isGenerating = false;
            cancelAnimationFrame(animationId);
            animationId = null;

            // Typewriter effect for hex stream
            const newHex = data.entropy_hex;
            let currentStr = "";
            let i = 0;
            const typeWriter = setInterval(() => {
                currentStr += newHex[i];
                // Update the top element in the stream to show typing, or push new if start
                if (i === 0) {
                    hexStream = [
                        `> [HARDWARE_ENTROPY] ${currentStr}`,
                        ...hexStream,
                    ].slice(0, 50);
                } else {
                    hexStream[0] = `> [HARDWARE_ENTROPY] ${currentStr}`;
                }

                i++;
                if (i >= newHex.length) {
                    clearInterval(typeWriter);
                    // Draw the final raw sample received from backend if available
                    if (data.raw_sample) {
                        // Note: raw sample from backend is small (central sample). We can just render something symbolic or expand it.
                        // For now, we leave the canvas displaying the chaotic state that generated it.
                    }
                }
            }, 10);
        } catch (e) {
            isGenerating = false;
            cancelAnimationFrame(animationId);
            animationId = null;
            error = e.message;
            console.error(e);
        }
    };
</script>

<div class="rng-container">
    <div class="header">
        <h2>TRUE RNG HARVESTER</h2>
        <p>
            Harvest mathematically perfect randomness by amplifying physical CPU
            hardware thermal noise at the Edge of Chaos.
        </p>
    </div>

    <div class="workspace">
        <div class="panel controls-panel">
            <h3>NATIVE ENTROPY</h3>
            <p class="desc">
                Bypasses deterministic pseudo-RNG. Injects 1500 cycles of
                chaotic wave amplification.
            </p>

            <button
                class="generate-btn"
                on:click={generateEntropy}
                disabled={isGenerating}
            >
                {isGenerating
                    ? "AMPLIFYING THERMAL NOISE..."
                    : "▶ GENERATE ENTROPY"}
            </button>

            {#if error}
                <div class="error-msg">{error}</div>
            {/if}

            <div class="stats mt-4">
                <div class="stat">
                    <span class="label">GRID SIZE:</span>
                    <span class="val">64x64</span>
                </div>
                <div class="stat">
                    <span class="label">CYCLES:</span>
                    <span class="val">1500</span>
                </div>
                <div class="stat">
                    <span class="label">MODE:</span>
                    <span class="val">Hardware Phase Angle</span>
                </div>
            </div>
        </div>

        <div class="panel visual-panel">
            <div class="canvas-block">
                <h4>THERMAL CHAOS FIELD (Φ)</h4>
                <canvas bind:this={canvas} width="400" height="400"></canvas>
            </div>
        </div>

        <div class="panel terminal-panel">
            <h4>RAW HEX STREAM</h4>
            <div class="terminal">
                {#if hexStream.length === 0}
                    <div class="text-muted">
                        Waiting for quantum entropy harvest...
                    </div>
                {/if}
                {#each hexStream as line}
                    <div>{line}</div>
                {/each}
            </div>
        </div>
    </div>
</div>

<style>
    .rng-container {
        padding: 40px;
        color: #fff;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
        font-family: "Courier New", Courier, monospace;
    }

    .header h2 {
        margin: 0 0 10px 0;
        font-weight: bold;
        letter-spacing: 4px;
        color: #f43f5e;
        text-shadow: 0 0 10px rgba(244, 63, 94, 0.4);
        font-family: sans-serif;
    }

    .header p {
        margin: 0;
        font-size: 0.9rem;
        color: #aaa;
        margin-bottom: 20px;
        max-width: 600px;
    }

    .workspace {
        display: flex;
        gap: 30px;
        flex: 1;
        align-items: stretch;
    }

    .panel {
        background: rgba(0, 5, 10, 0.8);
        border: 1px solid rgba(244, 63, 94, 0.3);
        box-shadow: 0 0 20px rgba(244, 63, 94, 0.05);
        padding: 25px;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
    }

    .controls-panel {
        width: 300px;
    }

    .visual-panel {
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.5);
    }

    .terminal-panel {
        flex: 1;
    }

    h3 {
        margin: 0 0 10px 0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #888;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 5px;
    }

    h4 {
        margin: 0 0 15px 0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #f43f5e;
        background: rgba(244, 63, 94, 0.1);
        padding: 4px 10px;
        border-left: 3px solid #f43f5e;
    }

    .desc {
        color: #bbb;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    .generate-btn {
        background: #f43f5e;
        color: #000;
        font-weight: bold;
        text-align: center;
        letter-spacing: 1px;
        padding: 15px;
        border: none;
        cursor: pointer;
        text-transform: uppercase;
        box-shadow: 0 0 20px rgba(244, 63, 94, 0.3);
        transition: all 0.2s;
    }

    .generate-btn:hover:not(:disabled) {
        background: #fff;
        box-shadow: 0 0 25px rgba(244, 63, 94, 0.8);
        transform: translateY(-2px);
    }

    .generate-btn:disabled {
        background: rgba(244, 63, 94, 0.2);
        color: #f43f5e;
        cursor: not-allowed;
    }

    canvas {
        background: #020202;
        border: 1px solid rgba(244, 63, 94, 0.4);
        box-shadow: 0 0 30px rgba(244, 63, 94, 0.1);
        image-rendering: pixelated;
    }

    .terminal {
        flex: 1;
        background: #000;
        border: 1px solid #333;
        padding: 15px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 0.8rem;
        line-height: 1.6;
        color: #f43f5e;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 1);
    }

    .text-muted {
        color: #444;
    }

    .error-msg {
        color: #ff5555;
        font-size: 0.8rem;
        background: rgba(255, 0, 0, 0.1);
        padding: 10px;
        border-left: 3px solid #ff5555;
        margin-top: 15px;
    }

    .stats {
        margin-top: 20px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .stat {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
    }

    .stat .label {
        color: #888;
    }
    .stat .val {
        color: #fff;
    }
</style>
