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
    const RENDER_LIMIT = 13;
    let showAllHistory = $state(false);

    let messagesToRender = $derived(
        showAllHistory ? messages : messages.slice(-RENDER_LIMIT),
    );

    let currentAudio: HTMLAudioElement | null = null;
    let speakingId = $state<string | null>(null);
    let audioCache = new Map<string, string>(); // msg index -> blob url

    // Voice Config
    const voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"];
    let selectedVoice = $state("Aoede");

    onMount(() => {
        if (browser) {
            const saved = localStorage.getItem("resonance_history");
            if (saved) {
                messages = JSON.parse(saved);
                // Inject Test Message if not present (skip in tests)
                if (import.meta.env.MODE !== "test") {
                    const last = messages[messages.length - 1];
                    const testTxt = `## 🔊 Audio System Test

**English Section:**
"Welcome to the Lineum research facility. The current status is: **Operational**."
"We are detecting specific field fluctuations."

**Czech Section (Česká sekce):**
"Vítejte. Teď vyzkoušíme výslovnost speciálních znaků."
"Rovnice: 3 * 4 = 12 (tři krát čtyři rovná se dvanáct)."
"Hodnoty: 0.012 (nula celá nula dvanáct) a 1,5 (jedna celá pět)."
"Symboly: α (alfa), Ω (omega), π (pí), Σ (suma)."
"Složitější: 10 * 5 = 50. Hvězdička (*) jako symbol."`;

                    if (!last || last.parts[0].text !== testTxt) {
                        messages = [
                            ...messages,
                            { role: "model", parts: [{ text: testTxt }] },
                        ];
                    }
                }
            } else {
                // Initial Test Message (Only if not in test mode)
                if (import.meta.env.MODE !== "test") {
                    messages = [
                        {
                            role: "model",
                            parts: [
                                {
                                    text: `## 🔊 Audio System Test

**English Section:**
"Welcome to the Lineum research facility. The current status is: **Operational**."
"We are detecting specific field fluctuations."

**Czech Section (Česká sekce):**
"Vítejte. Teď vyzkoušíme výslovnost speciálních znaků."
"Rovnice: 3 * 4 = 12 (tři krát čtyři rovná se dvanáct)."
"Hodnoty: 0.012 (nula celá nula dvanáct) a 1,5 (jedna celá pět)."
"Symboly: α (alfa), Ω (omega), π (pí), Σ (suma)."
"Složitější: 10 * 5 = 50. Hvězdička (*) jako symbol."`,
                                },
                            ],
                        },
                    ];
                }
            }
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
                    console.log(
                        `[SCROLL] Model response found. Element: ${last.tagName}, hasScrollIntoView: ${hasScroll}`,
                    );
                    if (hasScroll) {
                        try {
                            last.scrollIntoView({
                                behavior: "smooth",
                                block: "start",
                            });
                        } catch (e) {
                            console.error("[SCROLL] scrollIntoView failed:", e);
                        }
                    } else {
                        console.warn(
                            "[SCROLL] scrollIntoView missing on element.",
                        );
                    }
                } else {
                    console.log("[SCROLL] No model message to scroll to.");
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
                // 2. Asterisk Handling
                // "space * space" or "number * number" -> krát
                .replace(/(\d|\w)\s*\*\s*(\d|\w)/g, "$1 krát $2")
                // formatted bold/italic was already stripped in stripMarkdown, so remaining * are symbols
                .replace(/\*/g, "hvězdička")
                // 3. Greek & Special Symbols
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
        try {
            // Cache Key must include voice, otherwise switching voice plays old audio
            const id = `${index}-${selectedVoice}`;
            console.log(`[TTS] playTTS called for id ${id}`);
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
                console.log(
                    `[TTS] Requesting Cloud Audio. Voice: ${selectedVoice}, Text Length: ${text.length}`,
                );
                const res = await fetch("/api/tts", {
                    method: "POST",
                    body: JSON.stringify({ text, voice: selectedVoice }),
                    headers: { "Content-Type": "application/json" },
                });

                if (res.ok) {
                    const blob = await res.blob();
                    console.log(
                        `[TTS] Received Blob. Size: ${blob.size}, Type: ${blob.type}`,
                    );

                    if (blob.size < 100) {
                        console.warn(
                            "[TTS] Blob too small, likely error text.",
                        );
                        // Proceed to fallback
                    } else {
                        const url = URL.createObjectURL(blob);
                        audioCache.set(id, url);

                        currentAudio = new Audio(url);
                        currentAudio.onended = () => {
                            speakingId = null;
                        };
                        currentAudio.onerror = (e) => {
                            console.error("[TTS] Audio Playback Error:", e);
                            speakingId = null;
                        };
                        const playPromise = currentAudio.play();
                        if (playPromise !== undefined) {
                            playPromise.catch((error) => {
                                console.error(
                                    "[TTS] Playback Prevented/Failed:",
                                    error,
                                );
                                speakingId = null;
                            });
                        }
                        return;
                    }
                } else {
                    const errText = await res.text();
                    console.error(
                        `[TTS] API Error: ${res.status} - ${errText}`,
                    );
                }
            } catch (e) {
                console.warn(
                    "Cloud TTS failed, switching to local fallback.",
                    e,
                );
            }

            // 3. Fallback to Local Web Speech API
            console.log("[TTS] Switching to Local Fallback (Web Speech API).");
            const u = new SpeechSynthesisUtterance(text);
            u.lang = "cs-CZ";
            u.onend = () => {
                speakingId = null;
            };
            window.speechSynthesis.speak(u);
        } catch (err) {
            console.error("[TTS] Critical error in playTTS:", err);
        }
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

            <div class="voice-picker" onclick={(e) => e.stopPropagation()}>
                <select bind:value={selectedVoice} aria-label="Select Voice">
                    {#each voices as v}
                        <option value={v}>{v}</option>
                    {/each}
                </select>
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
                                        <div class="msg-actions top-right">
                                            <button
                                                class="icon-btn tts-btn"
                                                class:speaking={speakingId ===
                                                    `${index}-${selectedVoice}`}
                                                onclick={() =>
                                                    playTTS(
                                                        msg.parts[0].text,
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
                                        </div>
                                    </div>
                                {/if}
                                <div class="msg-bubble markdown-body">
                                    {@html marked.parse(msg.parts[0].text)}
                                </div>
                                {#if msg.role === "model"}
                                    <div class="msg-footer">
                                        <button
                                            class="icon-btn copy-btn"
                                            onclick={(e) => {
                                                const btn = e.currentTarget;
                                                copyToClipboard(
                                                    msg.parts[0].text,
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

    .voice-picker {
        margin-left: auto;
        margin-right: 1rem;
    }
    .voice-picker select {
        background: rgba(255, 255, 255, 0.05);
        color: #aaa;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        font-size: 0.7rem;
        padding: 2px 4px;
        cursor: pointer;
    }
    .voice-picker select:focus {
        outline: none;
        border-color: #0070f3;
    }

    .controls-hint {
        margin-left: 0; /* Reset since voice-picker pushes it */
    }
</style>
