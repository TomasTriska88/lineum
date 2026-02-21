<script lang="ts">
    import { onMount, onDestroy } from "svelte";

    // Místo Concurrenty opět voláme spouštění jen po jednom (čistší dev zkušenost)
    let canvas: HTMLCanvasElement = null as any;
    let gl: WebGLRenderingContext | null;
    let program: WebGLProgram | null;
    let animationFrameId: number;
    let positionBuffer: WebGLBuffer | null = null;

    const MAP_SIZE = 128;

    // Simulation state
    let kappaFlat = new Float32Array(MAP_SIZE * MAP_SIZE).fill(1);
    let phiFlat = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);
    // Využijeme Blue channel druhé textury pro trasu
    let pathMap = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);

    // Body zájmu (nyní re-assignované podle presetu)
    let startPoint = { x: 10, y: 10 };
    let targetPoint = { x: 110, y: 110 };

    // Net State
    let isSimulating = false;
    let socket: WebSocket | null = null;
    let currentStep = 0;

    // === STAV APLIKACE & PRESETY ===
    type PresetId = "urban_design" | "evacuation" | "vascular" | "dielectric";
    let activePreset: PresetId = "urban_design";

    // Dynamické Definice Agentů pro daný preset
    let scenarioAgents = [
        {
            id: "A",
            start: { x: 50, y: 15 },
            color: "#38bdf8",
            name: "Convoy Alpha",
            eta: "4.2 mins",
        },
    ];

    const PRESETS = {
        urban_design: {
            name: "1. Urban & Traffic Routing",
            desc: "Heavy momentum memory. Merges small paths into efficient wide highways.",
            target: { x: 60, y: 110 },
        },
        evacuation: {
            name: "2. Crowd Panic & Evacuation",
            desc: "Short memory, high pressure. Crowds scatter around bottlenecks chaotically.",
            target: { x: 60, y: 120 },
        },
        vascular: {
            name: "3. Vascular / Irrigation Network",
            desc: "High noise divergence. Fluid covers maximum tissue area forming fractals.",
            target: { x: 60, y: 100 },
        },
        dielectric: {
            name: "4. Dielectric Breakdown (Lightning)",
            desc: "Brutal gradient pressure. Burns straight through micro-pores in insulators.",
            target: { x: 60, y: 120 },
        },
    };

    // Textury pro GPU
    let kappaTexture: WebGLTexture | null = null;
    let dynTexture: WebGLTexture | null = null;

    // --- Shader sources ---
    const vs = `
        attribute vec2 a_position;
        varying vec2 v_uv;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
            // Prepočet -1..1 na 0..1 (UV)
            v_uv = a_position * 0.5 + 0.5; 
            // WebGL ma flipnuté Y
            v_uv.y = 1.0 - v_uv.y; 
        }
    `;

    // HLAVNÍ MÁGIE - Fyzikální Fragment Shader (Podobný jako na Homepage)
    const fs = `
        precision mediump float;
        varying vec2 v_uv;
        
        uniform sampler2D u_kappaMap; // R channel: 1=Volno, 0=Zel
        uniform sampler2D u_dynMap;   // R channel: Phi (Teplo), G channel: null, B channel: Cesta
        
        uniform float u_time;
        uniform vec2 u_resolution;
        uniform vec2 u_start;
        uniform vec2 u_target;

        // --- Golden Mean Hyper-Fidelity Palette z Homepage ---
        vec3 space_black  = vec3(0.004, 0.004, 0.012);
        vec3 nebula_purp = vec3(0.18, 0.05, 0.42);  
        vec3 nebula_mag  = vec3(0.48, 0.05, 0.32);  
        vec3 kappa_blue  = vec3(0.045, 0.13, 0.28); 
        vec3 neon_path   = vec3(0.22, 0.74, 0.97); // 38bdf8 Glow

        float hash(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
        }

        void main() {
            // Sampling hodnoty pre daný bod mapy
            vec4 kappaTex = texture2D(u_kappaMap, v_uv);
            vec4 dynTex = texture2D(u_dynMap, v_uv);
            
            float isWall = 1.0 - kappaTex.r; 
            float phi = dynTex.r;
            float path_vis = dynTex.b;

            // Zakladni space black
            vec3 color = space_black;
            
            // 1. Zdi (Dark Kappa Blue jako na strance, plus mírný pohyb/šum)
            if (isWall > 0.5) {
                // Mírná Cyber-mřížka přes zdi z úvodní stránky pro dojem Matrixu
                float grid = sin(v_uv.x * 400.0) * sin(v_uv.y * 400.0);
                color = mix(kappa_blue, kappa_blue * 0.5, grid * 0.2 + 0.2);
            } else {
                // 2. Heatmapa (Vlna Phi - přesný přepočet barev jako na HP)
                if (phi > 0.01) {
                    float cloud_mask = smoothstep(0.01, 0.5, phi);
                    vec3 nebula = mix(space_black, nebula_purp, cloud_mask);
                    
                    float threshold = 0.5;
                    float boundary = smoothstep(threshold - 0.1, threshold + 0.1, phi);
                    nebula = mix(nebula, nebula_mag, boundary);
                    
                    // Rim Light / Sharp Edge (vlna "naráží")
                    float rim = smoothstep(0.05, 0.0, abs(phi - threshold));
                    nebula += rim * nebula_mag * 0.8;
                    
                    color = nebula;
                    
                    // Interference Shimmer efekty v Heatmape (přidání času z u_time pro pulz)
                    color += sin(v_uv.x * 200.0 + u_time) * cos(v_uv.y * 200.0 - u_time) * 0.5 * nebula_purp * phi;
                }
            }

            // 3. Trasa Robota (Masivní neonový GLOW počítaný přímo v shaderu v blur oblasti pixelu)
            if (path_vis > 0.01) {
                // Vnitřní svítivé jádro blížící sa bielej farbe
                vec3 core = mix(neon_path, vec3(1.0), path_vis * path_vis);
                // Glow do strany v násobcích neon
                color += core * path_vis * 2.5; 
            }

            // 4. Start (Tepající Modrá Dióda)
            float distStart = length(v_uv - u_start);
            if (distStart < 0.012) {
                color += neon_path * smoothstep(0.012, 0.0, distStart) * (1.2 + 0.3 * sin(u_time * 5.0));
            }

            // 5. Cíl (Tepající Červená Dióda)
            float distTarget = length(v_uv - u_target);
            if (distTarget < 0.015) {
                color += vec3(0.93, 0.26, 0.26) * smoothstep(0.015, 0.0, distTarget) * (1.2 + 0.3 * cos(u_time * 4.0));
            }

            // Vignette (Jako na Homepage)
            vec2 uv_orig = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
            color *= 1.15 - length(uv_orig) * 0.5;

            gl_FragColor = vec4(color, 1.0);
        }
    `;

    function createShader(
        gl: WebGLRenderingContext,
        type: number,
        source: string,
    ) {
        const shader = gl.createShader(type);
        if (!shader) return null;
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error(gl.getShaderInfoLog(shader));
            gl.deleteShader(shader);
            return null;
        }
        return shader;
    }

    function initWebGL() {
        if (!canvas) return;
        gl = canvas.getContext("webgl", {
            antialias: false,
            preserveDrawingBuffer: true,
        }); // Preserve kvůli stabilitě sítě
        if (!gl) return;

        const vertexShader = createShader(gl, gl.VERTEX_SHADER, vs);
        const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fs);
        if (!vertexShader || !fragmentShader) return;

        program = gl.createProgram();
        if (!program) return;
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error("Shader Link Error:", gl.getProgramInfoLog(program));
            return;
        }

        // --- Atributy Geometry (Plocha mapy je jen čtverec -1,-1 až 1,1) ---
        const positions = new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]);
        positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

        const positionLocation = gl.getAttribLocation(program, "a_position");

        // --- Textury ---
        kappaTexture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, kappaTexture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); // Nechceme blur na zdech
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

        dynTexture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, dynTexture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); // LINEAR = Brutálně jemný Blur pro fyziku interpolací přes GPU (to co hledáme!)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    }

    function generateMapForPreset() {
        kappaFlat.fill(1);
        const addWall = (x: number, y: number, w: number, h: number) => {
            for (let j = y; j < y + h; j++) {
                for (let i = x; i < x + w; i++) {
                    if (i >= 0 && i < MAP_SIZE && j >= 0 && j < MAP_SIZE) {
                        kappaFlat[j * MAP_SIZE + i] = 0;
                    }
                }
            }
        };

        if (activePreset === "urban_design") {
            // Městské bloky
            addWall(20, 30, 80, 10);
            addWall(40, 60, 80, 10);
            addWall(10, 90, 80, 10);
            addWall(30, 40, 10, 20);
            addWall(90, 70, 10, 20);
            scenarioAgents = [
                {
                    id: "A",
                    start: { x: 50, y: 15 },
                    color: "#38bdf8",
                    name: "Convoy Alpha",
                    eta: "4.2 mins",
                },
            ];
            targetPoint = { x: 60, y: 110 };
        } else if (activePreset === "evacuation") {
            // Skupina v hale a úzký východ s překážkami kolem
            addWall(10, 40, 40, 5); // Levá zed
            addWall(70, 40, 50, 5); // Pravá zed
            addWall(55, 60, 10, 10); // Pilíř za dveřmi
            addWall(30, 80, 60, 5); // Další zdi
            scenarioAgents = [
                {
                    id: "Crowd_L",
                    start: { x: 30, y: 20 },
                    color: "#f87171",
                    name: "Sector A Panic",
                    eta: "T-50s",
                },
                {
                    id: "Crowd_R",
                    start: { x: 90, y: 20 },
                    color: "#fb923c",
                    name: "Sector B Panic",
                    eta: "T-80s",
                },
            ];
            targetPoint = { x: 60, y: 120 };
        } else if (activePreset === "vascular") {
            // Orgán tkáně, nepravidelné blokace, hledání cest skrz buňky
            for (let k = 0; k < 15; k++) {
                addWall(
                    Math.random() * 100 + 10,
                    Math.random() * 80 + 20,
                    Math.random() * 15 + 5,
                    Math.random() * 15 + 5,
                );
            }
            addWall(0, 110, 128, 5); // Membrána dole
            scenarioAgents = [
                {
                    id: "A",
                    start: { x: 64, y: 10 },
                    color: "#34d399",
                    name: "Artery Root",
                    eta: "Pulse",
                },
            ];
            targetPoint = { x: 64, y: 120 };
        } else if (activePreset === "dielectric") {
            // Izolant (tlustá zeď s malýma dírkama / kazy materiálu)
            addWall(0, 50, 128, 30);
            // Uděláme póry
            const p = 0; // zruseni zdi v dire
            for (let i = 0; i < 10; i++) {
                const px = Math.floor(Math.random() * 120);
                const py = Math.floor(Math.random() * 28) + 51;
                kappaFlat[py * MAP_SIZE + px] = 1;
                kappaFlat[py * MAP_SIZE + px + 1] = 1;
            }
            scenarioAgents = [
                {
                    id: "L",
                    start: { x: 64, y: 10 },
                    color: "#e879f9",
                    name: "Voltage Anode",
                    eta: "10 MV",
                },
            ];
            targetPoint = { x: 64, y: 120 };
        }
    }

    function handlePresetChange(e: any) {
        if (isSimulating) stopSimulation();
        activePreset = e.target.value as PresetId;
        generateMapForPreset();
        uploadKappa();
        phiFlat.fill(0);
        pathMap.fill(0);
        currentStep = 0;
        uploadDynamics();
    }

    // Nahrání dat do GPU Pamětové mapy: Kappa (Zdi)
    function uploadKappa() {
        if (!gl || !kappaTexture) return;
        const data = new Uint8Array(MAP_SIZE * MAP_SIZE * 4); // RGBA formát
        for (let i = 0; i < MAP_SIZE * MAP_SIZE; i++) {
            const v = kappaFlat[i] * 255;
            data[i * 4] = v; // R
            data[i * 4 + 1] = v; // G
            data[i * 4 + 2] = v; // B
            data[i * 4 + 3] = 255; // Alpha
        }
        gl.bindTexture(gl.TEXTURE_2D, kappaTexture);
        gl.texImage2D(
            gl.TEXTURE_2D,
            0,
            gl.RGBA,
            MAP_SIZE,
            MAP_SIZE,
            0,
            gl.RGBA,
            gl.UNSIGNED_BYTE,
            data,
        );
    }

    // Nahrání dat do GPU Pamětové mapy: Phi (Heatmap) + Path (Trasa v B kanálu pro Glow)
    function uploadDynamics() {
        if (!gl || !dynTexture) return;

        const data = new Uint8Array(MAP_SIZE * MAP_SIZE * 4);
        for (let i = 0; i < MAP_SIZE * MAP_SIZE; i++) {
            data[i * 4] = Math.min(255, phiFlat[i] * 255); // R = Fyzika tepla
            data[i * 4 + 1] = 0; // G = nic
            data[i * 4 + 2] = Math.min(255, pathMap[i] * 255); // B = Cesta z path_vis
            data[i * 4 + 3] = 255;
        }

        gl.bindTexture(gl.TEXTURE_2D, dynTexture);
        gl.texImage2D(
            gl.TEXTURE_2D,
            0,
            gl.RGBA,
            MAP_SIZE,
            MAP_SIZE,
            0,
            gl.RGBA,
            gl.UNSIGNED_BYTE,
            data,
        );
    }

    function renderFrame(time: number) {
        if (!gl || !program) return;

        // Resize Fix (Downsampling for GPU Performance)
        // Vynutíme limit výpočetní matice, aby 4K monitory netočily GPU větráčky na max.
        const scale = Math.min(1.0, 1280 / canvas.clientWidth);
        const displayWidth = Math.max(
            1,
            Math.floor(canvas.clientWidth * scale),
        );
        const displayHeight = Math.max(
            1,
            Math.floor(canvas.clientHeight * scale),
        );
        if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
            canvas.width = displayWidth;
            canvas.height = displayHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);
        }

        // Dynamické odeslani dat (Jen kdyz se změnily!)
        uploadDynamics();

        gl.clearColor(0, 0, 0, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);

        gl.useProgram(program);

        // Binding proměnných
        const positionLocation = gl.getAttribLocation(program, "a_position");
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        const timeLoc = gl.getUniformLocation(program, "u_time");
        const resLoc = gl.getUniformLocation(program, "u_resolution");
        const startLoc = gl.getUniformLocation(program, "u_start");
        const targetLoc = gl.getUniformLocation(program, "u_target");

        gl.uniform1f(timeLoc, time * 0.002); // mírně pomalejší puls pro klidný UI běh
        gl.uniform2f(resLoc, canvas.width, canvas.height);

        // Predáme relatvně - UV je odhora dolů z pohledu WebG (0,0..1,1) invertnuto.
        gl.uniform2f(
            startLoc,
            scenarioAgents[0].start.x / MAP_SIZE,
            scenarioAgents[0].start.y / MAP_SIZE,
        );
        gl.uniform2f(
            targetLoc,
            targetPoint.x / MAP_SIZE,
            targetPoint.y / MAP_SIZE,
        );

        const tex0Loc = gl.getUniformLocation(program, "u_kappaMap");
        const tex1Loc = gl.getUniformLocation(program, "u_dynMap");

        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, kappaTexture);
        gl.uniform1i(tex0Loc, 0);

        gl.activeTexture(gl.TEXTURE1);
        gl.bindTexture(gl.TEXTURE_2D, dynTexture);
        gl.uniform1i(tex1Loc, 1);

        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

        animationFrameId = requestAnimationFrame(renderFrame);
    }

    // Rasterizuje čáru definovanou body do naší Texture datové vrstvy
    function buildPathTextureBuffer(pathsDict: Record<string, any>) {
        pathMap.fill(0); // Clear starou cestu

        for (const [agentId, pd] of Object.entries(pathsDict)) {
            const px = pd.x;
            const py = pd.y;
            if (!px || px.length < 2) continue;

            // Jednoduše projedeme celou trasu (Matplotlib / Bresenham algoritmus interpolace pixelů)
            for (let i = 0; i < px.length - 1; i++) {
                const x0 = Math.floor(px[i]);
                const y0 = Math.floor(py[i]);
                const x1 = Math.floor(px[i + 1]);
                const y1 = Math.floor(py[i + 1]);

                // Super zjednodušený Bresenham pro vyplnění tlustší čáry do Uint8 Bufferu
                const dx = Math.abs(x1 - x0);
                const dy = Math.abs(y1 - y0);
                const sx = x0 < x1 ? 1 : -1;
                const sy = y0 < y1 ? 1 : -1;
                let err = dx - dy;

                let cx = x0;
                let cy = y0;

                while (true) {
                    // Děláme tlustší brush (3x3 grid) - To pak WebGL bilineárně neskutečně rozblurroije neonově na celý displej
                    for (let oy = -1; oy <= 1; oy++) {
                        for (let ox = -1; ox <= 1; ox++) {
                            const wx = cx + ox;
                            const wy = cy + oy;
                            if (
                                wx >= 0 &&
                                wx < MAP_SIZE &&
                                wy >= 0 &&
                                wy < MAP_SIZE
                            ) {
                                // Fade brush ze středu
                                const brushStr = ox == 0 && oy == 0 ? 1.0 : 0.4;
                                pathMap[wy * MAP_SIZE + wx] = Math.max(
                                    pathMap[wy * MAP_SIZE + wx],
                                    brushStr,
                                );
                            }
                        }
                    }

                    if (cx === x1 && cy === y1) break;
                    let e2 = 2 * err;
                    if (e2 > -dy) {
                        err -= dy;
                        cx += sx;
                    }
                    if (e2 < dx) {
                        err += dx;
                        cy += sy;
                    }
                }
            }
        }
    }

    async function startSimulation() {
        if (isSimulating) return;

        const payload = {
            size: MAP_SIZE,
            agents: scenarioAgents,
            target: targetPoint,
            kappa_flat: Array.from(kappaFlat),
            max_steps: 1000,
            preset: activePreset,
        };

        try {
            const backendUrl = "http://127.0.0.1:8000";
            const wsUrl = "ws://127.0.0.1:8000";

            const res = await fetch(`${backendUrl}/api/route/task`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            const taskId = data.task_id;

            isSimulating = true;
            phiFlat.fill(0);
            pathMap.fill(0);
            currentStep = 0;

            socket = new WebSocket(`${wsUrl}/api/route/stream/${taskId}`);

            socket.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                if (msg.error) {
                    console.error("Simulation anomaly:", msg.error);
                    stopSimulation();
                    return;
                }
                currentStep = msg.step;

                if (msg.phi_flat) {
                    phiFlat.set(msg.phi_flat);
                }
                if (msg.paths) {
                    buildPathTextureBuffer(msg.paths);
                }
            };

            socket.onclose = () => {
                isSimulating = false;
                socket = null;
            };
        } catch (error) {
            console.error(error);
            alert("Connection to Python Backend failed.");
        }
    }

    function stopSimulation() {
        if (socket) {
            socket.close();
        }
        isSimulating = false;
    }

    onMount(() => {
        initWebGL();
        generateMapForPreset();
        uploadKappa();
        animationFrameId = requestAnimationFrame(renderFrame);

        return () => {
            cancelAnimationFrame(animationFrameId);
            if (gl) {
                if (program) gl.deleteProgram(program);
                if (kappaTexture) gl.deleteTexture(kappaTexture);
                if (dynTexture) gl.deleteTexture(dynTexture);
                if (positionBuffer) gl.deleteBuffer(positionBuffer);

                // Explicite WebGL Extension cleanup
                const ext = gl.getExtension("WEBGL_lose_context");
                if (ext) ext.loseContext();
            }
        };
    });
