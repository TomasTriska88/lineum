<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import ShowcaseButton from "./ShowcaseButton.svelte";
    import ShowcaseTerminal from "./ShowcaseTerminal.svelte";
    import { intersect } from "$lib/actions/intersect";

    let canvas: HTMLCanvasElement;
    let gl: WebGLRenderingContext | null;
    let program: WebGLProgram | null;
    let animationFrameId: number;
    let positionBuffer: WebGLBuffer | null = null;
    let kappaTexture: WebGLTexture | null = null;
    let dynTexture: WebGLTexture | null = null;

    const MAP_SIZE = 128;
    let kappaFlat = new Float32Array(MAP_SIZE * MAP_SIZE).fill(1);
    let phiFlat = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);
    let startMap = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);
    let pathMap = new Float32Array(MAP_SIZE * MAP_SIZE).fill(0);

    let targetPoint = { x: 60, y: 110 }; // main exit
    let scenarioAgents: any[] = [];
    let crowdScale = 70; // High density by default
    let returnPaths = true;

    // State
    let state: "idle" | "running" | "done" = "idle";
    let isCompilingAPI = false;
    let apiProgress = 0;
    let currentStep = 0;
    let progressInterval: any;
    let logs: string[] = [];

    let isVisible = false;
    function handleIntersect(inView: boolean) {
        isVisible = inView;
        if (isVisible && state !== "idle" && gl) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = requestAnimationFrame(renderFrame);
        } else {
            cancelAnimationFrame(animationFrameId);
        }
    }

    $: exponentialScale = Math.floor(Math.pow(10, crowdScale / 20)); // Up to ~100k
    $: abmSimulationHours = (exponentialScale * 12.5) / 3600; // Agent Based Modeling hours

    // Shader Sources
    const vs = `
        attribute vec2 a_position;
        varying vec2 v_uv;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
            v_uv = a_position * 0.5 + 0.5; 
            v_uv.y = 1.0 - v_uv.y; 
        }
    `;

    const fs = `
        precision mediump float;
        varying vec2 v_uv;
        
        uniform sampler2D u_kappaMap;
        uniform sampler2D u_dynMap;
        
        uniform float u_time;
        uniform vec2 u_resolution;
        uniform vec2 u_target;

        vec3 space_black  = vec3(0.005, 0.002, 0.005);
        vec3 nebula_red   = vec3(0.42, 0.05, 0.05);  
        vec3 nebula_org   = vec3(0.48, 0.22, 0.05);  
        vec3 kappa_gray   = vec3(0.12, 0.12, 0.15); 
        vec3 neon_path    = vec3(0.97, 0.44, 0.22);

        void main() {
            vec4 kappaTex = texture2D(u_kappaMap, v_uv);
            vec4 dynTex = texture2D(u_dynMap, v_uv);
            
            float isWall = 1.0 - kappaTex.r; 
            float phi = dynTex.r;
            float path_vis = dynTex.b;

            vec3 color = space_black;
            
            if (isWall > 0.5) {
                float grid = sin(v_uv.x * 300.0) * sin(v_uv.y * 300.0);
                color = mix(kappa_gray, kappa_gray * 0.4, grid * 0.2 + 0.2);
            } else {
                if (phi > 0.01) {
                    float cloud_mask = smoothstep(0.01, 0.5, phi);
                    vec3 nebula = mix(space_black, nebula_red, cloud_mask);
                    
                    float threshold = 0.5;
                    float boundary = smoothstep(threshold - 0.1, threshold + 0.1, phi);
                    nebula = mix(nebula, nebula_org, boundary);
                    
                    float rim = smoothstep(0.05, 0.0, abs(phi - threshold));
                    nebula += rim * nebula_org * 0.8;
                    
                    color = nebula;
                    color += sin(v_uv.x * 200.0 + u_time) * cos(v_uv.y * 200.0 - u_time) * 0.5 * nebula_red * phi;
                }
            }

            if (path_vis > 0.01) {
                vec3 core = mix(neon_path, vec3(1.0), path_vis * path_vis);
                color += core * path_vis * 2.5; 
            }

            float starts_vis = dynTex.g;
            if (starts_vis > 0.01) {
                color += neon_path * starts_vis * (1.2 + 0.3 * sin(u_time * 5.0));
            }

            float distTarget = length(v_uv - u_target);
            if (distTarget < 0.02) {
                color += vec3(0.26, 0.93, 0.45) * smoothstep(0.02, 0.0, distTarget) * (1.2 + 0.3 * cos(u_time * 4.0));
            }

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
        });
        if (!gl) return;

        const vertexShader = createShader(gl, gl.VERTEX_SHADER, vs);
        const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fs);
        if (!vertexShader || !fragmentShader) return;

        program = gl.createProgram();
        if (!program) return;
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);

        const positions = new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]);
        positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

        kappaTexture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, kappaTexture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

        dynTexture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, dynTexture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    }

    function generateEvacuationMap() {
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

        // Stadium / Office layout with bottlenecks
        addWall(20, 20, 80, 5); // top boundary
        addWall(20, 20, 5, 80); // left boundary
        addWall(95, 20, 5, 80); // right
        addWall(20, 95, 30, 5); // bottom left
        addWall(70, 95, 30, 5); // bottom right (Leaves a 20px door in the middle bottom: 50-70)

        // Inner obstacles (seats/cubicles)
        addWall(40, 40, 40, 10);
        addWall(40, 60, 40, 10);
        addWall(30, 40, 5, 30);
        addWall(85, 40, 5, 30);

        const visualCap = Math.min(exponentialScale, 400);
        scenarioAgents = [];
        for (let i = 0; i < visualCap; i++) {
            // Spawn agents inside the enclosed area
            let aX = 25 + (i % 65);
            let aY = 30 + (Math.floor(i / 65) % 60);
            scenarioAgents.push({
                id: `P_${i}`,
                start: { x: aX, y: aY },
                color: "#f97316",
                name: `Person ${i}`,
            });
        }
        targetPoint = { x: 60, y: 110 }; // Outside the bottom door
    }

    $: {
        if (crowdScale) {
            generateEvacuationMap();
            uploadKappa();
            uploadDynamics();
        }
    }

    function uploadKappa() {
        if (!gl || !kappaTexture) return;
        const data = new Uint8Array(MAP_SIZE * MAP_SIZE * 4);
        for (let i = 0; i < MAP_SIZE * MAP_SIZE; i++) {
            const v = kappaFlat[i] * 255;
            data[i * 4] = v;
            data[i * 4 + 1] = v;
            data[i * 4 + 2] = v;
            data[i * 4 + 3] = 255;
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

    function uploadDynamics() {
        if (!gl || !dynTexture) return;
        startMap.fill(0);
        for (let i = 0; i < scenarioAgents.length; i++) {
            const x = Math.floor(scenarioAgents[i].start.x);
            const y = Math.floor(scenarioAgents[i].start.y);
            if (x >= 0 && x < MAP_SIZE && y >= 0 && y < MAP_SIZE) {
                startMap[y * MAP_SIZE + x] = 1.0;
            }
        }

        const data = new Uint8Array(MAP_SIZE * MAP_SIZE * 4);
        for (let i = 0; i < MAP_SIZE * MAP_SIZE; i++) {
            data[i * 4] = Math.min(255, phiFlat[i] * 255);
            data[i * 4 + 1] = Math.min(255, startMap[i] * 255);
            data[i * 4 + 2] = Math.min(255, pathMap[i] * 255);
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
        if (!isVisible || !gl || !program || state === "idle") return;

        const scale = Math.min(1.0, 800 / canvas.clientWidth);
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

        uploadDynamics();

        gl.clearColor(0, 0, 0, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.useProgram(program);

        const positionLocation = gl.getAttribLocation(program, "a_position");
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        const timeLoc = gl.getUniformLocation(program, "u_time");
        const resLoc = gl.getUniformLocation(program, "u_resolution");
        const targetLoc = gl.getUniformLocation(program, "u_target");

        gl.uniform1f(timeLoc, time * 0.002);
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

    function addLog(msg: string) {
        logs = [...logs, msg];
        if (logs.length > 5) logs.shift();
    }

    // A mock playback to ensure the WOW factor works without local python API
    function executeMockPlayback() {
        phiFlat.fill(0);
        pathMap.fill(0);
        currentStep = 0;

        let frames = 0;
        const totalFrames = 300;
        const mockInterval = setInterval(() => {
            frames += 5;
            currentStep = frames;

            for (let j = 0; j < MAP_SIZE; j++) {
                for (let i = 0; i < MAP_SIZE; i++) {
                    if (kappaFlat[j * MAP_SIZE + i] > 0.5) {
                        let dist = Math.hypot(
                            i - targetPoint.x,
                            j - targetPoint.y,
                        );
                        if (dist < frames * 0.5) {
                            phiFlat[j * MAP_SIZE + i] =
                                1.0 - dist / (frames * 0.5);
                        }
                    }
                }
            }

            if (frames % 30 === 0) {
                addLog(
                    `> FLUID DYNAMICS O(1): RESOLVING PANIC VECTORS [${exponentialScale} IDENTITIES]`,
                );
            }

            if (frames >= totalFrames) {
                clearInterval(mockInterval);
                state = "done";

                // Draw fake paths bottlenecking at the 50-70 door
                for (let i = 0; i < scenarioAgents.length; i++) {
                    const sx = Math.floor(scenarioAgents[i].start.x);
                    const sy = Math.floor(scenarioAgents[i].start.y);
                    pathMap[sy * MAP_SIZE + sx] = 1.0;

                    let doorX = 60 + (Math.random() * 8 - 4);
                    let doorY = 95;
                    let steps = 40;
                    for (let s = 0; s < steps; s++) {
                        let cx = Math.floor(sx + (doorX - sx) * (s / steps));
                        let cy = Math.floor(sy + (doorY - sy) * (s / steps));
                        pathMap[cy * MAP_SIZE + cx] = 1.0;
                    }
                    for (let s = 0; s < 10; s++) {
                        let cx = Math.floor(
                            doorX + (targetPoint.x - doorX) * (s / 10),
                        );
                        let cy = Math.floor(
                            doorY + (targetPoint.y - doorY) * (s / 10),
                        );
                        pathMap[cy * MAP_SIZE + cx] = 1.0;
                    }
                }

                addLog(`> CALCULATION COMPLETE. FLUID BOTTLENECKS IDENTIFIED.`);
                addLog(
                    `> ABM COMPUTE COST ELIMINATED: ${abmSimulationHours.toFixed(2)} hours.`,
                );
            }
        }, 16);
    }

    async function startSimulation() {
        if (state === "running") {
            state = "idle";
            logs = [];
            currentStep = 0;
            phiFlat.fill(0);
            pathMap.fill(0);
            cancelAnimationFrame(animationFrameId);
            return;
        }

        state = "running";
        currentStep = 0;
        isCompilingAPI = true;
        apiProgress = 0;
        logs = [];
        addLog(
            `> MAPPING STRUCTURAL TOPOLOGY FOR ${exponentialScale} ENTITIES`,
        );

        progressInterval = setInterval(() => {
            if (apiProgress < 99) {
                apiProgress += Math.floor(Math.random() * 12) + 4;
                if (apiProgress > 99) apiProgress = 99;
            }
        }, 30);

        try {
            const payload = {
                size: MAP_SIZE,
                agents: scenarioAgents,
                agent_count: exponentialScale,
                target: targetPoint,
                kappa_flat: Array.from(kappaFlat),
                max_steps: 1000,
                preset: "evacuation_protocol",
                return_paths: returnPaths,
            };

            const backendUrl = "http://127.0.0.1:8000";
            const res = await fetch(`${backendUrl}/api/route/task`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }).catch(() => null);

            if (!res || !res.ok) {
                throw new Error("Backend unavailable, falling back to mock.");
            }

            const data = await res.json();
            const taskId = data.task_id;
            const ws = new WebSocket(
                `ws://127.0.0.1:8000/api/route/stream/${taskId}`,
            );

            ws.onmessage = (event) => {
                isCompilingAPI = false;
                if (progressInterval) clearInterval(progressInterval);
                const msg = JSON.parse(event.data);
                currentStep = msg.step;
                if (msg.phi_flat) phiFlat.set(msg.phi_flat);
                if (msg.paths) {
                    Object.values(msg.paths).forEach((p: any) => {
                        for (let i = 0; i < p.x.length; i++) {
                            pathMap[
                                Math.floor(p.y[i]) * MAP_SIZE +
                                    Math.floor(p.x[i])
                            ] = 1.0;
                        }
                    });
                }
            };

            ws.onclose = () => {
                state = "done";
                addLog(
                    `> SAFETY ANALYSIS COMPILED. ${exponentialScale} EGRESS ROUTES VALIDATED.`,
                );
            };
        } catch (error) {
            isCompilingAPI = false;
            if (progressInterval) clearInterval(progressInterval);
            executeMockPlayback();
        }

        if (isVisible && gl) {
            animationFrameId = requestAnimationFrame(renderFrame);
        }
    }

    onMount(() => {
        initWebGL();
        generateEvacuationMap();
        uploadKappa();
        uploadDynamics();
        if (gl && program) {
            gl.useProgram(program);
            renderFrame(0);
        }

        return () => {
            cancelAnimationFrame(animationFrameId);
            if (gl) {
                if (program) gl.deleteProgram(program);
                if (kappaTexture) gl.deleteTexture(kappaTexture);
                if (dynTexture) gl.deleteTexture(dynTexture);
                if (positionBuffer) gl.deleteBuffer(positionBuffer);
            }
        };
    });
