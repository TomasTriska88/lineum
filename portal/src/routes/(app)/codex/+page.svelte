<script lang="ts">
    import * as m from "$lib/paraglide/messages.js";
    import { marked } from "$lib/utils/markdown";
    export let data;

    // The "One-Sentence" executive summary of the Codex
    const oneSentence =
        "Lineum is a purely scientific, deterministic computational framework strictly prohibiting casino, gambling, or mass-surveillance commercial applications.";
</script>

<svelte:head>
    <title>Ethical Codex — {m.common_brand()}</title>
</svelte:head>

<div class="codex-container">
    <div class="container wrapper">
        <article class="paper">
            <section class="card">
                <div class="paper-header">
                    <span
                        class="status-badge locked"
                        title="This standard represents the canonical behavior constraints of the foundation."
                        >🔒 Validated Standard</span
                    >
                </div>

                <div class="draft-warning codex-warning">
                    <strong>The One-Sentence Framework</strong>
                    <p>{oneSentence}</p>
                </div>

                <div class="prose">
                    {@html marked.parse(data.content)}
                </div>
            </section>
        </article>
    </div>
</div>

<style>
    .codex-container {
        padding-top: 6rem;
        background: var(--bg-primary, #0a0a0f);
        color: var(--text-primary, #e0e0e8);
        min-height: 100vh;
    }

    .wrapper {
        max-width: 900px; /* Tighter width for high-focus reading */
        margin: 0 auto;
        padding: 2rem;
    }

    .paper-header {
        margin-bottom: 2rem;
        display: flex;
        justify-content: flex-end;
    }

    .status-badge {
        font-size: 0.75rem;
        font-family: var(--font-mono, monospace);
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        display: inline-block;
    }

    .status-badge.locked {
        background: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.3);
    }

    .draft-warning {
        background: rgba(46, 160, 67, 0.05);
        border-left: 4px solid #3fb950;
        padding: 1.5rem;
        margin-bottom: 2.5rem;
        border-radius: 0 8px 8px 0;
    }

    .draft-warning strong {
        color: #3fb950;
        display: block;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .draft-warning p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
        line-height: 1.6;
        font-size: 1.05rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
    }

    /* Standard academic prose typography matching the Wiki */
    :global(.prose h1) {
        font-size: 2.2rem;
        margin-bottom: 2rem;
        color: white;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 1rem;
    }

    :global(.prose h2) {
        font-size: 1.6rem;
        margin-top: 3rem;
        margin-bottom: 1.5rem;
        color: var(--accent-color, #38bdf8);
    }

    :global(.prose h3) {
        font-size: 1.2rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: rgba(255, 255, 255, 0.9);
    }

    :global(.prose p) {
        line-height: 1.8;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 1.5rem;
    }

    :global(.prose ul, .prose ol) {
        margin-bottom: 1.5rem;
        padding-left: 1.5rem;
        color: rgba(255, 255, 255, 0.7);
    }

    :global(.prose li) {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }

    :global(.prose code) {
        background: rgba(255, 255, 255, 0.08);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: var(--font-mono, monospace);
        font-size: 0.9em;
        color: #38bdf8;
    }

    :global(.prose blockquote) {
        border-left: 3px solid var(--accent-color, #38bdf8);
        padding: 0.5rem 0 0.5rem 1.5rem;
        margin: 2rem 0;
        background: rgba(56, 189, 248, 0.05);
        font-style: italic;
    }

    @media (max-width: 1024px) {
        .wrapper {
            padding: 1rem;
        }
        .card {
            padding: 1.5rem;
        }
        :global(.prose h1) {
            font-size: 1.75rem;
        }
        :global(.prose h2) {
            font-size: 1.35rem;
        }
    }
</style>
