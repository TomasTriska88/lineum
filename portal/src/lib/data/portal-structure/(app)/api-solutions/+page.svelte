<script lang="ts">
    import * as m from "$lib/paraglide/messages.js";
    import { onMount, onDestroy } from "svelte";
    import LogoCloud from "$lib/components/LogoCloud.svelte";
    import ApiSnippet from "$lib/components/ApiSnippet.svelte";
    import { intersect } from "$lib/actions/intersect";
    import { portal } from "$lib/actions/portal";
    import CompressionDemo from "$lib/components/CompressionDemo.svelte";
    import FastTrngApp from "$lib/components/api-showcase/FastTrngApp.svelte";
    import ZetaEntropyApp from "$lib/components/api-showcase/ZetaEntropyApp.svelte";
    import Web3VrfApp from "$lib/components/api-showcase/Web3VrfApp.svelte";
    import LineumHashApp from "$lib/components/api-showcase/LineumHashApp.svelte";
    import GamingRngApp from "$lib/components/api-showcase/GamingRngApp.svelte";

    // Instead of Concurrency we launch one by one again (cleaner dev experience)
    let canvas: HTMLCanvasElement = null as any;
    let gl: WebGLRenderingContext | null;
    let program: WebGLProgram | null;
    let animationFrameId: number;
    let positionBuffer: WebGLBuffer | null = null;

    const MAP_SIZE = 128;

    // Simulation state
    let kappaFlat = new Float32Array(MAP_SIZE * MAP_SIZE).fill(1);
    let phiFlat = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);
    // Green channel for rendering all agent start dots
    let startMap = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);
    // We'll use the Blue channel of the second texture for the route
    let pathMap = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);

    // Points of interest (now re-assigned based on preset)
    let startPoint = { x: 10, y: 10 };
    let targetPoint = { x: 110, y: 110 };

    // Net State
    let isSimulating = false;
    let isScrubbing = false;
    let isCompilingAPI = false;
    let apiProgress = 0;
    let progressInterval: any;
    let socket: WebSocket | null = null;
    let currentStep = 0;

    // Scale Demo State
    let agentScale = 1; // 1 to 100,000 array scaling factor
    let returnPaths = true; // B2B Scalability bypass

    let isVisible = false;
    function handleIntersect(inView: boolean) {
        isVisible = inView;
        if (isVisible && gl) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = requestAnimationFrame(renderFrame);
        } else {
            cancelAnimationFrame(animationFrameId);
        }
    }

    // === APP STATE & PRESETS ===
    type PresetId =
        | "urban_design"
        | "evacuation"
        | "vascular"
        | "dielectric"
        | "city_connections";
    let activePreset: PresetId = "urban_design";

    // Dynamic Agent Definitions for given preset
    let scenarioAgents: any[] = [];

    const PRESETS = {
        urban_design: {
            name: "URBAN_LOGISTICS",
            desc: "Heavy momentum memory. Merges small paths into efficient wide highways.",
            target: { x: 60, y: 110 },
        },
        evacuation: {
            name: "CROWD_EVACUATION",
            desc: "Short memory, high pressure. Crowds scatter around bottlenecks chaotically.",
            target: { x: 60, y: 120 },
        },
        vascular: {
            name: "IRRIGATION_NETWORK",
            desc: "High noise divergence. Fluid covers maximum tissue area forming fractals.",
            target: { x: 60, y: 100 },
        },
        dielectric: {
            name: "DIELECTRIC_BREAKDOWN",
            desc: "Brutal gradient pressure. Burns straight through micro-pores in insulators.",
            target: { x: 60, y: 120 },
        },
        city_connections: {
            name: "TOPOGRAPHIC_CITIES",
            desc: "Connecting neighboring cities with minimal infrastructure, avoiding geographic obstacles.",
            target: { x: 64, y: 64 },
        },
    };

    // GPU Textures
    let kappaTexture: WebGLTexture | null = null;
    let dynTexture: WebGLTexture | null = null;

    // --- Shader sources ---
    const vs = `
        attribute vec2 a_position;
        varying vec2 v_uv;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
            // Recalculate -1..1 to 0..1 (UV)
            v_uv = a_position * 0.5 + 0.5; 
            // WebGL has flipped Y
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

            // 4. Start (Tepající Modré Diódy přes Raster Texture)
            float starts_vis = dynTex.g;
            if (starts_vis > 0.01) {
                color += neon_path * starts_vis * (1.2 + 0.3 * sin(u_time * 5.0));
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
            // City blocks
            addWall(20, 30, 80, 10);
            addWall(40, 60, 80, 10);
            addWall(10, 90, 80, 10);
            addWall(30, 40, 10, 20);
            addWall(90, 70, 10, 20);
            let swarmCount = Math.floor(agentScale);
            scenarioAgents = [];
            for (let i = 0; i < swarmCount; i++) {
                scenarioAgents.push({
                    id: `A_${i}`,
                    start: { x: 50 + (i % 5), y: 15 + (Math.floor(i / 5) % 5) },
                    color: "#38bdf8",
                    name: `Swarm Unit ${i}`,
                    eta: "4.2 mins",
                });
            }
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
            // Tissue organ, irregular blockages, pathfinding through cells
            for (let k = 0; k < 15; k++) {
                addWall(
                    Math.random() * 100 + 10,
                    Math.random() * 80 + 20,
                    Math.random() * 15 + 5,
                    Math.random() * 15 + 5,
                );
            }
            addWall(0, 110, 128, 5); // Bottom membrane
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
            // Insulator (thick wall with small pores / material defects)
            addWall(0, 50, 128, 30);
            // Create pores
            const p = 0; // remove wall in pore
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
        } else if (activePreset === "city_connections") {
            // Topographic mountain map (sine combinations for natural terrain)
            for (let j = 0; j < MAP_SIZE; j++) {
                for (let i = 0; i < MAP_SIZE; i++) {
                    let nx = (i / MAP_SIZE) * Math.PI * 4;
                    let ny = (j / MAP_SIZE) * Math.PI * 4;
                    let elevation =
                        Math.sin(nx) * Math.cos(ny) +
                        Math.sin(nx * 2.5 + 1) * 0.5;
                    if (elevation > 0.75) {
                        kappaFlat[j * MAP_SIZE + i] = 0.0; // Absolute rock/mountains
                    } else if (elevation > 0.45) {
                        kappaFlat[j * MAP_SIZE + i] = 0.1; // Heavy hill - high resistance (slow road building)
                    } else if (elevation > 0.2) {
                        kappaFlat[j * MAP_SIZE + i] = 0.5; // Undulating terrain
                    }
                }
            }
            scenarioAgents = [
                {
                    id: "City1",
                    start: { x: 15, y: 15 },
                    color: "#fcd34d",
                    name: "Alpha Hub",
                    eta: "Ready",
                },
                {
                    id: "City2",
                    start: { x: 110, y: 20 },
                    color: "#fcd34d",
                    name: "Beta Hub",
                    eta: "Ready",
                },
                {
                    id: "City3",
                    start: { x: 20, y: 110 },
                    color: "#fcd34d",
                    name: "Gamma Hub",
                    eta: "Ready",
                },
                {
                    id: "City4",
                    start: { x: 105, y: 105 },
                    color: "#fcd34d",
                    name: "Delta Hub",
                    eta: "Ready",
                },
                {
                    id: "City5",
                    start: { x: 110, y: 64 },
                    color: "#fcd34d",
                    name: "Echo Hub",
                    eta: "Ready",
                },
            ];
            targetPoint = { x: 64, y: 64 }; // Capital city in the central valley
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

        // Build startMap raster based on current agents (helps visualize slider scaling instantly)
        startMap.fill(0);
        for (let i = 0; i < scenarioAgents.length; i++) {
            const x = Math.floor(scenarioAgents[i].start.x);
            const y = Math.floor(scenarioAgents[i].start.y);
            if (x >= 0 && x < MAP_SIZE && y >= 0 && y < MAP_SIZE) {
                for (let oy = -1; oy <= 1; oy++) {
                    for (let ox = -1; ox <= 1; ox++) {
                        const wx = x + ox;
                        const wy = y + oy;
                        if (
                            wx >= 0 &&
                            wx < MAP_SIZE &&
                            wy >= 0 &&
                            wy < MAP_SIZE
                        ) {
                            const brush = ox === 0 && oy === 0 ? 1.0 : 0.4;
                            startMap[wy * MAP_SIZE + wx] = Math.max(
                                startMap[wy * MAP_SIZE + wx],
                                brush,
                            );
                        }
                    }
                }
            }
        }

        const data = new Uint8Array(MAP_SIZE * MAP_SIZE * 4);
        for (let i = 0; i < MAP_SIZE * MAP_SIZE; i++) {
            data[i * 4] = Math.min(255, phiFlat[i] * 255); // R = Fyzika tepla
            data[i * 4 + 1] = Math.min(255, startMap[i] * 255); // G = Start pozice z rasteru
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
        if (!isVisible || !gl || !program) return;

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
        const targetLoc = gl.getUniformLocation(program, "u_target");

        gl.uniform1f(timeLoc, time * 0.002); // mírně pomalejší puls pro klidný UI běh
        gl.uniform2f(resLoc, canvas.width, canvas.height);

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
        if (isSimulating || isCompilingAPI) return;
        isCompilingAPI = true;

        apiProgress = 0;
        if (progressInterval) clearInterval(progressInterval);
        progressInterval = setInterval(() => {
            if (apiProgress < 99) {
                // Rychlý fake loader odrážející čas výpočtu
                apiProgress += Math.floor(Math.random() * 12) + 4;
                if (apiProgress > 99) apiProgress = 99;
            }
        }, 30);

        const payload = {
            size: MAP_SIZE,
            agents: scenarioAgents,
            agent_count: exponentialScale,
            target: targetPoint,
            kappa_flat: Array.from(kappaFlat),
            max_steps: 1000,
            preset: activePreset,
            return_paths: returnPaths,
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

            if (!res.ok) {
                isCompilingAPI = false;
                if (progressInterval) clearInterval(progressInterval);
                alert(
                    `API Error (${res.status}): ${data.detail || "Server rejected request."}`,
                );
                return;
            }

            const taskId = data.task_id;

            phiFlat.fill(0);
            pathMap.fill(0);
            currentStep = 0;

            socket = new WebSocket(`${wsUrl}/api/route/stream/${taskId}`);

            socket.onmessage = (event) => {
                isSimulating = true;
                isCompilingAPI = false;
                if (progressInterval) clearInterval(progressInterval);

                const msg = JSON.parse(event.data);
                if (msg.error) {
                    console.error("Simulation anomaly:", msg.error);
                    stopSimulation();
                    alert(`Simulation Error: ${msg.error}`);
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
                isCompilingAPI = false;
                if (progressInterval) clearInterval(progressInterval);
                socket = null;
            };
        } catch (error) {
            console.error(error);
            isCompilingAPI = false;
            if (progressInterval) clearInterval(progressInterval);
            alert(
                "Connection to Python Backend failed. Ensure the server is running on port 8000.",
            );
        }
    }

    function handleScrubberInteraction() {
        if (!isSimulating && currentStep > 0) {
            isScrubbing = true;
            // Optimisticky upravíme vizuální progress scrubberu,
            // v praxi by se tu dál fetchoval stav z backend cache přes /state/:step
            // Pro prezentační účely pouze upravíme ticker.
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
        // handled by intersect: animationFrameId = requestAnimationFrame(renderFrame);

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

    const SNIPPETS = {
        python: `import lineum