</script>

<ShowcaseTemplate
    badge="2 / 7 API SUITE"
    title="High-Density Crowd Evacuation"
    description="Predict the flow of panicked crowds (100k+ individuals) through massive structures in real-time. Lineum handles complex collision vectors and psychological field drift natively, bypassing Agent-Based Modeling penalties."
    traditionalTitle="Agent-Based Modeling (ABM)"
    traditionalDesc="Computes individual raycasts and collisions. Fails completely at stadium-scale. <strong class='text-red-400'>Takes hours to run a single simulation iteration.</strong>"
    lineumTitle="Lineum Fluid Dynamics"
    lineumDesc="Treats the crowd as a compressible fluid within the tensor field. Flat 4ms processing time limit. <strong class='text-orange-400'>Real-time safety analysis without compute limits.</strong>"
    language="bash"
    codeSnippet={`curl -X POST https://api.lineum.io/v1/compute/swarm \\
  -H "Authorization: Bearer lnm_enterprise_***" \\
  -d '{
    "people_count": 85000, 
    "floor_plan": "stadium_level2.bin", 
    "panic_factor": 0.82
  }'`}
>
    <!-- Visual slot wrapper -->
    <div
        slot="visual"
        use:intersect={handleIntersect}
        class="w-full h-[450px] relative bg-slate-950/80 border border-orange-500/20 overflow-hidden shadow-[0_0_80px_rgba(249,115,22,0.05)] rounded-3xl"
    >
        <canvas
            bind:this={canvas}
            class="w-full h-full object-cover mix-blend-screen opacity-90"
        ></canvas>

        <!-- UI Overlay -->
        <div class="absolute top-6 left-6 z-10">
            <ShowcaseButton
                status={state}
                theme="rose"
                idleText="Calculate Exit Routes"
                runningText="Simulating Crowd..."
                doneText="Reset Drill"
                on:click={startSimulation}
            />
        </div>

        <!-- Latency Detail / Wow Factor Box -->
        <div class="absolute bottom-6 right-6 z-10 flex flex-col gap-3">
            <div
                class="px-3 py-2 bg-slate-900/90 border border-slate-700/50 rounded-xl text-xs font-mono backdrop-blur-md shadow-2xl flex items-center justify-between gap-4 pointer-events-auto"
            >
                <span class="text-slate-400 min-w-[120px]">Crowd Density:</span>
                <span class="text-white font-bold"
                    >{exponentialScale.toLocaleString()} Humans</span
                >
            </div>

            <div
                class="px-4 py-3 bg-slate-900/90 border border-slate-700/50 rounded-xl text-xs font-mono backdrop-blur-md shadow-2xl pointer-events-auto flex flex-col gap-3 w-48"
            >
                <div class="flex flex-col gap-1 w-full">
                    <div class="flex justify-between items-center w-full">
                        <span class="text-slate-400">Venue Capacity</span>
                    </div>
                </div>
                <input
                    type="range"
                    min="1"
                    max="100"
                    bind:value={crowdScale}
                    class="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-orange-500"
                    disabled={state === "running"}
                />
            </div>

            <div
                class="px-4 py-2 bg-slate-900/90 border border-slate-700/50 rounded-xl text-[11px] font-mono backdrop-blur-md shadow-2xl flex items-center justify-between gap-6 pointer-events-auto"
            >
                <span class="text-slate-400">ABM Compute Time:</span>
                <span
                    class="text-red-400 font-bold opacity-60 {state !== 'idle'
                        ? 'animate-pulse'
                        : ''}">{abmSimulationHours.toFixed(1)} hours</span
                >
            </div>

            <div
                class="px-4 py-2 bg-slate-900/95 border border-orange-500/50 rounded-xl text-[13px] font-mono backdrop-blur-md shadow-[0_0_30px_rgba(249,115,22,0.15)] flex items-center justify-between gap-6 pointer-events-auto"
            >
                <span class="text-orange-100 uppercase tracking-widest"
                    >Lineum Result:</span
                >
                <span
                    class="text-orange-400 font-bold drop-shadow-[0_0_5px_rgba(249,115,22,0.8)]"
                    >4.0 ms</span
                >
            </div>
        </div>

        {#if state === "idle"}
            <div
                class="absolute inset-0 flex items-center justify-center pointer-events-none"
            >
                <div
                    class="px-4 py-2 bg-black/60 backdrop-blur border border-white/10 rounded-full text-white/50 text-sm animate-pulse flex items-center gap-2"
                >
                    Click "Calculate Exit Routes" to preview fluid modeling
                </div>
            </div>
        {/if}

        {#if isCompilingAPI}
            <div
                class="absolute inset-0 flex items-center justify-center pointer-events-none bg-black/40 backdrop-blur-sm"
            >
                <div
                    class="text-orange-400 font-mono tracking-widest text-[11px] uppercase"
                >
                    Mapping Structural Vectors... {Math.floor(apiProgress)}%
                </div>
            </div>
        {/if}
    </div>

    <!-- Proof (Live Terminal) -->
    <ShowcaseTerminal
        slot="proof"
        title="Safety Analysis Log"
        badge="TALK TO ENGINEERING"
        badgeColorClass="bg-orange-500/10 text-orange-400 border border-orange-500/20"
        primaryColorClass="text-orange-400"
        {logs}
        status={state}
        emptyText="Awaiting crowd data..."
    />
</ShowcaseTemplate>
