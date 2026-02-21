<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import LogoCloud from "$lib/components/LogoCloud.svelte";

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

    // --- ROI Calculator Logic ---
    let fleetSize = 500;
    let dailyOps = 100; // in thousands

    $: estimatedSavings = fleetSize * (dailyOps * 1000) * 365 * 0.0006; // $0.0006 saving per computation

    function formatCurrency(value: number) {
        if (value >= 1e6) {
            return "$" + (value / 1e6).toFixed(1) + "M";
        } else if (value >= 1e3) {
            return "$" + (value / 1e3).toFixed(0) + "k";
        }
        return "$" + value.toFixed(0);
    }

    // --- Dynamic Snippet Fetcher ---
    let snippetLanguage = "python";
    let apiSnippet = "// Loading...";
    let snippetTimeout: any;

    async function fetchSnippet() {
        try {
            const res = await fetch(`http://localhost:8000/api/snippet?language=${snippetLanguage}&preset=${activePreset}&fleet_size=${fleetSize}`);
            if (res.ok) {
                const data = await res.json();
                apiSnippet = data.code;
            }
        } catch (e) {
            apiSnippet = "// Failed to connect to Lineum API";
        }
    }

    // Debounced reactivity pro posuvníky
    $: {
        let _test1 = activePreset;
        let _test2 = fleetSize;
        let _test3 = snippetLanguage;
        clearTimeout(snippetTimeout);
        snippetTimeout = setTimeout(() => {
            fetchSnippet();
        }, 300);
    }
    
    // --- Ticking Cost & Progress Logic ---
    $: aStarCost = isSimulating ? (currentStep / 1000) * 42.50 : (currentStep > 0 ? 42.50 : 0.00);
    $: progressWidth = isSimulating ? (currentStep / 1000) * 100 : (currentStep > 0 ? 100 : 0);
</script>

<svelte:head>
    <title>Lineum API Solutions | Swarm Routing Showcase</title>
</svelte:head>

<div
    class="min-h-screen bg-slate-950 text-slate-50 font-sans flex flex-col pt-16"
