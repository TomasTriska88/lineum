<script lang="ts">
    import { onMount, tick } from "svelte";
    import { fade, fly, slide } from "svelte/transition";
    import { browser } from "$app/environment";
    import { page } from "$app/stores";
    import { hudActive } from "$lib/stores/hudStore";
    import { marked } from "marked";

    let { active = false } = $props();

    let query = $state("");
    let isTyping = $state(false);
    let responseText = $state("");
    let isExpanded = $state(false);
    let messages = $state<
        { role: "user" | "model"; parts: { text: string }[] }[]
    >([]);
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
    let audioCache = new Map<string, string>(); // msg index -> blob url

    onMount(() => {
        if (browser) {
            const saved = localStorage.getItem("resonance_history");
            if (saved) messages = JSON.parse(saved);
            scrollToBottom();
        }
    });

    $effect(() => {
        if (messages.length > 0 && browser) {
            localStorage.setItem("resonance_history", JSON.stringify(messages));

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
    });

    $effect(() => {
        if (isTyping) {
            scrollToBottom(); // Scroll to show loading indicator
        }
    });

    function scrollToBottom() {
        if (chatContainer) {
            tick().then(() => {
                chatContainer!.scrollTo({
                    top: chatContainer!.scrollHeight,
                    behavior: "smooth",
                });
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
                    last.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            });
        }
    }

    // --- TTS LOGIC ---
    function stripMarkdown(text: string): string {
        let clean = text
            .replace(/\*\*(.*?)\*\*/g, "$1") // Bold
            .replace(/\*(.*?)\*/g, "$1") // Italic
            .replace(/`+(.*?)`+/g, "$1") // Code
            .replace(/\[(.*?)\]\(.*?\)/g, "$1") // Links
            .replace(/[*#_`]/g, ""); // Cleanup leftovers

        return transliterateSymbols(clean);
    }

    function transliterateSymbols(text: string): string {
        return (
            text
                // 1. Decimals: 0.012 -> 0,012 (Czech standard)
                .replace(/(\d+)\.(\d+)/g, "$1,$2")
                // 2. Greek & Special Symbols
                .replace(/φ/g, "fí")
                .replace(/ψ/g, "psí")
                .replace(/Ω/g, "omega")
                .replace(/κ/g, "kappa")
                .replace(/=/g, "rovná se")
                .replace(/λ/g, "lambda")
                .replace(/Σ/g, "suma")
                .replace(/α/g, "alfa")
                .replace(/β/g, "beta")
                .replace(/γ/g, "gama")
                .replace(/Δ/g, "delta")
                .replace(/π/g, "pí")
                .replace(/μ/g, "mikro")
        );
    }

    function stopTTS() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        window.speechSynthesis.cancel();
        speakingId = null;
    }

    async function playTTS(rawText: string, index: number) {
        const id = index.toString();
        const text = stripMarkdown(rawText); // Clean visuals for audio

        if (speakingId === id) {
            stopTTS();
            return;
        }
        stopTTS();
        speakingId = id;

        // 1. Check Cache
        if (audioCache.has(id)) {
            const url = audioCache.get(id)!;
            currentAudio = new Audio(url);
            currentAudio.onended = () => {
                speakingId = null;
            };
            currentAudio.play();
            return;
        }

        // 2. Try Cloud TTS (Hybrid)
        try {
            const res = await fetch("/api/tts", {
                method: "POST",
                body: JSON.stringify({ text }),
                headers: { "Content-Type": "application/json" },
            });

            if (res.ok) {
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                audioCache.set(id, url);

                currentAudio = new Audio(url);
                currentAudio.onended = () => {
                    speakingId = null;
                };
                currentAudio.play();
                return;
            }
        } catch (e) {
            console.warn("Cloud TTS failed, switching to local fallback.", e);
        }

        // 3. Fallback to Local Web Speech API
        const u = new SpeechSynthesisUtterance(text);
        u.lang = "cs-CZ"; // Default to Czech as per user context, or detect? keeping explicit for consistency or use 'en-US' if text is english.
        // Simple heuristic: if text has typical czech chars? Or just let browser detect.
        // Actually best to set lang if we know it.
        u.onend = () => {
            speakingId = null;
        };
        window.speechSynthesis.speak(u);
    }

    function copyToClipboard(text: string) {
        if (browser) {
            navigator.clipboard.writeText(text);
        }
    }

    async function handleSend() {
        if (!query.trim() || isTyping) return;

        const userMsg = query;
        query = "";
        isTyping = true;
        isExpanded = true;

        const contextPath = $page.url.pathname;

        messages = [...messages, { role: "user", parts: [{ text: userMsg }] }];

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages, context: contextPath }), // Send Page Context
            });

            if (!res.ok) {
                console.error("Chat API Error:", res.status);
            }

            const data = await res.json();

            if (data.error) {
                messages = [
                    ...messages,
                    {
                        role: "model",
                        parts: [{ text: `✨ Explorer: ${data.error}` }],
                    },
                ];
            } else if (data.text) {
                messages = [
                    ...messages,
                    {
                        role: "model",
                        parts: [{ text: data.text }],
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
                            text: "✨ Explorer: Resonance lost. Try again later.",
                        },
                    ],
                },
            ];
        } finally {
            isTyping = false;
        }
    }

    function toggleDeck() {
        isExpanded = !isExpanded;
        if (isExpanded) scrollToBottom();
    }
