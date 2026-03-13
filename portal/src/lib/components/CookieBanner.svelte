<script lang="ts">
    import { onMount } from "svelte";
    import { fade, fly } from "svelte/transition";
    import { isCookieBannerVisible } from "$lib/stores/uiStore";

    let visible = false;

    onMount(() => {
        const consent = localStorage.getItem("cookie_consent");
        if (!consent) {
            setTimeout(() => {
                visible = true;
                isCookieBannerVisible.set(true);
            }, 1000);
        }
    });

    function accept() {
        localStorage.setItem("cookie_consent", "accepted");
        visible = false;
        isCookieBannerVisible.set(false);
    }
</script>

{#if visible}
    <div class="cookie-banner" in:fly={{ y: 50, duration: 500 }} out:fade>
        <div class="content">
            <p>
                We use cookies to ensure you get the best experience on our
                website. By continuing to use the site, you agree to our <a
                    href="/privacy">Privacy Policy</a
                >.
            </p>
        </div>
        <div class="actions">
            <button on:click={accept}>Accept</button>
        </div>
    </div>
{/if}

<style>
    .cookie-banner {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(10, 10, 10, 0.95);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        z-index: 100000;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
    }

    .content p {
        margin: 0;
        color: #ccc;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    a {
        color: white;
        text-decoration: underline;
        font-weight: 500;
    }

    a:hover {
        color: var(--accent-color, #646cff);
    }

    button {
        background: white;
        color: black;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        border-radius: 4px;
        cursor: pointer;
        transition: transform 0.1s;
    }

    button:hover {
        transform: scale(1.05);
    }

    @media (max-width: 768px) {
        .cookie-banner {
            flex-direction: row; /* Keep row */
            align-items: center;
            padding: 0.75rem 1rem;
            gap: 1rem;
            justify-content: space-between;
        }

        .content p {
            font-size: 0.875rem;
            line-height: 1.3;
            text-align: left;
        }

        .actions {
            flex-shrink: 0;
        }

        button {
            padding: 0.4rem 1rem;
            font-size: 0.9rem;
        }
    }
</style>
