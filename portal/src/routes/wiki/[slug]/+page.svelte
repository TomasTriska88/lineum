<script lang="ts">
    import { marked } from "marked";
    export let data;
    const { content, title, slug } = data;

    // Rewrite image paths from ../source/ to /source/
    $: processedContent = content
        .replace(/src="\.\.\/source\//g, 'src="/source/')
        .replace(/\(!\[(.*?)\]\)\(\.\.\/source\//g, "![$1](/source/");
</script>

<svelte:head>
    <title>{title || "Whitepaper"} — Lineum</title>
</svelte:head>

<div class="wiki-container">
    <div class="container wrapper">
        <aside class="toc">
            <div class="toc-sticky">
                <a href="/wiki" class="back-link">&larr; Back to Wiki</a>
                <h3>On this page</h3>
                <ul>
                    <li><a href="#top">Introduction</a></li>
                </ul>
            </div>
        </aside>

        <article class="paper">
            <section class="card">
                <div class="prose">
                    {@html marked(processedContent)}
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
    }

    .back-link {
        display: block;
        margin-bottom: 2rem;
        font-size: 0.9rem;
        color: var(--accent-color);
        text-decoration: none;
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
        font-size: 0.85rem;
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
            grid-template-columns: 1fr;
        }
        .toc {
            display: none;
        }
    }
</style>
