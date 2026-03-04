<script lang="ts">
    import { onMount } from "svelte";

    let imprints: any[] = [];
    let loading = true;
    let errorMsg = "";

    // Default entity targeted in the backend
    let entityId = "lina";

    async function fetchImprints() {
        loading = true;
        errorMsg = "";
        try {
            const res = await fetch(
                `http://127.0.0.1:8000/entity/${entityId}/memory/imprints`,
            );
            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            imprints = data.imprints || [];
        } catch (err: any) {
            errorMsg = err.message || "Failed to fetch imprints.";
        } finally {
            loading = false;
        }
    }

    async function forgetImprint(imprint_id: string) {
        if (
            !confirm(
                "Are you sure you want to topologically subtract this imprint? This deterministic revert cannot be undone.",
            )
        )
            return;
        try {
            const res = await fetch(
                `http://127.0.0.1:8000/entity/${entityId}/memory/imprints/${imprint_id}`,
                {
                    method: "DELETE",
                },
            );
            if (!res.ok) throw new Error(await res.text());
            await fetchImprints();
        } catch (err: any) {
            alert("Failed to forget: " + err.message);
        }
    }

    onMount(() => {
        fetchImprints();
    });
</script>

<div class="journal-container">
    <div class="header-section">
        <h1>Memory Imprint Journal</h1>
        <p class="subtitle">
            Read-only audit of topological $\mu$ deformations and emergent
            affect states.
        </p>
    </div>

    <div class="controls">
        <label>
            Entity ID:
            <input type="text" bind:value={entityId} />
        </label>
        <button on:click={fetchImprints}>Refresh Journal</button>
    </div>

    {#if loading}
        <div class="sys-msg">Loading geometric memory topology...</div>
    {:else if errorMsg}
        <div class="sys-msg error">{errorMsg}</div>
    {:else if imprints.length === 0}
        <div class="sys-msg">
            No non-volatile memories burned yet. Grid $\mu$ is flat.
        </div>
    {:else}
        <div class="imprint-list">
            {#each imprints as imp}
                <div class="imprint-card">
                    <div class="card-header">
                        <h3>Imprint: {imp.imprint_id.substring(0, 8)}...</h3>
                        <span class="timestamp"
                            >{new Date(imp.ts * 1000).toLocaleString(
                                "en-GB",
                            )}</span
                        >
                    </div>

                    <div class="metrics-grid">
                        <div class="metric-box config">
                            <strong>Physics Config</strong><br />
                            Grid: {imp.grid}<br />
                            dt: {imp.dt}<br />
                            seed: {imp.seed}
                        </div>
                        <div class="metric-box stats">
                            <strong>Topological Footprint ($\Delta\mu$)</strong
                            ><br />
                            L1 Mass: {typeof imp.stats?.l1 === "number"
                                ? imp.stats.l1.toExponential(2)
                                : "N/A"}<br />
                            Max Peak: {typeof imp.stats?.max === "number"
                                ? imp.stats.max.toFixed(4)
                                : "N/A"}<br />
                            Spread Ratio (&gt;$\tau$): {typeof imp.stats
                                ?.ratio_tau === "number"
                                ? (imp.stats.ratio_tau * 100).toFixed(2)
                                : "0.00"}%
                        </div>
                        <div class="metric-box affect">
                            <strong>Emergent Affect (v0)</strong><br />
                            Arousal: {typeof imp.affect_v0?.arousal === "number"
                                ? imp.affect_v0.arousal.toExponential(2)
                                : "N/A"}<br />
                            Certainty: {typeof imp.affect_v0?.certainty ===
                            "number"
                                ? imp.affect_v0.certainty.toFixed(4)
                                : "N/A"}<br />
                            Valence: {imp.affect_v0?.valence > 0
                                ? "+"
                                : ""}{typeof imp.affect_v0?.valence === "number"
                                ? imp.affect_v0.valence.toFixed(4)
                                : "N/A"}<br />
                            Resonance: {typeof imp.affect_v0?.resonance ===
                            "number"
                                ? imp.affect_v0.resonance.toExponential(2)
                                : "0.00e+0"}
                        </div>
                    </div>

                    <div class="actions">
                        <span class="file-path" title={imp.delta_mu_path}
                            >Disk: {imp.delta_mu_path
                                ?.split(/[\\/]/)
                                .pop()}</span
                        >
                        <button
                            class="forget-btn"
                            on:click={() => forgetImprint(imp.imprint_id)}
                        >
                            Forget (Subtract $\Delta\mu$)
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .journal-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 3rem 2rem;
        font-family: "Courier New", Courier, monospace;
        color: #e0e0e0;
        min-height: 100vh;
    }
    .header-section {
        margin-bottom: 2rem;
        border-bottom: 2px solid #333;
        padding-bottom: 1rem;
    }
    h1 {
        color: #00d4ff;
        font-size: 2rem;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .subtitle {
        color: #888;
        margin: 0;
        font-size: 0.95rem;
    }
    .controls {
        margin: 0 0 2rem 0;
        display: flex;
        gap: 1.5rem;
        align-items: center;
        background: rgba(0, 212, 255, 0.05);
        padding: 1rem;
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 4px;
    }
    label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: bold;
        color: #aaa;
    }
    input {
        background: #111;
        color: #00d4ff;
        border: 1px solid #444;
        padding: 0.5rem;
        font-family: inherit;
        border-radius: 2px;
        width: 150px;
    }
    button {
        background: #00d4ff;
        color: #000;
        border: none;
        padding: 0.6rem 1.2rem;
        cursor: pointer;
        font-weight: bold;
        font-family: inherit;
        border-radius: 2px;
        transition: background 0.2s;
    }
    button:hover {
        background: #00b3d6;
    }
    .sys-msg {
        background: #111;
        padding: 2rem;
        text-align: center;
        border: 1px dashed #444;
        color: #aaa;
        font-size: 1.1rem;
    }
    .sys-msg.error {
        color: #ff4a4a;
        border-color: #ff4a4a;
        background: rgba(255, 74, 74, 0.05);
    }
    .imprint-list {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }
    .imprint-card {
        background: #15151a;
        border: 1px solid #333;
        padding: 1.5rem;
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #2a2a35;
        padding-bottom: 0.75rem;
    }
    .card-header h3 {
        margin: 0;
        color: #c9a0ff;
        font-size: 1.25rem;
    }
    .timestamp {
        color: #666;
        font-size: 0.9rem;
    }
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background: #0a0a0d;
        padding: 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #222;
        border-radius: 4px;
        color: #ccc;
    }
    .metric-box strong {
        color: #00d4ff;
        display: block;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #222;
        padding-bottom: 0.25rem;
    }
    .metric-box.stats strong {
        color: #f28b82;
    }
    .metric-box.affect strong {
        color: #81c995;
    }

    .actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #222;
    }
    .file-path {
        font-size: 0.85rem;
        color: #555;
    }
    .forget-btn {
        background: transparent;
        border: 1px solid #ff4a4a;
        color: #ff4a4a;
    }
    .forget-btn:hover {
        background: #ff4a4a;
        color: #fff;
    }
</style>
