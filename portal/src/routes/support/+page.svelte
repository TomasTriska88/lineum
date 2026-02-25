<script lang="ts">
    import { content } from "$lib/content";
    import { t } from "$lib/i18n";
</script>

<svelte:head>
    <title>{$t("nav.support")} | {$t("common.brand")}</title>
</svelte:head>

<div class="support-page">
    <div class="container narrow">
        <span class="label">Contribute</span>
        <h1>{content.support.title}</h1>
        <p class="subtitle">{content.support.subtitle}</p>

        <div class="content-block">
            <p>{content.support.description}</p>
        </div>

        <div class="goals-grid">
            {#each content.support.goals as goal}
                <div class="goal-card">
                    <h3>{goal.title}</h3>
                    <p>{goal.desc}</p>
                </div>
            {/each}
        </div>

        <div class="cta-section">
            <a
                href={content.support.cta_url}
                target="_blank"
                class="btn btn-primary btn-large"
            >
                {content.support.cta_label}
            </a>
            <p class="muted">Thank you for being part of this journey.</p>
        </div>
    </div>
</div>

<style>
    .support-page {
        padding-top: 8rem;
        padding-bottom: 8rem;
        min-height: 100vh;
    }

    .narrow {
        max-width: 800px;
    }

    .label {
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        color: var(--accent-color);
        margin-bottom: 1rem;
        display: block;
    }

    h1 {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }

    .subtitle {
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 3rem;
    }

    .content-block {
        font-size: 1.1rem;
        line-height: 1.8;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 4rem;
    }

    .goals-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1.5rem;
        margin-bottom: 4rem;
    }

    .goal-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .goal-card h3 {
        margin-bottom: 0.5rem;
        color: white;
    }

    .goal-card p {
        color: rgba(255, 255, 255, 0.5);
        margin: 0;
    }

    .cta-section {
        text-align: center;
        background: rgba(126, 184, 255, 0.05);
        padding: 4rem 2rem;
        border-radius: 12px;
        border: 1px solid rgba(126, 184, 255, 0.1);
    }

    .btn-large {
        padding: 1.25rem 3rem;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    .muted {
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.9rem;
    }

    @media (min-width: 768px) {
        .goals-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }
</style>
