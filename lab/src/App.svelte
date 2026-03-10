<script>
    import { onMount } from "svelte";
    import { TopographyEngine } from "./lib/engines/TopographyEngine";
    import ZetaScanner from "./lib/components/ZetaScanner.svelte";
    import TidalAnalyzer from "./lib/components/TidalAnalyzer.svelte";
    import HypothesisTester from "./lib/components/HypothesisTester.svelte";
    import ExtremeSpikes from "./lib/components/ExtremeSpikes.svelte";
    import InteractiveChart from "./lib/components/InteractiveChart.svelte";
    import LplCompiler from "./lib/components/LplCompiler.svelte";
    import ValidationDashboard from "./lib/components/ValidationDashboard.svelte";
    import WhitepaperClaims from "./lib/components/WhitepaperClaims.svelte";
    import ContactFooter from "./lib/components/ContactFooter.svelte";
    import Logo from "./lib/components/Logo.svelte";
    import { t } from "./lib/i18n";

    let container;
    let engine;
    let loading = true;
    let frame = 0;
    let totalFrames = 0;
    let playbackSpeed = 1.0;
    let manifest = [];
    let selectedRunId = "";
    let dataRoot = ""; // Path to current run data
    let resonanceData = null; // 🔬 Spectral data
    let metadata = null; // 📦 Audit metadata
    let harmonicData = null; // 🌀 Fibonacci & Golden Ratio
    let showSpiral = false;

    // Global Modal State
    let maximizedChart = null; // { title, config }
    let error = null;

    let auditConfig = null;
    let showCudaWarning = false;
    let auditProgressText = "GENERATING...";
    let auditProgressStep = 0;

    // Persist active tab across reloads
    const savedTab = localStorage.getItem("lab_active_tab");
    let activeTab = savedTab || "stats";

    // Persist main section via URL Hash + localStorage fallback
    const getInitialMode = () => {
        if (typeof window !== "undefined") {
            const hash = window.location.hash.replace("#", "");
            if (hash === "whitepapers" || hash === "whitepaper") {
                window.location.hash = "claims";
                return "claims";
            }
            const validModes = ["simulator", "validation", "claims", "lpl"];
            if (validModes.includes(hash)) return hash;
            const savedMode = localStorage.getItem("lab_main_mode");
            if (validModes.includes(savedMode)) return savedMode;
        }
        return "simulator";
    };

    let mainMode = getInitialMode();

    $: if (mainMode && typeof window !== "undefined") {
        localStorage.setItem("lab_main_mode", mainMode);
        if (window.location.hash !== "#" + mainMode) {
            window.location.hash = mainMode;
        }
    }

    $: if (activeTab) {
        localStorage.setItem("lab_active_tab", activeTab);
    }

    $: if (engine && playbackSpeed !== undefined) {
        engine.playbackSpeed = playbackSpeed;
    }

    $: if (engine && showSpiral !== undefined) {
        engine.showSpiral = showSpiral;
        if (engine.goldenSpiral) engine.goldenSpiral.visible = showSpiral;
    }

    // 🛑 Optimization: Pause the 3D Engine when not visible
    $: if (engine) {
        engine.isPaused = mainMode !== "simulator";
    }

    let engineInitialized = false;
    $: if (
        mainMode === "simulator" &&
        !engineInitialized &&
        manifest.length > 0
    ) {
        engineInitialized = true;
        loadRun(manifest[0].run_id);
    }

    onMount(async () => {
        window.addEventListener("hashchange", () => {
            let hash = window.location.hash.replace("#", "");
            if (hash === "whitepapers" || hash === "whitepaper") {
                window.location.hash = "claims";
                hash = "claims";
            }
            const validModes = ["simulator", "validation", "claims", "lpl"];
            if (validModes.includes(hash) && mainMode !== hash) {
                mainMode = hash;
            }
        });

        try {
            const res = await fetch("/data/manifest.json");
            if (!res.ok) throw new Error("Manifest not found");
            manifest = await res.json();
            if (manifest.length > 0 && mainMode === "simulator") {
                // Load run immediately only if we spawned directly into the simulator
                engineInitialized = true;
                await loadRun(manifest[0].run_id);
            } else {
                loading = false;
            }

            try {
                const cfgRes = await fetch(
                    "http://localhost:8000/api/lab/audit/config",
                );
                if (cfgRes.ok) auditConfig = await cfgRes.json();
            } catch (e) {
                console.warn("Could not fetch audit config", e);
            }
        } catch (e) {
            console.error("Initialization failed:", e);
            error = e.message;
            loading = false;
        }

        // ─── Global Tooltip System (viewport-aware, no native title) ───
        let tooltipEl = null;
        const TOOLTIP_OFFSET = 8;

        function showTooltip(e) {
            const target = e.currentTarget;
            const text = target.getAttribute("title");
            if (!text) return;

            // Suppress native tooltip, preserve accessibility
            target.setAttribute("data-tooltip", text);
            target.setAttribute("aria-label", text);
            target.removeAttribute("title");

            // Create tooltip div
            const tooltipId = "lab-tt-" + Date.now();
            tooltipEl = document.createElement("div");
            tooltipEl.className = "lab-tooltip";
            tooltipEl.setAttribute("role", "tooltip");
            tooltipEl.id = tooltipId;
            tooltipEl.textContent = text;
            target.setAttribute("aria-describedby", tooltipId);
            document.body.appendChild(tooltipEl);

            // Position calculation
            const rect = target.getBoundingClientRect();
            const ttRect = tooltipEl.getBoundingClientRect();
            let top, left;

            // Default: above element
            top = rect.top - ttRect.height - TOOLTIP_OFFSET;
            left = rect.left + rect.width / 2 - ttRect.width / 2;

            // If clipping top, show below
            if (top < 4) {
                top = rect.bottom + TOOLTIP_OFFSET;
                tooltipEl.classList.add("below");
            }
            // If clipping left
            if (left < 4) left = 4;
            // If clipping right
            if (left + ttRect.width > window.innerWidth - 4) {
                left = window.innerWidth - ttRect.width - 4;
            }

            tooltipEl.style.top = top + "px";
            tooltipEl.style.left = left + "px";
            tooltipEl.classList.add("visible");
        }

        function hideTooltip(e) {
            const target = e.currentTarget;
            const text = target.getAttribute("data-tooltip");
            if (text) {
                target.setAttribute("title", text);
                target.removeAttribute("data-tooltip");
                target.removeAttribute("aria-label");
                target.removeAttribute("aria-describedby");
            }
            if (tooltipEl) {
                tooltipEl.remove();
                tooltipEl = null;
            }
        }

        // Delegate via event listeners on document
        function handleMouseOver(e) {
            const target = e.target.closest("[title]");
            if (!target) return;
            target._tooltipBound = true;
            target.addEventListener("mouseleave", hideTooltip, { once: true });
            showTooltip({ currentTarget: target });
        }
        document.addEventListener("mouseover", handleMouseOver);

        return () => {
            document.removeEventListener("mouseover", handleMouseOver);
            if (tooltipEl) tooltipEl.remove();
        };
    });

    let isGeneratingAudit = false;

    function initiateAuditGeneration() {
        if (!auditConfig?.allowed) return;
        if (auditConfig.execution_device === "cpu") {
            showCudaWarning = true;
        } else {
            generateAuditContract();
        }
    }

    async function generateAuditContract() {
        if (isGeneratingAudit) return;
        isGeneratingAudit = true;
        showCudaWarning = false;
        auditProgressText = "Starting up...";

        try {
            const response = await fetch(
                "http://localhost:8000/api/lab/audit/generate",
                {
                    method: "POST",
                },
            );
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const lines = decoder
                    .decode(value, { stream: true })
                    .split("\n");
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            auditProgressText = data.detail || "GENERATING...";
                            auditProgressStep = data.step || 0;

                            if (data.status === "success") {
                                alert(
                                    "Audit Contract Generated!\nStatus: " +
                                        data.audit_status +
                                        "\nRun ID: " +
                                        data.new_run_id +
                                        "\nElapsed: " +
                                        data.elapsed +
                                        "s",
                                );
                                window.dispatchEvent(
                                    new CustomEvent("audit-completed"),
                                );
                                try {
                                    const mRes = await fetch(
                                        "/data/manifest.json",
                                    );
                                    if (mRes.ok) manifest = await mRes.json();
                                } catch (e) {}
                                isGeneratingAudit = false;
                                return;
                            } else if (data.status === "error") {
                                throw new Error(data.detail);
                            }
                        } catch (e) {
                            if (
                                e.message &&
                                e.message !== "Unexpected end of JSON input"
                            ) {
                                throw e;
                            }
                        }
                    }
                }
            }
        } catch (err) {
            console.error(err);
            alert("Failed to generate audit contract: " + err.message);
            isGeneratingAudit = false;
        }
    }

    async function loadRun(runId) {
        loading = true;
        selectedRunId = runId;
        dataRoot = `/data/runs/${runId}`;
        const t_now = Date.now();

        try {
            if (engine) engine.dispose();

            const phiRes = await fetch(
                `${dataRoot}/phi_frames.json?t=${t_now}`,
            );
            const phiData = await phiRes.json();

            const trajRes = await fetch(
                `${dataRoot}/trajectories.json?t=${t_now}`,
            );
            const trajData = await trajRes.json();

            const resRes = await fetch(`${dataRoot}/resonance.json?t=${t_now}`);
            resonanceData = await resRes.json();

            const metaRes = await fetch(`${dataRoot}/metadata.json?t=${t_now}`);
            metadata = await metaRes.json();

            const harmRes = await fetch(
                `${dataRoot}/harmonics.json?t=${t_now}`,
            );
            harmonicData = await harmRes.json();

            totalFrames = phiData.metadata.frame_count;

            engine = new TopographyEngine(container, phiData, trajData);
            engine.harmonicData = harmonicData;
            engine.playbackSpeed = playbackSpeed;
            engine.onFrameUpdate = (newFrame) => (frame = newFrame);
            engine.animate();
        } catch (e) {
            console.error("Failed to load run:", runId, e);
            error = e.message || "Failed to load data";
        } finally {
            console.log("DEBUG: Setting loading to false in finally block");
            loading = false;
        }
    }
