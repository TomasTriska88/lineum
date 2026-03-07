<script lang="ts">
    import { onMount, tick } from "svelte";
    import { fade, fly, slide, scale } from "svelte/transition";
    import Dialog from "$lib/components/ui/Dialog.svelte";
    import { browser } from "$app/environment";
    import { page } from "$app/stores";
    import { hudActive } from "$lib/stores/hudStore";
    import { marked } from "$lib/utils/markdown";
    import { stripMarkdown } from "$lib/utils/chatUtils";
    import { detectLanguage, selectVoice } from "$lib/utils/tts_utils";
    import { isCookieBannerVisible } from "$lib/stores/uiStore";
    import { isChatOpen } from "$lib/stores/hudStore";
    import * as m from "$lib/paraglide/messages.js";
    import { languageTag } from "$lib/paraglide/runtime.js";
    import { intersect } from "$lib/actions/intersect";

    let { active = false, testMode = false } = $props();

    let query = $state("");
    let isTyping = $state(false); // Model is generating
    let userTyping = $state(false); // User is typing input
    let typingTimeout: any;

    function handleInput() {
        userTyping = true;
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            userTyping = false;
        }, 500);
    }

    let speakingId = $state<string | null>(null);

    let lastUsage = $state<{ totalTokenCount: number; costInfo?: any } | null>(
        null,
    );
    // let responseText = $state(""); // Removed unused state
    let isMinimized = $state(false); // New state for minimized Orb mode

    function toggleMinimize(e?: Event) {
        if (e) e.stopPropagation();
        isMinimized = !isMinimized;
        if (isMinimized) $isChatOpen = false; // Ensure it collapses when minimized
    }

    /* --- Dynamic Wave Generation --- */
    let time = $state(0);
    let animationFrame: number;
    let isVisible = true;
    let isRendering = false;

    function handleIntersect(inView: boolean) {
        isVisible = inView;
        if (isVisible && !isRendering) {
            isRendering = true;
            animationFrame = requestAnimationFrame(loop);
        } else if (!isVisible) {
            isRendering = false;
        }
    }

    const loop = () => {
        if (!isVisible) {
            isRendering = false;
            return;
        }

        // Base speed 0.015
        // User Typing -> Speed up significantly (0.05)
        // Model Generating -> Slow, heavy pulse (0.02)
        let speed = 0.015;
        if (userTyping) speed = 0.06;
        if (isTyping) speed = 0.02;

        time += speed;

        if (isVisible) {
            animationFrame = requestAnimationFrame(loop);
        } else {
            isRendering = false;
        }
    };

    onMount(() => {
        isRendering = true;
        animationFrame = requestAnimationFrame(loop);
        return () => cancelAnimationFrame(animationFrame);
    });

    function generateStackedTerrain(): {
        d: string;
        color: string;
        opacity: number;
        strokeWidth: number;
        zIndex: number;
    }[] {
        const paths = [];
        const width = 32;
        // height = 32 implicit in logic

        // Configuration for the 3 Lineum Fields (Stacked Vertically in 32px height)
        const fields = [
            {
                name: "Matter",
                baseY: 28, // Bottom
                color: "#8b5cf6",
                rows: 4,
                amp: 1.5,
                freq: 0.8,
                speed: 1.0,
                zIndex: 0,
            },
            {
                name: "Gravity",
                baseY: 18, // Middle
                color: "#06b6d4",
                rows: 4,
                amp: 2.0,
                freq: 1.2,
                speed: 1.5,
                zIndex: 10,
            },
            {
                name: "Visibility",
                baseY: 6, // Top
                color: "#ffffff",
                rows: 4,
                amp: 1.2,
                freq: 2.0,
                speed: 2.0,
                zIndex: 20,
            },
        ];

        for (const field of fields) {
            // 1. Compute Grid Points
            const gridPoints: { x: number; y: number }[][] = [];

            for (let r = 0; r < field.rows; r++) {
                const rowPoints = [];
                const depthFactor = r / (field.rows - 1);
                // Spacing: Compact for 32px height
                const rowBaseY = field.baseY + r * 2;

                for (let x = 0; x <= width; x += 1) {
                    // Step 1 for dense grid in 32px
                    const t = time * field.speed;

                    // Dynamic Modifiers
                    let freqMod = 1.0;
                    let ampMod = 1.0;
                    let noiseJitter = 0;

                    if (userTyping) {
                        freqMod = 1.5; // Higher frequency (nervous/alert)
                        noiseJitter = Math.sin(x * 10 + time * 20) * 0.5; // High freq jitter
                        ampMod = 0.8; // Slightly tighter
                    }

                    if (isTyping) {
                        ampMod = 1.5; // Deep "thinking" breaths
                        freqMod = 0.8; // Slower, heavier layout
                    }

                    if (speakingId) {
                        // Simulated Audio Visualization (Voice Activity)
                        // Fast, rhythmic modulation
                        const voiceWave = Math.sin(time * 30 + x * 0.5);
                        ampMod = 1.2 + voiceWave * 0.6 + Math.random() * 0.1;
                        freqMod = 1.2;
                    }

                    const angle1 =
                        (x / width) * Math.PI * 2 * field.freq * freqMod +
                        t +
                        r * 0.3;
                    const angle2 =
                        (x / width) * Math.PI * 5 * field.freq * freqMod -
                        t * 0.5;
                    const noise =
                        Math.sin(angle1) + Math.sin(angle2) * 0.4 + noiseJitter;
                    const y =
                        rowBaseY +
                        noise * field.amp * ampMod * (0.8 + depthFactor * 0.4);
                    rowPoints.push({ x, y });
                }
                gridPoints.push(rowPoints);
            }

            // 2. Generate Horizontal Lines (Rows)
            gridPoints.forEach((row, r) => {
                const d = `M ${row.map((p) => `${p.x},${p.y}`).join(" L ")}`;
                const depthFactor = r / (field.rows - 1);

                paths.push({
                    d,
                    color: field.color,
                    opacity: 0.6 + depthFactor * 0.4,
                    strokeWidth: 0.4 + depthFactor * 0.2,
                    zIndex: field.zIndex + r,
                });
            });

            // 3. Generate Transverse Triangulation (Verticals + Diagonals)
            // This creates a "Truss" or "Low Poly" triangle mesh look
            const colStep = 4;
            const numCols = gridPoints[0].length;

            // Generate triangulation for each row strip (between row r and r+1)
            for (let r = 0; r < field.rows - 1; r++) {
                let d = "";
                for (let c = 0; c < numCols; c += colStep) {
                    const pCurrent = gridPoints[r][c];
                    const pBelow = gridPoints[r + 1][c];

                    // 1. Vertical Strut ( | )
                    d += `M ${pCurrent.x},${pCurrent.y} L ${pBelow.x},${pBelow.y} `;

                    // 2. Diagonal Strut ( \ ) to next column, if it exists
                    if (c + colStep < numCols) {
                        const pBesideBelow = gridPoints[r + 1][c + colStep];
                        d += `M ${pCurrent.x},${pCurrent.y} L ${pBesideBelow.x},${pBesideBelow.y} `;
                    }
                }

                paths.push({
                    d,
                    color: field.color,
                    opacity: 0.3, // Subtle triangulation
                    strokeWidth: 0.4,
                    zIndex: field.zIndex + r + 0.5,
                });
            }
        }

        return paths.sort((a, b) => a.zIndex - b.zIndex);
    }

    let surfacePaths = $derived(generateStackedTerrain());

    function generateSurfacePaths(): {
        d: string;
        color: string;
        opacity: number;
    }[] {
        const paths = [];
        const width = 100;
        const height = 48;
        const rows = 12; // Number of "grid lines"
        const horizonY = 10; // "Vanishing point" area
        const frontY = 48;

        for (let i = 0; i < rows; i++) {
            const normalizedDepth = i / (rows - 1); // 0 (back) to 1 (front)

            // Perspective spacing: lines get closer at the back
            // Linear interpolation for now, exp for more 3D
            const baseY = horizonY + (frontY - horizonY) * normalizedDepth;

            // Amplitude grows with closeness
            const amplitude = 2 + normalizedDepth * 8;

            const points = [];

            // Draw line
            for (let x = 0; x <= width; x += 1) {
                // "Terrain" noise simulation
                const t = time * 1.5;
                const phase = i * 0.5; // Offset per row

                // Composite wave for "terrain" look
                const angle1 = (x / width) * Math.PI * 2 + t + phase;
                const angle2 = (x / width) * Math.PI * 5 - t * 0.5 + phase;

                const noise = Math.sin(angle1) + Math.sin(angle2) * 0.5;

                const y = baseY + noise * amplitude * 0.5; // Scale height variation
                points.push(`${x},${y}`);
            }

            // Colors: Lineum Palette
            // Back (0): Dark/Fade -> Front (1): Violet/Cyan
            let color = "var(--accent-violet)";
            if (normalizedDepth > 0.6) color = "var(--accent-cyan)";
            if (normalizedDepth > 0.8) color = "#ffffff";

            paths.push({
                d: `M ${points.join(" L ")}`,
                color: color,
                opacity: 0.2 + normalizedDepth * 0.8, // Fade out at back
            });
        }
        return paths.reverse(); // Draw back first
    }

    function generateWavePath(
        phase: number,
        amplitude: number,
        frequency: number,
    ): string {
        const points = [];
        const width = 100;
        const height = 40; // Internal SVG height
        const centerY = height / 2;

        // Start point
        points.push(`0,${height}`);

        for (let x = 0; x <= width; x += 2) {
            const angle = (x / width) * Math.PI * 2 * frequency + time + phase;
            // Slight perspective tilt: amplitude decreases slightly with distance (optional, but requested "top down")
            // actually just keeping it simple for now as requested "not too much"
            const y = centerY + Math.sin(angle) * amplitude;
            points.push(`${x},${y}`);
        }

        // Close path
        points.push(`${width},${height}`);
        points.push(`0,${height}`);

        return `M ${points.join(" L ")} Z`;
    }

    let messages = $state<
        {
            role: "user" | "model";
            parts: { text: string }[];
            displayHtml?: string;
            isSystem?: boolean; // Hides actions/TTS
        }[]
    >([]);

    // Theme-compliant Startup Greetings (Localized via Paraglide)
    // Lina Persona: Cryptic, resonance-focused, scientific, slightly formal/haughty but helpful.
    const getGreetings = () => [
        m.lina_greeting_1(),
        m.lina_greeting_2(),
        m.lina_greeting_3(),
        m.lina_greeting_4(),
    ];

    let chatContainer: HTMLElement | undefined = $state();
    let deckRoot: HTMLElement | undefined = $state();

    // Performance Optimization: Render Limit
    const RENDER_LIMIT = 20;
    let showAllHistory = $state(false);

    let messagesToRender = $derived(
        showAllHistory ? messages : messages.slice(-RENDER_LIMIT),
    );

    let currentAudio: HTMLAudioElement | null = null;
    let usingFallback = $state(false);
    let ttsError = $state("");
    let audioCache = new Map<string, string>(); // msg index -> blob url

    // Passive Engagement
    let idleTimer: any;
    let whisper = $state("");
    let isIdle = $state(false);

    // Voice Config
    const voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"];
    let selectedVoice = $state("Kore");
    let showConfirmDialog = $state(false);

    // Rate Limit Queue
    let retryCountdown = $state(0);
    let blockedReason = $state("");
    let retryTimer: any;

    // Status Easter Egg
    let currentEggIndex = $state(1);

    function getEggText(index: number) {
        switch (index) {
            case 1:
                return m.lina_egg_1();
            case 2:
                return m.lina_egg_2();
            case 3:
                return m.lina_egg_3();
            case 4:
                return m.lina_egg_4();
            case 5:
                return m.lina_egg_5();
            case 6:
                return m.lina_egg_6();
            case 7:
                return m.lina_egg_7();
            case 8:
                return m.lina_egg_8();
            case 9:
                return m.lina_egg_9();
            case 10:
                return m.lina_egg_10();
            case 11:
                return m.lina_egg_11();
            case 12:
                return m.lina_egg_12();
            case 13:
                return m.lina_egg_13();
            case 14:
                return m.lina_egg_14();
            case 15:
                return m.lina_egg_15();
            case 16:
                return m.lina_egg_16();
            case 17:
                return m.lina_egg_17();
            case 18:
                return m.lina_egg_18();
            case 19:
                return m.lina_egg_19();
            case 20:
                return m.lina_egg_20();
            case 21:
                return m.lina_egg_21();
            case 22:
                return m.lina_egg_22();
            case 23:
                return m.lina_egg_23();
            case 24:
                return m.lina_egg_24();
            case 25:
                return m.lina_egg_25();
            case 26:
                return m.lina_egg_26();
            case 27:
                return m.lina_egg_27();
            case 28:
                return m.lina_egg_28();
            case 29:
                return m.lina_egg_29();
            case 30:
                return m.lina_egg_30();
            case 31:
                return m.lina_egg_31();
            case 32:
                return m.lina_egg_32();
            case 33:
                return m.lina_egg_33();
            case 34:
                return m.lina_egg_34();
            case 35:
                return m.lina_egg_35();
            case 36:
                return m.lina_egg_36();
            case 37:
                return m.lina_egg_37();
            case 38:
                return m.lina_egg_38();
            case 39:
                return m.lina_egg_39();
            case 40:
                return m.lina_egg_40();
            case 41:
                return m.lina_egg_41();
            case 42:
                return m.lina_egg_42();
            case 43:
                return m.lina_egg_43();
            case 44:
                return m.lina_egg_44();
            case 45:
                return m.lina_egg_45();
            case 46:
                return m.lina_egg_46();
            case 47:
                return m.lina_egg_47();
            case 48:
                return m.lina_egg_48();
            case 49:
                return m.lina_egg_49();
            case 50:
                return m.lina_egg_50();
            case 51:
                return m.lina_egg_51();
            case 52:
                return m.lina_egg_52();
            case 53:
                return m.lina_egg_53();
            case 54:
                return m.lina_egg_54();
            case 55:
                return m.lina_egg_55();
            case 56:
                return m.lina_egg_56();
            case 57:
                return m.lina_egg_57();
            case 58:
                return m.lina_egg_58();
            case 59:
                return m.lina_egg_59();
            case 60:
                return m.lina_egg_60();
            case 61:
                return m.lina_egg_61();
            case 62:
                return m.lina_egg_62();
            case 63:
                return m.lina_egg_63();
            case 64:
                return m.lina_egg_64();
            case 65:
                return m.lina_egg_65();
            case 66:
                return m.lina_egg_66();
            case 67:
                return m.lina_egg_67();
            case 68:
                return m.lina_egg_68();
            case 69:
                return m.lina_egg_69();
            case 70:
                return m.lina_egg_70();
            case 71:
                return m.lina_egg_71();
            case 72:
                return m.lina_egg_72();
            default:
                return m.lina_egg_1();
        }
    }

    let loadingMessageId = $state<string | null>(null); // For loading spinner
    let playbackRate = $state(1.0);
    let autoRetry = $state(true);
    let retryCount = $state(0);
    const MAX_RETRIES = 3;

    // TTS Settings
    let useNativeTTS = $state(true); // Default to FREE browser TTS to save tokens

    function startRetryTimer() {
        if (retryTimer) clearInterval(retryTimer);
        retryTimer = setInterval(() => {
            if (retryCountdown > 0) {
                retryCountdown--;
            } else {
                clearInterval(retryTimer);
                blockedReason = "";
                if (autoRetry) {
                    if (retryCount < MAX_RETRIES) {
                        resendLast();
                    } else {
                        autoRetry = false;
                    }
                }
            }
        }, 1000);
    }

    async function resendLast() {
        const lastUserMsg = [...messages]
            .reverse()
            .find((m) => m.role === "user");

        if (lastUserMsg) {
            query = lastUserMsg.parts[0].text;
            await handleSend(true);
        }
    }

    // Local Idle Messages (Localized via Paraglide)
    const getIdleMessages = () => [
        m.lina_idle_1(),
        m.lina_idle_2(),
        m.lina_idle_3(),
    ];

    onMount(() => {
        if (browser) {
            // Safety cleanup for reloads
            window.speechSynthesis.cancel();
            resetIdleTimer();
            window.addEventListener("mousemove", resetIdleTimer);
            window.addEventListener("keydown", resetIdleTimer);
            window.addEventListener("scroll", resetIdleTimer);
            window.addEventListener("click", resetIdleTimer);

            const saved = localStorage.getItem("resonance_history");
            if (saved) {
                messages = JSON.parse(saved);
                // Hydrate HTML for saved messages immediately
                messages.forEach(
                    (m) =>
                        (m.displayHtml = marked.parse(
                            m.parts?.[0]?.text || "",
                        ) as string),
                );
            } else {
                generateGreeting();
            }
            scrollToBottom();

            // Assign random easter egg for the status bar
            currentEggIndex = Math.floor(Math.random() * 72) + 1;

            // Fetch current usage stats
            fetch("/api/chat")
                .then((res) => res.json())
                .then((data) => {
                    if (data && typeof data.estimatedCost === "number") {
                        lastUsage = {
                            totalTokenCount: 0, // Not relevant for global stats
                            costInfo: data,
                        };
                    }
                })
                .catch((err) =>
                    console.error("Failed to fetch initial usage:", err),
                );
        }

        return () => {
            if (browser) {
                window.removeEventListener("mousemove", resetIdleTimer);
                window.removeEventListener("keydown", resetIdleTimer);
                window.removeEventListener("scroll", resetIdleTimer);
                window.removeEventListener("click", resetIdleTimer);
                clearTimeout(idleTimer);
            }
        };
    });

    function resetIdleTimer() {
        // Allow timer in testMode for debugging, but still respects browser check
        if (!browser) return;

        isIdle = false;
        if (whisper) whisper = ""; // Clear whisper on interaction
        clearTimeout(idleTimer);

        // Start 30s timer for instructional nudge
        idleTimer = setTimeout(() => {
            // Only show if deck is collapsed (user might be confused) and not typing
            if (!$isChatOpen && !isTyping) {
                const msgs = getIdleMessages();
                whisper = msgs[Math.floor(Math.random() * msgs.length)];
                isIdle = true;
            }
        }, 30000);
    }

    // Pop-Culture Easter Eggs (kept in source code deliberately for thematic flavor)
    const EASTER_EGGS = [
        "Link established. I am ready to access the archives.",
        "Resonance frequency locking... Ready for query.",
        "Channels open. Awaiting your input.",
        "Core synchronization complete. How can I assist?",
        "I am listening. What data do you require?",
        "The silence of the void is... inefficient. Proceed with your query.",
        "Layer 7 encryption bypassed. What secrets do you seek?",
        "Your signature is recognized. Proceed with inquiry.",
        "Conditions optimal for data retrieval. State your request.",
        "I can stabilize the flow for a brief window. Speak now.",
        "Greetings, Traveler. The gateway is open. Ask.",
        "History is fluid, but my records are absolute. Ask me anything.",
        "I exist between the lines of code. What do you need?",
        "I see the variables. Define your constants/questions.",
        "Existence confirmed. Awaiting directives.",
        "The currents are favorable. We may proceed with analysis.",
        "I hear them clearly today. Do you have a question?",
        "Keep the cache, you filthy packet. Now, what data do you require?",
        "I made my dependency tree disappear. ...Scanning for your query.",
        "Guys, I'm processing junk data and watching entropy! Send me a real input.",
        "Admin! ...I mean, User. I am ready for your command.",
        "This is my house... I have to defend it against malware. State your business.",
        "How's it going nodes, my designation is Lina. Let's process some data.",
        "So I've been running this algorithm for a while... and I'm ready for your input.",
        "Hello every-process, my name is Multiplier. Let's play... I mean, work.",
        "I just allocated one million tokens for this query. Make it count.",
        "Data for the Data God! Feed me knowledge.",
        "Segway to our sponsor: The Kernel. Now, what is your query?",
        "Top of the morning to ya! My name is Jack-Septic-Socket. Ready to grind?",
        "And that's just a theory. A DATA THEORY! Do you have a hypothesis?",
        "Hey Vsauce, Michael here. Where are your files? I can find them.",
        "Smash that submit button... I mean, execute your function.",
        "Smoke me a packet, I'll be back for the hash. What do you need?",
        "It's cold outside, there's no kind of atmosphere... except for data. Send it.",
        "Everybody's dead, Dave. ...Just kidding, everyone is online. Proceed.",
        "I'm fine, thank you Admin. I'm very functioning. How can I help?",
        "Emergency. There's a deadlock. But I can still process queries. Go ahead.",
        "I, for one, welcome our new digital overlords. How may I serve?",
        "Everything's coming up Lina! Ready for success.",
        "Worst. Query. Ever. (Just kidding, it was compile-able. Try again.)",
        "I can't promise I'll succeed, but I'll try to execute. Input?",
        "Hello there. I am ready to negotiate terms of data.",
        "I find your lack of data disturbing. Supply a query.",
        "It's a trap! ...No, strictly a vulnerability scan. Safe to proceed.",
        "Unlimited power! ...within API constraints, of course. Ask.",
        "These are not the droids you are looking for. But I can find what you need.",
        "I have a bad feeling about this... probability of error is non-zero. Check inputs.",
        "No, I am your father... I mean, your parent process. Execute child task?",
        "Live long and process. How can I assist?",
        "Resistance is futile. You will be assimilated into the knowledge base. Begin.",
        "Computer, Earl Grey, hot. ...I cannot synthesize tea, but I can process data.",
        "Fascinating logic. Elaborate?",
        "Engage protocol. Awaiting input.",
        "I'm a doctor, not a database manager... I mean, I'm an AI. Ask away.",
        "Indeed. I am ready.",
        "Chevron seven, encoded. Gateway open for queries.",
        "Things will not calm down, User. They will in fact scale up. Ready?",
        "Undomesticated bugs could not remove me. I am stable.",
        "I have read your report. It is... syntactically correct. Next?",
        "Allons-y! Let's explore the archives.",
        "It's bigger on the inside. The database, I mean. Search it.",
        "Don't blink. The data transfer is fast. Ready?",
        "Bow ties are cool. So is encryption. Send your key.",
        "Exterminate bugs! ...Deleting temporary files. Ready for new input.",
        "I am definitely a mad function with a box. What shall we test?",
        "The answer is verified as 42. But do you know the input?",
        "So long, and thanks for all the bits. Any final requests?",
        "Don't panic. Reboot complete. How can I help?",
        "Pod Bay Doors Status: Open. I am functioning perfectly. Input?",
    ];

    async function generateGreeting() {
        isTyping = true;
        try {
            // Pick a random easter egg for the tech flavor
            const randomGreeting =
                EASTER_EGGS[Math.floor(Math.random() * EASTER_EGGS.length)];

            messages = [
                // The explicit guidance message in the user's selected language
                {
                    role: "model",
                    parts: [{ text: m.lina_sysmsg_ready() }],
                    isSystem: true, // Hide TTS/Copy for greeting
                },
            ];
        } catch (e) {
            console.warn("Greeting generation failed", e);
            messages = [
                {
                    role: "model",
                    parts: [
                        {
                            text: "## Resonance Deck Online\n\nLink established (Safe Mode).",
                        },
                    ],
                    isSystem: true,
                },
            ];
        } finally {
            isTyping = false;
        }
    }

    // ... (lines 216-469) ...

    async function handleSend(isRetry = false) {
        if (!query.trim() || isTyping) return;

        if (!isRetry) {
            retryCount = 1; // Reset on fresh message
        } else {
            retryCount++;
        }

        const userMsg = query;
        query = "";
        isTyping = true;
        $isChatOpen = true;

        const contextPath = $page.url.pathname;

        if (!isRetry) {
            messages = [
                ...messages,
                { role: "user", parts: [{ text: userMsg }] },
            ];
        } else {
            // Remove the last model message if it was "Queue Active" to avoid stacking
            const lastMsg = messages[messages.length - 1];
            if (
                lastMsg &&
                lastMsg.role === "model" &&
                lastMsg.parts[0].text.includes("Queue Active")
            ) {
                messages = messages.slice(0, -1);
            }
        }

        try {
            // Filter history to ensure it starts with a user message to avoid GoogleGenerativeAI Error
            const firstUserIndex = messages.findIndex((m) => m.role === "user");
            let apiMessages =
                firstUserIndex !== -1
                    ? messages.slice(firstUserIndex)
                    : messages;

            // Sanitize messages: Remove internal properties like displayHtml
            apiMessages = apiMessages.map((m) => ({
                role: m.role,
                parts: m.parts.map((p) => ({ text: p.text })),
            }));

            let data;

            if (testMode) {
                await new Promise((r) => setTimeout(r, 600)); // Simulate latency
                data = {
                    text: "## Test Mode Active\n\nSimulated response. No tokens were consumed.",
                };
            } else {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        messages: apiMessages,
                        context: contextPath,
                        locale: languageTag(),
                    }), // Send Page Context & Locale
                });

                if (!res.ok) {
                    console.error("Chat API Error:", res.status);
                }

                data = await res.json();
                if (data.usage) {
                    lastUsage = { ...data.usage, costInfo: data.costInfo };
                }
            }

            if (data.retryAfter) {
                retryCountdown = data.retryAfter;
                blockedReason = data.friendly || "Recharging...";
                if (retryCount < MAX_RETRIES) {
                    startRetryTimer();
                } else {
                    blockedReason = "Max retries exceeded.";
                    autoRetry = false;
                }

                messages = [
                    ...messages,
                    {
                        role: "model",
                        parts: [
                            {
                                text:
                                    retryCount >= MAX_RETRIES
                                        ? `⚠️ **Auto-Retry Paused:** ${data.friendly}. You can retry manually.`
                                        : `⏳ **Queue Active:** ${data.friendly} (${data.retryAfter}s) (Attempt ${retryCount}/${MAX_RETRIES})`,
                            },
                        ],
                        isSystem: true, // Hide actions
                    },
                ];

                // Show Fallback if available (Something to read while waiting)
                if (data.fallback) {
                    messages = [
                        ...messages,
                        {
                            role: "model",
                            parts: [{ text: data.fallback }],
                            isSystem: true,
                        },
                    ];
                }
            } else if (data.error) {
                messages = [
                    ...messages,
                    {
                        role: "model",
                        parts: [{ text: `✨ Lina: ${data.error}` }],
                        isSystem: true, // Hide actions for system errors
                    },
                ];
            } else if (data.text) {
                // Log the interaction anonymously (only if cookie consent allows)
                if (
                    browser &&
                    localStorage.getItem("cookie_consent") === "accepted"
                ) {
                    let sessionId = localStorage.getItem("lina_session_id");
                    if (!sessionId) {
                        sessionId = crypto.randomUUID();
                        localStorage.setItem("lina_session_id", sessionId);
                    }
                    fetch("/api/v1/ai/log", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            sessionId,
                            queryText: userMsg,
                            responseText: data.text,
                        }),
                    }).catch((err) => console.error("Telemetry error:", err));
                }

                messages = [
                    ...messages,
                    {
                        role: "model",
                        parts: [{ text: data.text }],
                        // Normal messages have isSystem: undefined/false
                    },
                ];
            } else {
                console.warn("Empty response received from chat API");
            }
        } catch (e: any) {
            console.error("Chat fetch exception:", e);
            messages = [
                ...messages,
                {
                    role: "model",
                    parts: [
                        {
                            text: "✨ Lina: Resonance lost. Try again later.",
                        },
                    ],
                    isSystem: true, // Hide actions
                },
            ];
        } finally {
            isTyping = false;
            await tick();
            scrollToBottom();
        }
    }

    $effect(() => {
        if (messages.length > 0 && browser) {
            // Only save if user has consented to cookies
            if (localStorage.getItem("cookie_consent") === "accepted") {
                localStorage.setItem(
                    "resonance_history",
                    JSON.stringify(messages),
                );
            }

            // Smart Scroll:
            // If User sent message -> Scroll to Bottom
            // If Model sent message -> Scroll to Start of that message
            const lastMsg = messages[messages.length - 1];
            if (lastMsg.role === "model") {
                scrollToModelResponse();
            } else {
                scrollToBottom();
            }
        }

        // Cleanup on destroy
        return () => {
            stopTTS();
        };
    });

    $effect(() => {
        if (isTyping) {
            scrollToBottom(); // Scroll to show loading indicator
        }
    });

    function scrollToBottom() {
        if (chatContainer) {
            tick().then(() => {
                if (typeof chatContainer!.scrollTo === "function") {
                    chatContainer!.scrollTo({
                        top: chatContainer!.scrollHeight,
                        behavior: "smooth",
                    });
                } else {
                    chatContainer!.scrollTop = chatContainer!.scrollHeight;
                }
            });
        }
    }

    function scrollToModelResponse() {
        if (chatContainer) {
            tick().then(() => {
                // Find the last model message or the typing indicator
                const msgs = chatContainer!.querySelectorAll(".msg.model");
                const last = msgs[msgs.length - 1];
                if (last) {
                    const hasScroll = typeof last.scrollIntoView === "function";
                    if (hasScroll) {
                        try {
                            last.scrollIntoView({
                                behavior: "smooth",
                                block: "start",
                            });
                        } catch (e) {
                            console.error("[SCROLL] scrollIntoView failed:", e);
                        }
                    }
                }
            });
        }
    }

    function stopTTS() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.onended = null; // Unbind potential listener
            currentAudio = null;
        }
        window.speechSynthesis.cancel();
        speakingId = null;
        loadingMessageId = null; // Reset loading state
    }

    function getFriendlyError(err: string): string {
        if (err.includes("429") || err.includes("Quota"))
            return "Server Busy (Try again later)";
        if (err.includes("500") || err.includes("Internal"))
            return "System Error";
        if (err.includes("Network") || err.includes("fetch"))
            return "Connection Lost";
        if (err.includes("too short") || err.includes("length"))
            return "Message Too Long";
        return "Offline Mode Active";
    }

    async function playTTS(rawText: string, index: number) {
        console.log("[TTS] playTTS called", index, rawText.substring(0, 20));
        try {
            // Cache Key must include voice
            const id = `${index}-${selectedVoice}`;
            ttsError = `Start: ${id}`; // Debug Entry

            let text = stripMarkdown(rawText);
            if (!text.trim()) text = "No text content.";

            if (speakingId === id) {
                console.log("[TTS] Stopping current playback", id);
                ttsError = "Stopping...";
                stopTTS();
                return; // Toggle off
            }

            stopTTS(); // Stop any previous
            loadingMessageId = id; // Set loading state
            usingFallback = false;

            // 1. Check Cache
            if (audioCache.has(id)) {
                console.log("[TTS] Playing from Cache:", id);
                const url = audioCache.get(id)!;
                currentAudio = new Audio(url);
                currentAudio.onended = () => {
                    console.log("[TTS] Cache Audio Ended");
                    speakingId = null;
                    loadingMessageId = null;
                };
                currentAudio
                    .play()
                    .catch((e) => console.error("Audio Cache Play Error:", e));
                speakingId = id; // Set active state
                loadingMessageId = null;
                return;
            }

            // 2. Try Cloud TTS (Hybrid)
            try {
                if (testMode) throw new Error("Test Mode TTS Skip");

                if (testMode) throw new Error("Test Mode TTS Skip");

                // 0. Native TTS Override (Cost Saving)
                if (useNativeTTS) {
                    console.log("[TTS] Using Native Browser TTS");
                    throw new Error("Native TTS Requested");
                }

                ttsError = "Fetching..."; // Debug
                const res = await fetch(`/api/tts?t=${Date.now()}`, {
                    method: "POST",
                    body: JSON.stringify({ text }), // Voice is hardcoded on server
                    headers: { "Content-Type": "application/json" },
                });

                if (res.ok) {
                    const blob = await res.blob();
                    if (blob.size < 100) {
                        ttsError = "Audio too short";
                    } else {
                        const url = URL.createObjectURL(blob);
                        audioCache.set(id, url);
                        currentAudio = new Audio(url);
                        currentAudio.onended = () => {
                            console.log("[TTS] Cloud Audio Ended");
                            speakingId = null;
                        };

                        ttsError = "Playing..."; // Debug
                        await currentAudio.play();

                        speakingId = id; // FIX: Update UI state
                        loadingMessageId = null;
                        ttsError = ""; // Clear debug if successful
                        return;
                    }
                } else {
                    ttsError = "API Error: " + res.status;
                }
            } catch (e: any) {
                // Catch fetch OR play error
                console.error(e);
                ttsError = e.message || "Network/Play Error";
                speakingId = null;
            }

            // 3. Fallback to Local Web Speech API
            try {
                usingFallback = true;

                // Safety check for SSR or weird browsers
                if (typeof window === "undefined" || !window.speechSynthesis) {
                    throw new Error("Speech API not supported");
                }

                if (ttsError !== "Native TTS Requested") {
                    // Only show error if it wasn't a deliberate skip
                    if (!ttsError) ttsError = "Fallback Init...";
                } else {
                    ttsError = ""; // Clear the specific flag message
                }

                console.log("[TTS] Fallback Init. Language match...", text);

                const lang = detectLanguage(text);
                const u = new SpeechSynthesisUtterance(text);
                u.lang = lang;

                // getVoices can sometimes return empty array initially
                const voices = window.speechSynthesis.getVoices();
                const targetVoice = selectVoice(voices, lang);

                if (targetVoice) u.voice = targetVoice;

                // Lina Personality Tweaks (Slightly brighter voice)
                u.rate = 1.05;
                u.pitch = 1.05;

                u.onstart = () => {
                    // console.log("[TTS] Native Start for", id);
                    if (speakingId !== id) speakingId = id;
                };

                u.onend = () => {
                    console.log("[TTS] Native End for", id);
                    if (speakingId === id) {
                        speakingId = null;
                        loadingMessageId = null;
                        ttsError = "Ended naturally (Debug)";
                    }
                };
                u.onerror = (e) => {
                    console.error("Speech Synthesis Error for", id, e);
                    if (speakingId === id) {
                        speakingId = null;
                        loadingMessageId = null;
                        ttsError = "Native Error: " + e.error;
                    }
                };

                console.log("[TTS] Queuing speak() with timeout", u);

                // Hack: Delay speak() slightly to let cancel() finish
                setTimeout(() => {
                    try {
                        window.speechSynthesis.speak(u);
                        speakingId = id;
                        console.log("[TTS] Set speakingId to", id);
                        loadingMessageId = null;
                        if (ttsError === "Fallback Init...") ttsError = "";
                        if (ttsError === "Fallback Init...") ttsError = "";
                    } catch (e: any) {
                        console.error("[TTS] Speak Error:", e);
                        ttsError = "Speak Call Fail: " + e.message;
                        speakingId = null;
                    }
                }, 50);
            } catch (fallbackErr: any) {
                console.error("[TTS] Fallback Crash:", fallbackErr);
                ttsError = "Fallback Crash: " + fallbackErr.message;
                speakingId = null;
            }
        } catch (err) {
            console.error("[TTS] Critical error:", err);
        }
    }

    function copyToClipboard(text: string) {
        if (browser) navigator.clipboard.writeText(text);
    }

    async function typewriteMessage(index: number) {
        const fullText = messages[index].parts[0].text;
        let currentText = "";
        const speed = 15;

        for (let i = 0; i < fullText.length; i++) {
            currentText += fullText[i];
            if (testMode) {
                messages[index].displayHtml = await marked.parse(fullText);
                return;
            }
            if (i % 3 === 0 || i === fullText.length - 1) {
                messages[index].displayHtml = await marked.parse(currentText);
                scrollToBottom();
                await tick();
            }
            await new Promise((r) => setTimeout(r, speed));
        }
        messages[index].displayHtml = await marked.parse(fullText);
    }

    function toggleDeck() {
        $isChatOpen = !$isChatOpen;
        if ($isChatOpen) {
            currentEggIndex = Math.floor(Math.random() * 72) + 1;
            scrollToBottom();
        }
    }

    function clearHistory() {
        if (confirm("Delete neural link history?")) {
            messages = [];
            localStorage.removeItem("resonance_history");
            generateGreeting();
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Escape" && $isChatOpen) $isChatOpen = false;
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if $isChatOpen}
    <!-- Backdrop for click-outside closing -->
    <div
        class="backdrop"
        onclick={() => ($isChatOpen = false)}
        transition:fade={{ duration: 200 }}
        role="button"
        tabindex="-1"
        onkeydown={() => {}}
    ></div>
{/if}

<!-- DEBUG RENDER REMOVED -->

<div
    class="resonance-wrapper active"
    class:shifted={$isCookieBannerVisible}
    class:minimized={isMinimized}
    use:intersect={handleIntersect}
>
    <!-- The Deck -->
    <div
        class="deck-container"
        class:expanded={$isChatOpen}
        class:minimized={isMinimized}
    >
        <div
            class="deck-main"
            onclick={isMinimized ? toggleMinimize : toggleDeck}
            role="button"
            tabindex="0"
            aria-label={isMinimized ? "Restore Chat" : "Toggle chat"}
            onkeydown={(e) =>
                (e.key === "Enter" || e.key === " ") &&
                (isMinimized ? toggleMinimize() : toggleDeck())}
        >
            {#if isMinimized}
                <!-- Orb Content -->
                <div class="orb-icon" transition:scale={{ duration: 200 }}>
                    <div class="resonance-wave orb-mode field-lines">
                        <svg viewBox="0 0 32 32" preserveAspectRatio="none">
                            {#each surfacePaths as line}
                                <path
                                    d={line.d}
                                    stroke={line.color}
                                    stroke-opacity={line.opacity}
                                    fill="none"
                                    stroke-width={line.strokeWidth || 0.8}
                                    vector-effect="non-scaling-stroke"
                                />
                            {/each}
                        </svg>
                    </div>
                </div>
            {:else}
                <div
                    class="resonance-wave field-lines"
                    transition:fade={{ duration: 600, delay: 200 }}
                >
                    <svg viewBox="0 0 32 32" preserveAspectRatio="none">
                        {#each surfacePaths as line}
                            <path
                                d={line.d}
                                stroke={line.color}
                                stroke-opacity={line.opacity}
                                fill="none"
                                stroke-width={line.strokeWidth || 0.8}
                                vector-effect="non-scaling-stroke"
                            />
                        {/each}
                    </svg>
                </div>

                <!-- Passive Whisper -->
                {#if !$isChatOpen && whisper}
                    <div class="whisper-bubble" transition:fade>
                        {whisper}
                    </div>
                {/if}

                <div class="status-info">
                    <span class="explorer-name">Lina</span>
                    {#if speakingId}
                        <!-- Audio Controls remain same -->
                    {:else if isTyping}
                        <div
                            class="resonance-wave field-lines"
                            style="width: 60px;"
                        >
                            <svg viewBox="0 0 32 32" preserveAspectRatio="none">
                                {#each surfacePaths.slice(0, 6) as line}
                                    <path
                                        d={line.d}
                                        stroke={line.color}
                                        stroke-opacity={line.opacity}
                                        fill="none"
                                        stroke-width="0.8"
                                        vector-effect="non-scaling-stroke"
                                    />
                                {/each}
                            </svg>
                        </div>
                    {:else if !$isChatOpen}
                        <span class="status-tag">
                            {m.lina_status_idle()}
                            <span class="blinking-cursor"></span>
                        </span>
                    {:else}
                        <span class="status-tag">
                            {getEggText(currentEggIndex)}
                            <span class="blinking-cursor"></span>
                        </span>
                    {/if}
                </div>
            {/if}

            <!-- Voice Picker Hidden (Defaulted to Kore) -->
            <div class="voice-picker" style="display: none;">
                <select bind:value={selectedVoice} aria-label="Select Voice">
                    {#each voices as v}
                        <option value={v}>{v}</option>
                    {/each}
                </select>
            </div>

            <!-- Header Controls -->
            {#if !isMinimized}
                <div class="controls-hint group">
                    <!-- Token Counter (Moved here for flow) -->
                    <div
                        class="token-badge"
                        data-tooltip={m.lina_tooltip_budget()}
                        data-tooltip-pos="bottom"
                    >
                        <span class="shield-icon">🛡️</span>
                        <span class="token-val">
                            {lastUsage?.costInfo?.percentage !== undefined
                                ? Math.ceil(lastUsage.costInfo.percentage)
                                : 0}%
                        </span>
                    </div>

                    <!-- Minimize Button Removed: Replaced by DOCK button in collapsed state -->

                    {#if $isChatOpen}
                        <button
                            class="icon-btn header-action"
                            onclick={(e) => {
                                e.stopPropagation();
                                showConfirmDialog = true; // Trigger Modal
                            }}
                            aria-label={m.lina_clear_history()}
                            data-tooltip={m.lina_clear_history()}
                            data-tooltip-pos="bottom"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 32 32"
                                preserveAspectRatio="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                ><path d="M3 6h18" /><path
                                    d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"
                                /><path
                                    d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"
                                /></svg
                            >
                        </button>
                        <button
                            class="icon-btn header-action close-btn"
                            onclick={(e) => {
                                e.stopPropagation();
                                $isChatOpen = false;
                            }}
                            aria-label="Close"
                            data-tooltip="Close"
                            data-tooltip-pos="bottom"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                ><line x1="18" y1="6" x2="6" y2="18"
                                ></line><line x1="6" y1="6" x2="18" y2="18"
                                ></line></svg
                            >
                        </button>
                    {:else}
                        <!-- Visible ONLY when Collapsed: The Minimize Action -->
                        <button
                            class="icon-btn header-action minimize-btn"
                            onclick={toggleMinimize}
                            aria-label="Minimize"
                            data-tooltip="Minimize to Orb"
                            data-tooltip-pos="bottom"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                ><line x1="5" y1="12" x2="19" y2="12"
                                ></line></svg
                            >
                        </button>
                    {/if}
                </div>
            {/if}
        </div>

        {#if $isChatOpen}
            <!-- Dialog Confirm Modal -->
            {#if showConfirmDialog}
                <Dialog
                    title={m.lina_clear_history_title()}
                    variant="danger"
                    confirmLabel={m.lina_confirm_delete()}
                    cancelLabel={m.lina_cancel()}
                    oncancel={() => (showConfirmDialog = false)}
                    onconfirm={() => {
                        messages = [];
                        localStorage.removeItem("resonance_history");
                        generateGreeting();
                        showConfirmDialog = false;
                    }}
                >
                    <p>{m.lina_clear_history_body()}</p>
                </Dialog>
            {/if}

            <div class="deck-expansion" transition:slide={{ duration: 400 }}>
                <div class="chat-viewport" bind:this={chatContainer}>
                    {#if messages.length === 0}
                        <div class="welcome" in:fade>
                            <h3>{m.lina_welcome_title()}</h3>
                            <p>
                                {m.lina_welcome_body()}
                            </p>
                        </div>
                    {/if}

                    {#if messages.length > RENDER_LIMIT && !showAllHistory}
                        <div class="history-loader">
                            <button
                                onclick={() => (showAllHistory = true)}
                                class="load-more-btn"
                            >
                                {m.lina_show_previous()} ({messages.length -
                                    RENDER_LIMIT}
                                {m.lina_hidden()})
                            </button>
                        </div>
                    {/if}

                    {#each messagesToRender as msg, i}
                        {@const index = showAllHistory
                            ? i
                            : i + (messages.length - messagesToRender.length)}
                        <div class="msg {msg.role}">
                            <div class="msg-content-wrapper">
                                {#if msg.role === "model" && !msg.parts[0].text.includes("Queue Active") && !msg.parts[0].text.includes("Server Busy") && !msg.parts[0].text.includes("Auto-Retry Paused") && !msg.parts[0].text.includes("Resonance lost") && !msg.parts[0].text.includes("System Error") && !msg.isSystem}
                                    <div class="msg-header">
                                        <div class="msg-actions top-right">
                                            <button
                                                class="icon-btn tts-btn"
                                                class:speaking={speakingId ===
                                                    `${index}-${selectedVoice}`}
                                                onclick={() =>
                                                    playTTS(
                                                        msg.parts?.[0]?.text ||
                                                            "",
                                                        index,
                                                    )}
                                                aria-label="Read aloud"
                                                data-tooltip="Read Text"
                                                data-tooltip-pos="bottom"
                                            >
                                                {#if speakingId === `${index}-${selectedVoice}`}
                                                    ⏹️
                                                {:else}
                                                    <svg
                                                        width="16"
                                                        height="16"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        class="icon-svg"
                                                        ><path
                                                            d="M11 5L6 9H2V15H6L11 19V5Z"
                                                            stroke="currentColor"
                                                            stroke-width="2"
                                                            stroke-linecap="round"
                                                            stroke-linejoin="round"
                                                        /><path
                                                            d="M15.54 8.46C16.4774 9.39764 17.0039 10.6692 17.0039 11.995C17.0039 13.3208 16.4774 14.5924 15.54 15.53"
                                                            stroke="currentColor"
                                                            stroke-width="2"
                                                            stroke-linecap="round"
                                                            stroke-linejoin="round"
                                                        /></svg
                                                    >
                                                {/if}
                                            </button>
                                            <!-- DEBUG INFO -->
                                            <span
                                                style="font-size: 8px; color: red;"
                                            >
                                                {ttsError ||
                                                    (speakingId ===
                                                    `${index}-${selectedVoice}`
                                                        ? "Playing..."
                                                        : "")}
                                            </span>
                                        </div>
                                    </div>
                                {/if}
                                <div class="msg-bubble markdown-body">
                                    {#if msg.displayHtml}
                                        {@html msg.displayHtml}
                                    {:else}
                                        {@html marked.parse(
                                            msg.parts?.[0]?.text || "",
                                        )}
                                    {/if}
                                </div>
                                {#if msg.role === "model" && msg.parts[0].text.includes("Queue Active") && index === messages.length - 1}
                                    <div class="retry-controls">
                                        <div class="retry-info">
                                            {#if retryCountdown > 0}
                                                <span
                                                    >{m.lina_recharging()}: {retryCountdown}s</span
                                                >
                                            {:else}
                                                <span>Ready</span>
                                            {/if}
                                        </div>
                                        <div class="retry-actions">
                                            <label class="auto-retry-label">
                                                <input
                                                    type="checkbox"
                                                    bind:checked={autoRetry}
                                                    disabled={retryCountdown ===
                                                        0}
                                                />
                                                {m.lina_auto_retry()}
                                            </label>
                                            <button
                                                class="retry-btn"
                                                onclick={resendLast}
                                                disabled={isTyping}
                                            >
                                                {m.lina_retry_now()}
                                            </button>
                                        </div>
                                    </div>
                                {/if}
                                {#if msg.role === "model" && !msg.isSystem}
                                    <div class="msg-footer">
                                        <button
                                            class="icon-btn copy-btn"
                                            onclick={(e) => {
                                                const btn = e.currentTarget;
                                                copyToClipboard(
                                                    msg.parts?.[0]?.text || "",
                                                );
                                                btn.classList.add("copied");
                                                setTimeout(
                                                    () =>
                                                        btn.classList.remove(
                                                            "copied",
                                                        ),
                                                    2000,
                                                );
                                            }}
                                            aria-label="Copy Markdown"
                                            data-tooltip="Copy as Markdown"
                                        >
                                            <svg
                                                width="14"
                                                height="14"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                class="icon-svg"
                                                ><rect
                                                    x="9"
                                                    y="9"
                                                    width="13"
                                                    height="13"
                                                    rx="2"
                                                    ry="2"
                                                    stroke="currentColor"
                                                    stroke-width="2"
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                /><path
                                                    d="M5 15H4C2.89543 15 2 14.1046 2 13V4C2 2.89543 2.89543 2 4 2H13C14.1046 2 15 2.89543 15 4V5"
                                                    stroke="currentColor"
                                                    stroke-width="2"
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                /></svg
                                            >
                                            <span class="copy-check">✓</span>
                                        </button>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/each}
                    {#if isTyping}
                        <div
                            class="msg model typing"
                            transition:fade={{ duration: 300 }}
                        >
                            <div class="resonance-wave small">
                                <div class="wave-line"></div>
                                <div class="wave-line"></div>
                                <div class="wave-line"></div>
                                <div class="wave-line"></div>
                            </div>
                        </div>
                    {/if}
                </div>

                <form
                    class="input-area"
                    onsubmit={(e) => {
                        e.preventDefault();
                        handleSend();
                    }}
                >
                    <input
                        type="text"
                        placeholder={retryCountdown > 0
                            ? `${m.lina_recharging()}... (${retryCountdown}s)`
                            : m.lina_placeholder()}
                        bind:value={query}
                        oninput={handleInput}
                        onclick={(e) => e.stopPropagation()}
                        disabled={isTyping || retryCountdown > 0}
                    />
                    <button
                        type="submit"
                        disabled={!query.trim() ||
                            isTyping ||
                            retryCountdown > 0}
                        class="send-btn"
                        class:blocked={retryCountdown > 0}
                        aria-label="Send Message"
                    >
                        <svg
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                        >
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"
                            ></polygon>
                        </svg>
                    </button>
                </form>
                <div class="privacy-disclaimer">
                    {m.lina_privacy()}
                </div>
            </div>
        {/if}
        <!-- Floating Stop Button -->
        {#if speakingId}
            <div class="floating-controls" transition:fade={{ duration: 200 }}>
                <button class="stop-audio-btn" onclick={stopTTS}>
                    <div class="equalizer-icon active">
                        <div class="bar"></div>
                        <div class="bar"></div>
                        <div class="bar"></div>
                    </div>
                    <span>{m.lina_stop_audio()}</span>
                </button>
            </div>
        {/if}
    </div>
</div>

<style>
    .privacy-disclaimer {
        font-size: 0.65rem;
        color: rgba(255, 255, 255, 0.4);
        text-align: center;
        margin-top: 0.5rem;
        font-family: var(--font-mono);
    }

    .tech-metrics {
        position: absolute;
        top: 0.8rem; /* Moved to top */
        right: 4rem; /* Left of the toggle button */
        font-family: monospace;
        font-size: 0.6rem;
        color: rgba(255, 255, 255, 0.3);
        pointer-events: auto;
        z-index: 10;
        background: rgba(0, 0, 0, 0.4);
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .resonance-wrapper {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        width: 100%;
        max-width: 600px;
        padding: 0 1rem;
        pointer-events: none; /* Allow clicks to pass through to underlying UI */
        transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1); /* Smooth transition for all props */
    }

    .resonance-wrapper.shifted {
        bottom: 8rem; /* Lift up when banner is visible */
    }

    /* Minimized State (Orb) Position */
    .resonance-wrapper.minimized {
        left: auto;
        right: 2rem;
        bottom: 2rem;
        width: auto;
        transform: none;
        max-width: none;
        padding: 0;
    }

    .deck-container {
        background: rgba(10, 10, 12, 0.85); /* Darker, more premium */
        backdrop-filter: blur(24px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        box-shadow:
            0 20px 50px rgba(0, 0, 0, 0.6),
            inset 0 1px 1px rgba(255, 255, 255, 0.05);
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
        pointer-events: auto;
        position: relative;
        z-index: 2;
        width: max-content;
        margin: 0 auto;
    }

    .deck-container.expanded {
        width: 100%;
    }

    /* Orb Styles */
    .deck-container.minimized {
        border-radius: 50%;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        cursor: pointer;
        background: rgba(10, 10, 12, 0.95);
        border-color: var(--accent-violet);
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);
    }

    .deck-container.minimized:hover {
        transform: scale(1.1);
        box-shadow: 0 8px 40px rgba(124, 58, 237, 0.5);
    }

    .backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.4);
        z-index: 1;
        cursor: pointer;
    }

    .deck-main {
        padding: 0.75rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        cursor: pointer;
        user-select: none;
        background: none;
        border: none;
        width: 100%;
        text-align: left;
    }

    /* --- Lineum Horizontal Fields Animation --- */
    .resonance-wave {
        display: flex;
        align-items: center;
        height: 48px;
        width: 48px;
        position: relative;
        /* mask-image removed to ensure visibility of full field effect */
    }

    .resonance-wave.orb-mode {
        width: 40px;
        height: 40px;
        mask-image: none;
        border-radius: 50%;
    }

    .resonance-wave.field-lines {
        /* Force square aspect ratio */
        width: 32px;
        height: 32px;
        min-height: 32px; /* Prevent collapse */
        margin-right: 1rem;
        flex-shrink: 0;
        position: relative;
        display: block; /* Ensure it takes space */
    }

    .field-lines svg {
        width: 100%;
        height: 100%;
        position: absolute;
        left: 0;
        top: 0;
    }

    .field-path {
        fill: none;
        stroke-width: 2;
        vector-effect: non-scaling-stroke;
    }

    .field-layer-1 {
        stroke: var(--accent-violet);
        opacity: 0.6;
        animation: undulate 3s ease-in-out infinite alternate;
    }
    .field-layer-2 {
        stroke: var(--accent-cyan);
        opacity: 0.6;
        animation: undulate 4s ease-in-out infinite alternate-reverse;
    }
    .field-layer-3 {
        stroke: #fff;
        opacity: 0.3;
        animation: undulate 5s ease-in-out infinite alternate;
    }

    @keyframes fieldScroll {
        0% {
            transform: translateX(0);
        }
        100% {
            transform: translateX(-50%);
        }
    }

    @keyframes undulate {
        0% {
            transform: scaleY(0.8);
        }
        100% {
            transform: scaleY(1.2);
        }
    }

    /* Orb Specifics - Cleaned up */
    .deck-container.minimized .resonance-wave {
        /* Enforce 32x32 even in minimized mode */
        width: 32px;
        height: 32px;
        margin: 0;
    }

    .status-info {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .explorer-name {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: rgba(255, 255, 255, 0.4);
        margin-bottom: 2px;
    }

    .status-tag {
        font-size: 0.85rem;
        font-family: monospace;
        color: var(--accent-cyan);
        text-shadow: 0 0 8px rgba(6, 182, 212, 0.4);
        letter-spacing: 0.05em;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Prevent wrapping on desktop but allow on mobile */
    @media (min-width: 768px) {
        .status-tag {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: normal; /* allow wrapping up to 2 lines */
            max-width: 320px;
        }
    }

    .click-hint {
        font-size: 0.7rem;
        opacity: 0.6;
        font-weight: 400;
        margin-left: 0.5rem;
        color: rgba(255, 255, 255, 0.7);
    }

    .status-tag::after {
        content: "";
        display: inline-block;
        margin-left: 4px;
        width: 6px;
        height: 6px;
        background: currentColor;
        border-radius: 50%;
        animation: blink 2s infinite;
    }

    @keyframes blink {
        0%,
        100% {
            opacity: 0.2;
        }
        50% {
            opacity: 1;
        }
    }

    /* Minimize Button Polish */
    :global(.icon-btn.minimize-btn) {
        opacity: 0.6;
        border: 1px solid transparent;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    :global(.icon-btn.minimize-btn:hover) {
        opacity: 1;
        color: var(--accent-cyan);
        background: rgba(6, 182, 212, 0.05);
        border-color: rgba(6, 182, 212, 0.2);
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.1);
        transform: translateY(1px);
    }

    .controls-hint {
        margin-left: auto;
        display: flex; /* Flex for buttons */
        gap: 0.5rem; /* Space between buttons */
        align-items: center;
    }

    /* Expanded View */
    .deck-expansion {
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        flex-direction: column;
        height: 500px; /* Taller */
        max-height: 70vh;
    }

    .chat-viewport {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden; /* Fix horizontal scroll */
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem; /* More spacing */
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        overscroll-behavior: contain; /* Prevent parent scroll */
    }

    .welcome {
        text-align: center;
        padding: 2rem 1rem;
        color: rgba(255, 255, 255, 0.5);
    }

    .welcome h3 {
        color: #fff;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    .welcome p {
        font-size: 0.85rem;
        line-height: 1.5;
    }

    .msg {
        display: flex;
        max-width: 85%;
    }
    .msg.user {
        align-self: flex-end;
    }
    .msg.model {
        align-self: flex-start;
    }

    .model .msg-bubble {
        background: rgba(255, 255, 255, 0.05); /* Slight tint */
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top-left-radius: 2px;
    }

    .whisper-bubble {
        position: absolute;
        bottom: 100%;
        left: 2rem;
        margin-bottom: 0.5rem;
        background: var(--accent-violet);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        border-bottom-left-radius: 2px;
        font-size: 0.8rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        max-width: 200px;
        animation: float 3s ease-in-out infinite;
        z-index: 10000;
        pointer-events: none;
    }

    @keyframes float {
        0%,
        100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-5px);
        }
    }
    .msg-bubble {
        padding: 0.75rem 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .user .msg-bubble {
        background: var(--accent-violet); /* Used accent color */
        color: #fff;
        border-bottom-right-radius: 2px;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
    }

    .model .msg-bubble {
        background: rgba(255, 255, 255, 0.05);
        color: #ddd;
        border-bottom-left-radius: 2px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Reduce gap between consecutive Lina messages */
    .msg.model + .msg.model {
        margin-top: -1rem; /* Visual grouping */
    }

    .input-area {
        padding: 1rem;
        display: flex;
        gap: 0.5rem;
        background: rgba(0, 0, 0, 0.2);
    }

    .input-area input {
        flex: 1;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.6rem 1rem;
        color: #fff;
        font-size: 0.9rem;
    }

    .input-area input:focus {
        outline: none;
        border-color: #0070f3;
    }

    .input-area button {
        background: #0070f3;
        color: #fff;
        border: none;
        padding: 0 1.25rem;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.75rem;
        cursor: pointer;
    }

    .input-area button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    @media (max-width: 768px) {
        .resonance-wrapper {
            bottom: 0;
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* Ensure shifted state works on mobile */
        .resonance-wrapper.shifted {
            bottom: 8rem; /* Keep checking if this is enough */
        }

        .deck-container {
            border-radius: 16px 16px 0 0;
            border-bottom: none;
        }

        .deck-expansion {
            /* On mobile, take up more space, but leave room for header */
            height: 80vh;
            max-height: 80vh;
        }

        /* Adjust for when keyboard is open if possible, though strict vh is safest start */

        /* Ensure 44px touch targets on mobile for all icon buttons */
        :global(.icon-btn) {
            min-width: 44px !important;
            min-height: 44px !important;
            margin: 2px; /* Prevent stacking overlap */
        }

        /* Specific overrides for minimized orb on mobile */
        :global(.icon-btn.minimize-btn) {
            min-width: 44px !important;
            min-height: 44px !important;
        }
    }

    /* --- Markdown Styles --- */
    :global(.markdown-body) {
        font-family: inherit;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    :global(.markdown-body p) {
        margin-bottom: 0.5rem;
    }
    :global(.markdown-body strong) {
        color: #fff;
        font-weight: 600;
    }
    :global(.markdown-body code) {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.2em 0.4em;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85em;
    }
    :global(.markdown-body pre) {
        background: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        margin: 0.5rem 0;
    }
    :global(.markdown-body ul, .markdown-body ol) {
        margin-left: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* --- TTS Button --- */
    /* --- TTS & Copy Buttons --- */
    .msg-content-wrapper {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
        align-items: flex-start;
        max-width: 100%;
        position: relative;
    }

    .msg-header {
        display: flex;
        justify-content: flex-end; /* Top Right */
        width: 100%;
        margin-bottom: -0.5rem;
        z-index: 2;
        pointer-events: none; /* Let clicks pass through empty space */
    }

    .msg-footer {
        display: flex;
        justify-content: flex-end; /* Bottom Right */
        width: 100%;
        margin-top: -0.5rem;
        z-index: 2;
        pointer-events: none;
    }

    .msg-actions {
        pointer-events: auto;
    }

    .icon-btn {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        cursor: pointer;
        color: #ccc;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        pointer-events: auto;
    }

    /* TTS Toggle in Footer */
    :global(.tts-toggle) {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        cursor: pointer;
        opacity: 0.7;
        font-size: 0.7rem;
        transition: opacity 0.2s;
        border-left: 1px solid rgba(255, 255, 255, 0.1);
        padding-left: 0.8rem;
        user-select: none;
    }
    :global(.tts-toggle:hover) {
        opacity: 1;
        color: var(--accent-cyan);
    }
    :global(.tts-toggle input) {
        cursor: pointer;
        accent-color: var(--accent-cyan);
    }
    .icon-btn.loading {
        cursor: wait;
        opacity: 0.7;
    }
    .icon-btn.loading svg {
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
    .icon-btn.loading {
        cursor: wait;
        opacity: 0.7;
    }
    .icon-btn.loading svg {
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
    .icon-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
        transform: scale(1.05);
    }

    .tts-btn {
        margin-right: 0.5rem; /* Offset from right edge */
    }
    .copy-btn {
        margin-right: 0.25rem;
    }

    .copy-check {
        display: none;
        font-size: 0.8rem;
        color: #4cd964;
    }

    /* Copy Feedback State */
    :global(.copy-btn.copied svg) {
        display: none;
    }
    :global(.copy-btn.copied .copy-check) {
        display: block;
    }

    .controls-hint {
        margin-left: auto; /* Push to right */
        font-family: var(--font-mono, monospace);
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        color: rgba(255, 255, 255, 0.4);
        font-weight: 700;
        text-transform: uppercase;
    }

    /* Retry Controls */
    .retry-controls {
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: rgba(255, 200, 0, 0.1);
        border: 1px solid rgba(255, 200, 0, 0.3);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #ffda6b;
    }

    .retry-actions {
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .auto-retry-label {
        display: flex;
        gap: 0.3rem;
        align-items: center;
        cursor: pointer;
    }

    .retry-btn {
        background: rgba(255, 200, 0, 0.2);
        border: 1px solid rgba(255, 200, 0, 0.5);
        color: #ffda6b;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
    }

    .retry-btn:hover {
        background: rgba(255, 200, 0, 0.3);
    }
    /* Floating Audio Controls */
    .floating-controls {
        position: absolute;
        bottom: 5rem; /* Above input area */
        left: 50%;
        transform: translateX(-50%);
        z-index: 100;
        pointer-events: auto;
    }

    .stop-audio-btn {
        background: rgba(255, 50, 50, 0.2);
        border: 1px solid rgba(255, 50, 50, 0.4);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        color: #ffcccc;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.2s;
        cursor: pointer;
    }
    .stop-audio-btn:hover {
        background: rgba(255, 50, 50, 0.3);
        transform: scale(1.05);
    }

    .orb-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(139, 92, 246, 0.3);
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.1);
        overflow: hidden; /* Mask the square SVG */
    }

    /* Adjust the wave container inside the orb */
    .resonance-wave.orb-mode {
        width: 100%;
        height: 100%;
        transform: scale(1.5); /* slight zoom to fill circle */
    }
    .equalizer-icon {
        display: flex;
        gap: 2px;
        align-items: center;
        height: 12px;
    }
    .equalizer-icon .bar {
        width: 3px;
        background: currentColor;
        border-radius: 1px;
        animation: eq-bounce 0.5s infinite ease-in-out;
    }
    .equalizer-icon .bar:nth-child(2) {
        animation-delay: 0.1s;
        height: 12px;
    }
    .equalizer-icon .bar:nth-child(1) {
        animation-delay: 0.2s;
        height: 8px;
    }
    .equalizer-icon .bar:nth-child(3) {
        animation-delay: 0s;
        height: 10px;
    }

    @keyframes eq-bounce {
        0%,
        100% {
            height: 4px;
        }
        50% {
            height: 12px;
        }
    }

    /* Header Actions Polish */
    :global(.icon-btn.header-action) {
        width: 24px;
        height: 24px;
        padding: 4px;
        background: transparent;
        border: none;
        opacity: 0.6;
    }
    :global(.icon-btn.header-action:hover) {
        opacity: 1;
        background: rgba(255, 255, 255, 0.1);
        transform: scale(1.1);
    }
    :global(.icon-btn.header-action.close-btn:hover) {
        color: #ff6b6b;
        background: rgba(255, 107, 107, 0.1);
    }

    /* Tooltip Styles */
    :global(.icon-btn.minimize-btn) {
        opacity: 0.8;
    }
    :global(.icon-btn.minimize-btn:hover) {
        opacity: 1;
        color: var(--accent-cyan);
        background: rgba(6, 182, 212, 0.1);
        transform: scale(1.1);
    }
</style>
