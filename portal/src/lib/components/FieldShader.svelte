<script lang="ts">
    import { onMount } from "svelte";

    let canvas: HTMLCanvasElement;
    let gl: WebGLRenderingContext | null;
    let program: WebGLProgram | null;
    let animationFrameId: number;

    const vs = `
        attribute vec2 position;
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
        }
    `;

    const fs = `
        precision highp float;
        uniform float u_time;
        uniform vec2 u_resolution;

        // --- Tesla-Edison Synchronicity Hook (Live Constants) ---
        // These MUST match lineum.py exactly. Checked by tools/sync_portal.py
        #define DISSIPATION_RATE 0.00462
        #define REACTION_STRENGTH 0.00070
        #define PSI_PHI_COUPLING 0.004
        #define PHI_INTERACTION_STRENGTH 0.04
        #define PHI_DIFFUSION 0.30
        #define PSI_DIFFUSION 0.05
        #define VACUUM_FLUCTUATION 0.005

        #define COUNT 6
        #define PI 3.14159265359

        // --- Galaxy Palette ---
        vec3 space_black  = vec3(0.01, 0.01, 0.03);
        vec3 nebula_purp = vec3(0.25, 0.1, 0.5);
        vec3 nebula_mag  = vec3(0.6, 0.1, 0.4);
        vec3 linon_cyan  = vec3(0.1, 0.8, 0.9);
        vec3 vortex_core = vec3(1.0, 1.0, 1.0);

        float hash(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
            float t = u_time * 0.3;

            // --- 1. Starfield (Vacuum State) ---
            float stars = pow(hash(floor(uv * 120.0)), 30.0);
            vec3 color = space_black + stars * 0.3;

            // --- 2. Discrete Field Dynamics Sim ---
            float psi_amp = 0.0;
            float phi_field = 0.0;
            float filament = 0.0;
            float phase_winding = 0.0;
            
            vec2 linon_pos[COUNT];

            for(int i = 0; i < COUNT; i++) {
                float offset = float(i) * (PI * 2.0 / float(COUNT));
                
                // --- PHI (Memory Envelope & Center) ---
                vec2 phi_center = vec2(
                    0.6 * sin(t * 0.15 + offset),
                    0.4 * cos(t * 0.2 + offset * 1.2)
                );
                
                // PSI (Linon Core) - Guided by drift + flow
                vec2 psi_pos = phi_center + vec2(
                    0.2 * sin(t * 4.0 + offset),
                    0.2 * cos(t * 4.0 + offset)
                );
                linon_pos[i] = psi_pos;

                float dist_psi = length(uv - psi_pos);
                float dist_phi = length(uv - phi_center);

                // Phi field buildah
                phi_field += 0.15 / (dist_phi + 0.3);

                // --- Spin Aura Dipole ---
                float ang = atan(uv.y - psi_pos.y, uv.x - psi_pos.x);
                float dipole = sin(ang + t * 10.0) * 0.5 + 0.5;
                float core = 0.012 / (dist_psi + 0.035);
                psi_amp += core * mix(0.7, 1.0, dipole);

                // Vortex singularity
                phase_winding += 0.001 / (dist_psi + 0.005);
            }

            // --- Filamentary Tension (Connections) ---
            for(int i = 0; i < COUNT; i++) {
                // Nested loops in WebGL 1.0 MUST have constant bounds and simple initializers
                for(int j = 0; j < COUNT; j++) {
                    if (j > i) {
                        vec2 p1 = linon_pos[i];
                        vec2 p2 = linon_pos[j];
                        
                        // Simple segment distance
                        vec2 v = p2 - p1;
                        vec2 w = uv - p1;
                        float c1 = dot(w, v);
                        float c2 = dot(v, v);
                        float b = clamp(c1 / c2, 0.0, 1.0);
                        vec2 pb = p1 + b * v;
                        float d = length(uv - pb);
                        
                        // Only show filaments for nearby excitations (phi coupling)
                        float proximity = smoothstep(1.5, 0.0, length(p1 - p2));
                        filament += (0.001 / (d + 0.02)) * proximity;
                    }
                }
            }

            // --- 3. Composite Rendering ---
            vec3 nebula = mix(space_black, nebula_purp, phi_field * 0.5);
            nebula = mix(nebula, nebula_mag, smoothstep(0.8, 2.0, phi_field));
            
            // Contours (Topography of the Vacuum)
            float layers = 10.0;
            float contours = fract(phi_field * layers);
            float edge = smoothstep(0.0, 0.02, contours) - smoothstep(0.02, 0.04, contours);
            nebula += edge * nebula_mag * 0.3;
            
            color += nebula;
            color += filament * nebula_mag * 0.5;
            color += psi_amp * linon_cyan;
            color += phase_winding * vortex_core;

            // Vacuum Fluctuations (Synced Noise)
            float noise = hash(uv + t) * VACUUM_FLUCTUATION * 5.0;
            color += noise * nebula_purp;

            // Phase interference
            float interf = sin(uv.x * 30.0 + sin(t)) * cos(uv.y * 30.0 - t) * 0.02;
            color += interf * linon_cyan * phi_field;

            color *= 1.2 - length(uv) * 0.8;
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

    onMount(() => {
        gl = canvas.getContext("webgl");
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
            console.error(gl.getProgramInfoLog(program));
            return;
        }

        const positions = new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]);
        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

        const positionLocation = gl.getAttribLocation(program, "position");
        const timeLocation = gl.getUniformLocation(program, "u_time");
        const resolutionLocation = gl.getUniformLocation(
            program,
            "u_resolution",
        );

        function render(time: number) {
            if (!gl || !program) return;

            // Resize handle
            const displayWidth = canvas.clientWidth;
            const displayHeight = canvas.clientHeight;
            if (
                canvas.width !== displayWidth ||
                canvas.height !== displayHeight
            ) {
                canvas.width = displayWidth;
                canvas.height = displayHeight;
                gl.viewport(0, 0, canvas.width, canvas.height);
            }

            gl.clearColor(0, 0, 0, 0);
            gl.clear(gl.COLOR_BUFFER_BIT);

            gl.useProgram(program);
            gl.enableVertexAttribArray(positionLocation);
            gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
            gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

            gl.uniform1f(timeLocation, time * 0.001);
            gl.uniform2f(resolutionLocation, canvas.width, canvas.height);

            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

            animationFrameId = requestAnimationFrame(render);
        }

        animationFrameId = requestAnimationFrame(render);

        return () => {
            cancelAnimationFrame(animationFrameId);
        };
    });
</script>

<canvas bind:this={canvas} class="shader-canvas"></canvas>

<style>
    .shader-canvas {
        width: 100%;
        height: 100%;
        display: block;
        opacity: 0.6;
    }
</style>
