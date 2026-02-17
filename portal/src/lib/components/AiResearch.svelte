<script lang="ts">
    import { onMount } from "svelte";
    import { fade, fly } from "svelte/transition";

    export let title = "Lineum Intelligence";
    export let description =
        "Ask our AI guide anything about the Lineum project, from core whitepapers to research hypotheses.";

    let query = "";
    let isTyping = false;
    let messages: { role: "user" | "model"; parts: { text: string }[] }[] = [];
    let chatContainer: HTMLElement;

    onMount(() => {
        const saved = localStorage.getItem("lineum_research_history");
        if (saved) {
            messages = JSON.parse(saved);
        }
    });

    $: if (messages.length > 0) {
        localStorage.setItem(
            "lineum_research_history",
            JSON.stringify(messages),
        );
        scrollToBottom();
    }

    async function scrollToBottom() {
        if (chatContainer) {
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 10);
        }
    }

    async function handleSubmit() {
        if (!query.trim() || isTyping) return;

        const userMessage = query;
        query = "";

        const newMessages = [
            ...messages,
            { role: "user" as const, parts: [{ text: userMessage }] },
        ];
        messages = newMessages;
        isTyping = true;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages: messages }),
            });

            const data = await response.json();

            if (data.error) {
                messages = [
                    ...messages,
                    {
                        role: "model" as const,
                        parts: [
                            {
                                text: `✨ Explorer: I had a small hiccup! ${data.error}`,
                            },
                        ],
                    },
                ];
            } else {
                messages = [
                    ...messages,
                    { role: "model" as const, parts: [{ text: data.text }] },
                ];
            }
        } catch (err) {
            messages = [
                ...messages,
                {
                    role: "model" as const,
                    parts: [
                        {
                            text: "✨ Explorer: I've lost the resonance with the server. Please try again in a moment!",
                        },
                    ],
                },
            ];
        } finally {
            isTyping = false;
        }
    }

    function clearHistory() {
        messages = [];
        localStorage.removeItem("lineum_research_history");
    }
</script>

<section class="ai-research-card">
    <div class="glow-bg"></div>

    <div class="card-header">
        <div class="header-text">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        {#if messages.length > 0}
            <button class="clear-btn" on:click={clearHistory} transition:fade>
                Clear History
            </button>
        {/if}
    </div>

    <div class="chat-display" bind:this={chatContainer}>
        {#if messages.length === 0}
            <div class="empty-state" in:fade>
                <div class="bot-icon">✨</div>
                <p>
                    Greetings, researcher! I'm the Lineum Explorer. I've indexed
                    over 30 project files to help you dive deep into our
                    simulations.
                </p>
                <div class="suggestions">
                    <button
                        on:click={() => {
                            query =
                                "Explain Vortex-Particle duality like I'm five.";
                            handleSubmit();
                        }}>"Explain Vortex duality simply"</button
                    >
                    <button
                        on:click={() => {
                            query =
                                "What are the latest hypotheses in lineum-core?";
                            handleSubmit();
                        }}>"What are the latest hypotheses?"</button
                    >
                </div>
            </div>
        {/if}

        {#each messages as msg}
            <div
                class="message-wrapper {msg.role}"
                in:fly={{ y: 10, duration: 400 }}
            >
                <div class="message-icon">
                    {msg.role === "user" ? "👤" : "✨"}
                </div>
                <div class="message-bubble">
                    {msg.parts[0].text}
                </div>
            </div>
        {/each}

        {#if isTyping}
            <div class="message-wrapper model typing">
                <div class="message-icon">✨</div>
                <div class="message-bubble">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        {/if}
    </div>

    <form class="interaction-area" on:submit|preventDefault={handleSubmit}>
        <input
            type="text"
            placeholder="Search our research base or ask a question..."
            bind:value={query}
            disabled={isTyping}
        />
        <button
            type="submit"
            disabled={!query.trim() || isTyping}
            class="send-btn"
        >
            {#if isTyping}
                Thinking...
            {:else}
                Ask Explorer
            {/if}
        </button>
    </form>
</section>

<style>
    .ai-research-card {
        position: relative;
        background: rgba(15, 15, 15, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        margin: 4rem 0;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        min-height: 500px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }

    .glow-bg {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            circle at center,
            rgba(0, 112, 243, 0.1) 0%,
            transparent 50%
        );
        pointer-events: none;
        z-index: 0;
    }

    .card-header {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 2rem;
    }

    .header-text h2 {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #fff 0%, #aaa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }

    .header-text p {
        color: #888;
        margin: 0.5rem 0 0;
        font-size: 1.1rem;
        max-width: 500px;
    }

    .clear-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #666;
        padding: 0.5rem 1rem;
        border-radius: 99px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .clear-btn:hover {
        background: rgba(255, 0, 0, 0.1);
        color: #ff4d4d;
        border-color: rgba(255, 0, 0, 0.2);
    }

    .chat-display {
        position: relative;
        z-index: 1;
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
    }

    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
        color: #aaa;
        padding: 2rem;
    }

    .bot-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 0 15px rgba(0, 112, 243, 0.5));
    }

    .suggestions {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
        margin-top: 1.5rem;
    }

    .suggestions button {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #fff;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s;
    }

    .suggestions button:hover {
        background: var(--accent-color, #0070f3);
        transform: translateY(-2px);
    }

    .message-wrapper {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        max-width: 90%;
    }

    .message-wrapper.user {
        flex-direction: row-reverse;
        align-self: flex-end;
    }

    .message-icon {
        width: 36px;
        height: 36px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .message-bubble {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1rem 1.25rem;
        border-radius: 16px;
        color: #eee;
        line-height: 1.6;
        font-size: 1rem;
        white-space: pre-wrap;
    }

    .user .message-bubble {
        background: var(--accent-color, #0070f3);
        color: white;
        border: none;
        border-top-right-radius: 4px;
    }

    .model .message-bubble {
        border-top-left-radius: 4px;
        background: rgba(255, 255, 255, 0.03);
    }

    .interaction-area {
        position: relative;
        z-index: 1;
        display: flex;
        gap: 1rem;
    }

    .interaction-area input {
        flex: 1;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        color: white;
        font-size: 1.1rem;
        transition: all 0.2s;
    }

    .interaction-area input:focus {
        outline: none;
        background: rgba(255, 255, 255, 0.08);
        border-color: var(--accent-color, #0070f3);
        box-shadow: 0 0 20px rgba(0, 112, 243, 0.2);
    }

    .send-btn {
        background: var(--accent-color, #0070f3);
        color: white;
        border: none;
        padding: 0 2rem;
        border-radius: 16px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .send-btn:hover:not(:disabled) {
        transform: scale(1.02);
        filter: brightness(1.1);
    }

    .send-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Typing Animation */
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 5px 0;
    }

    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: #666;
        border-radius: 50%;
        animation: typing 1s infinite ease-in-out;
    }

    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes typing {
        0%,
        100% {
            transform: translateY(0);
            opacity: 0.5;
        }
        50% {
            transform: translateY(-5px);
            opacity: 1;
        }
    }

    @media (max-width: 768px) {
        .ai-research-card {
            padding: 1.5rem;
            margin: 2rem 0;
        }

        .header-text h2 {
            font-size: 1.5rem;
        }

        .interaction-area {
            flex-direction: column;
        }

        .send-btn {
            padding: 1rem;
        }
    }
</style>