</script>

<svelte:head>
    <title>Lineum Physical Swarm Routing | Urban Traffic</title>
</svelte:head>

<div class="holo-deck">
    <!-- 1. ABSOLUTÍ POZADÍ: WebGL Canvas Simulation -->
    <div class="canvas-container">
        <canvas bind:this={canvas} class="webgl-canvas"></canvas>
        <div class="vignette"></div>
    </div>

    <!-- 2. UI VRSTVA: Top NavBar "Holo-HUD" -->
    <header class="hud-header">
        <!-- Levý Blok: Titulek a Status -->
        <div class="hud-left">
            <a href="/" class="nav-back"><span>←</span> Back to Dashboard</a>
            <h1 class="hud-title">
                Lineum <span class="text-gradient">Swarm</span> Routing
            </h1>

            <div class="status-bars">
                {#if isSimulating}
                    <div class="status-badge active-badge">
                        <span class="pulse-dot"></span>
                        TENSOR CORE:
                        <span class="hz-text">{currentStep} / 1000 hz</span>
                    </div>
                {:else}
                    <div class="status-badge idle-badge">
                        <span class="idle-dot"></span>
                        SYSTEM: IDLE
                    </div>
                {/if}

                <div class="status-badge hw-badge">GLSL HARDWARE ACCEL</div>
            </div>
        </div>

        <!-- Pravý Blok: Hlavní Akce -->
        <div class="hud-right">
            {#if isSimulating}
                <button class="btn-abort" on:click={stopSimulation}>
                    ABORT SIMULATION
                </button>
            {:else}
                <button class="btn-initiate" on:click={startSimulation}>
                    <div class="btn-glow"></div>
                    <span>▲ INITIATE SHOWCASE</span>
                </button>
            {/if}
        </div>
    </header>

    <!-- 3. UI VRSTVA: Spodní a Boční Ovládací Panely (Holo-Deck) -->
    <div class="hud-panels">
        <!-- Levý Panel: Parametry Prostředí -->
        <div class="panel-left">
            <div class="glass-panel">
                <div class="panel-glow-top"></div>

                <h3 class="panel-title">
                    Business Use-Cases
                    <span class="badge-locked">Active</span>
                </h3>

                <div class="slider-group">
                    <div class="slider-info">
                        <span>Application Domain</span>
                        <span class="cyan-mono">SYS-MODE</span>
                    </div>
                    <select
                        class="holo-select"
                        on:change={handlePresetChange}
                        value={activePreset}
                    >
                        {#each Object.entries(PRESETS) as [key, pData]}
                            <option value={key}>{pData.name}</option>
                        {/each}
                    </select>
                </div>

                <div class="slider-group" style="margin-top: 2rem;">
                    <div class="slider-info">
                        <span>Algorithm Description</span>
                    </div>
                    <div
                        style="font-size: 0.65rem; color: #94a3b8; font-family: monospace; line-height: 1.4;"
                    >
                        {PRESETS[activePreset].desc}
                    </div>
                </div>
            </div>

            <!-- Vysvětlující panel technologie -->
            <div class="glass-panel-sub">
                <p>
                    Lineum's emergent solver eliminates the need for complex
                    deep-learning layers. By computing localized continuum field
                    propagation via <strong class="text-white"
                        >native PyTorch tensor operations</strong
                    >, it achieves real-time path discovery in impossibly dense
                    NP-hard datasets.
                    <strong class="magenta-text"
                        >Experience physical AI in action.</strong
                    >
                </p>
            </div>
        </div>

        <!-- Pravý Panel: Agenti a Trasy -->
        <div class="panel-right">
            <div class="glass-panel stretch-panel">
                <h3 class="panel-title">
                    Active Fleets
                    <span class="badge-active"
                        >{scenarioAgents.length} Active</span
                    >
                </h3>

                <div class="agent-list">
                    {#each scenarioAgents as agent}
                        <!-- Karta Agenta -->
                        <div class="agent-card">
                            <!-- Avatar/Barva -->
                            <div
                                class="agent-avatar"
                                style="border-color: {agent.color}; box-shadow: 0 0 10px {agent.color};"
                            >
                                <div
                                    class="avatar-dot"
                                    style="background: {agent.color};"
                                ></div>
                            </div>
                            <!-- Info -->
                            <div class="agent-info">
                                <div
                                    class="agent-name"
                                    style="color: {agent.color};"
                                >
                                    {agent.name}
                                </div>
                                <div class="agent-dist">
                                    Metrics: {agent.eta}
                                </div>
                            </div>
                        </div>
                    {/each}

                    <!-- Plus Button -->
                    <button class="btn-add-unit">+ ADD FLEET</button>
                </div>
            </div>

            <!-- Data Flow Log -->
            {#if isSimulating}
                <div class="log-panel">
                    <div class="log-line cyan-dim">> Buffer sync completed</div>
                    <div class="log-line magenta-dim">
                        > Calculating dynamic bottlenecks...
                    </div>
                    <div class="log-line green-bright">
                        > Packet {currentStep} received [OK]
                    </div>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    /* Absolute reset for the Holo-Deck */
    .holo-deck {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100vw;
        height: 100vh;
        background-color: #020205;
        color: #f1f5f9;
        font-family: var(--font-sans, system-ui, sans-serif);
        overflow: hidden;
        z-index: 9999; /* Overlay over standard portal layout */
    }

    /* WebGL Background */
    .canvas-container {
        position: absolute;
        inset: 0;
        z-index: 0;
    }
    .webgl-canvas {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .vignette {
        position: absolute;
        inset: 0;
        pointer-events: none;
        background: radial-gradient(
            circle at center,
            transparent 20%,
            #000 120%
        );
        opacity: 0.8;
    }

    /* HUD Header */
    .hud-header {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        z-index: 20;
        padding: 5rem 2.5rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        pointer-events: none;
    }

    .hud-left {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        pointer-events: auto;
    }

    .nav-back {
        font-size: 0.65rem;
        font-family: var(--font-mono, monospace);
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        transition: color 0.2s;
        text-decoration: none;
        width: max-content;
    }
    .nav-back span {
        color: #38bdf8;
    }
    .nav-back:hover {
        color: #38bdf8;
    }

    .hud-title {
        font-size: 2.25rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        margin: 0;
        line-height: 1;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
    }
    .text-gradient {
        background: linear-gradient(to right, #e879f9, #38bdf8);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Status Badges */
    .status-bars {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-top: 0.25rem;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.65rem;
        font-family: var(--font-mono, monospace);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
    }
    .active-badge {
        border: 1px solid rgba(232, 121, 249, 0.3);
        color: #e879f9;
        box-shadow: 0 0 10px rgba(232, 121, 249, 0.2);
    }
    .pulse-dot {
        width: 6px;
        height: 6px;
        background: #e879f9;
        border-radius: 50%;
        box-shadow: 0 0 8px #e879f9;
        animation: pulse 2s infinite;
    }
    .hz-text {
        color: white;
        font-weight: bold;
    }
    .idle-badge {
        border: 1px solid rgba(51, 65, 85, 0.5);
        color: #94a3b8;
    }
    .idle-dot {
        width: 6px;
        height: 6px;
        background: #64748b;
        border-radius: 50%;
    }
    .hw-badge {
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
    }

    /* Buttons */
    .hud-right {
        pointer-events: auto;
    }

    .btn-initiate,
    .btn-abort {
        padding: 0.75rem 2rem;
        font-size: 0.875rem;
        font-weight: bold;
        border-radius: 0.75rem;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(16px);
    }

    .btn-initiate {
        background: rgba(4, 4, 10, 0.8);
        color: white;
        border: 1px solid rgba(192, 132, 252, 0.5);
        box-shadow: 0 0 25px rgba(192, 132, 252, 0.3);
    }
    .btn-initiate:hover {
        background: #000;
        border-color: #e879f9;
        box-shadow: 0 0 35px rgba(192, 132, 252, 0.6);
    }
    .btn-initiate:active {
        transform: scale(0.95);
    }

    .btn-glow {
        position: absolute;
        inset: 0;
        background: linear-gradient(
            to right,
            rgba(88, 28, 135, 0.5),
            rgba(2, 132, 199, 0.5),
            rgba(88, 28, 135, 0.5)
        );
        opacity: 0;
        transition: opacity 0.5s;
    }
    .btn-initiate:hover .btn-glow {
        opacity: 1;
    }
    .btn-initiate span {
        position: relative;
        z-index: 1;
        letter-spacing: 0.05em;
    }

    .btn-abort {
        background: rgba(69, 10, 10, 0.6);
        color: #fecaca;
        border: 1px solid rgba(239, 68, 68, 0.5);
        box-shadow: 0 0 20px rgba(153, 27, 27, 0.4);
    }
    .btn-abort:hover {
        background: rgba(127, 29, 29, 0.8);
        color: white;
    }
    .btn-abort:active {
        transform: scale(0.95);
    }

    /* HUD Panels Bottom */
    .hud-panels {
        position: absolute;
        inset: 0;
        z-index: 10;
        pointer-events: none;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding: 2.5rem;
    }

    .panel-left {
        width: 320px;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        pointer-events: auto;
    }
    .panel-right {
        width: 280px;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        pointer-events: auto;
    }

    .glass-panel {
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s;
    }
    .glass-panel:hover {
        border-color: rgba(255, 255, 255, 0.2);
    }

    .stretch-panel {
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .panel-glow-top {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(
            to right,
            transparent,
            rgba(192, 132, 252, 0.5),
            transparent
        );
        opacity: 0;
        transition: opacity 0.3s;
    }
    .glass-panel:hover .panel-glow-top {
        opacity: 1;
    }

    .panel-title {
        font-size: 0.75rem;
        font-family: var(--font-mono, monospace);
        color: #94a3b8;
        margin: 0 0 1.25rem 0;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .badge-locked,
    .badge-active {
        font-size: 0.6rem;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: var(--font-mono, monospace);
    }
    .badge-locked {
        background: rgba(56, 189, 248, 0.1);
        color: #38bdf8;
    }
    .badge-active {
        background: rgba(52, 211, 153, 0.1);
        color: #34d399;
    }

    /* Sliders */
    .slider-group {
        margin-bottom: 1.25rem;
    }
    .slider-group:last-child {
        margin-bottom: 0;
    }
    .slider-info {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #cbd5e1;
        margin-bottom: 0.5rem;
    }
    .cyan-mono {
        font-family: var(--font-mono, monospace);
        color: #38bdf8;
    }

    .holo-select {
        width: 100%;
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #f1f5f9;
        font-family: var(--font-mono, monospace);
        font-size: 0.75rem;
        padding: 0.5rem;
        border-radius: 6px;
        outline: none;
        cursor: pointer;
        transition: border-color 0.2s;
    }
    .holo-select:hover {
        border-color: rgba(56, 189, 248, 0.8);
    }

    .glass-panel-sub {
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .glass-panel-sub p {
        font-size: 0.75rem;
        color: #94a3b8;
        line-height: 1.6;
        font-weight: 300;
        margin: 0;
    }
    .text-white {
        color: white;
        font-weight: 600;
    }
    .magenta-text {
        color: #c084fc !important;
    }

    /* Agents */
    .agent-list {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .agent-card {
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0.75rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        cursor: pointer;
        transition: background 0.2s;
    }
    .agent-card:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    .agent-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #04040a;
        border: 1px solid #38bdf8;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 0 10px #38bdf8;
    }
    .avatar-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #38bdf8;
        animation: pulse 2s infinite;
    }
    .agent-info {
        flex: 1;
    }
    .agent-name {
        font-size: 0.75rem;
        font-weight: 700;
        color: white;
        margin-bottom: 2px;
        transition: color 0.2s;
    }
    .agent-card:hover .agent-name {
        color: #38bdf8;
    }
    .agent-dist {
        font-size: 0.65rem;
        color: #94a3b8;
        font-family: var(--font-mono, monospace);
    }

    .btn-add-unit {
        width: 100%;
        padding: 0.6rem;
        border-radius: 0.75rem;
        border: 1px dashed #334155;
        background: transparent;
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-add-unit:hover {
        border-color: #64748b;
        color: #cbd5e1;
    }

    /* Logs */
    .log-panel {
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(40px);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 0.75rem;
        padding: 1rem;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.1);
        height: 128px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }
    .log-line {
        font-size: 0.65rem;
        font-family: var(--font-mono, monospace);
        margin-bottom: 4px;
    }
    .cyan-dim {
        color: #38bdf8;
        opacity: 0.7;
    }
    .magenta-dim {
        color: #e879f9;
        opacity: 0.8;
    }
    .green-bright {
        color: #34d399;
        font-weight: bold;
    }

    @keyframes pulse {
        0% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.5;
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
</style>
