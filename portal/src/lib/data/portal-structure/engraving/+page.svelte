<script lang="ts">
    import { onMount } from "svelte";

    // State Types
    type Block = {
        block_id: string;
        source_file: string;
        text: string;
        offsets: number[];
        sha256: string;
        category: "A" | "B" | "UNCERTAIN";
        why: {
            score: number;
            hits: string[];
        };
    };

    // UI State
    let files: FileList;
    let isUploading = false;
    let errorMsg = "";

    // Staging State
    let stagingId = "";
    let blocks: Block[] = [];
    let overrides: Record<string, "A" | "B"> = {};

    // Run State
    let isRunning = false;
    let jobId = "";
    let runProgress = 0;
    let runLogs: string[] = [];
    let runStatus = "";
    let outputBundle = "";

    // Physics Config
    let stencilType = "LAP4";
    let encoderVersion = "v1";
    let personalizationDepth = 1.0;
    let identityName = "Lina_Beta";

    // Derived logic
    $: allResolved = blocks.every((b) => {
        if (b.category !== "UNCERTAIN") return true;
        return overrides[b.block_id] !== undefined;
    });

    $: unresolvedCount = blocks.filter(
        (b) => b.category === "UNCERTAIN" && !overrides[b.block_id],
    ).length;

    async function uploadFiles() {
        if (!files || files.length === 0) return;

        isUploading = true;
        errorMsg = "";
        const formData = new FormData();
        formData.append("file", files[0]);

        try {
            const res = await fetch(
                "http://127.0.0.1:8000/api/engraving/preview",
                {
                    method: "POST",
                    body: formData,
                },
            );

            if (!res.ok) throw new Error(await res.text());

            const data = await res.json();
            stagingId = data.staging_id;
            blocks = data.blocks;
            // Reset state
            overrides = {};
            jobId = "";
            runProgress = 0;
            runLogs = [];
            runStatus = "";
            outputBundle = "";
        } catch (err: any) {
            errorMsg = err.message || "Failed to upload.";
        } finally {
            isUploading = false;
        }
    }

    function toggleOverride(
        blockId: string,
        currentFallback: "A" | "B" | "UNCERTAIN",
        target: "A" | "B",
    ) {
        if (
            overrides[blockId] === target ||
            (currentFallback === target && !overrides[blockId])
        ) {
            // It's already this category natively, or we are unclicking
            delete overrides[blockId];
            overrides = overrides; // trigger reactivity
        } else {
            overrides[blockId] = target;
        }
    }

    function getEffectiveCategory(block: Block) {
        if (overrides[block.block_id]) return overrides[block.block_id];
        return block.category;
    }

    async function runEngraving() {
        if (!allResolved) return;

        isRunning = true;
        errorMsg = "";
        runLogs = ["Connecting to physics core..."];

        try {
            const payload = {
                staging_id: stagingId,
                overrides: overrides,
                config: {
                    stencil_type: stencilType,
                    encoder_version: encoderVersion,
                    personalization_depth: personalizationDepth,
                },
                identity_name: identityName,
            };

            const res = await fetch("http://127.0.0.1:8000/api/engraving/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            jobId = data.job_id;

            connectSSE();
        } catch (err: any) {
            errorMsg = err.message || "Failed to start job.";
            isRunning = false;
        }
    }

    function connectSSE() {
        const eventSource = new EventSource(
            `http://127.0.0.1:8000/api/engraving/stream/${jobId}`,
        );

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.error) {
                    errorMsg = data.error;
                    eventSource.close();
                    isRunning = false;
                    return;
                }

                runStatus = data.status;
                runProgress = data.progress;
                if (data.logs && data.logs.length > 0) {
                    // Keep last 100 logs to prevent DOM freezing
                    runLogs = [...runLogs, ...data.logs].slice(-100);
                }

                if (data.output_dir) {
                    outputBundle = data.output_dir;
                }

                if (
                    data.status === "completed" ||
                    data.status === "error" ||
                    data.status === "cancelled"
                ) {
                    eventSource.close();
                    isRunning = false;
                }
            } catch (err: any) {
                console.error(
                    "Failed to parse SSE event data:",
                    event.data,
                    err,
                );
                errorMsg = "SSE parse error: " + err.message;
                eventSource.close();
                isRunning = false;
            }
        };

        eventSource.onerror = (err) => {
            if (
                runStatus === "completed" ||
                runStatus === "error" ||
                runStatus === "cancelled"
            )
                return;
            console.error("SSE Connection Error event fired", err);
            errorMsg = "SSE Connection Lost.";
            eventSource.close();
            isRunning = false;
        };
    }

    async function cancelJob() {
        if (!jobId) return;
        try {
            await fetch(`http://127.0.0.1:8000/api/engraving/cancel/${jobId}`, {
                method: "POST",
            });
        } catch (e) {}
    }
