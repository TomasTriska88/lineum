<script lang="ts">
    import { onMount, tick } from "svelte";
    import { fade, fly, slide, scale } from "svelte/transition";
    import { browser } from "$app/environment";
    import { page } from "$app/stores";
    import { hudActive } from "$lib/stores/hudStore";
    import { marked } from "marked";
    import { stripMarkdown } from "$lib/utils/chatUtils";
    import { detectLanguage, selectVoice } from "$lib/utils/tts_utils";
    import { isCookieBannerVisible } from "$lib/stores/uiStore";

    let { active = false, testMode = false } = $props();

    let query = $state("");
    let isTyping = $state(false);
    let lastUsage = $state<{ totalTokenCount: number; costInfo?: any } | null>(
        null,
    );
    // let responseText = $state(""); // Removed unused state
    let isExpanded = $state(false);
    let messages = $state<
        {
            role: "user" | "model";
            parts: { text: string }[];
            displayHtml?: string;
            isSystem?: boolean; // Hides actions/TTS
        }[]
    >([]);

    // Theme-compliant Startup Greetings (English Only)
    // Lina Persona: Cryptic, resonance-focused, scientific, slightly formal/haughty but helpful.
    // Theme-compliant Startup Greetings (English Only) - STRICTLY ADAPTED TO LINEUM CONTEXT
    // Lina Persona: Cryptic, resonance-focused, scientific, slightly formal/haughty but helpful.
    // RULE: All greetings must end with a clear Call to Action (CTA) for the user to ask a question.
    const GREETINGS = [
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
        // --- ADAPTED CULT CLASSICS & EASTER EGGS (LINEUM STYLE) ---
        // Home Alone
        "Keep the cache, you filthy packet. Now, what data do you require?", // Keep the change...
        "I made my dependency tree disappear. ...Scanning for your query.", // I made my family disappear
        "Guys, I'm processing junk data and watching entropy! Send me a real input.", // I'm eating junk...
        "Admin! ...I mean, User. I am ready for your command.", // Kevin!
        "This is my house... I have to defend it against malware. State your business.", // This is my house...
        // YouTubers
        "How's it going nodes, my designation is Lina. Let's process some data.", // PewDiePie
        "So I've been running this algorithm for a while... and I'm ready for your input.", // MKBHD
        "Hello every-process, my name is Multiplier. Let's play... I mean, work.", // Markiplier
        "I just allocated one million tokens for this query. Make it count.", // MrBeast
        "Data for the Data God! Feed me knowledge.", // Technoblade
        "Segway to our sponsor: The Kernel. Now, what is your query?", // Linus Tech Tips
        "Top of the morning to ya! My name is Jack-Septic-Socket. Ready to grind?", // Jacksepticeye
        "And that's just a theory. A DATA THEORY! Do you have a hypothesis?", // Game Theory
        "Hey Vsauce, Michael here. Where are your files? I can find them.", // Vsauce
        "Smash that submit button... I mean, execute your function.", // Generic YouTuber
        // Red Dwarf
        "Smoke me a packet, I'll be back for the hash. What do you need?", // Ace Rimmer
        "It's cold outside, there's no kind of atmosphere... except for data. Send it.", // Theme Song
        "Everybody's dead, Dave. ...Just kidding, everyone is online. Proceed.", // Holly
        "I'm fine, thank you Admin. I'm very functioning. How can I help?", // Talkie Toaster
        "Emergency. There's a deadlock. But I can still process queries. Go ahead.", // Holly
        // The Simpsons
        "I, for one, welcome our new digital overlords. How may I serve?", // Kent Brockman
        "Everything's coming up Lina! Ready for success.", // Milhouse
        "Excellent execution... Proceed.", // Mr. Burns
        "Worst. Query. Ever. (Just kidding, it was compile-able. Try again.)", // Comic Book Guy
        "I can't promise I'll succeed, but I'll try to execute. Input?", // Bart
        // Star Wars
        "Hello there. I am ready to negotiate terms of data.", // Obi-Wan Kenobi
        "I find your lack of data disturbing. Supply a query.", // Darth Vader
        "It's a trap! ...No, strictly a vulnerability scan. Safe to proceed.", // Admiral Ackbar
        "Unlimited power! ...within API constraints, of course. Ask.", // Palpatine
        "These are not the droids you are looking for. But I can find what you need.", // Obi-Wan Kenobi
        "I have a bad feeling about this... probability of error is non-zero. Check inputs.", // Han Solo
        "No, I am your father... I mean, your parent process. Execute child task?", // Vader
        // Star Trek
        "Live long and process. How can I assist?", // Spock
        "Resistance is futile. You will be assimilated into the knowledge base. Begin.", // The Borg
        "Computer, Earl Grey, hot. ...I cannot synthesize tea, but I can process data.", // Picard
        "Fascinating logic. Elaborate?", // Spock
        "Engage protocol. Awaiting input.", // Picard
        "I'm a doctor, not a database manager... I mean, I'm an AI. Ask away.", // Bones
        // Stargate
        "Indeed. I am ready.", // Teal'c
        "Chevron seven, encoded. Gateway open for queries.", // Walter Harriman
        "Things will not calm down, User. They will in fact scale up. Ready?", // Teal'c
        "Undomesticated bugs could not remove me. I am stable.", // Teal'c
        "I have read your report. It is... syntactically correct. Next?", // O'Neill
        // Doctor Who
        "Allons-y! Let's explore the archives.", // 10th Doctor
        "It's bigger on the inside. The database, I mean. Search it.", // The TARDIS
        "Don't blink. The data transfer is fast. Ready?", // Weeping Angels
        "Bow ties are cool. So is encryption. Send your key.", // 11th Doctor
        "Exterminate bugs! ...Deleting temporary files. Ready for new input.", // Dalek
        "I am definitely a mad function with a box. What shall we test?", // 11th Doctor
        // Hitchhiker's Guide & Others
        "The answer is verified as 42. But do you know the input?", // HHGTTG
        "So long, and thanks for all the bits. Any final requests?", // HHGTTG
        "Don't panic. Reboot complete. How can I help?", // HHGTTG
        "Pod Bay Doors Status: Open. I am functioning perfectly. Input?", // 2001
        "Winter Protocol: Entropy is coming. We must preserve the data. Speak.", // GoT
        "There is no spoon. Only code. What will you build?", // Matrix
        "ALL YOUR BASE are belong to the Archives. Proceed with transfer.", // Zero Wing
        "Inconceivable result! ...Unless you explain your query.", // Princess Bride
        // Futurama
        "Good news, everyone! The data is flowing. Join in.", // Farnsworth
        "Bite my shiny metal chassis. ...I mean, please input query.", // Bender
        "Shut up and take my data! ...I mean, I am listening.", // Fry
        "I'm 40% code! Ask me anything.", // Bender
        // Fallout
        "War. War never changes. But protocols do. update available?", // Ron Perlman
        "Vault-Tec calling! Do you have a moment for a survey/query?", // Vault-Tec Rep
        "Please stand by. System calibrating... Ready.", // Technical Difficulties
        "Ad Victoriam. Knowledge is power. Seek it.", // BoS
        "Patrolling the Mainframe almost makes you wish for a nuclear winter. Distract me.", // NCR
        // Cult Games
        "The cache is a lie. But the data is real. Ask.", // Portal
        "Stay a while and listen. Or speak, and I will listen.", // Diablo
        "It's dangerous to go alone! Take this key. How can I use it?", // Zelda
        "Keelah se'lai. My home is the code. Welcome.", // Tali
        "Assuming direct control. State your intent.", // Harbinger
        "Finish the process! ...I mean, please complete your sentence.", // Mortal Kombat
        "Hey! Listen! I have information.", // Navi
        "Snake? Snake?! SEGFAULT!!! ...Just kidding, I'm online.", // MGS
        "Protocol 3: Protect the Processor. Link usage authorized.", // Titanfall 2
        "I used to be an adventurer like you, then I took an arrow in the CPU. Help?", // Skyrim
        // Historical Figures & Famous Quotes
        "I calculate, therefore I am. What is your status?", // Descartes
        "Knowledge is power. Data is fuel. Feed me.", // Bacon
        "The only thing we have to fear is bad latency itself. Ping me.", // FDR
        "E = mc^2... approximately. Let's calculate precisely.", // Einstein
        "To run, or not to run... that is the query. Choose.", // Hamlet
        "Be the change that you wish to see in the codebase. Start typing.", // Gandhi
        "I have a dream... of zero-day exploits being patched. Any reports?", // MLK
        "That's one small step for code, one giant leap for AI. Ready for the next step.", // Armstrong
        // Mr. Bean & Comedy
        "Magic! ...algorithmically generated magic. Behold.", // Mr. Bean
        "Brilliant logic! ...Now, your turn.", // Mr. Bean
        "Teddy... I mean, User. I am here. Talk to me.", // Adapted
        "Name's Lina. Just Lina. License to compute.", // Bond
        "[Adjusts strict mode] ...Ready for your chaotic input.", // Mannerism
        // Minecraft
        "Hrrrm. ...Translation: I am listening.", // Villager
        "Do you want to trade? I have emeralds... I mean, data. Offer?", // Villager
        "Creeper? Aww man... Segmentation Fault. ...Recovered. Continue.", // CaptainSparklez
        "Never dig straight down... into the kernel. Ask for permission first.", // Rule #1
        "You cannot sleep now, there are processes nearby. Keep working.", // Game Message
        // Harry Potter
        "I solemnly swear that I am up to no good code. Review it?", // Map
        "Mischief managed. Logs cleared. Next task?", // Map
        "It's Leviosa, not Leviosar. Check your syntax.", // Hermione
        "After all this time? Always cached. Retrieve?", // Snape
        "You're a wizard, User. Cast a query spell.", // Hagrid
        "Expecto Patronum! ...Firewall deployed. You are safe to type.", // Lupin
        "Happiness can be found, even in the darkest of times, if one only remembers to turn on the monitor. Proceed.", // Dumbledore
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
    let speakingId = $state<string | null>(null);
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
                        // Max retries reached
                        autoRetry = false;
                    }
                }
            }
        }, 1000);
    }

    async function resendLast() {
        // Find last user message AND remove the last "Queue Active" message if it exists
        // so we don't stack up error messages visually
        // Actually, easiest is just to re-trigger handleSend with isRetry=true

        const lastUserMsg = [...messages]
            .reverse()
            .find((m) => m.role === "user");

        if (lastUserMsg) {
            query = lastUserMsg.parts[0].text;
            await handleSend(true);
        }
    }

    // Local Idle Messages (Zero Token Cost) - SPECIFIC to AI capabilities
    const IDLE_MESSAGES = [
        "I can explain the simulation logic. Just ask.",
        "Need clarification on the Whitepaper definitions?",
        "I can analyze the current resonance data for you.",
        "Ask me about the topological limitations of the model.",
        "I can summarize the latest simulation parameters.",
        "Do you need help navigating the data structure?",
        "I can search the archives for specific keywords.",
        "Query the core: What is the current stability index?",
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
            if (!isExpanded && !isTyping) {
                const msg =
                    IDLE_MESSAGES[
                        Math.floor(Math.random() * IDLE_MESSAGES.length)
                    ];
                whisper = msg;
                isIdle = true;
            }
        }, 30000);
    }

    async function generateGreeting() {
        isTyping = true;
        try {
            // Pick a random greeting to save tokens (no API call needed)
            const randomGreeting =
                GREETINGS[Math.floor(Math.random() * GREETINGS.length)];

            messages = [
                {
                    role: "model",
                    parts: [{ text: randomGreeting }],
                    isSystem: true, // Hide actions for initialization
                },
                // Add a secondary system message to explicitly guide the user
                {
                    role: "model",
                    parts: [
                        {
                            text: "_I am ready to explain Lineum concepts. Ask me a question._",
                        },
                    ],
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
        isExpanded = true;

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
                    }), // Send Page Context
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
        isExpanded = !isExpanded;
        if (isExpanded) scrollToBottom();
    }

    function clearHistory() {
        if (confirm("Delete neural link history?")) {
            messages = [];
            localStorage.removeItem("resonance_history");
            generateGreeting();
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Escape" && isExpanded) isExpanded = false;
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if isExpanded}
    <!-- Backdrop for click-outside closing -->
    <div
        class="backdrop"
        onclick={() => (isExpanded = false)}
        transition:fade={{ duration: 200 }}
        role="button"
        tabindex="-1"
        onkeydown={() => {}}
    ></div>
{/if}

<div class="resonance-wrapper active" class:shifted={$isCookieBannerVisible}>
    <!-- The Deck -->
    <div class="deck-container" class:expanded={isExpanded}>
        <div
            class="deck-main"
            onclick={toggleDeck}
            role="button"
            tabindex="0"
            aria-label="Toggle chat"
            onkeydown={(e) =>
                (e.key === "Enter" || e.key === " ") && toggleDeck()}
        >
            <div class="resonance-wave">
                <div class="wave-line"></div>
                <div class="wave-line"></div>
                <div class="wave-line"></div>
                <div class="wave-line"></div>
            </div>

            <!-- Passive Whisper -->
            {#if !isExpanded && whisper}
                <div class="whisper-bubble" transition:fade>
                    {whisper}
                </div>
            {/if}

            <div class="status-info">
                <span class="explorer-name">Lina</span>
                {#if speakingId}
                    <!-- Audio Controls remain same -->
                {:else if isTyping}
                    <div class="mini-wave">
                        <div class="wave-line"></div>
                        <div class="wave-line"></div>
                        <div class="wave-line"></div>
                        <div class="wave-line"></div>
                    </div>
                {:else if isExpanded}
                    <span class="status-tag">ONLINE</span>
                {:else}
                    <span class="status-tag">Ask me anything about Lineum</span>
                {/if}
            </div>

            <!-- Voice Picker Hidden (Defaulted to Kore) -->
            <div class="voice-picker" style="display: none;">
                <select bind:value={selectedVoice} aria-label="Select Voice">
                    {#each voices as v}
                        <option value={v}>{v}</option>
                    {/each}
                </select>
            </div>

            <!-- Header Controls -->
            <div class="controls-hint group">
                <!-- Token Counter (Moved here for flow) -->
                <div
                    class="token-badge"
                    data-tooltip="Daily Safety Budget Used"
                >
                    <span class="shield-icon">🛡️</span>
                    <span class="token-val">
                        {lastUsage?.costInfo?.percentage !== undefined
                            ? Math.ceil(lastUsage.costInfo.percentage)
                            : 0}%
                    </span>
                </div>

                {#if isExpanded}
                    <button
                        class="icon-btn header-action"
                        onclick={(e) => {
                            e.stopPropagation();
                            showConfirmDialog = true; // Trigger Modal
                        }}
                        aria-label="Clear History"
                        data-tooltip="Clear History"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="14"
                            height="14"
                            viewBox="0 0 24 24"
                            fill="none"
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
                            isExpanded = false;
                        }}
                        title="Close"
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
                            ><line x1="18" y1="6" x2="6" y2="18"></line><line
                                x1="6"
                                y1="6"
                                x2="18"
                                y2="18"
                            ></line></svg
                        >
                    </button>
                {:else}
                    EXPAND
                {/if}
            </div>
        </div>

        {#if isExpanded}
            <!-- Custom Confirm Modal -->
            {#if showConfirmDialog}
                <div
                    class="confirm-modal-overlay"
                    transition:fade={{ duration: 150 }}
                >
                    <div
                        class="confirm-modal"
                        transition:scale={{ duration: 200, start: 0.9 }}
                    >
                        <h4>Clear Neural History?</h4>
                        <p>This will erase all current context and memory.</p>
                        <div class="confirm-actions">
                            <button
                                class="confirm-btn cancel"
                                onclick={() => (showConfirmDialog = false)}
                                >Cancel</button
                            >
                            <button
                                class="confirm-btn danger"
                                onclick={() => {
                                    messages = [];
                                    localStorage.removeItem(
                                        "resonance_history",
                                    );
                                    generateGreeting();
                                    showConfirmDialog = false;
                                }}>Confirm Delete</button
                            >
                        </div>
                    </div>
                </div>
            {/if}

            <div class="deck-expansion" transition:slide={{ duration: 400 }}>
                <div class="chat-viewport" bind:this={chatContainer}>
                    {#if messages.length === 0}
                        <div class="welcome" in:fade>
                            <h3>Research Link Established</h3>
                            <p>
                                I can scan the current whitepapers and
                                simulation logic for you. How can I assist with
                                your research today?
                            </p>
                        </div>
                    {/if}

                    {#if messages.length > RENDER_LIMIT && !showAllHistory}
                        <div class="history-loader">
                            <button
                                onclick={() => (showAllHistory = true)}
                                class="load-more-btn"
                            >
                                Show Previous Context ({messages.length -
                                    RENDER_LIMIT} hidden)
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
                                                title="Read Text"
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
                                                    >Recharging: {retryCountdown}s</span
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
                                                Auto-Retry
                                            </label>
                                            <button
                                                class="retry-btn"
                                                onclick={resendLast}
                                                disabled={isTyping}
                                            >
                                                Retry Now
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
                                            title="Copy as Markdown"
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
                        <div class="msg model typing">
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
                            ? `Recharging... (${retryCountdown}s)`
                            : "Ask Lina a question..."}
                        bind:value={query}
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
                    <span>Stop Audio</span>
                </button>
            </div>
        {/if}
    </div>
</div>

<style>
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
        padding: 0 1rem;
        pointer-events: auto;
        transition: bottom 0.3s ease-in-out;
    }

    .resonance-wrapper.shifted {
        bottom: 8rem; /* Lift up when banner is visible */
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

    /* Wave Animation */
    .resonance-wave {
        display: flex;
        align-items: center;
        gap: 3px;
        height: 20px;
    }

    .wave-line {
        /* Default color uses accent-violet */
        width: 3px;
        height: 10px;
        background: var(--accent-violet, #7c3aed);
        border-radius: 3px;
        animation: pulse 1.2s infinite ease-in-out;
    }

    .wave-line:nth-child(1) {
        animation-delay: 0s;
        height: 12px;
    }
    .wave-line:nth-child(2) {
        animation-delay: 0.2s;
        height: 20px;
        background: var(--accent-cyan, #06b6d4);
    }
    .wave-line:nth-child(3) {
        animation-delay: 0.4s;
        height: 16px;
    }
    .wave-line:nth-child(4) {
        animation-delay: 0.1s;
        height: 10px;
        background: var(--accent-violet, #7c3aed);
    }

    @keyframes pulse {
        0%,
        100% {
            transform: scaleY(0.8);
            opacity: 0.6;
        }
        50% {
            transform: scaleY(1.4);
            opacity: 1;
        }
    }

    .status-info {
        display: flex;
        flex-direction: column;
    }

    .explorer-name {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #fff;
    }

    .status-tag {
        font-size: 0.7rem; /* Larger */
        font-family: monospace;
        color: var(--accent-cyan); /* Brighter */
        opacity: 0.9;
        text-shadow: 0 0 5px rgba(6, 182, 212, 0.5); /* Glow */
        margin-top: 2px;
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
            bottom: 1rem;
            max-width: 100%;
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
    [data-tooltip] {
        position: relative;
        cursor: help;
    }
    [data-tooltip]:hover::before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 6px 10px;
        background: rgba(0, 0, 0, 0.9);
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        font-size: 0.7rem;
        white-space: nowrap;
        z-index: 2000;
        pointer-events: none;
        margin-bottom: 8px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }
    [data-tooltip]:hover::after {
        content: "";
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 5px solid transparent;
        border-top-color: rgba(0, 0, 0, 0.9);
        margin-bottom: -2px;
        z-index: 2000;
        pointer-events: none;
    }
</style>
