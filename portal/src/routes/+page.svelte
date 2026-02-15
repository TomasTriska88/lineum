<script lang="ts">
    import FieldShader from "$lib/components/FieldShader.svelte";
</script>

<svelte:head>
    <title>Lineum | Discrete Field Dynamics</title>
    <meta
        name="description"
        content="Official portal for the Lineum project. Discover the emergence of stable localized excitations in discrete field models."
    />
</svelte:head>

<section class="hero">
    <div class="shader-overlay">
        <FieldShader />
    </div>

    <div class="hero-content container">
        <div class="logo">
            <span class="logo-symbol">Λ</span>
            <span class="logo-text">Lineum</span>
        </div>
        <h1>Věda o polích, která dýchají.</h1>
        <p>
            Odkrýváme vznik stabilních excitací (Linonů) v diskrétních polích. <br
            /> Bez globálních konstant. Bez předdefinované metrické geometrie. Jen
            čistá lokální kauzalita.
        </p>
        <div class="cta-group">
            <a href="/wiki" class="btn btn-primary">Lineum Core v1.0.17</a>
            <a href="#evidence" class="btn btn-outline">Auditní Důkazy</a>
        </div>
    </div>
</section>

<section id="layman" class="info-section">
    <div class="container grid-2">
        <div class="text-block">
            <span class="label">Pro laiky</span>
            <h2>Co je to Lineum?</h2>
            <p>
                Představte si vesmír ne jako prázdnotu, ale jako jemnou
                digitální mřížku. Lineum je model, který ukazuje, jak se v tomto
                prostředí mohou "samy od sebe" vytvořit stabilní vlny, které se
                chovají jako částice.
            </p>
            <p>
                Není to jen simulace; je to hledání základních pravidel, ze
                kterých vzniká hmota.
            </p>
        </div>
        <div class="visual-placeholder">
            <!-- Future: Interactive Lottie or Simplified Canvas -->
            <div class="placeholder-box">Visual Metaphor</div>
        </div>
    </div>
</section>

<section id="scientist" class="info-section alternate">
    <div class="container">
        <span class="label">Pro vědce</span>
        <h2>Deep Science & Auditable Reality</h2>
        <div class="scientific-grid">
            <div class="card">
                <h3>Bílá Kniha (v1.0.17)</h3>
                <p>
                    Kompletní derivace rovnice, numerické schéma a interpretace
                    výsledků.
                </p>
                <a href="/wiki">Otevřít Wiki →</a>
            </div>
            <div class="card">
                <h3>Zenodo (DOI)</h3>
                <p>
                    Oficiální vědecký archiv s garantovanou dohledatelností dat.
                </p>
                <a
                    href="https://doi.org/10.5281/zenodo.16934359"
                    target="_blank">10.5281/zenodo...</a
                >
            </div>
            <div class="card">
                <h3>Audit Hub</h3>
                <p>
                    Každý run je ověřitelný. Transparentnost od prvního seedu.
                </p>
                <a href="/audits">Prohlédnout audity →</a>
            </div>
        </div>
    </div>
</section>

<footer class="container">
    <div class="footer-content">
        <p>© 2026 Lineum Project • lineum.io</p>
        <div class="footer-links">
            <a href="https://revolut.me/tomastriska" target="_blank"
                >Podpořit projekt (Revolut)</a
            >
            <a
                href="https://github.com/TomasTriska88/lineum-private"
                target="_blank">GitHub</a
            >
        </div>
    </div>
</footer>

<style>
    .hero {
        height: 100vh;
        display: flex;
        align-items: center;
        position: relative;
        overflow: hidden;
    }

    .shader-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
    }

    .hero-content {
        position: relative;
        z-index: 2;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .logo-symbol {
        font-size: 4rem;
        font-family: serif;
        background: linear-gradient(
            135deg,
            var(--accent-violet),
            var(--accent-cyan)
        );
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(124, 58, 237, 0.4));
    }

    .logo-text {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        color: white;
    }

    h1 {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        color: white;
    }

    p {
        font-size: 1.25rem;
        color: #aaa;
        max-width: 600px;
        margin-bottom: 2.5rem;
    }

    .cta-group {
        display: flex;
        gap: 1.5rem;
    }

    .btn {
        padding: 1rem 2rem;
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 0.1em;
        transition: all 0.3s;
    }

    .btn-primary {
        background-color: var(--accent-color);
        color: white;
    }

    .btn-outline {
        border: 1px solid var(--accent-color);
        color: var(--accent-color);
    }

    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    }

    .info-section {
        padding: 8rem 0;
    }

    .info-section.alternate {
        background: rgba(255, 255, 255, 0.02);
    }

    .label {
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        color: var(--accent-color);
        margin-bottom: 1rem;
        display: block;
    }

    h2 {
        font-size: 3rem;
        margin-bottom: 2rem;
    }

    .grid-2 {
        display: grid;
        grid-template-columns: 1.2fr 1fr;
        gap: 4rem;
        align-items: center;
    }

    .placeholder-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px dashed rgba(255, 255, 255, 0.2);
        height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #555;
    }

    .scientific-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        margin-top: 4rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.03);
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: border-color 0.3s;
    }

    .card:hover {
        border-color: var(--accent-color);
    }

    .card h3 {
        margin-bottom: 1rem;
    }

    .card p {
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    footer {
        padding: 4rem 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 4rem;
    }

    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #555;
        font-size: 0.9rem;
    }

    .footer-links {
        display: flex;
        gap: 2rem;
    }

    @media (max-width: 768px) {
        .logo-text {
            font-size: 3rem;
        }
        .grid-2 {
            grid-template-columns: 1fr;
        }
        .scientific-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