</script>

<main>
    {#if loading}
        <div class="loader">
            <div class="spinner"></div>
            <p>{$t("loading")}</p>
        </div>
    {:else if error}
        <div class="loader">
            <div class="error-msg">
                <h3>INITIALIZATION FAILURE</h3>
                <p>{error}</p>
                <button on:click={() => window.location.reload()}>RETRY</button>
            </div>
        </div>
    {/if}

    <div
        class="canvas-container"
        class:dimmed={activeTab === "lpl"}
        style:visibility={mainMode === "simulator" ? "visible" : "hidden"}
        style:opacity={mainMode === "simulator" ? 1 : 0}
        data-engine-paused={engine ? engine.isPaused : true}
        bind:this={container}
    ></div>

    <nav class="top-nav">
        <div class="nav-brand">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <Logo
                    width={20}
                    height={20}
                    color="#00ffff"
                    variant="infinity_draw"
                />
                <h1>SIMULACRUM</h1>
            </div>
            <span class="subtitle">Lineum Lab | Hypothesis Sandbox</span>
        </div>

        <div class="nav-modes">
            <button
                class:active={mainMode === "simulator"}
                on:click={() => (mainMode = "simulator")}
            >
                3D Simulator
            </button>
            <button
                class:active={mainMode === "validation"}
                on:click={() => (mainMode = "validation")}
            >
                Validation Core
            </button>
            <button
                class:active={mainMode === "claims"}
                on:click={() => (mainMode = "claims")}
            >
                Claims
            </button>
            <button
                class:active={mainMode === "lpl"}
                on:click={() => (mainMode = "lpl")}
            >
                LPL Compiler
            </button>
            <div class="divider"></div>
            <button
                class="btn-generate-audit"
                class:pulse={isGeneratingAudit}
                class:disabled-audit={auditConfig && !auditConfig.allowed}
                on:click={initiateAuditGeneration}
                disabled={(auditConfig && !auditConfig.allowed) ||
                    isGeneratingAudit}
                title={auditConfig?.reason ||
                    "Generates a local canonical contract in output_wp/"}
            >
                {#if isGeneratingAudit}
                    <span class="icon">⏳</span> {auditProgressText}
                {:else if auditConfig && !auditConfig.allowed}
                    <span class="icon">🔒</span> LOCAL ONLY
                {:else}
                    🛡️ GENERATE AUDIT CONTRACT
                {/if}
            </button>
        </div>

        <div class="header-controls">
            {#if mainMode === "simulator" && manifest.length > 0}
                <select
                    class="run-selector"
                    bind:value={selectedRunId}
                    on:change={(e) => loadRun(e.target.value)}
                >
                    {#each manifest as run}
                        <option value={run.run_id}>
                            {run.run_tag} ({run.timestamp})
                        </option>
                    {/each}
                </select>
            {/if}
        </div>
    </nav>

    {#if mainMode === "validation"}
        <div class="fullscreen-mode">
            <ValidationDashboard />
        </div>
    {:else if mainMode === "claims"}
        <div class="fullscreen-mode">
            <WhitepaperClaims />
        </div>
    {:else if mainMode === "lpl"}
        <div class="fullscreen-mode">
            <LplCompiler />
        </div>
    {:else if mainMode === "simulator"}
        <div class="overlay">
            <div class="header-section">
                <div
                    class="discovery-headline"
                    class:prime={metadata?.pearson_r > 0.9}
                    class:tuning={metadata?.pearson_r > 0.5 &&
                        metadata?.pearson_r <= 0.9}
                >
                    <span class="status-icon"></span>
                    <span class="status-msg">
                        SYSTEM STATUS: BREAKTHROUGH DETECTED:
                        {metadata?.pearson_r > 0.9
                            ? "PRIME RESONANCE (1:1 ALIGNMENT)"
                            : metadata?.pearson_r > 0.5
                              ? "GEOMETRY TUNING"
                              : "STOCHASTIC NOISE (CHAOS)"}
                    </span>
                </div>
            </div>

            {#if frame >= 391}
                <div class="central-alert-system">
                    <div class="event-marker">
                        SYSTEM ALERT: LINON DETECTION [birth]
                    </div>
                </div>
            {/if}

            <div class="side-panel side-panel-left">
                <div class="panel-tabs">
                    <button
                        class="tab-btn"
                        class:active={activeTab === "stats"}
                        on:click={() => (activeTab = "stats")}
                    >
                        STATISTICS
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "scanner"}
                        on:click={() => (activeTab = "scanner")}
                    >
                        SCANNER
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "tidal"}
                        on:click={() => (activeTab = "tidal")}
                    >
                        Tidal
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "hypothesis"}
                        on:click={() => (activeTab = "hypothesis")}
                    >
                        HYPOTHESIS DISCOVERY
                    </button>
                    <button
                        class="tab-btn"
                        class:active={activeTab === "spikes"}
                        on:click={() => (activeTab = "spikes")}
                    >
                        Phenomena
                    </button>
                </div>

                <div class="tab-content">
                    {#if activeTab === "stats"}
                        <div class="stats-panel">
                            <div class="stat">
                                <span class="label">MODE:</span>
                                <span class="value"
                                    >FIELD Φ TOPOGRAPHY (3D)</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">METRIC:</span>
                                <span class="value"
                                    >z = field Φ height [AUDIT]</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">FRAME:</span>
                                <span class="value"
                                    >{frame} / {totalFrames}</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">SOURCE:</span>
                                <span class="value"
                                    >{metadata?.run_tag || "Audit"}</span
                                >
                            </div>
                            <div class="stat">
                                <span class="label">STATUS:</span>
                                <span class="value"
                                    >{frame >= (metadata?.birth_frame || 391)
                                        ? "LINON DETECTION"
                                        : "FIELD Φ INITIALIZATION"}</span
                                >
                                {#if metadata && frame < metadata.birth_frame}
                                    <button
                                        class="jump-btn"
                                        on:click={() =>
                                            engine.jumpToFrame(
                                                metadata.birth_frame,
                                            )}
                                    >
                                        JUMP TO BIRTH [{metadata.birth_frame}]
                                    </button>
                                {/if}
                            </div>
                            <div class="stat speed-control">
                                <span class="label">SPEED:</span>
                                <span class="value"
                                    >{playbackSpeed.toFixed(1)}x</span
                                >
                                <input
                                    type="range"
                                    min="0.1"
                                    max="5.0"
                                    step="0.1"
                                    bind:value={playbackSpeed}
                                />
                            </div>

                            <div class="stat toggle-control">
                                <span class="label">GOLDEN RATIO:</span>
                                <button
                                    class="toggle-btn {showSpiral
                                        ? 'active'
                                        : ''}"
                                    on:click={() => (showSpiral = !showSpiral)}
                                >
                                    {showSpiral ? "ON" : "OFF"}
                                </button>
                            </div>
                        </div>
                    {:else if activeTab === "scanner"}
                        <ZetaScanner
                            {frame}
                            data={resonanceData}
                            harmonics={harmonicData}
                        />
                    {:else if activeTab === "tidal"}
                        <TidalAnalyzer
                            {dataRoot}
                            on:maximize={(e) => (maximizedChart = e.detail)}
                        />
                    {:else if activeTab === "hypothesis"}
                        <HypothesisTester
                            {dataRoot}
                            on:maximize={(e) => (maximizedChart = e.detail)}
                        />
                    {:else if activeTab === "spikes"}
                        <ExtremeSpikes {engine} {frame} />
                    {/if}
                </div>
            </div>
            {#if activeTab !== "lpl" && activeTab !== "rng"}
                <div class="side-panel side-panel-right">
                    <div class="guide-panel">
                        <h3>{$t("guide_title")}</h3>
                        <div class="guide-item">
                            <strong>{$t("guide_watch_title")}</strong>
                            {$t("guide_watch_desc")}
                        </div>
                        <div class="guide-item">
                            <strong>{$t("guide_linons_title")}</strong>
                            {$t("guide_linons_desc")}
                        </div>
                        <div class="guide-item">
                            <strong>{$t("guide_topo_title")}</strong>
                            {$t("guide_topo_desc")}
                        </div>
                        <div class="guide-item">
                            <strong>{$t("guide_zeta_title")}</strong>
                            {$t("guide_zeta_desc")}
                        </div>
                    </div>
                </div>
            {/if}

        </div>
    {/if}

    {#if maximizedChart}
        <div
            class="global-modal-overlay"
            on:click|self={() => (maximizedChart = null)}
            role="dialog"
            aria-modal="true"
            on:keydown={(e) => e.key === "Escape" && (maximizedChart = null)}
            tabindex="-1"
        >
            <div class="modal-content">
                <div class="modal-header">
                    <h3>{maximizedChart.title}</h3>
                    <button
                        type="button"
                        class="close-btn"
                        on:click={() => (maximizedChart = null)}
                        aria-label="Close">&times;</button
                    >
                </div>
                <div class="modal-body">
                    {#key maximizedChart}
                        <InteractiveChart
                            title={maximizedChart.title}
                            config={maximizedChart.config}
                            showMax={false}
                        />
                    {/key}
                </div>
            </div>
        </div>
    {/if}

    {#if showCudaWarning}
        <div class="global-modal-overlay">
            <div class="modal-content warning-modal" style="max-width: 500px">
                <div class="modal-header">
                    <h3>⚠️ Performance Warning</h3>
                    <button
                        class="close-btn"
                        on:click={() => (showCudaWarning = false)}
                        >&times;</button
                    >
                </div>
                <div class="modal-body">
                    <p
                        style="margin-bottom: 12px; font-size: 1.1rem; color: #ffeb3b;"
                    >
                        <strong>Canonical runs enforced on CPU</strong>
                    </p>
                    <div
                        style="background: rgba(0,0,0,0.3); border: 1px solid #1f1f35; padding: 12px; border-radius: 6px; margin-bottom: 12px; font-family: monospace; font-size: 0.85rem; color: #a0aec0;"
                    >
                        <div>
                            <strong style="color: #cbd5e1;"
                                >Execution Device:</strong
                            >
                            {auditConfig?.execution_device || "CPU"}
                        </div>
                        <div>
                            <strong style="color: #cbd5e1;"
                                >Deterministic Mode:</strong
                            >
                            {auditConfig?.deterministic_mode
                                ? "Enabled"
                                : "Disabled"}
                        </div>
                        <div>
                            <strong style="color: #cbd5e1;"
                                >CUDA Available:</strong
                            >
                            {auditConfig?.cuda_available ? "Yes" : "No"}
                        </div>
                        <div>
                            <strong style="color: #cbd5e1;"
                                >Canonical on CUDA Allowed:</strong
                            >
                            {auditConfig?.canonical_audit_allowed_on_cuda
                                ? "Yes"
                                : "No"}
                        </div>
                        {#if auditConfig?.reason}
                            <div style="margin-top: 8px; color: #f87171;">
                                <strong style="color: #cbd5e1;">Reason:</strong>
                                {auditConfig.reason}
                            </div>
                        {/if}
                    </div>
                    <p style="color: #cbd5e1; line-height: 1.5;">
                        This canonical audit requires solving the Lineum Eq-7
                        wavefield over 2,000 steps. It will run on <strong
                            >{auditConfig?.device_name || "CPU"}</strong
                        > and may be much slower (approx 2-5 minutes). Do you want
                        to continue?
                    </p>
                    <div
                        style="display: flex; gap: 16px; margin-top: 24px; justify-content: flex-end;"
                    >
                        <button
                            class="btn-cancel"
                            on:click={() => (showCudaWarning = false)}
                            style="background: transparent; border: 1px solid #4a4a5a; padding: 8px 16px; border-radius: 6px; cursor: pointer; color: #fff;"
                            >Cancel</button
                        >
                        <button
                            class="btn-proceed"
                            on:click={generateAuditContract}
                            style="background: rgba(234, 179, 8, 0.2); border: 1px solid #eab308; padding: 8px 16px; border-radius: 6px; cursor: pointer; color: #fef08a; font-weight: bold;"
                            >Continue on CPU</button
                        >
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <ContactFooter />
</main>

<svelte:window
    on:keydown={(e) => e.key === "Escape" && (maximizedChart = null)}
/>

<style>
    main {
        width: 100vw;
        height: 100vh;
        background: #050505;
        position: relative;
        overflow: hidden;
    }

    .canvas-container {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
        pointer-events: none;
        transition:
            opacity 0.5s ease,
            filter 0.5s ease;
    }

    .canvas-container.dimmed {
        opacity: 0.15;
        filter: blur(8px) grayscale(100%);
    }

    .overlay {
        position: absolute;
        top: 32px;
        left: 32px;
        right: 32px;
        bottom: 32px;
        pointer-events: none;
        z-index: 100;
        display: grid;
        grid-template-columns: 400px 1fr 400px;
        grid-template-rows: auto 60px 1fr auto;
        grid-template-areas:
            "header header header"
            "alert alert alert"
            "left . right"
            "footer footer footer";
        gap: 20px;
        box-sizing: border-box;
        overflow: hidden;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .fullscreen-mode {
        position: absolute;
        top: 60px; /* height of top-nav */
        left: 0;
        right: 0;
        bottom: 0;
        overflow-y: auto;
        box-sizing: border-box;
        z-index: 10;
        background: transparent;
    }

    .header-section {
        grid-area: header;
        display: flex;
        flex-direction: column;
        gap: 10px;
        pointer-events: all;
    }

    .header-controls {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .run-selector {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
        color: #00ffff;
        font-size: 0.7rem;
        padding: 4px 8px;
        outline: none;
        cursor: pointer;
    }

    .run-selector option {
        background: #050505;
        color: #fff;
    }

    .central-alert-system {
        grid-area: alert;
        display: flex;
        justify-content: center;
        align-items: center;
        pointer-events: none;
        min-height: 50px;
    }

    .side-panel {
        pointer-events: all;
        display: flex;
        flex-direction: column;
        gap: 20px;
        min-height: 0; /* Crucial for scrolling inside grid/flex */
        height: 100%;
    }

    .side-panel-left {
        grid-area: left;
    }

    .side-panel-right {
        grid-area: right;
    }

    h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 200;
        letter-spacing: 0.5rem;
        color: #fff;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
    }

    .discovery-headline {
        margin-top: 15px;
        background: rgba(0, 255, 255, 0.05);
        border-left: 4px solid rgba(0, 255, 255, 0.3);
        padding: 10px 15px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.5s ease;
    }

    .discovery-headline.prime {
        background: rgba(0, 255, 0, 0.1);
        border-color: #00ff00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
    }

    .discovery-headline.tuning {
        background: rgba(255, 170, 0, 0.1);
        border-color: #ffaa00;
    }

    .status-icon {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00ffff;
        box-shadow: 0 0 8px #00ffff;
        animation: blink 2s infinite;
    }

    .prime .status-icon {
        background: #00ff00;
        box-shadow: 0 0 10px #00ff00;
    }

    .tuning .status-icon {
        background: #ffaa00;
        box-shadow: 0 0 10px #ffaa00;
    }

    .status-msg {
        font-size: 0.8rem;
        font-weight: bold;
        letter-spacing: 1px;
        color: #fff;
        text-transform: uppercase;
    }

    /* Provance Badge */
    :global(.data-badge) {
        display: inline-block;
        font-size: 0.55rem;
        background: rgba(0, 255, 255, 0.2);
        color: #00ffff;
        padding: 1px 4px;
        border-radius: 2px;
        margin-left: 8px;
        vertical-align: middle;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    @keyframes blink {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.3;
        }
    }

    .subtitle {
        margin: 0;
        font-size: 0.8rem;
        letter-spacing: 0.1rem;
        color: #00ffff;
        opacity: 0.7;
        margin-top: 8px;
        text-transform: uppercase;
    }

    /* Tabs Styling */
    .panel-tabs {
        display: flex;
        gap: 2px;
        background: rgba(0, 255, 255, 0.1);
        padding: 2px;
    }

    .tab-btn {
        flex: 1;
        background: transparent;
        border: none;
        color: rgba(0, 255, 255, 0.5);
        padding: 8px;
        cursor: pointer;
        font-size: 0.7rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.2s;
    }

    .tab-btn.active {
        background: rgba(0, 255, 255, 0.2);
        color: #00ffff;
        box-shadow: inset 0 -2px 0 #00ffff;
    }


    .tab-content {
        flex: 1;
        overflow-y: auto;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        scrollbar-width: thin;
        scrollbar-color: rgba(0, 255, 255, 0.3) transparent;
        border-bottom: 1px solid rgba(0, 255, 255, 0.1);
    }

    .tab-content::-webkit-scrollbar {
        width: 6px;
    }

    .tab-content::-webkit-scrollbar-thumb {
        background: rgba(0, 255, 255, 0.3);
        border-radius: 3px;
    }

    .stats-panel {
        background: rgba(0, 0, 0, 0.5);
        border-left: 2px solid #00ffff;
        padding: 16px;
        backdrop-filter: blur(10px);
    }

    .stat {
        margin-bottom: 8px;
        display: flex;
        gap: 16px;
        align-items: center;
    }

    .label {
        font-size: 0.7rem;
        color: #888;
        width: 80px;
    }

    .value {
        font-size: 0.8rem;
        color: #fff;
        font-family: monospace;
    }

    .jump-btn {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid #00ffff;
        color: #00ffff;
        font-size: 0.6rem;
        padding: 4px 8px;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s;
        margin-left: 8px;
    }

    .jump-btn:hover {
        background: rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }

    input[type="range"] {
        accent-color: #00ffff;
        cursor: pointer;
        width: 100px;
    }

    .speed-control {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }

    .toggle-btn {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.4);
        color: #00ffff;
        padding: 2px 10px;
        cursor: pointer;
        font-size: 0.6rem;
        transition: all 0.2s;
    }

    .toggle-btn.active {
        background: #00ffff;
        color: #000;
        box-shadow: 0 0 10px #00ffff;
    }

    /* Loader Styles */
    .loader {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #050505;
        z-index: 200;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 2px solid rgba(0, 255, 255, 0.1);
        border-top-color: #00ffff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 24px;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .loader p {
        font-size: 0.7rem;
        letter-spacing: 0.3rem;
        color: #00ffff;
        opacity: 0.5;
    }

    .error-msg {
        text-align: center;
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid #ff0000;
        padding: 40px;
        color: #ff0000;
        max-width: 400px;
    }

    .error-msg h3 {
        margin-top: 0;
        letter-spacing: 4px;
        font-size: 1.2rem;
    }

    .error-msg button {
        margin-top: 20px;
        background: #ff0000;
        color: #fff;
        border: none;
        padding: 8px 16px;
        cursor: pointer;
        font-weight: bold;
    }

    .event-marker {
        background: rgba(255, 170, 0, 0.3);
        color: #fff;
        padding: 6px 16px;
        font-size: 0.7rem;
        font-weight: bold;
        border: 2px solid #ffaa00;
        text-align: center;
        animation:
            blink 1s infinite,
            pulse-alert 2s infinite;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(255, 170, 0, 0.4);
        pointer-events: all;
        letter-spacing: 2px;
    }

    @keyframes pulse-alert {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }

    .guide-panel {
        background: rgba(0, 40, 40, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.3);
        padding: 24px;
        backdrop-filter: blur(5px);
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
    }

    .guide-panel h3 {
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 0.9rem;
        letter-spacing: 0.2rem;
        border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        padding-bottom: 15px;
        text-transform: uppercase;
        color: #00ffff;
    }

    .guide-item {
        margin-bottom: 20px;
        font-size: 0.75rem;
        line-height: 1.6;
        color: #eee;
    }

    .guide-item strong {
        color: #00ffff;
        display: block;
        margin-bottom: 6px;
        letter-spacing: 1px;
    }

    @keyframes blink {
        50% {
            opacity: 0.6;
        }
    }

    /* Global Modal Overlay */
    .global-modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(20px);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 60px;
        pointer-events: all;
    }

    .global-modal-overlay .modal-content {
        width: 100%;
        max-width: 1300px;
        height: 100%;
        max-height: 85vh;
        background: #050505;
        border: 1px solid #00ffff;
        display: flex;
        flex-direction: column;
        padding: 30px;
        box-shadow: 0 0 100px rgba(0, 255, 255, 0.3);
        position: relative;
    }

    .global-modal-overlay .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 2px solid rgba(0, 255, 255, 0.2);
        padding-bottom: 15px;
    }

    .global-modal-overlay .modal-header h3 {
        font-size: 1.2rem;
        letter-spacing: 4px;
        color: #00ffff;
        margin: 0;
        border: none;
    }

    .global-modal-overlay .modal-body {
        flex: 1;
        min-height: 0;
    }

    .global-modal-overlay .close-btn {
        background: transparent;
        border: none;
        color: #00ffff;
        font-size: 2.5rem;
        cursor: pointer;
        line-height: 1;
        transition: color 0.2s;
    }

    .global-modal-overlay .close-btn:hover {
        color: #fff;
    }

    /* ─── Global Dark Tooltip (JS-positioned div) ─── */
    :global(.lab-tooltip) {
        position: fixed;
        padding: 6px 10px;
        background: #1c2128;
        color: #c9d1d9;
        font-size: 12px;
        font-weight: 400;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
            Arial, sans-serif;
        line-height: 1.4;
        white-space: nowrap;
        border: 1px solid #30363d;
        border-radius: 6px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.15s ease-out;
    }
    :global(.lab-tooltip.visible) {
        opacity: 1;
    }

    .top-nav {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: rgba(0, 5, 15, 0.8);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(0, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
        z-index: 200;
        pointer-events: auto;
        box-sizing: border-box;
    }

    .nav-brand {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .nav-brand h1 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: 300;
        letter-spacing: 0.3rem;
        color: #fff;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.4);
    }

    .nav-brand .subtitle {
        font-size: 0.6rem;
        color: #00ffff;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.1rem;
        margin-top: 2px;
    }

    .nav-modes {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .nav-modes button {
        background: transparent;
        border: 1px solid transparent;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 6px 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        border-radius: 4px;
    }

    .nav-modes button:hover {
        color: #00ffff;
        background: rgba(0, 255, 255, 0.05);
    }

    .nav-modes button.active {
        color: #00ffff;
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.1);
    }

    .nav-modes .divider {
        width: 1px;
        height: 20px;
        background: rgba(255, 255, 255, 0.2);
        margin: 0 10px;
    }

    .btn-generate-audit {
        background: rgba(0, 255, 0, 0.1) !important;
        color: #00ff00 !important;
        border: 1px solid rgba(0, 255, 0, 0.3) !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .btn-generate-audit:hover:not(:disabled) {
        background: rgba(0, 255, 0, 0.2) !important;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2) !important;
    }

    .btn-generate-audit:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
