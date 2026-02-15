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

        // --- Galaxy & Lab Palette ---
        vec3 space_black  = vec3(0.01, 0.01, 0.03);
        vec3 nebula_purp = vec3(0.25, 0.1, 0.5);   // Phi (Memory)
        vec3 nebula_mag  = vec3(0.6, 0.1, 0.4);   // Struct. Closure
        vec3 linon_cyan  = vec3(0.1, 0.8, 0.9);   // Psi (Core)
        vec3 kappa_grid  = vec3(0.1, 0.2, 0.4);   // Kappa (Substrate)

        float hash(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
        }

        // --- 🧪 Lab Hook: Hexagonal Kappa Map Substrate ---
        float kappa_map(vec2 p, float t) {
            p *= 2.0; // scale
            vec2 r = vec2(1.0, 1.732);
            vec2 h = r * 0.5;
            vec2 a = mod(p, r) - h;
            vec2 b = mod(p - h, r) - h;
            vec2 g = length(a) < length(b) ? a : b;
            float hex = smoothstep(0.02, 0.0, abs(max(abs(g.x) * 0.866 + g.y * 0.5, g.y) - 0.45));
            return hex * (0.5 + 0.5 * sin(t * 0.5 + p.x * 0.5));
        }

        void main() {
            vec2 uv_orig = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
            float t = u_time * 0.3;
            
            // --- 🌀 1. Topological Warping (Field Curvature) ---
            vec2 uv = uv_orig;
            for(int i = 0; i < COUNT; i++) {
                float offset = float(i) * (PI * 2.0 / float(COUNT));
                vec2 center = vec2(0.6 * sin(t * 0.15 + offset), 0.4 * cos(t * 0.2 + offset * 1.2));
                float dist = length(uv - center);
                // Swirl effect: proportional to 1/r (phase winding singularity)
                float swirl = 0.05 / (dist + 0.15);
                float s = sin(swirl); float c = cos(swirl);
                uv -= center;
                uv = vec2(uv.x * c - uv.y * s, uv.x * s + uv.y * c);
                uv += center;
            }

            // --- 🧊 2. Starfield & Kappa Substrate ---
            float stars = pow(hash(floor(uv_orig * 120.0)), 40.0);
            float kappa = kappa_map(uv_orig, t);
            vec3 color = space_black + stars * 0.2 + kappa * kappa_grid * 0.15;

            // --- ⚡ 3. Field Dynamics Sim ---
            float psi_amp = 0.0;
            float phi_field = 0.0;
            float closure_ripples = 0.0;
            float phase_winding = 0.0;
            
            vec2 linon_pos[COUNT];

            for(int i = 0; i < COUNT; i++) {
                float offset = float(i) * (PI * 2.0 / float(COUNT));
                vec2 phi_center = vec2(0.6 * sin(t * 0.15 + offset), 0.4 * cos(t * 0.2 + offset * 1.2));
                vec2 psi_pos = phi_center + vec2(0.2 * sin(t * 4.0 + offset), 0.2 * cos(t * 4.0 + offset));
                linon_pos[i] = psi_pos;

                float d_psi = length(uv - psi_pos);
                float d_phi = length(uv - phi_center);

                // Phi buildup (slow field memory)
                phi_field += 0.12 / (d_phi + 0.3);

                // Psi core (fast localized excitation) with Spin Aura
                float ang = atan(uv.y - psi_pos.y, uv.x - psi_pos.x);
                float spin = sin(ang + t * 12.0) * 0.5 + 0.5;
                psi_amp += (0.015 / (d_psi + 0.04)) * mix(0.8, 1.0, spin);

                // Vortex singularity (High bit)
                phase_winding += 0.001 / (d_psi + 0.006);

                // 🧪 Structural Closure Ripples (nonlinear feedback)
                closure_ripples += sin(d_psi * 40.0 - t * 15.0) * (0.01 / (d_psi + 0.1));
            }

            // --- 🕸️ 4. Filamentary Tension (Coupling) ---
            float filaments = 0.0;
            for(int i = 0; i < COUNT; i++) {
                for(int j = 0; j < COUNT; j++) {
                    if (j > i) {
                        vec2 p1 = linon_pos[i]; vec2 p2 = linon_pos[j];
                        vec2 v = p2 - p1; vec2 w = uv - p1;
                        float b = clamp(dot(w, v) / dot(v, v), 0.0, 1.0);
                        float d = length(uv - (p1 + b * v));
                        float prox = smoothstep(1.5, 0.0, length(p1 - p2));
                        filaments += (0.0015 / (d + 0.025)) * prox;
                    }
                }
            }

            // --- 🖌️ 5. Final Composite ---
            vec3 nebula = mix(space_black, nebula_purp, phi_field * 0.45);
            nebula = mix(nebula, nebula_mag, smoothstep(0.7, 1.8, phi_field));
            
            // Field Contours
            float layers = 8.0;
            float cntr = fract(phi_field * layers);
            nebula += (smoothstep(0.0, 0.02, cntr) - smoothstep(0.02, 0.04, cntr)) * nebula_mag * 0.25;
            
            color += nebula;
            color += closure_ripples * nebula_mag * 0.6; // Structural feedback
            color += filaments * nebula_mag * 0.4;
            color += psi_amp * linon_cyan;
            color += phase_winding * vec3(1.0);

            // Sync Vacuum Noise
            color += hash(uv_orig + t) * VACUUM_FLUCTUATION * 2.0 * nebula_purp;

            // Interference
            color += sin(uv.x * 30.0 + sin(t)) * cos(uv.y * 30.0 - t) * 0.02 * linon_cyan * phi_field;

            // Lab-Grade Vignette
            color *= 1.1 - length(uv_orig) * 0.5;
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
