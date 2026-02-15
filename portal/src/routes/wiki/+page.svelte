<script lang="ts">
    import Paper from '$lib/whitepapers/lineum-core.md';
</script>

<div class="wiki-container">
    <div class="container wrapper">
        <aside class="toc">
            <div class="toc-sticky">
                <h3>Obsah</h3>
                <!-- Future: Computed TOC from head tags -->
                <ul>
                    <li><a href="#abstract">Abstract</a></li>
                    <li><a href="#introduction">Introduction</a></li>
                    <li><a href="#equation">The Equation</a></li>
                    <li><a href="#numerical">Numerical Scheme</a></li>
                </ul>
            </div>
        </aside>

        <article class="paper">
            <Paper />
        </article>
    </div>
</div>

<style>
    .wiki-container {
        padding-top: 6rem;
        background: #fafafa;
        color: #111;
        min-height: 100vh;
    }

    .wrapper {
        display: grid;
        grid-template-columns: 250px 1fr;
        gap: 4rem;
    }

    .toc-sticky {
        position: sticky;
        top: 8rem;
    }

    .toc h3 {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1.5rem;
        color: #888;
    }

    .toc ul {
        list-style: none;
    }

    .toc li {
        margin-bottom: 0.8rem;
    }

    .toc a {
        color: #555;
        font-size: 0.95rem;
    }

    .toc a:hover {
        color: var(--accent-color);
    }

    .paper {
        max-width: 800px;
        background: white;
        padding: 4rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05);
        border-radius: 4px;
        font-family: 'Inter', serif;
    }

    :global(.paper h1) { font-size: 2.5rem; margin-bottom: 2rem; border-bottom: 2px solid #eee; padding-bottom: 1rem; }
    :global(.paper h2) { font-size: 1.8rem; margin-top: 3rem; margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }
    :global(.paper p) { margin-bottom: 1.5rem; font-size: 1.1rem; line-height: 1.7; }
    :global(.paper pre) { background: #f4f4f4; padding: 1.5rem; border-radius: 4px; overflow-x: auto; margin-bottom: 2rem; font-family: var(--font-mono); }
    :global(.paper code) { background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
    :global(.paper table) { width: 100%; border-collapse: collapse; margin: 2rem 0; }
    :global(.paper th, .paper td) { border: 1px solid #ddd; padding: 1rem; text-align: left; }
    :global(.paper th) { background: #f9f9f9; }

    @media (max-width: 1024px) {
        .wrapper { grid-template-columns: 1fr; }
        .toc { display: none; }
    }
</style>