</script>

<svelte:head>
    <title>Lineum Edge | Memory Engraving</title>
</svelte:head>

<main class="dashboard-container">
    <header class="header">
        <h1>
            <span class="gradient-text">MODE=train</span> Memory Engraving
        </h1>
        <p class="subtitle">
            Compile chat histories into native thermodynamic Lineum `.npz`
            structures.
        </p>
    </header>

    <section class="section">
        <div class="card glass">
            <h2>1. Establish Source Archive</h2>
            <p>
                Upload a `.zip` containing user markdown or text chat exports.
            </p>
            <div class="upload-row">
                <input
                    type="file"
                    bind:files
                    class="file-input"
                    accept=".zip,.txt,.md"
                />
                <button
                    class="primary-btn pulse-hover"
                    on:click={uploadFiles}
                    disabled={isUploading || !files}
                >
                    {isUploading ? "Staging..." : "Upload & Preview"}
                </button>
            </div>
            {#if errorMsg}
                <div class="alert error">{errorMsg}</div>
            {/if}
        </div>
    </section>

    {#if stagingId && !jobId}
        <section class="section config-section fade-in">
            <div class="card glass">
                <h2>2. Physics Configuration</h2>
                <div class="grid-2">
                    <div class="input-group">
                        <label>Discretization Stencil</label>
                        <select bind:value={stencilType}>
                            <option value="LAP4"
                                >LAP4 (Default, Deterministic)</option
                            >
                            <option value="LAP8"
                                >LAP8 (Isotropic, Experimental)</option
                            >
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Identity Alias</label>
                        <input
                            type="text"
                            bind:value={identityName}
                            placeholder="E.g. Lina_Base"
                        />
                    </div>
                    <div class="input-group">
                        <label>Personalization Depth (Scraping Strength)</label>
                        <input
                            type="range"
                            min="0.1"
                            max="2.0"
                            step="0.1"
                            bind:value={personalizationDepth}
                        />
                        <span class="range-val">{personalizationDepth}x</span>
                    </div>
                </div>
            </div>
        </section>

        <section class="section logs-section fade-in">
            <div class="card glass">
                <div class="card-header">
                    <h2>3. Categorization Staging</h2>
                    <div
                        class="badge {unresolvedCount === 0
                            ? 'success'
                            : 'warning'}"
                    >
                        {unresolvedCount} Uncertain Blocks Remaining
                    </div>
                </div>

                <p class="helper-text">
                    Review how the semantic heuristic (v1) routed your memories. <b
                        >Category A</b
                    >
                    structurally modifies the $\mu$ terrain. <b>Category B</b> appends
                    to JSON context without physics cost.
                </p>

                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>ID (SHA-256)</th>
                                <th>Content Snippet</th>
                                <th>Rule Hits</th>
                                <th>Destination</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each blocks as block}
                                {@const effCat = getEffectiveCategory(block)}
                                <tr class="row-{effCat}">
                                    <td class="mono"
                                        >{block.sha256.substring(0, 8)}</td
                                    >
                                    <td class="snippet" title={block.text}
                                        >{block.text.substring(0, 80)}...</td
                                    >
                                    <td>
                                        {#if block.why.hits.length > 0}
                                            <span class="kw-tag"
                                                >{block.why.hits.join(
                                                    ", ",
                                                )}</span
                                            >
                                        {:else}
                                            <span class="kw-tag empty"
                                                >None</span
                                            >
                                        {/if}
                                    </td>
                                    <td class="actions">
                                        <div class="toggle-group">
                                            <button
                                                class="tgl-btn {effCat === 'A'
                                                    ? 'active-a'
                                                    : ''}"
                                                on:click={() =>
                                                    toggleOverride(
                                                        block.block_id,
                                                        block.category,
                                                        "A",
                                                    )}>Cat-A</button
                                            >
                                            <button
                                                class="tgl-btn {effCat === 'B'
                                                    ? 'active-b'
                                                    : ''}"
                                                on:click={() =>
                                                    toggleOverride(
                                                        block.block_id,
                                                        block.category,
                                                        "B",
                                                    )}>Cat-B</button
                                            >
                                            {#if effCat === "UNCERTAIN"}
                                                <span class="alert-icon"
                                                    >⚠️</span
                                                >
                                            {/if}
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>

                <div class="action-footer">
                    <button
                        class="burn-btn"
                        disabled={!allResolved}
                        on:click={runEngraving}
                    >
                        Burn Identity &rarr;
                    </button>
                </div>
            </div>
        </section>
    {/if}

    {#if jobId || isRunning}
        <section class="section stream-section fade-in">
            <div class="card glass border-glow">
                <div class="card-header">
                    <h2>4. Core Execution Stream</h2>
                    <button
                        class="danger-btn"
                        on:click={cancelJob}
                        disabled={runStatus === "completed" ||
                            runStatus === "cancelled"}>Halt Compute</button
                    >
                </div>

                <div class="progress-bar-bg">
                    <div
                        class="progress-bar-fill"
                        style="width: {runProgress}%"
                    ></div>
                </div>
                <div class="progress-stats">
                    <span>{runStatus.toUpperCase()}</span>
                    <span>{runProgress}% Complete</span>
                </div>

                <div class="terminal-window" id="terminal">
                    {#each runLogs as log}
                        <div class="log-line">> {log}</div>
                    {/each}
                </div>

                {#if outputBundle}
                    <div class="success-banner">
                        <h3>✅ Identity Successfully Compiled</h3>
                        <p>
                            Output Bundle saved to: <code>{outputBundle}</code>
                        </p>
                        <ul class="manifest-list">
                            <li>📄 identity_seed_{identityName}.npz</li>
                            <li>📄 cfg.json (Hash Locked)</li>
                            <li>📄 context.json</li>
                            <li>📄 classification_report.json</li>
                            <li>📄 audit_trace.log</li>
                        </ul>
                    </div>
                {/if}
            </div>
        </section>
    {/if}
</main>

<style>
    @import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&family=JetBrains+Mono:wght@400&display=swap");

    :global(body) {
        margin: 0;
        background: radial-gradient(circle at top right, #0a0a10, #030305);
        color: #e2e8f0;
        font-family: "Space Grotesk", sans-serif;
        min-height: 100vh;
    }

    .dashboard-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    .header {
        text-align: center;
        margin-bottom: 3rem;
    }

    .header h1 {
        font-size: 2.5rem;
        margin: 0 0 0.5rem 0;
        letter-spacing: -1px;
    }

    .gradient-text {
        background: linear-gradient(90deg, #ff4b4b, #ff7e5f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
    }

    .section {
        margin-bottom: 2rem;
    }

    .glass {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 2rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    h2 {
        font-size: 1.5rem;
        margin-top: 0;
        margin-bottom: 1rem;
        color: #f8fafc;
        font-weight: 600;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
    }

    .upload-row {
        display: flex;
        gap: 1rem;
        align-items: center;
        margin-top: 1.5rem;
    }

    .file-input {
        flex: 1;
        padding: 0.75rem;
        background: rgba(0, 0, 0, 0.5);
        border: 1px dashed rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #fff;
        cursor: pointer;
    }

    .primary-btn {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .primary-btn:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    .primary-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }

    .input-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        color: #94a3b8;
    }

    .input-group select,
    .input-group input[type="text"] {
        width: 100%;
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        padding: 0.75rem;
        border-radius: 6px;
        font-family: inherit;
    }

    .input-group input[type="range"] {
        width: calc(100% - 40px);
        margin-right: 10px;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    .card-header h2 {
        border: none;
        padding: 0;
        margin: 0;
    }

    .badge {
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge.warning {
        background: rgba(234, 179, 8, 0.2);
        color: #fde047;
        border: 1px solid rgba(234, 179, 8, 0.4);
    }
    .badge.success {
        background: rgba(34, 197, 94, 0.2);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.4);
    }

    .helper-text {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }

    .table-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        background: rgba(0, 0, 0, 0.2);
    }

    table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }

    th {
        position: sticky;
        top: 0;
        background: #111118;
        padding: 1rem;
        font-size: 0.9rem;
        color: #94a3b8;
        z-index: 10;
    }

    td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .mono {
        font-family: "JetBrains Mono", monospace;
        color: #8b5cf6;
        font-size: 0.85rem;
    }

    .snippet {
        font-size: 0.9rem;
        color: #e2e8f0;
        max-width: 300px;
    }

    .kw-tag {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .kw-tag.empty {
        opacity: 0.5;
    }

    /* Row Highlights based on Effective Category */
    .row-A {
        background: rgba(239, 68, 68, 0.03);
    }
    .row-B {
        background: rgba(59, 130, 246, 0.03);
    }
    .row-UNCERTAIN {
        background: rgba(234, 179, 8, 0.05);
    }

    .toggle-group {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .tgl-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8rem;
        transition: all 0.2s;
    }

    .tgl-btn:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    .tgl-btn.active-a {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border-color: rgba(239, 68, 68, 0.5);
    }
    .tgl-btn.active-b {
        background: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
        border-color: rgba(59, 130, 246, 0.5);
    }

    .action-footer {
        display: flex;
        justify-content: flex-end;
        margin-top: 1.5rem;
    }

    .burn-btn {
        background: linear-gradient(135deg, #ef4444, #f97316);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
        transition: all 0.2s;
    }
    .burn-btn:hover:not(:disabled) {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5);
    }
    .burn-btn:disabled {
        background: #333;
        color: #777;
        box-shadow: none;
        cursor: not-allowed;
    }

    /* Streaming Section */
    .border-glow {
        animation: glowBorder 4s infinite alternate;
    }

    @keyframes glowBorder {
        0% {
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.2);
        }
        100% {
            box-shadow: 0 0 25px rgba(249, 115, 22, 0.2);
            border-color: rgba(249, 115, 22, 0.4);
        }
    }

    .progress-bar-bg {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #ef4444, #f97316);
        transition: width 0.3s ease;
    }

    .progress-stats {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    .terminal-window {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 8px;
        padding: 1rem;
        height: 250px;
        overflow-y: auto;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.85rem;
        color: #4ade80;
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
    }

    .log-line {
        border-bottom: 1px solid transparent;
    }

    .danger-btn {
        background: transparent;
        border: 1px solid #ef4444;
        color: #ef4444;
        padding: 0.4rem 1rem;
        border-radius: 4px;
        cursor: pointer;
    }
    .danger-btn:hover:not(:disabled) {
        background: rgba(239, 68, 68, 0.1);
    }
    .danger-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        border-color: #555;
        color: #555;
    }

    .success-banner {
        margin-top: 2rem;
        padding: 1.5rem;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 8px;
    }

    .success-banner h3 {
        color: #86efac;
        margin-top: 0;
    }
    .manifest-list {
        color: #cbd5e1;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.9rem;
    }
    .manifest-list li {
        margin: 0.3rem 0;
    }
    code {
        background: rgba(0, 0, 0, 0.3);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }

    .fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
