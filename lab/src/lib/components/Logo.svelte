<script lang="ts">
    export let width = 32;
    export let height = 32;
    export let color = "currentColor";
    export let className = "";
    export let variant = "infinity_draw";
</script>

<svg
    {width}
    {height}
    viewBox="0 0 100 100"
    xmlns="http://www.w3.org/2000/svg"
    class="lineum-logo {variant} {className}"
>
    <!-- Background / Border Glow -->
    <defs>
        <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color={color} stop-opacity="0.6" />
            <stop offset="50%" stop-color={color} stop-opacity="1" />
            <stop offset="100%" stop-color={color} stop-opacity="0.3" />
        </linearGradient>
    </defs>

    <!-- Rotating Outer Diamond Hexagon Frame (Shared) -->
    <polygon
        points="50,5 95,28 95,72 50,95 5,72 5,28"
        fill="none"
        stroke={color}
        stroke-width="2"
        stroke-opacity="0.2"
        class="anim-rotate-slow"
        style="transform-origin: 50px 50px;"
    />
    <!-- Counter-rotating Inner Hexagon (Shared) -->
    <polygon
        points="50,15 85,33 85,67 50,85 15,67 15,33"
        fill="none"
        stroke={color}
        stroke-width="1"
        stroke-opacity="0.5"
        class="anim-rotate-reverse"
        style="transform-origin: 50px 50px;"
    />

    <!-- Continous Infinity Wave Loop (Drawing Stroke) -->
    <path
        d="M 50 50 C 30 20, 10 20, 10 50 C 10 80, 30 80, 50 50 C 70 20, 90 20, 90 50 C 90 80, 70 80, 50 50 Z"
        fill="none"
        stroke="url(#waveGradient)"
        stroke-width="2"
        filter="url(#neonGlow)"
        class="anim-draw-line-slow"
    />
    <path
        d="M 50 50 C 30 20, 10 20, 10 50 C 10 80, 30 80, 50 50 C 70 20, 90 20, 90 50 C 90 80, 70 80, 50 50 Z"
        fill="none"
        stroke={color}
        stroke-width="1"
        stroke-opacity="0.3"
    />

    <!-- Pulsing Central Excitations (Shared) -->
    <circle cx="50" cy="50" r="1.5" fill="#fff" class="anim-pulse-fast" />
    <circle
        cx="50"
        cy="50"
        r="5"
        fill="none"
        stroke={color}
        filter="url(#neonGlow)"
        class="anim-expand-fade"
    />
    <circle
        cx="50"
        cy="50"
        r="12"
        fill="none"
        stroke={color}
        stroke-opacity="0.5"
        class="anim-expand-fade"
        style="animation-delay: 1s;"
    />
</svg>

<style>
    .lineum-logo {
        display: inline-block;
        transition:
            transform 0.3s ease,
            filter 0.3s ease;
    }

    .lineum-logo:hover {
        transform: scale(1.05);
        filter: brightness(1.2);
    }

    /* Keyframe Animations */
    .anim-pulse-slow {
        animation: pulseOpacity 4s ease-in-out infinite;
    }
    .anim-pulse-fast {
        animation: pulseOpacity 1.5s ease-in-out infinite alternate;
    }
    .anim-rotate-slow {
        animation: rotateFull 20s linear infinite;
    }
    .anim-rotate-reverse {
        animation: rotateFullReverse 15s linear infinite;
    }
    .anim-draw-line {
        stroke-dasharray: 200;
        stroke-dashoffset: 200;
        animation: drawPath 3s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
    }
    .anim-draw-line-slow {
        stroke-dasharray: 250;
        stroke-dashoffset: 250;
        animation: drawPathSlow 4s ease-in-out infinite alternate;
    }
    .anim-expand-fade {
        animation: expandFade 2s cubic-bezier(0.16, 1, 0.3, 1) infinite;
        transform-origin: 50px 50px;
    }

    .anim-wave-1 {
        animation: waveShift 4s ease-in-out infinite alternate;
    }
    .anim-wave-2 {
        animation: waveShift 5s ease-in-out infinite alternate-reverse;
    }
    .anim-wave-3 {
        animation: waveShift 6s ease-in-out infinite alternate;
    }

    @keyframes pulseOpacity {
        0%,
        100% {
            opacity: 0.5;
        }
        50% {
            opacity: 1;
        }
    }

    @keyframes rotateFull {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }

    @keyframes rotateFullReverse {
        from {
            transform: rotate(360deg);
        }
        to {
            transform: rotate(0deg);
        }
    }

    @keyframes drawPath {
        0%,
        10% {
            stroke-dashoffset: 200;
        }
        90%,
        100% {
            stroke-dashoffset: 0;
        }
    }

    @keyframes drawPathSlow {
        0%,
        10% {
            stroke-dashoffset: 250;
        }
        90%,
        100% {
            stroke-dashoffset: 0;
        }
    }

    @keyframes expandFade {
        0% {
            transform: scale(0.5);
            opacity: 1;
        }
        100% {
            transform: scale(3);
            opacity: 0;
        }
    }

    @keyframes waveShift {
        0% {
            transform: translateY(-2px);
        }
        100% {
            transform: translateY(2px);
        }
    }

    /* New Infinity Flow Variants */
    .anim-flow-continuous {
        stroke-dasharray: 250;
        stroke-dashoffset: 250;
        animation: flowLoop 4s linear infinite;
    }
    .anim-dash-race {
        stroke-dasharray: 10 30;
        animation: raceLoop 3s linear infinite;
    }
    .anim-asym-draw {
        stroke-dasharray: 250;
        stroke-dashoffset: 250;
        animation: drawAsym 4s cubic-bezier(0.1, 0.8, 0.9, 0.2) infinite;
    }

    @keyframes flowLoop {
        to {
            stroke-dashoffset: -250;
        }
    }
    @keyframes raceLoop {
        to {
            stroke-dashoffset: -200;
        }
    }
    @keyframes drawAsym {
        0% {
            stroke-dashoffset: 250;
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        50% {
            stroke-dashoffset: 0;
            opacity: 1;
        }
        90% {
            stroke-dashoffset: -250;
            opacity: 0;
        }
        100% {
            stroke-dashoffset: -250;
            opacity: 0;
        }
    }
</style>
