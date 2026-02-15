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

        // --- Lineum Constants (Dimensionless) ---
        #define PI 3.14159265359
        #define PHI_INTENSITY 0.04
        #define VACUUM_FLUCTUATION 0.05
        #define COUPLING 0.004

        // --- Galaxy Palette ---
        vec3 space_black  = vec3(0.01, 0.01, 0.03);
        vec3 nebula_purp = vec3(0.25, 0.1, 0.5);
        vec3 nebula_mag  = vec3(0.6, 0.1, 0.4);
        vec3 linon_cyan  = vec3(0.1, 0.8, 0.9);
        vec3 vortex_core = vec3(1.0, 1.0, 1.0); // White singularity

        float hash(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
            float t = u_time * 0.4;

            // --- 1. Starfield (Vacuum State) ---
            float stars = pow(hash(floor(uv * 120.0)), 30.0);
            vec3 color = space_black + stars * 0.4;

            // --- 2. Discrete Field Dynamics Sim ---
            float psi_amp = 0.0;
            float phi_field = 0.0;
            float phase_winding = 0.0;
            
            // We simulate 5 "Linon" excitations
            for(float i = 0.0; i < 5.0; i++) {
                float offset = i * (PI * 2.0 / 5.0);
                
                // --- PHI (Memory Envelope) ---
                // Simulating a slow-moving background field that "guides" psi
                vec2 phi_center = vec2(
                    0.5 * sin(t * 0.2 + offset),
                    0.3 * cos(t * 0.15 + offset * 1.5)
                );
                float dist_phi = length(uv - phi_center);
                phi_field += 0.15 / (dist_phi + 0.25);

                // --- PSI (Linon Core) ---
                // Guided by the local gradient of phi (simulated by adding drift)
                vec2 psi_pos = phi_center + vec2(
                    0.15 * sin(t * 5.0 + offset),
                    0.15 * cos(t * 5.0 + offset)
                );
                float dist_psi = length(uv - psi_pos);
                
                // Localization: bright core (psi excitation)
                float linon = 0.015 / (dist_psi + 0.04);
                psi_amp += linon * (0.9 + 0.1 * sin(t * 8.0 + offset));

                // --- VORTICES (Singularities) ---
                // Simple winding representation: bright points at the center of rotation
                float vortex = 0.001 / (dist_psi + 0.01);
                phase_winding += vortex;
            }

            // --- 3. Composite Rendering ---
            // Background: Phi (Environmental Memory)
            // Rendered as "Galaxy Nebula" with layered contours
            vec3 nebula = mix(space_black, nebula_purp, phi_field * 0.6);
            nebula = mix(nebula, nebula_mag, smoothstep(0.5, 1.5, phi_field));
            
            // Contours of Phi (Topography of the Vacuum)
            float contours = fract(phi_field * 12.0);
            float edge = smoothstep(0.0, 0.02, contours) - smoothstep(0.02, 0.04, contours);
            nebula += edge * nebula_mag * 0.4;
            
            color += nebula;

            // Foreground: Psi (Linons)
            // Cyan localized excitations
            color += psi_amp * linon_cyan;

            // Singularities: White Vortex cores
            color += phase_winding * vortex_core;

            // Vacuum Fluctuations (High freq interference)
            float noise = hash(uv + t) * VACUUM_FLUCTUATION;
            color += noise * nebula_purp;

            // Phase interference patterns (psi alignment)
            float interf = sin(uv.x * 40.0 + sin(t)) * cos(uv.y * 40.0 - t) * 0.03;
            color += interf * linon_cyan * phi_field;

            // Cosmic Vignette
            color *= 1.2 - length(uv) * 0.7;

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
