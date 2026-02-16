<script>
    import "../app.css";
</script>

<nav>
    <div class="container nav-content">
        <a href="/" class="nav-logo">Lineum</a>
        <div class="nav-links">
            <a href="/wiki">Bílá Kniha</a>
            <a href="https://simulacrum.lineum.io">Simulakrum</a>
            <a href="#scientist">Pro vědce</a>
            <a href="https://revolut.me/tomastriska" class="nav-cta">Podpořit</a
            >
        </div>
    </div>
</nav>

<div class="grid-bg"></div>

<main>
    <slot />
</main>

<style>
    nav {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        padding: 1.5rem 0;
        z-index: 100;
        background: rgba(5, 5, 5, 0.8);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .nav-logo {
        font-weight: 700;
        font-size: 1.2rem;
        letter-spacing: -0.05em;
        color: white;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .nav-links a {
        font-size: 0.9rem;
        font-weight: 500;
        color: #aaa;
    }

    .nav-links a:hover {
        color: white;
    }

    .nav-cta {
        background: var(--accent-color);
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }

    main {
        position: relative;
        z-index: 1;
        padding-top: 64px;
    }
</style>