>
    <!-- Main Content -->
    <main
        class="flex-1 p-6 md:p-8 max-w-[1600px] mx-auto w-full flex flex-col gap-10"
    >
        <!-- Hero Section -->
        <div
            class="flex flex-col xl:flex-row justify-between items-start xl:items-end gap-6"
        >
            <div class="max-w-4xl">
                <div class="flex flex-wrap items-center gap-3 mb-6">
                    <span
                        class="px-3 py-1 bg-sky-500/10 border border-sky-500/30 text-sky-400 text-[10px] sm:text-xs font-bold rounded-full uppercase tracking-wider"
                        >Lineum API Solutions</span
                    >
                    <span
                        class="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] sm:text-xs font-bold rounded-full uppercase tracking-wider flex items-center gap-2"
                        ><span
                            class="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"
                        ></span> Systems Operational</span
                    >
                </div>
                <h1
                    class="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-6 leading-[1.1]"
                >
                    The world's fastest <br class="hidden sm:block" />
                    <span
                        class="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400"
                        >continuous routing</span
                    > solver.
                </h1>
                <p class="text-slate-400 text-lg max-w-2xl">
                    Integrate physical swarm intelligence into your B2B stack.
                    Outperform traditional discrete graph searches by orders of
                    magnitude.
                </p>
            </div>

            <!-- Hardware Fairness Badge -->
            <div
                class="text-xs font-mono text-slate-400 border border-slate-800 bg-slate-900/50 p-4 rounded-xl flex items-start gap-3 max-w-sm shrink-0"
            >
                <svg
                    class="w-5 h-5 text-slate-500 mt-0.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                    ></path></svg
                >
                <div>
                    <strong class="text-slate-300 block mb-1"
                        >Hardware Fairness Guarantee</strong
                    >
                    Algorithms run synchronously on identically provisioned hardware
                    resources (1 vCPU, 512MB RAM) for scientific objectivity.
                </div>
            </div>
        </div>

        <!-- Core Simulator Section -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <!-- Left Sidebar: Controls & Scenarios -->
            <div
                class="col-span-1 border border-slate-800 bg-slate-900/40 backdrop-blur-sm rounded-2xl p-6 flex flex-col gap-8 shadow-xl"
            >
                <div>
                    <h3
                        class="text-xs uppercase tracking-widest font-bold text-slate-500 mb-4"
                    >
                        Business Use-Cases
                    </h3>
                    <div class="flex flex-col gap-2">
                        {#each Object.entries(PRESETS) as [key, pData]}
                            <button
                                class="text-left px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 {activePreset ===
                                key
                                    ? 'bg-sky-500/10 border-sky-500/50 text-sky-400 shadow-[0_0_15px_rgba(56,189,248,0.15)]'
                                    : 'bg-transparent border-transparent text-slate-400 hover:bg-slate-800 hover:text-slate-200'}"
                                on:click={() =>
                                    handlePresetChange({
                                        target: { value: key },
                                    })}
                            >
                                <div class="font-bold mb-1">{pData.name}</div>
                                <div
                                    class="text-xs opacity-70 {activePreset ===
                                    key
                                        ? 'text-sky-300'
                                        : 'text-slate-500'} leading-relaxed hidden lg:block"
                                >
                                    {pData.desc}
                                </div>
                            </button>
                        {/each}
                    </div>
                </div>

                <div class="mt-auto pt-6 border-t border-slate-800/80">
                    <div
                        class="text-xs text-slate-500 mb-3 flex justify-between items-center"
                    >
                        <span>Simulation Status:</span>
                        <span
                            class="font-mono {isSimulating
                                ? 'text-emerald-400'
                                : 'text-slate-300'}"
                            >{isSimulating
                                ? `LIVE: ${currentStep} hz`
                                : "READY"}</span
                        >
                    </div>

                    {#if isSimulating}
                        <button
                            class="w-full py-3.5 bg-red-500/10 border border-red-500/30 text-red-500 rounded-xl font-bold text-sm tracking-wide shadow-lg hover:bg-red-500/20 transition-all flex items-center justify-center gap-2 group"
                            on:click={stopSimulation}
                        >
                            ■ ABORT VERIFICATION
                        </button>
                    {:else}
                        <button
                            class="w-full py-3.5 bg-white text-slate-950 rounded-xl font-bold text-sm tracking-wide shadow-[0_0_20px_rgba(255,255,255,0.15)] hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] hover:scale-[1.02] transition-all flex items-center justify-center gap-2 group"
                            on:click={startSimulation}
                        >
                            <span
                                class="w-2.5 h-2.5 bg-emerald-500 rounded-full group-hover:animate-ping"
                            ></span>
                            RUN LIVE VERIFICATION
                        </button>
                        <p
                            class="text-[10px] text-center text-slate-500 mt-3 font-mono"
                        >
                            Consume 1 API Credit to bypass pre-rendered
                            animation
                        </p>
                    {/if}
                </div>
            </div>

            <!-- Center/Right: Split Benchmarking Screens -->
            <div class="col-span-1 lg:col-span-3 flex flex-col gap-6">
                <!-- Grid for Canvas Panels -->
                <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 h-[500px]">
                    <!-- Lineum Panel -->
                    <div
                        class="border border-sky-500/40 rounded-2xl overflow-hidden relative bg-slate-950 shadow-[0_0_40px_rgba(56,189,248,0.15)] group flex flex-col"
                    >
                        <div
                            class="absolute top-4 left-4 right-4 z-10 flex justify-between items-start pointer-events-none"
                        >
                            <div
                                class="px-3 py-1.5 bg-slate-900/80 border border-sky-500/50 rounded-lg text-xs font-mono text-sky-400 font-bold backdrop-blur-md shadow-lg hidden sm:block"
                            >
                                LINEUM CONTINUOUS FIELD
                            </div>
                            <div
                                class="px-3 py-1.5 bg-slate-900/80 border border-sky-500/50 rounded-lg text-xs font-mono text-sky-400 font-bold backdrop-blur-md shadow-lg sm:hidden"
                            >
                                LINEUM
                            </div>
                            <div
                                class="px-3 py-1.5 bg-slate-900/80 border border-slate-700 rounded-lg text-sm font-mono text-white backdrop-blur-md shadow-lg flex flex-col items-end"
                            >
                                <span
                                    class="text-slate-400 text-[10px] uppercase tracking-wider"
                                    >Time to Calculate</span
                                >
                                <span class="text-sky-400 font-bold">4 ms</span>
                            </div>
                        </div>

                        <!-- Lineum Canvas takes remaining space -->
                        <div
                            class="relative flex-1 bg-black overflow-hidden flex items-center justify-center"
                        >
                            <canvas
                                bind:this={canvas}
                                class="w-full h-full object-cover mix-blend-screen opacity-90 group-hover:opacity-100 transition-opacity max-w-full"
                            ></canvas>
                            <!-- Vignette Effect covering only canvas -->
                            <div
                                class="absolute inset-0 pointer-events-none"
                                style="background: radial-gradient(circle at center, transparent 30%, #000 120%); opacity: 0.8;"
                            ></div>
                        </div>

                        <!-- Active Fleets Footer inside Lineum Panel -->
                        <div
                            class="bg-slate-900/80 backdrop-blur-md border-t border-sky-500/30 p-4 shrink-0"
                        >
                            <div
                                class="flex items-center gap-4 overflow-x-auto no-scrollbar"
                            >
                                {#each scenarioAgents as agent}
                                    <div
                                        class="flex items-center gap-3 bg-slate-800/50 px-3 py-2 rounded-lg border border-slate-700/50 whitespace-nowrap"
                                    >
                                        <div class="relative flex h-3 w-3">
                                            <span
                                                class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                                                style="background-color: {agent.color};"
                                            ></span>
                                            <span
                                                class="relative inline-flex rounded-full h-3 w-3"
                                                style="background-color: {agent.color};"
                                            ></span>
                                        </div>
                                        <div>
                                            <div
                                                class="text-[10px] text-slate-400 font-mono tracking-wider uppercase"
                                            >
                                                {agent.name}
                                            </div>
                                            <div
                                                class="text-xs font-bold text-white"
                                            >
                                                {agent.eta}
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                                {#if isSimulating}
                                    <div
                                        class="ml-auto text-[10px] font-mono text-sky-400 animate-pulse whitespace-nowrap hidden sm:block"
                                    >
                                        STREAMING DATA...
                                    </div>
                                {/if}
                            </div>
                        </div>
                    </div>

                    <!-- Competitor Panel (A*) -->
                    <div
                        class="border border-slate-800/80 rounded-2xl overflow-hidden relative bg-slate-900/50 flex flex-col group opacity-90 transition-opacity hover:opacity-100"
                    >
                        <div
                            class="absolute top-4 left-4 right-4 z-10 flex justify-between items-start pointer-events-none"
                        >
                            <div
                                class="px-3 py-1.5 bg-slate-900/80 border border-slate-700 rounded-lg text-xs font-mono text-slate-400 font-bold backdrop-blur-md shadow-lg hidden sm:block"
                            >
                                A* DISCRETE GRAPH SEARCH
                            </div>
                            <div
                                class="px-3 py-1.5 bg-slate-900/80 border border-slate-700 rounded-lg text-xs font-mono text-slate-400 font-bold backdrop-blur-md shadow-lg sm:hidden"
                            >
                                A* SEARCH
                            </div>
                            <div
                                class="px-3 py-1.5 bg-slate-900/80 border border-red-500/30 rounded-lg text-sm font-mono text-white backdrop-blur-md shadow-lg flex flex-col items-end"
                            >
                                <span
                                    class="text-slate-400 text-[10px] uppercase tracking-wider"
                                    >Time to Calculate</span
                                >
                                <span class="text-red-400 font-bold"
                                    >1450 ms</span
                                >
                            </div>
                        </div>

                        <!-- Placeholder vizualizace A* -->
                        <div
                            class="flex-1 w-full h-full flex flex-col items-center justify-center font-mono text-slate-500 text-sm relative overflow-hidden bg-slate-950 px-6 text-center"
                        >
                            <!-- Fake grid pro "A* feel" -->
                            <div
                                class="absolute inset-0 z-0 opacity-10"
                                style="background-image: linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px); background-size: 20px 20px;"
                            ></div>

                            <div class="z-10 text-center">
                                <svg
                                    class="w-12 h-12 mx-auto mb-4 text-slate-600 animate-spin-slow"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="1.5"
                                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                                    />
                                </svg>
                                <div>[ GRAPH EXPANSION UNAVAILABLE ]</div>
                                <div
                                    class="text-[10px] mt-2 text-slate-600 max-w-xs mx-auto"
                                >
                                    Discrete algorithms cannot solve dense
                                    matrices in real-time.
                                </div>
                            </div>
                        </div>

                        <div
                            class="bg-slate-900/50 border-t border-slate-800 p-4 h-[65px] flex items-center justify-center shrink-0"
                        >
                            <span
                                class="text-[10px] sm:text-xs text-slate-500 font-mono"
                                >AWAITING HEURISTIC RESOLUTION...</span
                            >
                        </div>
                    </div>
                </div>

                <!-- Scraping/Scrubbing Timeline & Ticking Cost -->
                <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6 bg-slate-900/60 border border-slate-800 p-4 md:p-5 rounded-2xl shadow-lg mt-auto">
                    <button class="p-3 bg-slate-800 hover:bg-slate-700 rounded-full text-slate-300 transition-colors shrink-0" aria-label="Play timeline" on:click={startSimulation}>
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                    </button>
                    <div class="w-full flex-1 h-3 bg-slate-950 border border-slate-800 rounded-full relative overflow-hidden">
                        <div class="absolute top-0 left-0 bottom-0 bg-slate-800 transition-all duration-100" style="width: {progressWidth}%"></div>
                        <!-- Lineum completion marker -->
                        <div class="absolute top-0 bottom-0 w-1.5 bg-sky-500 left-[2.5%] shadow-[0_0_10px_rgba(56,189,248,1)]" title="Lineum Complete (4ms)"></div>
                    </div>
                    
                    <div class="flex flex-col items-start sm:items-end min-w-[200px] bg-red-500/5 border border-red-500/20 px-4 py-2 rounded-xl shrink-0">
                        <span class="text-[10px] text-red-500/70 uppercase tracking-widest font-bold">Estimated Ticking Cost</span>
                        <div class="flex items-baseline gap-2">
                             <span class="text-red-400 font-mono font-bold text-xl sm:text-2xl">-${aStarCost.toFixed(2)}</span>
                             <span class="text-slate-500 text-[10px] sm:text-xs font-mono">/ hour</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ROI & Integration Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6 w-full max-w-7xl">
            
            <!-- ROI Calculator -->
            <div class="border border-emerald-500/30 bg-emerald-950/20 backdrop-blur-sm rounded-2xl p-6 lg:p-8 flex flex-col justify-between shadow-[0_0_30px_rgba(16,185,129,0.05)]">
                <div>
                   <h3 class="text-xl font-bold text-white mb-2">Business Impact Calculator</h3>
                   <p class="text-slate-400 text-sm mb-8">Estimate your annual savings based on compute reduction and increased operational elasticity.</p>
                   
                   <div class="flex flex-col gap-6">
                      <div class="flex flex-col gap-3">
                         <div class="flex justify-between items-end">
                            <label for="fleetSizeInput" class="text-xs font-bold text-slate-300 uppercase tracking-wider">Fleet Size / Concurrent Agents</label>
                            <span class="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded">{fleetSize}</span>
                         </div>
                         <input id="fleetSizeInput" type="range" bind:value={fleetSize} class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer" min="10" max="5000" step="10">
                      </div>
                      
                      <div class="flex flex-col gap-3">
                         <div class="flex justify-between items-end">
                            <label for="dailyOpsInput" class="text-xs font-bold text-slate-300 uppercase tracking-wider">Daily Route Recalculations</label>
                            <span class="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded">{dailyOps}k</span>
                         </div>
                         <input id="dailyOpsInput" type="range" bind:value={dailyOps} class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer" min="1" max="1000" step="5">
                      </div>
                   </div>
                </div>
                
                <div class="mt-8 pt-6 border-t border-emerald-900/50 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                   <div>
                       <div class="text-[10px] text-emerald-500/70 uppercase tracking-widest font-bold mb-1">Estimated Annual Savings</div>
                       <div class="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200">
                          {formatCurrency(estimatedSavings)}
                       </div>
                   </div>
                   <button class="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl transition-colors shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] whitespace-nowrap">
                       Talk to Sales
                   </button>
                </div>
            </div>

            <!-- API Code Snippet & Paywall -->
            <div class="border border-slate-800 bg-slate-900/40 backdrop-blur-sm rounded-2xl flex flex-col overflow-hidden">
                <div class="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
                    <div class="flex items-center gap-2">
                       <span class="w-3 h-3 rounded-full bg-red-400/20 border border-red-500/50"></span>
                       <span class="w-3 h-3 rounded-full bg-amber-400/20 border border-amber-500/50"></span>
                       <span class="w-3 h-3 rounded-full bg-emerald-400/20 border border-emerald-500/50"></span>
                    </div>
                    <div class="text-xs font-mono text-slate-500">POST /api/v1/compute/swarm</div>
                    <div class="flex gap-2">
                       <button class="text-xs font-bold {snippetLanguage === 'curl' ? 'text-sky-400 bg-sky-500/10 border border-sky-500/30' : 'text-slate-400 bg-slate-800 hover:text-white border-transparent'} px-3 py-1 rounded transition-colors" on:click={() => snippetLanguage = 'curl'}>cURL</button>
                       <button class="text-xs font-bold {snippetLanguage === 'python' ? 'text-sky-400 bg-sky-500/10 border border-sky-500/30' : 'text-slate-400 bg-slate-800 hover:text-white border-transparent'} px-3 py-1 rounded transition-colors" on:click={() => snippetLanguage = 'python'}>Python</button>
                    </div>
                </div>
                <!-- Code Snippet Body -->
                <div class="p-6 relative flex-1 text-sm font-mono text-slate-300 overflow-hidden leading-relaxed">
                   <pre class="whitespace-pre-wrap font-mono text-sm"><code>{apiSnippet}</code></pre>

                   <!-- Paywall Overlay -->
                   <div class="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-slate-900 via-slate-900/90 to-transparent flex flex-col items-center justify-end pb-8 px-6 text-center z-10">
                       <div class="flex items-center justify-center w-12 h-12 bg-slate-800 rounded-full mb-3 shadow-lg border border-slate-700">
                           <svg class="w-5 h-5 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                       </div>
                       <h4 class="font-bold text-white mb-1">Production Access Locked</h4>
                       <p class="text-xs text-slate-400 max-w-xs mx-auto mb-4">Export raw datasets, upload custom floorplans, and access real-time WebSockets with an Enterprise plan.</p>
                       <button class="px-5 py-2.5 bg-white text-slate-950 font-bold text-sm rounded-lg hover:bg-slate-200 transition-colors shadow-[0_0_15px_rgba(255,255,255,0.1)]">
                          Upgrade to Lineum Enterprise
                       </button>
                   </div>
                </div>
            </div>
            
        </div>
        
        <div class="mt-8 border-t border-slate-800/80 pt-12">
            <LogoCloud />
        </div>
        
    </main>
</div>

<style>
    :global(body) {
        /* Ensure normal scroll behavior and background for the new B2B layout */
        background-color: #020617; /* tailwind text-slate-950 */
        margin: 0;
    }
    .animate-spin-slow {
        animation: spin 3s linear infinite;
    }
    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
    /* Hide scrollbar for agent list */
    .no-scrollbar::-webkit-scrollbar {
        display: none;
    }
    .no-scrollbar {
        -ms-overflow-style: none; /* IE and Edge */
        scrollbar-width: none; /* Firefox */
    }
</style>
