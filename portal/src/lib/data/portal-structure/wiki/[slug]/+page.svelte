<script lang="ts">
    import * as m from "$lib/paraglide/messages.js";
    import { marked } from "marked";
    export let data;
    const { content, title, slug } = data;

    let displayContent = "";
    let toc: { level: number; text: string; id: string }[] = [];

    $: {
        // Rewrite image paths from local markdown references to static serve paths
        let text = content
            .replace(
                /!\[(.*?)\]\(\.\.\/source\/(.*?)\)/g,
                "![$1](/data/source/$2)",
            )
            .replace(/src="\.\.\/source\/(.*?)"/g, 'src="/data/source/$1"');

        toc = [];
        const regex = /^(#{1,4})\s+(.+)$/gm;
        displayContent = text.replace(
            regex,
            (match: string, hashes: string, rawText: string) => {
                const level = hashes.length;
                const cleanText = rawText
                    .replace(/[*_`]/g, "")
                    .replace(/\{#.*?\}/g, "")
                    .trim();
                let id = cleanText
                    .toLowerCase()
                    .replace(/[^\w\s-]/g, "")
                    .replace(/\s+/g, "-");

                // Handle duplicate IDs
                let count = 1;
                let originalId = id;
                while (toc.find((t) => t.id === id)) {
                    id = `${originalId}-${count++}`;
                }

                toc.push({ level, text: cleanText, id });
                return `${hashes} <a id="${id}" class="anchor-offset"></a>${rawText}`;
            },
        );
    }
</script>

<svelte:head>
    <title>{title || m.nav_wiki()} — {m.common_brand()}</title>
</svelte:head>

<div class="wiki-container">
    <div class="container wrapper">
        <aside class="toc">
            <div class="toc-sticky">
                <a href="/wiki" class="back-link">&larr; Back to Wiki</a>
                <h3>On this page</h3>
                <ul>
                    {#if toc.length === 0}
                        <li><em>No sections found</em></li>
                    {/if}
                    {#each toc as item}
                        <li
                            style="margin-left: {(item.level - 1) *
                                1.25}rem; font-size: {item.level === 1
                                ? '1.05rem'
                                : '0.85rem'}; font-weight: {item.level === 1
                                ? '600'
                                : 'normal'}; margin-top: {item.level === 1
                                ? '0.75rem'
                                : '0'}"
                        >
                            <a href="#{item.id}">{item.text}</a>
                        </li>
                    {/each}
                </ul>
            </div>
        </aside>

        <article class="paper">
            <section class="card">
                <div class="paper-header">
                    {#if status === "Locked"}
                        <span
                            class="status-badge locked"
                            title="Structurally locked and validated"
                            >🔒 Locked</span
                        >
                    {:else if status === "Falsified"}
                        <span
                            class="status-badge falsified"
                            title="Mathematically or empirically disproven"
                            >❌ Falsified</span
                        >
                    {:else if status === "Retracted"}
                        <span
                            class="status-badge retracted"
                            title="Retracted hypothesis or dead end"
                            >🚫 Retracted</span
                        >
                    {:else}
                        <span
                            class="status-badge draft"
                            title="Working draft subject to revision"
                            >⚠️ Draft</span
                        >
                    {/if}
                </div>

                {#if status === "Falsified"}
                    <div class="draft-warning falsified">
                        <strong>Falsified Theory</strong>
                        <p>
                            This whitepaper details a theory or hypothesis that
                            has been explicitly mathematically or systemically
                            <b>disproven</b>. It is preserved here as a
                            documented dead end to prevent repeated research.
                        </p>
                    </div>
                {:else if status === "Retracted"}
                    <div class="draft-warning retracted">
                        <strong>Retracted Document</strong>
                        <p>
                            This whitepaper details a theory or hypothesis that
                            has been withdrawn or superseded. It is preserved
                            here for historical context and should not be
                            treated as part of the current Lineum canon.
                        </p>
                    </div>
                {:else if status !== "Locked"}
                    <div class="draft-warning">
                        <strong>Draft Document</strong>
                        <p>
                            This whitepaper is an active working draft and has
                            not been structurally locked or canonically
                            validated by the contract suite. Concepts and claims
                            herein are subject to active revision.
                        </p>
                    </div>
                {/if}

                <div class="prose">
                    {@html marked(displayContent)}
                </div>
            </section>
        </article>
    </div>
</div>

<style>
    .wiki-container {
        padding-top: 6rem;
        background: var(--bg-primary, #0a0a0f);
        color: var(--text-primary, #e0e0e8);
        min-height: 100vh;
    }

    .wrapper {
        display: grid;
        grid-template-columns: 220px minmax(0, 1fr);
        gap: 3rem;
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    .toc-sticky {
        position: sticky;
        top: 8rem;
        max-height: calc(100vh - 10rem);
        overflow-y: auto;
        padding-right: 1rem;
    }

    /* Scrollbar styling for TOC */
    .toc-sticky::-webkit-scrollbar {
        width: 4px;
    }
    .toc-sticky::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    .toc-sticky::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    .toc-sticky::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    .back-link {
        display: block;
        margin-bottom: 2rem;
        font-size: 0.9rem;
        color: var(--accent-color);
        text-decoration: none;
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

    .status-badge.draft {
        background: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.3);
    }

    .status-badge.retracted {
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.3);
    }

    .status-badge.falsified {
        background: rgba(186, 26, 26, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(255, 107, 107, 0.4);
        font-weight: 600;
    }

    .draft-warning {
        background: rgba(210, 153, 34, 0.05);
        border-left: 4px solid #d29922;
        padding: 1.5rem;
        margin-bottom: 2.5rem;
        border-radius: 0 8px 8px 0;
    }

    .draft-warning.retracted {
        background: rgba(248, 81, 73, 0.05);
        border-left: 4px solid #f85149;
    }

    .draft-warning.falsified {
        background: rgba(186, 26, 26, 0.1);
        border-left: 4px solid #ff6b6b;
    }

    .draft-warning strong {
        color: #d29922;
        display: block;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .draft-warning.retracted strong {
        color: #f85149;
    }

    .draft-warning.falsified strong {
        color: #ff6b6b;
    }

    .draft-warning p {
        color: rgba(255, 255, 255, 0.8);
        margin: 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    .toc h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 1.5rem;
        color: rgba(255, 255, 255, 0.35);
        font-family: var(--font-mono, "JetBrains Mono", monospace);
    }

    .toc ul {
        list-style: none;
        padding: 0;
    }

    .toc li {
        margin-bottom: 0.75rem;
    }

    .toc a {
        color: rgba(255, 255, 255, 0.45);
        font-size: inherit;
        text-decoration: none;
        transition: color 0.2s;
        font-family: var(--font-mono, monospace);
    }

    .toc a:hover {
        color: var(--accent-color, #7eb8ff);
    }

    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
    }

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
        color: var(--accent-color);
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

    :global(.prose) {
        max-width: 100%;
        overflow-x: hidden;
        overflow-wrap: break-word;
        word-wrap: break-word;
    }

    :global(.prose img) {
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        margin: 2rem 0;
    }

    :global(.prose li) {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }

    :global(.prose blockquote) {
        border-left: 3px solid var(--accent-color);
        padding: 0.5rem 0 0.5rem 1.5rem;
        margin: 2rem 0;
        background: rgba(126, 184, 255, 0.05);
        font-style: italic;
    }

    :global(.prose table) {
        width: 100%;
        border-collapse: collapse;
        margin: 2rem 0;
        font-size: 0.9rem;
    }

    :global(.prose th) {
        text-align: left;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.05);
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        color: white;
    }

    :global(.prose td) {
        padding: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.6);
    }

    :global(.prose code) {
        background: rgba(255, 255, 255, 0.08);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: var(--font-mono, monospace);
        font-size: 0.9em;
        color: #7eb8ff;
        word-break: break-word;
    }

    :global(.prose pre) {
        background: #050505;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 2rem 0;
        overflow-x: auto;
    }

    :global(.prose pre code) {
        background: transparent;
        padding: 0;
        color: #ccc;
    }

    @media (max-width: 1024px) {
        .wrapper {
            grid-template-columns: minmax(0, 1fr);
            padding: 1rem;
            min-width: 0;
        }
        .toc {
            display: none;
        }
        .card {
            padding: 1.5rem;
            min-width: 0;
            overflow-x: hidden;
        }
        :global(.prose h1) {
            font-size: 1.75rem;
        }
        :global(.prose h2) {
            font-size: 1.35rem;
        }
    }

    /* Anchor offset to account for fixed navbar */
    :global(.anchor-offset) {
        display: block;
        position: relative;
        top: -120px;
        visibility: hidden;
    }
</style>
