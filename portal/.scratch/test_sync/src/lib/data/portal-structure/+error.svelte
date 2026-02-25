<script lang="ts">
    import { page } from "$app/stores";
</script>

<div class="error-page">
    <div class="container">
        <span class="error-code">{$page.status}</span>
        <h1>{$page.error?.message || "Something went wrong"}</h1>
        <p>
            The requested resource could not be found or an unexpected error
            occurred.
        </p>
        <div class="actions">
            <a href="/" class="btn-primary">Back to Home</a>
            {#if $page.url.pathname.startsWith("/wiki")}
                <a href="/wiki" class="btn-secondary">Back to Wiki</a>
            {/if}
        </div>
    </div>
</div>

<style>
    .error-page {
        height: calc(100vh - 80px);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 0;
        background: var(--bg-primary, #0a0a0f);
        color: var(--text-primary, #e0e0e8);
        text-align: center;
    }

    .error-code {
        font-family: var(--font-mono, monospace);
        font-size: 5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-color, #7eb8ff), #fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: block;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    h1 {
        font-size: 2rem;
        margin-bottom: 2rem;
    }

    p {
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 3rem;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }

    .actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }

    .btn-primary,
    .btn-secondary {
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s;
        font-size: 0.9rem;
    }

    .btn-primary {
        background: var(--accent-color, #7eb8ff);
        color: var(--bg-primary, #0a0a0f);
    }

    .btn-primary:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }

    .btn-secondary {
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
    }

    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.05);
    }
</style>
