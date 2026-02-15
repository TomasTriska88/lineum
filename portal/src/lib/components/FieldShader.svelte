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

        // --- Balanced Hyper-Fidelity Palette ---
        vec3 space_black  = vec3(0.003, 0.003, 0.01);
        vec3 nebula_purp = vec3(0.15, 0.05, 0.4);   // Phi (Memory)
        vec3 nebula_mag  = vec3(0.45, 0.05, 0.3);   // Struct. Closure
        vec3 kappa_blue  = vec3(0.04, 0.12, 0.25);  // Kappa (Substrate)

        float hash(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
        }

        // --- 🧪 Hue from Phase (arg ψ) ---
        vec3 phase_to_hue(float a) {
            vec3 c = cos(a + vec3(0.0, 2.094, 4.188)) * 0.5 + 0.5;
            // Calmer, less neon spectrum
            return mix(vec3(0.1, 0.6, 0.7), c, 0.45);
        }

        // --- 🧪 Voronoi Kappa Islands ---
        float kappa_islands(vec2 p, float t) {
            vec2 g = floor(p * 1.5);
            vec2 f = fract(p * 1.5);
            float min_d = 1.0;
            for(int y = -1; y <= 1; y++) {
                for(int x = -1; x <= 1; x++) {
                    vec2 neighbor = vec2(float(x), float(y));
                    vec2 point = vec2(hash(g + neighbor), hash(g + neighbor + 121.1));
                    point = 0.5 + 0.5 * sin(t * 0.15 + 6.2831 * point); // Slower islands
                    float d = length(neighbor + point - f);
                    min_d = min(min_d, d);
                }
            }
            return smoothstep(0.4, 0.0, min_d);
        }

        void main() {
            vec2 uv_orig = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
            float t = u_time * 0.25; // Slower time overall
            
            // --- 🌀 1. Topological Warping ---
            vec2 uv = uv_orig;
            for(int i = 0; i < COUNT; i++) {
                float offset = float(i) * (PI * 2.0 / float(COUNT));
                vec2 center = vec2(0.6 * sin(t * 0.1 + offset), 0.4 * cos(t * 0.15 + offset * 1.3));
                float dist = length(uv - center);
                float swirl = 0.06 / (dist + 0.25);
                float s = sin(swirl); float c = cos(swirl);
                uv -= center;
                uv = vec2(uv.x * c - uv.y * s, uv.x * s + uv.y * c);
                uv += center;
            }

            // --- 🧊 2. Starfield & Kappa Islands ---
            float stars = pow(hash(floor(uv_orig * 90.0)), 60.0);
            float islands = kappa_islands(uv_orig, t);
            vec3 color = space_black + stars * 0.3 + islands * kappa_blue * 0.15;

            // --- ⚡ 3. Field Dynamics & Phase Mapping ---
            float phi_field = 0.0;
            float closure_ripples = 0.0;
            vec3 psi_visual = vec3(0.0);
            float ghosts = 0.0;
            
            vec2 linon_pos[COUNT];

            for(int i = 0; i < COUNT; i++) {
                float offset = float(i) * (PI * 2.0 / float(COUNT));
                vec2 phi_center = vec2(0.6 * sin(t * 0.1 + offset), 0.4 * cos(t * 0.15 + offset * 1.3));
                vec2 psi_pos = phi_center + vec2(0.2 * sin(t * 3.0 + offset), 0.2 * cos(t * 3.0 + offset));
                linon_pos[i] = psi_pos;

                float d_psi = length(uv - psi_pos);
                float d_phi = length(uv - phi_center);

                // --- 🧬 Phi & Structural Closure ---
                phi_field += 0.09 / (d_phi + 0.38);
                closure_ripples += sin(d_psi * 30.0 - t * 10.0) * (0.012 / (d_psi + 0.18));

                // --- 👻 Return Echo (Ghosts) ---
                vec2 ghost_pos = phi_center + vec2(0.2 * sin((t-1.8) * 3.0 + offset), 0.2 * cos((t-1.8) * 3.0 + offset));
                ghosts += 0.003 / (length(uv - ghost_pos) + 0.12);

                // --- 🌈 Phase-Hue Mapping (arg ψ) ---
                float ang = atan(uv.y - psi_pos.y, uv.x - psi_pos.x);
                float phase = ang + t * 12.0 + offset;
                vec3 hue = phase_to_hue(phase);
                psi_visual += (0.018 / (d_psi + 0.06)) * hue;
                
                // Singularity Sparkle
                psi_visual += (0.0008 / (d_psi + 0.01)) * vec3(1.0);
            }

            // --- 🕸️ 4. Filamentary Tension ---
            float filaments = 0.0;
            for(int i = 0; i < COUNT; i++) {
                for(int j = 0; j < COUNT; j++) {
                    if (j > i) {
                        vec2 p1 = linon_pos[i]; vec2 p2 = linon_pos[j];
                        vec2 v = p2 - p1; vec2 w = uv - p1;
                        float b = clamp(dot(w, v) / dot(v, v), 0.0, 1.0);
                        float d = length(uv - (p1 + b * v));
                        float prox = smoothstep(1.2, 0.0, length(p1 - p2));
                        filaments += (0.001 / (d + 0.035)) * prox;
                    }
                }
            }

            // --- 🖌️ 5. Final Composite ---
            vec3 nebula = mix(space_black, nebula_purp, phi_field * 0.35);
            nebula = mix(nebula, nebula_mag, smoothstep(0.8, 2.2, phi_field));
            
            // Subtle Precision Contours
            float cntr = fract(phi_field * 6.0);
            nebula += (smoothstep(0.0, 0.01, cntr) - smoothstep(0.01, 0.02, cntr)) * nebula_mag * 0.2;
            
            color += nebula;
            color += closure_ripples * nebula_mag * 0.5;
            color += ghosts * nebula_purp * 0.3;
            color += filaments * nebula_mag * 0.2;
            color += psi_visual;

            // Interference
            color += sin(uv.x * 35.0 + sin(t)) * cos(uv.y * 35.0 - t) * 0.008 * nebula_purp * phi_field;

            // Balanced Vignette
            color *= 1.12 - length(uv_orig) * 0.55;
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