</script>

<div class="resonance-wrapper active">
    <!-- The Deck -->
    <div class="deck-container" class:expanded={isExpanded}>
        <div
            class="deck-main"
            onclick={toggleDeck}
            role="button"
            tabindex="0"
            onkeydown={(e) =>
                (e.key === "Enter" || e.key === " ") && toggleDeck()}
        >
            <div class="resonance-wave">
                <div class="wave-line"></div>
                <div class="wave-line"></div>
                <div class="wave-line"></div>
            </div>

            <div class="status-info">
                <span class="explorer-name">Lineum Explorer</span>
                {#if speakingId}
                    <button
                        class="stop-btn-global"
                        onclick={(e) => {
                            e.stopPropagation();
                            stopTTS();
                        }}
                    >
                        ⏹️ STOP READING
                    </button>
                {:else if isTyping}
                    <span class="status-tag">ANALYZING FIELDS...</span>
                {:else if isExpanded}
                    <span class="status-tag">ACTIVE LINK</span>
                {:else}
                    <span class="status-tag">READY</span>
                {/if}
            </div>

            <div class="controls-hint">
                {isExpanded ? "CLOSE" : "EXPAND EXPLORER"}
            </div>
        </div>

        {#if isExpanded}
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
                                {#if msg.role === "model"}
                                    <div class="msg-header">
                                        <div class="msg-actions">
                                            <button
                                                class="icon-btn tts-btn"
                                                class:speaking={speakingId ===
                                                    index.toString()}
                                                onclick={() =>
                                                    playTTS(
                                                        msg.parts[0].text,
                                                        index,
                                                    )}
                                                aria-label="Read aloud"
                                                title="Read Text"
                                            >
                                                {#if speakingId === index.toString()}
                                                    ⏹️
                                                {:else}
                                                    🔊
                                                {/if}
                                            </button>
                                            <button
                                                class="icon-btn copy-btn"
                                                onclick={() =>
                                                    copyToClipboard(
                                                        msg.parts[0].text,
                                                    )}
                                                aria-label="Copy Markdown"
                                                title="Copy as Markdown"
                                            >
                                                📋
                                            </button>
                                        </div>
                                    </div>
                                {/if}
                                <div class="msg-bubble markdown-body">
                                    {@html marked.parse(msg.parts[0].text)}
                                </div>
                            </div>
                        </div>
                    {/each}
                    {#if isTyping}
                        <div class="msg model typing">
                            <div class="resonance-wave small">
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
                        placeholder="Ask the Explorer..."
                        bind:value={query}
                        onclick={(e) => e.stopPropagation()}
                        disabled={isTyping}
                    />
                    <button type="submit" disabled={!query.trim() || isTyping}>
                        LINK &rarr;
                    </button>
                </form>
            </div>
        {/if}
    </div>
</div>

<style>
    .resonance-wrapper {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        width: 100%;
        max-width: 600px;
        padding: 0 1rem;
        pointer-events: auto;
    }

    .deck-container {
        background: rgba(15, 15, 15, 0.7);
        backdrop-filter: blur(24px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        box-shadow:
            0 20px 50px rgba(0, 0, 0, 0.4),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
        pointer-events: auto;
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
        gap: 4px;
        height: 20px;
    }

    .wave-line {
        width: 3px;
        height: 10px;
        background: #0070f3;
        border-radius: 3px;
        animation: pulse 1.5s infinite ease-in-out;
    }

    .wave-line:nth-child(2) {
        animation-delay: 0.2s;
        height: 16px;
        background: #00c2ff;
    }
    .wave-line:nth-child(3) {
        animation-delay: 0.4s;
        height: 12px;
    }

    @keyframes pulse {
        0%,
        100% {
            transform: scaleY(1);
            opacity: 0.5;
        }
        50% {
            transform: scaleY(1.5);
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
        font-size: 0.6rem;
        font-family: monospace;
        color: #0070f3;
        opacity: 0.8;
    }

    .controls-hint {
        margin-left: auto;
        font-family: var(--font-mono, monospace);
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        color: rgba(255, 255, 255, 0.4);
        font-weight: 700;
        text-transform: uppercase;
    }

    /* Expanded View */
    .deck-expansion {
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        flex-direction: column;
        height: 400px;
    }

    .chat-viewport {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        scrollbar-width: none;
    }

    .welcome {
        text-align: center;
        padding: 2rem 1rem;
        color: #888;
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

    .msg-bubble {
        padding: 0.75rem 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .user .msg-bubble {
        background: #0070f3;
        color: #fff;
        border-bottom-right-radius: 2px;
    }

    .model .msg-bubble {
        background: rgba(255, 255, 255, 0.05);
        color: #ddd;
        border-bottom-left-radius: 2px;
        border: 1px solid rgba(255, 255, 255, 0.05);
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
        gap: 0.25rem;
        align-items: flex-start;
        max-width: 100%;
    }

    .msg-header {
        display: flex;
        justify-content: flex-start;
        width: 100%;
        padding-left: 0.5rem;
        margin-bottom: -0.25rem;
    }

    .msg-actions {
        display: flex;
        gap: 0.5rem;
        background: rgba(0, 0, 0, 0.3);
        padding: 0.2rem 0.5rem;
        border-radius: 8px 8px 0 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: none;
    }

    .icon-btn {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 0.85rem;
        opacity: 0.6;
        transition: all 0.2s;
        padding: 0.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .icon-btn:hover,
    .icon-btn.speaking {
        opacity: 1;
        transform: scale(1.1);
    }

    /* --- Small Wave for Typing --- */
    .resonance-wave.small {
        height: 12px;
        gap: 3px;
    }
    .resonance-wave.small .wave-line {
        width: 2px;
        background: rgba(255, 255, 255, 0.5);
    }

    /* --- Pagination --- */
    .history-loader {
        display: flex;
        justify-content: center;
        padding-bottom: 1rem;
    }
    .load-more-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.75rem;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.2s;
        min-height: 44px; /* Mobile touch target */
        display: flex;
        align-items: center;
    }
    .load-more-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
    }

    .stop-btn-global {
        background: rgba(255, 50, 50, 0.2);
        border: 1px solid rgba(255, 50, 50, 0.4);
        color: #ffcccc;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        cursor: pointer;
        animation: pulse 2s infinite;
        min-height: 32px; /* A bit smaller for header but accessible */
    }

    /* Scroll Containment */
    .chat-viewport {
        overscroll-behavior: contain;
    }
</style>
