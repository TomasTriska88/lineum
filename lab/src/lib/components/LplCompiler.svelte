<script>
    import { onMount } from "svelte";
    import { t } from "../i18n";

    let size = 32;
    let mask = new Array(size * size).fill(1.0);
    let inputs = [];

    let mode = "draw_wall"; // 'draw_wall', 'erase_wall', 'add_input'
    let isDrawing = false;
    let canvas;
    let resultCanvas;
    let ctx;
    let resultCtx;

    let isCompiling = false;
    let error = null;

    // Load some preset?
    const clearMask = () => {
        mask = new Array(size * size).fill(1.0);
        inputs = [];
        compileResult = null;
        drawMask();
        if (resultCtx)
            resultCtx.clearRect(0, 0, resultCanvas.width, resultCanvas.height);
    };

    onMount(() => {
        ctx = canvas.getContext("2d");
        resultCtx = resultCanvas.getContext("2d");
        drawMask();
    });

    const getPixelCoords = (e) => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        let x = (e.clientX - rect.left) * scaleX;
        let y = (e.clientY - rect.top) * scaleY;

        return {
            px: Math.floor(x / (canvas.width / size)),
            py: Math.floor(y / (canvas.height / size)),
        };
    };

    const handlePointerDown = (e) => {
        isDrawing = true;
        applyTool(e);
    };

    const handlePointerMove = (e) => {
        if (!isDrawing) return;
        applyTool(e);
    };

    const handlePointerUp = () => {
        isDrawing = false;
    };

    const applyTool = (e) => {
        const { px, py } = getPixelCoords(e);
        if (px < 0 || px >= size || py < 0 || py >= size) return;

        const idx = py * size + px;

        if (mode === "draw_wall") {
            mask[idx] = 0.0;
        } else if (mode === "erase_wall") {
            mask[idx] = 1.0;
            // Remove input if erasing
            inputs = inputs.filter((i) => !(i.x === px && i.y === py));
        } else if (mode === "add_input") {
            // only add if not already wall and not already input
            if (
                mask[idx] === 1.0 &&
                !inputs.some((i) => i.x === px && i.y === py)
            ) {
                inputs = [...inputs, { x: px, y: py }];
            }
        }
        drawMask();
    };

    const drawMask = () => {
        if (!ctx) return;
        const cellSize = canvas.width / size;

        ctx.fillStyle = "#050505";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw fluid (1.0) and walls (0.0)
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                const idx = y * size + x;
                if (mask[idx] === 1.0) {
                    ctx.fillStyle = "#111"; // fluid
                } else {
                    ctx.fillStyle = "#00ffff"; // walls are neon
                }
                ctx.fillRect(
                    x * cellSize,
                    y * cellSize,
                    cellSize - 1,
                    cellSize - 1,
                );
            }
        }

        // Draw inputs
        ctx.fillStyle = "#ffaa00";
        for (const inp of inputs) {
            ctx.fillRect(
                inp.x * cellSize,
                inp.y * cellSize,
                cellSize - 1,
                cellSize - 1,
            );
        }
    };

    const drawResult = (phiFlat) => {
        if (!resultCtx) return;
        const cellSize = resultCanvas.width / size;

        // Render colormap
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                const idx = y * size + x;
                const val = phiFlat[idx];

                // fluid vs wall base
                if (mask[idx] === 0.0) {
                    resultCtx.fillStyle = "#00ffff"; // Keep wall visible
                } else {
                    // map val (0 to 1) to a heatmap (dark to neon green/blue)
                    const intensity = Math.floor(val * 255);
                    resultCtx.fillStyle = `rgb(0, ${intensity}, ${Math.floor(intensity / 2)})`;
                }

                resultCtx.fillRect(
                    x * cellSize,
                    y * cellSize,
                    cellSize,
                    cellSize,
                );
            }
        }

        // Highlight inputs
        resultCtx.fillStyle = "#ffaa00";
        for (const inp of inputs) {
            resultCtx.beginPath();
            resultCtx.arc(
                inp.x * cellSize + cellSize / 2,
                inp.y * cellSize + cellSize / 2,
                cellSize / 3,
                0,
                Math.PI * 2,
            );
            resultCtx.fill();
        }
    };

    const compile = async () => {
        if (inputs.length === 0) {
            error = "Please place at least one Input (Laser) on the grid.";
            setTimeout(() => (error = null), 3000);
            return;
        }

        isCompiling = true;
        error = null;

        try {
            const res = await fetch(
                "http://127.0.0.1:8000/api/v1/ai/lpl-compile",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        mask_flat: mask,
                        size: size,
                        inputs: inputs,
                        iterations: 500,
                    }),
                },
            );

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Build failed");
            }

            const data = await res.json();
            drawResult(data.phi_flat);
        } catch (e) {
            console.error(e);
            error = e.message;
        } finally {
            isCompiling = false;
        }
    };

    // Presets
    const loadPresetAND = () => {
        clearMask();
        // create a Y shape for AND gate
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                mask[y * size + x] = 0.0; // all walls
            }
        }
        // Carve channels
        const carve = (x, y) => (mask[y * size + x] = 1.0);

        // Left input channel
        for (let x = 4; x < 14; x++) {
            carve(x, 8);
            carve(x, 9);
        }
        // Right input channel
        for (let x = 4; x < 14; x++) {
            carve(x, 22);
            carve(x, 23);
        }
        // Diagonal merge
        for (let i = 0; i < 6; i++) {
            carve(14 + i, 9 + i);
            carve(14 + i, 10 + i);
            carve(14 + i, 22 - i);
            carve(14 + i, 21 - i);
        }
        // Output channel
        for (let x = 20; x < 30; x++) {
            carve(x, 15);
            carve(x, 16);
        }

        // Waste channels
        for (let x = 13; x < 18; x++) {
            carve(x, 5);
            carve(x, 26);
        }

        inputs = [
            { x: 4, y: 8 },
            { x: 4, y: 22 },
        ]; // Both A and B active
        drawMask();
    };