# 1. Initialize the AI LTM Field
solver = lineum.Client(api_key="lnm_enterprise_***")

# 2. True RNG: Harvest Edge-of-Chaos float variance
random_entropy = solver.generate_true_rng(
    resolution=64, 
    pump_cycles=1500
)

# 3. Cryptographic Hash: One-way topology fracture
secure_hash = solver.hash(
    payload="LINEUM_ENTERPRISE",
    avalanche_threshold=0.01
)

# 4. LPL Compile: Calculate logic via geometric CAD masks
logic_result = solver.compile_lpl(
    mask="reservoir_cad.png",
    inputs=[1.0, 1.0] # Simulating AND gate
)
`,
        curl: `curl -X POST https://api.lineum.io/v1/ai/hash \\
  -H "Authorization: Bearer lnm_enterprise_***" \\
  -H "Content-Type: application/json" \\
  -d '{
    "payload": "LINEUM_ENTERPRISE",
    "parameters": {
      "grid_size": 64,
      "iterations": 1500
    }
  }'`,
    };

    $: apiSnippet = SNIPPETS[snippetLanguage as keyof typeof SNIPPETS];

    // --- Ticking Cost & Progress Logic ---
    $: exponentialScale = Math.floor(Math.pow(10, agentScale / 20)); // Up to ~100k

    // Pre-generate a stable pool of 500 visual slider agents so their starting positions don't jump around when the user drags the slider.
    const sliderAgentsPool = Array.from({ length: 500 }).map((_, i) => ({
        id: `slider_agent_${i}`,
        start: {
            x: Math.floor(10 + Math.random() * 40),
            y: Math.floor(10 + Math.random() * 108),
        },
        color: "#ef4444",
    }));

    // Reactively update local visual agents without freezing the browser (cap at 500 for visual canvas drawing)
    $: {
        const visualCap = Math.min(exponentialScale, 500);
        if (
            activePreset === "urban_design" &&
            (!scenarioAgents || scenarioAgents.length !== visualCap)
        ) {
            scenarioAgents = sliderAgentsPool.slice(0, visualCap);
        }
    }

    // Lineum is O(1) ~ 4ms. A* is O(N) ~ 1.5ms per agent per step.
    $: aStarCostThisStepMs = exponentialScale * 1.5;

    $: aStarCost =
        isSimulating || isScrubbing
            ? ((currentStep * aStarCostThisStepMs) / (1000 * 60 * 60)) * 42.5 // converting ms to hours of server time cost
            : currentStep > 0
              ? ((1000 * aStarCostThisStepMs) / (1000 * 60 * 60)) * 42.5
              : 0.0;
    $: progressWidth =
        isSimulating || isScrubbing
            ? (currentStep / 1000) * 100
            : currentStep > 0
              ? 100
              : 0;
