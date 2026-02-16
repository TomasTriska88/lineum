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

        // --- Golden Mean Hyper-Fidelity Palette ---
        vec3 space_black  = vec3(0.004, 0.004, 0.012);
        vec3 nebula_purp = vec3(0.18, 0.05, 0.42);  // Phi (Memory) - Restored to subtle plum
        vec3 nebula_mag  = vec3(0.48, 0.05, 0.32);  // Struct. Closure
        vec3 kappa_blue  = vec3(0.045, 0.13, 0.28); // Kappa (Substrate)
        vec3 ghost_color = vec3(0.5, 0.6, 0.85);    // Neutral Spectral Indigo for Trails

        float hash(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
        }

        // --- 🧪 Hue from Phase (arg ψ) ---
        vec3 phase_to_hue(float a) {
            vec3 c = cos(a + vec3(0.0, 2.094, 4.188)) * 0.5 + 0.5;
            // Golden Mean: Balanced spectrum saturation
            return mix(vec3(0.1, 0.7, 0.8), c, 0.52);
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
                    point = 0.5 + 0.5 * sin(t * 0.18 + 6.2831 * point);
                    float d = length(neighbor + point - f);
                    min_d = min(min_d, d);
                }
            }
            return smoothstep(0.4, 0.0, min_d);
        }

        void main() {
            vec2 uv_orig = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
            float t = u_time * 0.28; // Balanced time
            
            // --- 🌀 1. Topological Warping ---
            vec2 uv = uv_orig;
            for(int i = 0; i < COUNT; i++) {
                float offset = float(i) * (PI * 2.0 / float(COUNT));
                vec2 center = vec2(0.6 * sin(t * 0.11 + offset), 0.4 * cos(t * 0.16 + offset * 1.3));
                float dist = length(uv - center);
                float swirl = 0.065 / (dist + 0.22);
                float s = sin(swirl); float c = cos(swirl);
                uv -= center;
                uv = vec2(uv.x * c - uv.y * s, uv.x * s + uv.y * c);
                uv += center;
            }

            // --- 🧊 2. Starfield & Kappa Islands ---
            float stars = pow(hash(floor(uv_orig * 95.0)), 55.0);
            float islands = kappa_islands(uv_orig, t);
            // Enhanced Kappa coloring: Mix blue and subtle magenta for the islands
            vec3 kappa_color = mix(kappa_blue, nebula_mag * 0.4, 0.5 + 0.5 * sin(t * 0.5));
            vec3 color = space_black + stars * 0.35 + islands * kappa_color * 0.45; // Increased intensity (was 0.18)

            // --- ⚡ 3. Field Dynamics & Phase Mapping ---
            float phi_field = 0.0;
            float closure_ripples = 0.0;
            vec3 psi_visual = vec3(0.0);
            float ghosts = 0.0;
            
            vec2 linon_pos[COUNT];

            for(int i = 0; i < COUNT; i++) {
                float offset = float(i) * (PI * 2.0 / float(COUNT));
                vec2 phi_center = vec2(0.6 * sin(t * 0.11 + offset), 0.4 * cos(t * 0.16 + offset * 1.3));
                vec2 psi_pos = phi_center + vec2(0.2 * sin(t * 3.2 + offset), 0.2 * cos(t * 3.2 + offset));
                linon_pos[i] = psi_pos;

                float d_psi = length(uv - psi_pos);
                float d_phi = length(uv - phi_center);

                // --- 🧬 Phi & Structural Closure ---
                // Balanced "Golden Mean" field accumulation
                phi_field += 0.42 / (d_phi + 0.38); // Middle ground (was 0.85)
                closure_ripples += sin(d_psi * 42.0 - t * 11.0) * (0.016 / (d_psi + 0.12)); 
                

                // --- 👻 Ghost Trails (7-stage Subtle Wake) ---
                for(int j = 1; j <= 7; j++) {
                    float step_back = float(j) * 0.038; 
                    vec2 h_phi = vec2(0.6 * sin((t-step_back) * 0.11 + offset), 0.4 * cos((t-step_back) * 0.16 + offset * 1.3));
                    vec2 h_psi = h_phi + vec2(0.2 * sin((t-step_back) * 3.2 + offset), 0.2 * cos((t-step_back) * 3.2 + offset));
                    
                    float d_trail = length(uv - h_psi);
                    float fade = 1.0 - (float(j) / 8.0);
                    // Even sharper decay and lower intensity for "companion" feel
                    ghosts += fade * exp(-d_trail * 180.0) * 0.25; 
                }

                // --- 🌈 Phase-Hue Mapping (arg ψ) ---
                float ang = atan(uv.y - psi_pos.y, uv.x - psi_pos.x);
                float phase = ang + t * 13.5 + offset;
                vec3 hue = phase_to_hue(phase);
                
                // Needle-sharp Linon Point (True Singularity)
                // Even higher slope (220.0) for razor-sharp focus
                psi_visual += exp(-d_psi * 220.0) * hue * 1.5;
                psi_visual += (0.003 / (d_psi + 0.012)) * hue * 0.4; // Very minimal                // Singularity Sparkle - High intensity needle center
                psi_visual += exp(-d_psi * 550.0) * vec3(1.5);

                // --- 🧬 2.5 Geodetic Tension (Dashed Force Vector) ---
                vec2 dir = normalize(phi_center - psi_pos);
                vec2 perp = vec2(-dir.y, dir.x);
                vec2 diff = uv - psi_pos;
                float projection = dot(diff, dir);
                float lateral = dot(diff, perp);
                
                float line_len = length(phi_center - psi_pos) * 0.75;
                float line_mask = step(0.005, projection) * step(projection, line_len);
                
                // 1. Dashed Line Body
                float dash = step(0.5, fract(projection * 18.0 - t * 15.0));
                float d_line = abs(lateral);
                float line_vis = smoothstep(0.004, 0.0, d_line) * dash * 0.6;
                
                // 2. Arrowhead Tip (at line_len) - Now microscopic and hollow
                float dist_from_tip = projection - line_len;
                // Tiny "V" shape rather than solid triangle
                float arrow_v = smoothstep(0.0, -0.02, dist_from_tip) * 0.012;
                float arrow_vis = smoothstep(arrow_v, arrow_v - 0.003, abs(lateral)) 
                                 * smoothstep(arrow_v - 0.006, arrow_v, abs(lateral)) // Hollow effect
                                 * step(dist_from_tip, 0.0) * step(-0.025, dist_from_tip);
                
                psi_visual += (line_vis + arrow_vis * 1.2) * nebula_mag * line_mask;
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
                        float prox = smoothstep(1.25, 0.0, length(p1 - p2));
                        filaments += (0.0011 / (d + 0.032)) * prox;
                    }
                }
            }

            // --- 🖌️ 5. Final Composite (Balanced Phase Clouds) ---
            // Balanced contrast cloud base
            float cloud_mask = smoothstep(0.1, 0.5, phi_field * 0.42);
            vec3 nebula = mix(space_black, nebula_purp, cloud_mask * 0.65);
            
            // Sharp Phase Transition (The 'Cloud' Boundary)
            float threshold = 0.55;
            float boundary = smoothstep(threshold - 0.08, threshold, phi_field);
            nebula = mix(nebula, nebula_mag, boundary * 0.45);
            
            // Subtle "Topological Rails" (Phase Lines)
            // Visible inside clouds, gives clear intuition of Linon pathing
            float rails = smoothstep(0.025, 0.0, abs(fract(phi_field * 16.0) - 0.5));
            nebula += rails * nebula_mag * 0.45 * cloud_mask;
            
            // Rim Light / Sharp Edge definition
            float rim = smoothstep(0.04, 0.0, abs(phi_field - threshold));
            nebula += rim * nebula_mag * 0.7; 
            
            color += nebula;
            color += closure_ripples * nebula_mag * 1.15; 
            color += ghosts * ghost_color * 1.5; // Discrete comet tail
            color += filaments * nebula_mag * 0.25;
            color += psi_visual;

            // Interference Shimmer
            color += sin(uv.x * 38.0 + sin(t)) * cos(uv.y * 38.0 - t) * 0.012 * nebula_purp * phi_field;

            // Golden Mean Vignette
            color *= 1.13 - length(uv_orig) * 0.58;
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