</script>

<div class="lpl-container">
    <div class="header">
        <h2>LINEUM POLYGON LANGUAGE (LPL) COMPILER</h2>
        <p>
            Design spatial topology and run Universal Logic Gates via continuous
            fluid dynamics. Draw walls to guide the wave.
        </p>
    </div>

    <div class="workspace">
        <!-- TOOLBAR -->
        <div class="toolbar">
            <h3>TOOLS</h3>
            <button
                class:active={mode === "draw_wall"}
                on:click={() => (mode = "draw_wall")}
            >
                🟦 Draw Walls (Crystal)
            </button>
            <button
                class:active={mode === "erase_wall"}
                on:click={() => (mode = "erase_wall")}
            >
                ⬛ Erase (Fluid)
            </button>
            <button
                class:active={mode === "add_input"}
                on:click={() => (mode = "add_input")}
            >
                🟠 Place Input (Laser)
            </button>

            <div class="divider"></div>

            <h3>PRESETS</h3>
            <button on:click={loadPresetAND}>Load AND Gate</button>
            <button on:click={clearMask} class="danger">Clear Space</button>

            <div class="divider"></div>

            <button
                class="compile-btn"
                disabled={isCompiling}
                on:click={compile}
            >
                {isCompiling ? "COMPILING WAVES..." : "▶ RUN COMPILER (API)"}
            </button>

            {#if error}
                <div class="error-msg">{error}</div>
            {/if}
        </div>

        <!-- CANVAS AREA -->
        <div class="canvas-wrapper">
            <div class="canvas-block">
                <h4>PHYSICAL MASK (CAD)</h4>
                <canvas
                    bind:this={canvas}
                    width="500"
                    height="500"
                    on:pointerdown={handlePointerDown}
                    on:pointermove={handlePointerMove}
                    on:pointerup={handlePointerUp}
                    on:pointerleave={handlePointerUp}
                ></canvas>
                <div class="legend">Click & drag to shape the geometry.</div>
            </div>

            <div class="arrow">➔</div>

            <div class="canvas-block">
                <h4>WAVEFORM TELEMETRY (Φ)</h4>
                <canvas bind:this={resultCanvas} width="500" height="500"
                ></canvas>
                <div class="legend">
                    Resulting Standing Waves after 500 iterations.
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .lpl-container {
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
        color: #00ffff;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.4);
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
        gap: 40px;
        flex: 1;
        align-items: stretch;
    }

    .toolbar {
        width: 300px;
        background: rgba(0, 5, 10, 0.8);
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.05);
        padding: 25px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        border-radius: 4px;
    }

    .toolbar h3 {
        margin: 15px 0 5px 0;
        font-size: 0.8rem;
        letter-spacing: 3px;
        color: #888;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 5px;
    }

    button {
        background: rgba(0, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 255, 0.2);
        color: #ccc;
        padding: 12px 15px;
        cursor: pointer;
        text-align: left;
        font-size: 0.85rem;
        font-family: "Courier New", Courier, monospace;
        letter-spacing: 1px;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        border-radius: 2px;
    }

    button:hover {
        background: rgba(0, 255, 255, 0.1);
        color: #fff;
        box-shadow: inset 0 0 10px rgba(0, 255, 255, 0.1);
    }

    button.active {
        background: rgba(0, 255, 255, 0.15);
        border-color: #00ffff;
        color: #00ffff;
        box-shadow:
            0 0 15px rgba(0, 255, 255, 0.2),
            inset 4px 0 0 #00ffff;
        font-weight: bold;
    }

    button.danger {
        border-color: rgba(255, 60, 60, 0.4);
        color: #ff5555;
    }

    button.danger:hover {
        background: rgba(255, 60, 60, 0.15);
        color: #ff8888;
        box-shadow: inset 0 0 10px rgba(255, 60, 60, 0.2);
    }

    .compile-btn {
        margin-top: auto;
        background: #00ffff;
        color: #000;
        font-weight: bold;
        text-align: center;
        letter-spacing: 2px;
        padding: 15px;
        text-transform: uppercase;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    }

    .compile-btn:hover {
        background: #fff;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.8);
        transform: translateY(-2px);
    }

    .compile-btn:disabled {
        background: rgba(255, 255, 255, 0.1);
        color: #555;
        border-color: #333;
        box-shadow: none;
        cursor: not-allowed;
        transform: none;
    }

    .divider {
        height: 1px;
        background: rgba(0, 255, 255, 0.2);
        margin: 5px 0;
    }

    .canvas-wrapper {
        display: flex;
        align-items: center;
        gap: 50px;
        flex: 1;
        justify-content: center;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 40px;
        border-radius: 4px;

        /* Blueprint Grid pattern */
        background-image: linear-gradient(
                rgba(0, 255, 255, 0.03) 1px,
                transparent 1px
            ),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
    }

    .canvas-block {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .canvas-block h4 {
        margin: 0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #00ffff;
        background: rgba(0, 255, 255, 0.1);
        padding: 4px 10px;
        border-left: 3px solid #00ffff;
    }

    canvas {
        background: #020202;
        border: 1px solid rgba(0, 255, 255, 0.4);
        box-shadow:
            0 0 30px rgba(0, 255, 255, 0.1),
            inset 0 0 20px rgba(0, 255, 255, 0.05);
        cursor: crosshair;
        image-rendering: pixelated;
        border-radius: 2px;
    }

    .arrow {
        font-size: 3rem;
        color: rgba(0, 255, 255, 0.3);
        text-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
    }

    .legend {
        font-size: 0.8rem;
        color: #777;
        font-style: italic;
    }

    .error-msg {
        color: #ff5555;
        font-size: 0.8rem;
        background: rgba(255, 0, 0, 0.1);
        padding: 10px;
        border-left: 3px solid #ff5555;
        margin-top: 15px;
        font-weight: bold;
    }
</style>