</script>

<svelte:head>
    <title>{m.common_brand()} API Solutions | Swarm Routing Showcase</title>
</svelte:head>

<div class="min-h-screen text-slate-50 font-sans flex flex-col pt-[104px]">
    <!-- Main Content -->
    <main class="flex-1 w-full flex flex-col items-center">
        <!-- VERCEL-STYLE HERO SECTION (Centered, Clean, Massive) -->
        <div
            class="w-full flex flex-col items-center justify-center text-center px-4 pt-16 pb-16 max-w-5xl mx-auto"
            style="margin-top: 120px;"
        >
            <div class="flex items-center gap-3 mb-8">
                <span
                    class="px-3 py-1 bg-white/5 border border-white/10 text-slate-300 text-xs font-bold rounded-full uppercase tracking-wider backdrop-blur-md"
                >
                    {m.api_solutions_hero_domain()}
                </span>
                <span
                    class="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full uppercase tracking-wider flex items-center gap-2 backdrop-blur-md"
                >
                    <span
                        class="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"
                    ></span>
                    {m.common_beta()}
                </span>
            </div>

            <h1
                class="text-5xl sm:text-7xl font-extrabold tracking-tight mb-8 leading-[1.05]"
                style="font-family: var(--font-sans);"
            >
                {@html m.api_solutions_hero_title_full({
                    highlight_span: "<span class='text-gradient-multi'>",
                    highlight_span_end: "</span>",
                })}
            </h1>

            <p class="text-slate-400 text-xl max-w-2xl font-light mb-12">
                {m.api_solutions_hero_subtitle()}
            </p>

            <div class="cta-group">
                <a
                    href="#roi"
                    class="btn btn-primary"
                    style="background-color: var(--accent-cyan); color: #020617;"
                    >{m.api_solutions_hero_cta_build()}</a
                >
                <a
                    href="/wiki"
                    class="btn btn-outline"
                    style="border-color: rgba(255,255,255,0.2); color: white;"
                    >{m.api_solutions_hero_cta_docs()}</a
                >
            </div>

            <div class="mt-8 md:mt-16 w-full">
                <LogoCloud />
            </div>
        </div>

        <!-- Core Paradigm Shift (B2B Marketing) -->
        <div
            id="roi"
            class="w-full max-w-5xl mx-auto px-4 mb-32 flex flex-col items-center"
        >
            <div class="text-center mb-16">
                <h2 class="text-3xl md:text-5xl font-bold text-white mb-6">
                    {m.api_solutions_roi_title()}
                </h2>
                <p class="text-slate-400 text-xl font-light max-w-3xl mx-auto">
                    {@html m.api_solutions_roi_subtitle()}
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
                <!-- Feature 1: Scaling -->
                <div
                    class="group relative bg-slate-950 border border-slate-800 rounded-2xl p-8 flex flex-col items-center text-center overflow-hidden hover:border-violet-500/50 hover:shadow-[0_0_40px_rgba(139,92,246,0.15)] transition-all"
                >
                    <!-- Background Glow -->
                    <div
                        class="absolute -top-24 -left-24 w-48 h-48 bg-violet-500/20 rounded-full blur-[80px] pointer-events-none group-hover:bg-violet-500/30 transition-all"
                    ></div>

                    <!-- Massive Callout -->
                    <div
                        class="text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-b from-white to-violet-500/50 drop-shadow-[0_0_15px_rgba(139,92,246,0.3)] select-none uppercase"
                    >
                        ENTROPY
                    </div>
                    <h4 class="text-lg font-bold text-white mb-3">
                        {m.api_solutions_features_rng_title()}
                    </h4>
                    <p
                        class="text-slate-400 text-sm leading-relaxed max-w-[200px]"
                    >
                        {m.api_solutions_features_rng_desc()}
                    </p>
                </div>

                <!-- Feature 2: Latency -->
                <div
                    class="group relative bg-slate-950 border border-slate-800 rounded-2xl p-8 flex flex-col items-center text-center overflow-hidden hover:border-emerald-500/50 hover:shadow-[0_0_40px_rgba(16,185,129,0.15)] transition-all"
                >
                    <!-- Background Glow -->
                    <div
                        class="absolute -top-24 -left-24 w-48 h-48 bg-emerald-500/20 rounded-full blur-[80px] pointer-events-none group-hover:bg-emerald-500/30 transition-all"
                    ></div>

                    <!-- Massive Callout -->
                    <div
                        class="text-4xl sm:text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-b from-white to-emerald-500/50 drop-shadow-[0_0_15px_rgba(16,185,129,0.3)] select-none uppercase"
                    >
                        AVALANCHE
                    </div>
                    <h4 class="text-xl font-bold text-white mb-3">
                        {m.api_solutions_features_hash_title()}
                    </h4>
                    <p
                        class="text-slate-400 text-sm leading-relaxed max-w-[200px]"
                    >
                        {m.api_solutions_features_hash_desc()}
                    </p>
                </div>

                <!-- Feature 3: DevOps -->
                <div
                    class="group relative bg-slate-950 border border-slate-800 rounded-2xl p-8 flex flex-col items-center text-center overflow-hidden hover:border-sky-500/50 hover:shadow-[0_0_40px_rgba(56,189,248,0.15)] transition-all"
                >
                    <!-- Background Glow -->
                    <div
                        class="absolute -top-24 -left-24 w-48 h-48 bg-sky-500/20 rounded-full blur-[80px] pointer-events-none group-hover:bg-sky-500/30 transition-all"
                    ></div>

                    <!-- Massive Callout -->
                    <div
                        class="text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-b from-white to-sky-500/50 drop-shadow-[0_0_15px_rgba(56,189,248,0.3)] select-none uppercase"
                    >
                        LOGIC
                    </div>
                    <h4 class="text-xl font-bold text-white mb-3">
                        {m.api_solutions_features_lpl_title()}
                    </h4>
                    <p
                        class="text-slate-400 text-sm leading-relaxed max-w-[200px]"
                    >
                        {m.api_solutions_features_lpl_desc()}
                    </p>
                </div>
            </div>
        </div>

        <!-- Scroll Anchor & Navigation Tabs -->
        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-12 max-w-4xl mx-auto"
        ></div>

        <!-- Floating Side Navigation (Desktop) -->
        <nav
            use:portal
            class="hidden xl:flex fixed left-8 top-1/2 -translate-y-1/2 z-50 flex-col gap-3 bg-slate-900/60 backdrop-blur-xl border border-slate-800 p-4 rounded-3xl shadow-2xl"
        >
            <a
                href="#routing"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-sky-400 group-hover:shadow-[0_0_15px_rgba(56,189,248,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Routing</span
                >
            </a>
            <a
                href="#fast_trng"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-violet-400 group-hover:shadow-[0_0_15px_rgba(139,92,246,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Fast TRNG</span
                >
            </a>
            <a
                href="#zeta"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-rose-400 group-hover:shadow-[0_0_15px_rgba(244,63,94,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Zeta Entropy</span
                >
            </a>
            <a
                href="#web3"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-sky-400 group-hover:shadow-[0_0_15px_rgba(56,189,248,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Web3 Oracle</span
                >
            </a>
            <a
                href="#hash"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-emerald-400 group-hover:shadow-[0_0_15px_rgba(16,185,129,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >LineumHash</span
                >
            </a>
            <a
                href="#gaming"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-emerald-400 group-hover:shadow-[0_0_15px_rgba(16,185,129,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Gaming RNG</span
                >
            </a>
        </nav>

        <!-- Mobile/Tablet Top Navigation (Hidden on Large Screens) -->
        <div
            class="w-full max-w-6xl mx-auto px-4 mb-24 sticky top-[100px] z-[110] xl:hidden"
        >
            <div
                class="flex items-center gap-3 bg-slate-900/90 backdrop-blur-xl border border-slate-700 p-3 rounded-2xl shadow-xl overflow-x-auto overflow-y-hidden snap-x snap-mandatory"
            >
                <a
                    href="#routing"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Routing</a
                >
                <a
                    href="#fast_trng"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Fast TRNG</a
                >
                <a
                    href="#zeta"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Zeta</a
                >
                <a
                    href="#web3"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Web3</a
                >
                <a
                    href="#hash"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Hash</a
                >
                <a
                    href="#gaming"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Gaming</a
                >
            </div>
        </div>

        <!-- content wrapped -->
        <div
            id="routing"
            class="w-full flex-col flex items-center scroll-mt-48"
        >
            <!-- Use Case 1: Urban Traffic & Logistics -->
            <div
                class="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-32"
            >
                <!-- Text Left -->
                <div class="flex flex-col gap-6">
                    <div
                        class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-bold font-mono w-fit"
                    >
                        <span
                            class="w-2 h-2 rounded-full bg-sky-500 animate-pulse"
                        ></span>
                        USE CASE 01
                    </div>
                    <h2
                        class="text-3xl md:text-5xl font-bold text-white leading-tight"
                    >
                        {@html m.api_solutions_scenarios_urban_title()}
                    </h2>
                    <p class="text-slate-400 text-lg leading-relaxed">
                        {m.api_solutions_scenarios_urban_description()}
                    </p>

                    <ul class="flex flex-col gap-4 mt-4">
                        <li class="flex items-start gap-4">
                            <div
                                class="mt-1 w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center shrink-0 border border-slate-700"
                            >
                                <svg
                                    class="w-3.5 h-3.5 text-sky-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2.5"
                                        d="M5 13l4 4L19 7"
                                    /></svg
                                >
                            </div>
                            <div>
                                <strong class="text-white block">Problem</strong
                                >
                                <span class="text-slate-500 text-sm"
                                    >{m.api_solutions_scenarios_urban_problem()}</span
                                >
                            </div>
                        </li>
                        <li class="flex items-start gap-4">
                            <div
                                class="mt-1 w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center shrink-0 border border-slate-700"
                            >
                                <svg
                                    class="w-3.5 h-3.5 text-sky-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2.5"
                                        d="M5 13l4 4L19 7"
                                    /></svg
                                >
                            </div>
                            <div>
                                <strong class="text-white block"
                                    >Solution</strong
                                >
                                <span class="text-slate-500 text-sm"
                                    >{m.api_solutions_scenarios_urban_solution()}</span
                                >
                            </div>
                        </li>
                    </ul>

                    <div
                        class="mt-8 p-6 bg-slate-900/50 border border-slate-800 rounded-xl relative overflow-hidden group/scale"
                    >
                        <div
                            class="absolute inset-0 bg-sky-500/5 opacity-0 group-hover/scale:opacity-100 transition-opacity"
                        ></div>
                        <div class="relative z-10">
                            <div class="flex justify-between items-end mb-4">
                                <div>
                                    <h4
                                        class="text-white font-bold text-sm tracking-wider uppercase mb-1"
                                    >
                                        Fleet Scale Validation
                                    </h4>
                                    <p class="text-slate-500 text-xs">
                                        A* Server Cost vs Lineum O(1)
                                    </p>
                                </div>
                                <div class="text-right">
                                    <span
                                        class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400"
                                        >{exponentialScale.toLocaleString()}</span
                                    >
                                    <span
                                        class="text-slate-500 text-sm font-bold ml-1"
                                        >AGENTS</span
                                    >
                                </div>
                            </div>

                            <input
                                type="range"
                                min="1"
                                max="100"
                                step="1"
                                bind:value={agentScale}
                                on:change={generateMapForPreset}
                                class="w-full accent-sky-500 bg-slate-800 rounded-full h-2 appearance-none cursor-pointer outline-none focus:ring-2 focus:ring-sky-500/50"
                            />
                            <div
                                class="flex justify-between mt-2 text-[10px] text-slate-500 font-mono font-bold"
                            >
                                <span>1 TRUCK</span>
                                <span>100K LOGISTICS SWARM</span>
                            </div>

                            <div
                                class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="text-slate-300 text-xs font-bold leading-tight"
                                        >Request Individual Vector Paths
                                        (Browser Only)</span
                                    >
                                    <span
                                        class="text-slate-500 text-[10px] mt-0.5"
                                        >Toggle off to bench raw O(1)
                                        mathematical throughput.</span
                                    >
                                </div>
                                <label
                                    class="relative inline-flex items-center cursor-pointer ml-4"
                                >
                                    <input
                                        type="checkbox"
                                        bind:checked={returnPaths}
                                        class="sr-only peer"
                                    />
                                    <div
                                        class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500"
                                    ></div>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Visual Right (Live WebGL Simulation) -->
                <div
                    class="border border-sky-500/30 rounded-2xl bg-slate-900/50 flex flex-col overflow-hidden relative shadow-[0_0_40px_rgba(56,189,248,0.1)] group"
                >
                    <!-- Top Header: Status & Controls -->
                    <div
                        class="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 p-4 flex justify-between items-center z-20"
                    >
                        <div class="flex items-center gap-3">
                            <span class="relative flex h-2 w-2">
                                {#if isSimulating}
                                    <span
                                        class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
                                    ></span>
                                {/if}
                                <span
                                    class="relative inline-flex rounded-full h-2 w-2 {isSimulating
                                        ? 'bg-emerald-500'
                                        : 'bg-slate-600'}"
                                ></span>
                            </span>
                            <span
                                class="text-xs font-mono font-bold {isSimulating
                                    ? 'text-emerald-400'
                                    : 'text-slate-400'}"
                            >
                                {isSimulating
                                    ? `LIVE: ${currentStep} hz`
                                    : "SYSTEM READY"}
                            </span>
                        </div>
                        <div class="flex items-center gap-4">
                            <select
                                class="bg-slate-950 border border-slate-700 text-sky-400 text-xs font-mono rounded px-2 py-1 outline-none focus:border-sky-500 transition-colors shadow-inner"
                                bind:value={activePreset}
                                on:change={handlePresetChange}
                            >
                                {#each Object.entries(PRESETS) as [key, p]}
                                    <option value={key}
                                        >SCENARIO: {p.name}</option
                                    >
                                {/each}
                            </select>
                            {#if isSimulating}
                                <button
                                    class="whitespace-nowrap px-4 py-1.5 bg-red-500/10 border border-red-500/30 text-red-500 rounded-lg text-[10px] font-bold tracking-wider hover:bg-red-500/20 transition-all font-mono shadow-lg"
                                    on:click={stopSimulation}
                                >
                                    ■ ABORT
                                </button>
                            {:else}
                                <button
                                    class="whitespace-nowrap px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg text-[10px] font-bold tracking-wider hover:bg-emerald-500/20 hover:shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all font-mono shadow-lg group-hover:bg-emerald-500/20"
                                    on:click={() => {
                                        generateMapForPreset();
                                        startSimulation();
                                    }}
                                >
                                    ▶ RUN LIVE CALCULATION
                                </button>
                            {/if}
                        </div>
                    </div>

                    <!-- WebGL Canvas Area -->
                    <div
                        use:intersect={handleIntersect}
                        class="relative w-full aspect-square bg-black overflow-hidden flex items-center justify-center"
                    >
                        <canvas
                            bind:this={canvas}
                            class="w-full h-full object-cover mix-blend-screen opacity-90 transition-opacity max-w-full group-hover:opacity-100"
                        ></canvas>
                        <div
                            class="absolute inset-0 pointer-events-none"
                            style="background: radial-gradient(circle at center, transparent 20%, #000 120%); opacity: 0.8;"
                        ></div>

                        <!-- Metric Overlay (A* time vs Lineum time) -->
                        <div
                            class="absolute bottom-6 right-6 flex flex-col gap-3 z-10 transition-transform duration-500 transform {isSimulating
                                ? 'translate-y-4 opacity-0 pointer-events-none'
                                : 'translate-y-0 opacity-100'}"
                        >
                            <div
                                class="px-4 py-2 bg-slate-900/90 border border-slate-700/50 rounded-xl text-[11px] font-mono backdrop-blur-md shadow-2xl flex items-center justify-between gap-6"
                            >
                                <span class="text-slate-400">A* Search:</span>
                                <span
                                    class="text-red-400 font-bold opacity-60 line-through"
                                    >{aStarCostThisStepMs.toFixed(0)} ms</span
                                >
                            </div>
                            <div
                                class="px-4 py-2 bg-slate-900/95 border border-sky-500/50 rounded-xl text-sm font-mono backdrop-blur-md shadow-[0_0_30px_rgba(56,189,248,0.15)] flex items-center justify-between gap-6"
                            >
                                <span class="text-sky-100">Lineum Field:</span>
                                <span
                                    class="text-sky-400 font-bold drop-shadow-[0_0_5px_rgba(56,189,248,0.8)]"
                                    >4 ms</span
                                >
                            </div>
                        </div>

                        <!-- Instruction Overlay -->
                        {#if isCompilingAPI}
                            <div
                                class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-10 bg-black/40 backdrop-blur-sm transition-all"
                            >
                                <div class="w-12 h-12 mb-4 relative">
                                    <div
                                        class="absolute inset-0 border-t-2 border-emerald-500 rounded-full animate-spin"
                                    ></div>
                                    <div
                                        class="absolute inset-1 border-r-2 border-sky-400 rounded-full animate-[spin_1.5s_linear_infinite_reverse]"
                                    ></div>
                                    <div
                                        class="absolute inset-0 flex items-center justify-center text-[10px] font-mono font-bold text-white drop-shadow-md"
                                    >
                                        {apiProgress}%
                                    </div>
                                </div>
                                <div
                                    class="px-6 py-2 bg-slate-900/80 border border-emerald-500/30 rounded-full text-emerald-400 font-mono text-sm tracking-widest uppercase shadow-[0_0_20px_rgba(16,185,129,0.2)]"
                                >
                                    {#if apiProgress < 99}
                                        GENERATING {exponentialScale >= 1000
                                            ? (exponentialScale / 1000).toFixed(
                                                  0,
                                              ) + "k"
                                            : exponentialScale} AGENTS...
                                    {:else}
                                        EXTRACTING ROUTES...
                                    {/if}
                                </div>
                            </div>
                        {:else if !isSimulating && currentStep === 0}
                            <div
                                class="absolute inset-0 flex items-center justify-center pointer-events-none z-10"
                            >
                                <div
                                    class="px-4 py-2 bg-black/60 backdrop-blur border border-white/10 rounded-full text-white/50 text-sm animate-pulse flex items-center gap-2"
                                >
                                    <svg
                                        class="w-4 h-4"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                        ><path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                                        /><path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                        /></svg
                                    >
                                    Click "Run Live" above
                                </div>
                            </div>
                        {/if}
                    </div>

                    <!-- Bottom Scrubber & Cost Panel -->
                    <div
                        class="bg-slate-900/80 backdrop-blur-md border-t border-slate-800 p-5 shrink-0 flex flex-col gap-4 z-20"
                    >
                        <!-- Ticking Cost display -->
                        <div class="flex justify-between items-center px-1">
                            <span
                                class="text-[10px] text-red-500/70 uppercase tracking-widest font-bold"
                                >Latency Waste Cost (A*)</span
                            >
                            <span
                                class="text-red-400 font-mono font-bold text-sm"
                                >-${aStarCost.toFixed(4)}
                                <span
                                    class="text-slate-500 text-[10px] font-mono"
                                    >/ batch</span
                                ></span
                            >
                        </div>

                        <!-- Scrubber Track -->
                        <div
                            class="w-full relative flex items-center group/scrub cursor-pointer h-6"
                        >
                            <input
                                type="range"
                                min="0"
                                max="1000"
                                bind:value={currentStep}
                                on:input={handleScrubberInteraction}
                                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10 p-0 m-0"
                            />
                            <div
                                class="w-full h-2 bg-slate-950 border border-slate-800 rounded-full relative overflow-hidden pointer-events-none"
                            >
                                <div
                                    class="absolute top-0 left-0 bottom-0 bg-slate-700 transition-all duration-75 group-hover/scrub:bg-slate-600"
                                    style="width: {progressWidth}%"
                                ></div>
                                <div
                                    class="absolute top-0 bottom-0 w-1.5 bg-sky-500 left-[0.4%] shadow-[0_0_10px_rgba(56,189,248,1)] z-10"
                                    title="Lineum Complete (4ms)"
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Scroll Anchor -->
            <div
                class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-24 max-w-4xl mx-auto"
            ></div>

            <!-- Use Case 2: Crowd Panic & Evacuation (Mirrored Layout) -->
            <div
                class="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-32"
            >
                <!-- Visual Left (Pre-rendered Demo Placeholder) -->
                <div
                    class="order-2 lg:order-1 border border-rose-500/30 rounded-2xl bg-slate-900/50 flex flex-col overflow-hidden relative shadow-[0_0_40px_rgba(244,63,94,0.05)] group"
                >
                    <div
                        class="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 p-4 flex justify-between items-center z-20"
                    >
                        <div class="flex items-center gap-3">
                            <span class="relative flex h-2 w-2">
                                <span
                                    class="relative inline-flex rounded-full h-2 w-2 bg-slate-600"
                                ></span>
                            </span>
                            <span
                                class="text-xs font-mono font-bold text-slate-400"
                            >
                                PRE-RENDERED SCENARIO
                            </span>
                        </div>
                        <div>
                            <button
                                class="px-4 py-1.5 bg-slate-800 border border-slate-700 text-slate-300 rounded-lg text-[10px] font-bold tracking-wider hover:bg-slate-700 transition-all font-mono"
                                on:click={() => {
                                    activePreset = "evacuation";
                                    generateMapForPreset();
                                    window.scrollTo({
                                        top: 400,
                                        behavior: "smooth",
                                    });
                                }}
                            >
                                LOAD INTO MAIN CANVAS ↑
                            </button>
                        </div>
                    </div>

                    <!-- Static Visual Area (Using CSS gradients to simulate the evacuation field) -->
                    <div
                        class="relative w-full aspect-square bg-slate-950 overflow-hidden flex items-center justify-center"
                    >
                        <!-- Fake Crowd Heatmap -->
                        <div
                            class="absolute inset-0 opacity-40 mix-blend-screen"
                            style="background: radial-gradient(circle at 40% 60%, rgba(225,29,72,0.4) 0%, transparent 50%), radial-gradient(circle at 60% 30%, rgba(225,29,72,0.6) 0%, transparent 60%); filter: contrast(1.5) saturate(1.5);"
                        ></div>
                        <!-- Fake Level Geometry -->
                        <div
                            class="absolute inset-x-0 bottom-1/4 h-8 bg-slate-900 border-y border-slate-800 z-10"
                        ></div>
                        <div
                            class="absolute top-1/4 right-1/4 w-8 h-32 bg-slate-900 border border-slate-800 z-10"
                        ></div>

                        <!-- Agents rendering -->
                        <div
                            class="absolute inset-0 z-20"
                            style="background-image: radial-gradient(circle at center, rgba(244,63,94,0.8) 1.5px, transparent 2px); background-size: 16px 16px; opacity: 0.3; mask-image: radial-gradient(circle at 50% 50%, black 20%, transparent 80%); -webkit-mask-image: radial-gradient(circle at 50% 50%, black 20%, transparent 80%);"
                        ></div>

                        <!-- Target Exit -->
                        <div
                            class="absolute top-8 left-1/2 -translate-x-1/2 w-16 h-4 bg-emerald-500/20 border border-emerald-500/50 rounded flex items-center justify-center z-30"
                        >
                            <span
                                class="text-[8px] text-emerald-400 font-mono font-bold tracking-widest"
                                >EXIT</span
                            >
                        </div>

                        <div
                            class="absolute inset-0 pointer-events-none z-40"
                            style="background: radial-gradient(circle at center, transparent 30%, #000 120%); opacity: 0.8;"
                        ></div>
                    </div>
                </div>

                <!-- Text Right -->
                <div
                    class="order-1 lg:order-2 flex flex-col gap-6 pl-0 lg:pl-8"
                >
                    <div
                        class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-bold font-mono w-fit"
                    >
                        <span class="w-2 h-2 rounded-full bg-rose-500"></span>
                        USE CASE 02
                    </div>
                    <h2
                        class="text-3xl md:text-5xl font-bold text-white leading-tight"
                    >
                        {@html m.api_solutions_scenarios_evac_title()}
                    </h2>
                    <p class="text-slate-400 text-lg leading-relaxed">
                        {m.api_solutions_scenarios_evac_description()}
                    </p>

                    <ul class="flex flex-col gap-4 mt-4">
                        <li class="flex items-start gap-4">
                            <div
                                class="mt-1 w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center shrink-0 border border-slate-700"
                            >
                                <svg
                                    class="w-3.5 h-3.5 text-rose-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2.5"
                                        d="M5 13l4 4L19 7"
                                    /></svg
                                >
                            </div>
                            <div>
                                <strong class="text-white block">Problem</strong
                                >
                                <span class="text-slate-500 text-sm"
                                    >{m.api_solutions_scenarios_evac_problem()}</span
                                >
                            </div>
                        </li>
                        <li class="flex items-start gap-4">
                            <div
                                class="mt-1 w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center shrink-0 border border-slate-700"
                            >
                                <svg
                                    class="w-3.5 h-3.5 text-rose-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2.5"
                                        d="M5 13l4 4L19 7"
                                    /></svg
                                >
                            </div>
                            <div>
                                <strong class="text-white block"
                                    >Solution</strong
                                >
                                <span class="text-slate-500 text-sm"
                                    >{m.api_solutions_scenarios_evac_solution()}</span
                                >
                            </div>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Developer Snippets Section -->
            <ApiSnippet />
        </div>
        <!-- End of routing section div -->

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="fast_trng" class="scroll-mt-48 w-full">
            <FastTrngApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="zeta" class="scroll-mt-48 w-full">
            <ZetaEntropyApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="web3" class="scroll-mt-48 w-full">
            <Web3VrfApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="hash" class="scroll-mt-48 w-full">
            <LineumHashApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="gaming" class="scroll-mt-48 w-full">
            <GamingRngApp />
        </div>

        <!-- Explore Specialized Domains (Grid to Subpages) -->
        <div class="w-full max-w-7xl mx-auto mb-32 flex flex-col items-center">
            <div class="text-center mb-12">
                <h3 class="text-3xl md:text-4xl font-bold text-white mb-4">
                    {m.api_solutions_domains_title()}
                </h3>
                <p class="text-slate-400 text-lg max-w-2xl mx-auto">
                    {m.api_solutions_domains_desc()}
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
                <!-- Hardware & Circuits -->
                <a
                    href="/api-solutions/hardware-routing"
                    class="group relative bg-slate-900/40 border border-slate-800 rounded-2xl p-6 overflow-hidden transition-all hover:bg-slate-900/60 hover:border-violet-500/50 hover:shadow-[0_0_30px_rgba(139,92,246,0.15)] flex flex-col h-full"
                >
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                    ></div>
                    <div class="relative z-10 flex flex-col h-full">
                        <div
                            class="w-10 h-10 rounded-lg bg-violet-500/20 border border-violet-500/30 flex items-center justify-center mb-4 shrink-0 text-violet-400"
                        >
                            <svg
                                class="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                                ></path></svg
                            >
                        </div>
                        <h4
                            class="text-xl font-bold text-white mb-2 group-hover:text-violet-300 transition-colors"
                        >
                            {m.api_solutions_domains_hardware_title()}
                        </h4>
                        <p class="text-sm text-slate-400 mb-6 flex-grow">
                            {m.api_solutions_domains_hardware_desc()}
                        </p>
                        <div
                            class="flex items-center text-violet-400 text-sm font-bold mt-auto"
                        >
                            {m.api_solutions_domains_hardware_link()}
                            <span
                                class="ml-2 group-hover:translate-x-1 transition-transform"
                                >→</span
                            >
                        </div>
                    </div>
                </a>

                <!-- Generative Antennas -->
                <a
                    href="/api-solutions/generative-antennas"
                    class="group relative bg-slate-900/40 border border-slate-800 rounded-2xl p-6 overflow-hidden transition-all hover:bg-slate-900/60 hover:border-sky-500/50 hover:shadow-[0_0_30px_rgba(56,189,248,0.15)] flex flex-col h-full"
                >
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-sky-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                    ></div>
                    <div class="relative z-10 flex flex-col h-full">
                        <div
                            class="w-10 h-10 rounded-lg bg-sky-500/20 border border-sky-500/30 flex items-center justify-center mb-4 shrink-0 text-sky-400"
                        >
                            <svg
                                class="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"
                                ></path></svg
                            >
                        </div>
                        <h4
                            class="text-xl font-bold text-white mb-2 group-hover:text-sky-300 transition-colors"
                        >
                            {m.api_solutions_domains_antennas_title()}
                        </h4>
                        <p class="text-sm text-slate-400 mb-6 flex-grow">
                            {m.api_solutions_domains_antennas_desc()}
                        </p>
                        <div
                            class="flex items-center text-sky-400 text-sm font-bold mt-auto"
                        >
                            {m.api_solutions_domains_antennas_link()}
                            <span
                                class="ml-2 group-hover:translate-x-1 transition-transform"
                                >→</span
                            >
                        </div>
                    </div>
                </a>

                <!-- Medical / Vasculature -->
                <a
                    href="/api-solutions/vascular-medicine"
                    class="group relative bg-slate-900/40 border border-slate-800 rounded-2xl p-6 overflow-hidden transition-all hover:bg-slate-900/60 hover:border-emerald-500/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.15)] flex flex-col h-full"
                >
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                    ></div>
                    <div class="relative z-10 flex flex-col h-full">
                        <div
                            class="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mb-4 shrink-0 text-emerald-400"
                        >
                            <svg
                                class="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                                ></path></svg
                            >
                        </div>
                        <h4
                            class="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors"
                        >
                            {m.api_solutions_domains_fluid_title()}
                        </h4>
                        <p class="text-sm text-slate-400 mb-6 flex-grow">
                            {m.api_solutions_domains_fluid_desc()}
                        </p>
                        <div
                            class="flex items-center text-emerald-400 text-sm font-bold mt-auto"
                        >
                            {m.api_solutions_domains_fluid_link()}
                            <span
                                class="ml-2 group-hover:translate-x-1 transition-transform"
                                >→</span
                            >
                        </div>
                    </div>
                </a>
            </div>

            <div class="mt-8 text-center">
                <button
                    class="px-6 py-2 rounded-full border border-slate-700 bg-slate-800/50 text-slate-300 text-sm font-bold hover:bg-slate-800 hover:text-white transition-all flex items-center gap-2 mx-auto"
                >
                    <svg
                        class="w-4 h-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        ></path></svg
                    >
                    {m.api_solutions_domains_btn_download()}
                </button>
            </div>
        </div>

        <!-- The True Potential Explainer -->
        <div class="w-full max-w-5xl mx-auto mb-32 px-4">
            <div
                class="bg-slate-900 border border-slate-800 rounded-3xl p-8 md:p-12 relative overflow-hidden"
            >
                <!-- Background Glow -->
                <div
                    class="absolute top-0 right-0 w-[500px] h-[500px] bg-sky-500/5 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3"
                ></div>

                <div
                    class="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-12 items-center"
                >
                    <div>
                        <div
                            class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-bold font-mono w-fit mb-6"
                        >
                            {m.api_solutions_vision_tag()}
                        </div>
                        <h2
                            class="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight"
                        >
                            {@html m.api_solutions_vision_title()}
                        </h2>
                        <p class="text-slate-400 text-lg leading-relaxed mb-6">
                            {m.api_solutions_vision_p1()}
                        </p>
                        <p class="text-slate-400 text-lg leading-relaxed mb-6">
                            {@html m.api_solutions_vision_p2()}
                        </p>
                        <p
                            class="text-slate-400 text-lg leading-relaxed font-medium"
                        >
                            {m.api_solutions_vision_p3()}
                        </p>
                    </div>

                    <div class="flex flex-col gap-4">
                        <div
                            class="p-6 rounded-2xl bg-black/50 border border-slate-800 backdrop-blur-sm"
                        >
                            <h4
                                class="text-white font-bold mb-2 flex items-center gap-2"
                            >
                                {@html m.api_solutions_vision_f1_title()}
                            </h4>
                            <p class="text-sm text-slate-500">
                                {m.api_solutions_vision_f1_desc()}
                            </p>
                        </div>
                        <div
                            class="p-6 rounded-2xl bg-black/50 border border-slate-800 backdrop-blur-sm"
                        >
                            <h4
                                class="text-white font-bold mb-2 flex items-center gap-2"
                            >
                                {@html m.api_solutions_vision_f2_title()}
                            </h4>
                            <p class="text-sm text-slate-500">
                                {m.api_solutions_vision_f2_desc()}
                            </p>
                        </div>
                        <div
                            class="p-6 rounded-2xl bg-black/50 border border-slate-800 backdrop-blur-sm"
                        >
                            <h4
                                class="text-white font-bold mb-2 flex items-center gap-2"
                            >
                                {@html m.api_solutions_vision_f3_title()}
                            </h4>
                            <p class="text-sm text-slate-500">
                                {m.api_solutions_vision_f3_desc()}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ROI & Integration Section -->
        <div
            class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6 w-full max-w-7xl"
        >
            <!-- ROI Calculator -->
            <div
                class="border border-emerald-500/30 bg-emerald-950/20 backdrop-blur-sm rounded-2xl p-6 lg:p-8 flex flex-col justify-between shadow-[0_0_30px_rgba(16,185,129,0.05)]"
            >
                <div>
                    <h3 class="text-xl font-bold text-white mb-2">
                        {m.api_solutions_calculator_title()}
                    </h3>
                    <p class="text-slate-400 text-sm mb-8">
                        {m.api_solutions_calculator_desc()}
                    </p>

                    <div class="flex flex-col gap-6">
                        <div class="flex flex-col gap-3">
                            <div class="flex justify-between items-end">
                                <label
                                    for="fleetSizeInput"
                                    class="text-xs font-bold text-slate-300 uppercase tracking-wider"
                                    >{m.api_solutions_calculator_fleet_label()}</label
                                >
                                <span
                                    class="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded"
                                    >{fleetSize}</span
                                >
                            </div>
                            <input
                                id="fleetSizeInput"
                                type="range"
                                bind:value={fleetSize}
                                class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                                min="10"
                                max="5000"
                                step="10"
                            />
                        </div>

                        <div class="flex flex-col gap-3">
                            <div class="flex justify-between items-end">
                                <label
                                    for="dailyOpsInput"
                                    class="text-xs font-bold text-slate-300 uppercase tracking-wider"
                                    >{m.api_solutions_calculator_ops_label()}</label
                                >
                                <span
                                    class="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded"
                                    >{dailyOps}k</span
                                >
                            </div>
                            <input
                                id="dailyOpsInput"
                                type="range"
                                bind:value={dailyOps}
                                class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                                min="1"
                                max="1000"
                                step="5"
                            />
                        </div>
                    </div>
                </div>

                <div
                    class="mt-8 pt-6 border-t border-emerald-900/50 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4"
                >
                    <div>
                        <div
                            class="text-[10px] text-emerald-500/70 uppercase tracking-widest font-bold mb-1"
                        >
                            {m.api_solutions_calculator_savings_label()}
                        </div>
                        <div
                            class="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200"
                        >
                            {formatCurrency(estimatedSavings)}
                        </div>
                    </div>
                    <button
                        class="btn btn-primary"
                        style="background-color: var(--accent-color); color: white;"
                    >
                        {m.api_solutions_calculator_btn_sales()}
                    </button>
                </div>
            </div>

            <!-- API Code Snippet & Paywall -->
            <div
                class="border border-slate-800 bg-slate-900/40 backdrop-blur-sm rounded-2xl flex flex-col overflow-hidden"
            >
                <div
                    class="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between"
                >
                    <div class="flex items-center gap-2">
                        <span
                            class="w-3 h-3 rounded-full bg-red-400/20 border border-red-500/50"
                        ></span>
                        <span
                            class="w-3 h-3 rounded-full bg-amber-400/20 border border-amber-500/50"
                        ></span>
                        <span
                            class="w-3 h-3 rounded-full bg-emerald-400/20 border border-emerald-500/50"
                        ></span>
                    </div>
                    <div class="text-xs font-mono text-slate-500">
                        POST /api/v1/compute/swarm
                    </div>
                    <div class="flex gap-2">
                        <button
                            class="text-xs font-bold {snippetLanguage === 'curl'
                                ? 'text-sky-400 bg-sky-500/10 border border-sky-500/30'
                                : 'text-slate-400 bg-slate-800 hover:text-white border-transparent'} px-3 py-1 rounded transition-colors"
                            on:click={() => (snippetLanguage = "curl")}
                            >cURL</button
                        >
                        <button
                            class="text-xs font-bold {snippetLanguage ===
                            'python'
                                ? 'text-sky-400 bg-sky-500/10 border border-sky-500/30'
                                : 'text-slate-400 bg-slate-800 hover:text-white border-transparent'} px-3 py-1 rounded transition-colors"
                            on:click={() => (snippetLanguage = "python")}
                            >Python</button
                        >
                    </div>
                </div>
                <!-- Code Snippet Body -->
                <div
                    class="p-6 relative flex-1 text-sm font-mono text-slate-300 overflow-hidden leading-relaxed"
                >
                    <pre class="whitespace-pre-wrap font-mono text-sm">
                            {apiSnippet}
                        </pre>

                    <!-- Paywall Overlay -->
                    <div
                        class="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-slate-900 via-slate-900/90 to-transparent flex flex-col items-center justify-end pb-8 px-6 text-center z-10"
                    >
                        <div
                            class="flex items-center justify-center w-12 h-12 bg-slate-800 rounded-full mb-3 shadow-lg border border-slate-700"
                        >
                            <svg
                                class="w-5 h-5 text-sky-400"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                ></path></svg
                            >
                        </div>
                        <h4 class="font-bold text-white mb-1">
                            Production Access Locked
                        </h4>
                        <p class="text-xs text-slate-400 max-w-xs mx-auto mb-4">
                            Export raw datasets, upload custom floorplans, and
                            access real-time WebSockets with an Enterprise plan.
                        </p>
                        <button
                            class="btn btn-outline"
                            style="border-color: var(--accent-cyan); color: white;"
                        >
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
    :global(:root) {
        --nav-height: 0px;
    }
    :global(body) {
        /* Ensure normal scroll behavior and background for the new B2B layout */
        background-color: #020617; /* tailwind text-slate-950 */
        margin: 0;
    }
</style>
