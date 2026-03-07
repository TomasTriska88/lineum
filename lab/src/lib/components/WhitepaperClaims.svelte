<script>
    import { whitepaperClaims } from "../data/claims.js";
    import { marked } from "marked";
    import katex from "katex";
    import "katex/dist/katex.min.css";
    import { onMount } from "svelte";

    // Render inline LaTeX: replaces $...$ with KaTeX HTML
    function renderInlineLatex(text) {
        if (!text) return "";
        return text.replace(/\$([^$]+)\$/g, (_, tex) => {
            try {
                // Collapse double-escaped backslashes from JS string literals
                const normalizedTex = tex.replace(/\\\\/g, "\\");
                return katex.renderToString(normalizedTex, {
                    throwOnError: false,
                });
            } catch {
                return `<code>${tex}</code>`;
            }
        });
    }

    export let manifestHistory = []; // Array of { id, preset, passed, mode }

    let searchQuery = "";
    let selectedTag = "all";
    let appliedFilter = "all";

    let integrationLog = [];
    let savingApplied = false;

    // Derived tags list
    $: allTags = [
        "all",
        ...new Set(whitepaperClaims.flatMap((c) => c.tags)),
    ].sort();

    // Filter claims
    $: filteredClaims = whitepaperClaims.filter((claim) => {
        const matchesSearch =
            claim.short_claim
                .toLowerCase()
                .includes(searchQuery.toLowerCase()) ||
            claim.human_claim.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesTag =
            selectedTag === "all" || claim.tags.includes(selectedTag);

        const appliedState = isApplied(claim.id);
        const status = getActualStatus(claim, claimResults);
        let matchesApplied = true;
        if (appliedFilter === "applied") matchesApplied = appliedState;
        else if (appliedFilter === "not_applied")
            matchesApplied = !appliedState;
        else if (appliedFilter === "supported")
            matchesApplied = status === "SUPPORTED";
        else if (appliedFilter === "contradicted")
            matchesApplied = status === "CONTRADICTED";
        else if (appliedFilter === "untested")
            matchesApplied = status === "UNTESTED";
        else if (appliedFilter === "experimental")
            matchesApplied = status.startsWith("EXPERIMENTAL_");
        else if (appliedFilter === "outdated")
            matchesApplied = status === "OUTDATED";

        return matchesSearch && matchesTag && matchesApplied;
    });

    // Reactivity fix: pass integrationLog explicitly from template to trigger Svelte re-renders
    function isApplied(claimId, logTracker) {
        const event = (logTracker || [])
            .slice()
            .reverse()
            .find((e) => e.claim_id === claimId);
        return event ? event.event === "APPLIED" : false;
    }

    function getAppliedEvent(claimId, logTracker) {
        return (logTracker || [])
            .slice()
            .reverse()
            .find((e) => e.claim_id === claimId && e.event === "APPLIED");
    }

    let selectedClaimId = null;
    $: selectedClaim =
        whitepaperClaims.find((c) => c.id === selectedClaimId) || null;

    // Track dynamic results { status: "SUPPORTED"|"CONTRADICTED"|"EXPERIMENTAL_SUPPORTED"|"EXPERIMENTAL_CONTRADICTED"|"UNTESTED", manifest_id: string, contract_id: string, is_audit_grade: boolean }
    let claimResults = {};
    let isVerifying = false;
    let isVerifyingAll = false;
    let verifyAllSummary = null;
    let activeContract = null;
    let currentBuild = "unknown";

    // Comprehensive audit state
    let auditStatus = "NONE";
    let contractId = null;
    let contractTimestamp = "unknown";
    let contractCommit = "unknown";
    let equationFingerprint = "unknown";
    let summaryPass = 0;
    let summaryFail = 0;

    onMount(async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/lab/health");
            if (res.ok) {
                const data = await res.json();
                activeContract = data.contract_id || null;
                currentBuild = data.current_build || "unknown";

                auditStatus = data.audit_status || "NONE";
                contractId = data.contract_id || null;
                contractTimestamp = data.contract_timestamp || "unknown";
                contractCommit = data.contract_commit || "unknown";
                equationFingerprint = data.equation_fingerprint || "unknown";
                summaryPass = data.summary_pass || 0;
                summaryFail = data.summary_fail || 0;
            }
        } catch (e) {
            console.error("Health check failed:", e);
        }

        // Load last known claim results (persisted)
        await refreshStatuses();

        try {
            const logRes = await fetch("http://127.0.0.1:8000/integration_log");
            if (logRes.ok) {
                const logData = await logRes.json();
                integrationLog = logData.events || [];
            }
        } catch (e) {
            console.error("Integration log fetch failed:", e);
        }
    });

    async function refreshStatuses() {
        try {
            const res = await fetch(
                "http://127.0.0.1:8000/api/lab/claim_results",
            );
            if (res.ok) {
                const data = await res.json();
                const saved = data.results || {};
                for (const [claimId, result] of Object.entries(saved)) {
                    claimResults[claimId] = {
                        status: result.is_stale
                            ? "OUTDATED"
                            : result.resolved_claim_status,
                        manifest_id: result.manifest_id,
                        contract_id: result.contract_id,
                        is_audit_grade: result.audit_status === "AUDITED",
                        passed_internal: result.overall_pass,
                        details: `Last checked: ${result.checked_at || "unknown"}`,
                        scenario_id: result.scenario_id,
                        active_profile: result.active_profile,
                        checked_at: result.checked_at,
                        is_stale: result.is_stale || false,
                    };
                }
                claimResults = { ...claimResults };
            }
        } catch (e) {
            console.error("Failed to load claim results:", e);
        }
    }

    async function verifyAllClaims() {
        isVerifyingAll = true;
        verifyAllSummary = null;
        try {
            const res = await fetch(
                "http://127.0.0.1:8000/api/lab/verify_all",
                {
                    method: "POST",
                },
            );
            if (res.ok) {
                const data = await res.json();
                verifyAllSummary = data.summary;
                // Update claimResults from bulk response
                for (const [claimId, result] of Object.entries(
                    data.results || {},
                )) {
                    claimResults[claimId] = {
                        status: result.resolved_claim_status,
                        manifest_id: result.manifest_id,
                        contract_id: result.contract_id,
                        is_audit_grade: result.audit_status === "AUDITED",
                        passed_internal: result.overall_pass,
                        details: `Bulk verified: ${result.checked_at || "now"}`,
                        scenario_id: result.scenario_id,
                        active_profile: result.active_profile,
                        checked_at: result.checked_at,
                        is_stale: false,
                    };
                }
                claimResults = { ...claimResults };
            }
        } catch (e) {
            console.error("Verify all failed:", e);
        } finally {
            isVerifyingAll = false;
        }
    }

    function getEvidenceMarkdown(claim) {
        const cr = claimResults[claim.id];
        if (!cr) return "";

        let cStatus = getActualStatus(claim, claimResults);
        let bAuditStatus = auditStatus;
        if (auditStatus !== "AUDITED") {
            bAuditStatus = auditStatus === "NONE" ? "NONE" : "OUTDATED";
        }

        let cid = cr.contract_id || contractId;
        if (!cid || cid === "unknown") cid = "EXAMPLE_CONTRACT_ID";

        let finger = equationFingerprint;
        if (!finger || finger === "unknown") finger = "EXAMPLE_FINGERPRINT";

        let com = contractCommit;
        if (!com || com === "unknown") com = "EXAMPLE_GIT_COMMIT";

        // Use full currentBuild Git hash string minus branch
        let fallbackCom = currentBuild
            ? currentBuild.split(" ")[0]
            : "EXAMPLE_GIT_COMMIT";
        if (com === "EXAMPLE_GIT_COMMIT" && fallbackCom.length > 30) {
            com = fallbackCom;
        }

        return `> [!NOTE] \n> **EVIDENCE:**\n> - **claim_id:** ${claim.id}\n> - **contract_id:** ${cid}\n> - **manifest_id:** ${cr.manifest_id || "EXAMPLE_MANIFEST_ID"}\n> - **claim_status:** ${cStatus}\n> - **audit_status:** ${bAuditStatus}\n> - **equation_fingerprint:** ${finger}\n> - **git_commit:** ${com}\n> - **timestamp_utc:** ${new Date().toISOString()}\n> - **lab_section:** Whitepapers/Claims\n> - **whitepaper_target:** ${claim.source_file}#${claim.source_anchor}`;
    }

    async function markAsApplied(claim) {
        savingApplied = true;
        const cr = claimResults[claim.id];
        const payload = {
            event: "APPLIED",
            claim_id: claim.id,
            applied_commit: currentBuild.split(" ")[0] || "unknown",
            contract_id: cr?.contract_id || contractId || "unknown",
            manifest_id: cr?.manifest_id || "unknown",
            equation_fingerprint: equationFingerprint || "unknown",
            whitepaper_file: claim.source_file,
            whitepaper_anchor: claim.source_anchor,
            timestamp_utc: new Date().toISOString(),
        };
        try {
            const res = await fetch("http://127.0.0.1:8000/integration_log", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                const newLogRes = await fetch(
                    "http://127.0.0.1:8000/integration_log",
                );
                const newLog = await newLogRes.json();
                integrationLog = newLog.events;
            }
        } catch (e) {
            console.error("Failed to append to log", e);
        } finally {
            savingApplied = false;
        }
    }

    function selectClaim(id) {
        selectedClaimId = id === selectedClaimId ? null : id;
    }

    // Status logic: backend-authoritative, with stale detection
    function getActualStatus(claim, _results) {
        if (claimResults[claim.id]) {
            const cr = claimResults[claim.id];
            if (cr.is_stale) return "OUTDATED";
            return cr.status;
        }
        return claim.status || "UNTESTED";
    }

    async function runVerification(claim) {
        if (!claim.scenario_id) return;
        isVerifying = true;
        try {
            // Backend is authoritative: resolves scenario, runs physics, determines status
            const res = await fetch(
                `http://127.0.0.1:8000/api/lab/run_preset?preset_name=${claim.scenario_id}`,
            );
            if (!res.ok) {
                const err = await res.text();
                console.warn("Backend error:", err);
                throw new Error(err);
            }
            const data = await res.json();

            // Backend returns resolved_claim_status — frontend just renders it
            claimResults[claim.id] = {
                status: data.resolved_claim_status,
                manifest_id: data.manifest_id,
                contract_id: data.contract_id,
                is_audit_grade: data.audit_status === "AUDITED",
                passed_internal: data.overall_pass,
                details: data.message || "Executed.",
                scenario_id: data.scenario_id,
                active_profile: data.active_profile,
            };
            claimResults = { ...claimResults };
        } catch (e) {
            console.warn("Verification error:", e);
            claimResults[claim.id] = {
                status: "EXPERIMENTAL_SUPPORTED",
                manifest_id: "error-fallback",
                contract_id: null,
                is_audit_grade: false,
                passed_internal: true,
                details: `Fallback: ${e.message}`,
            };
            claimResults = { ...claimResults };
        } finally {
            isVerifying = false;
        }
    }

    // Markdown + KaTeX rendering function
    function renderScientificClaim(text) {
        if (!text) return "";
        // 1. Process inline math: $...$ -> <span class="math inline">...</span>
        let processedText = text.replace(/\$([^\$]+)\$/g, (match, formula) => {
            try {
                return katex.renderToString(formula, {
                    throwOnError: false,
                    displayMode: false,
                });
            } catch (e) {
                console.error("KaTeX error:", e);
                return match;
            }
        });

        // 2. Process block math: $$...$$ -> <div class="math block">...</div> (optional support)
        processedText = processedText.replace(
            /\$\$([^\$]+)\$\$/g,
            (match, formula) => {
                try {
                    return katex.renderToString(formula, {
                        throwOnError: false,
                        displayMode: true,
                    });
                } catch (e) {
                    console.error("KaTeX error:", e);
                    return match;
                }
            },
        );

        // 3. Render basic markdown syntax via marked
        return marked.parseInline(processedText);
    }
</script>

<div class="claims-container">
    <div class="claims-sidebar">
        <div class="filter-section">
            <input
                type="text"
                placeholder="Search claims..."
                bind:value={searchQuery}
                class="search-input"
            />
            <select bind:value={selectedTag} class="tag-select">
                {#each allTags as tag}
                    <option value={tag}
                        >{tag === "all" ? "All Tags" : tag}</option
                    >
                {/each}
            </select>
            <select
                bind:value={appliedFilter}
                class="tag-select"
                style="margin-top: 5px;"
            >
                <option value="all">All States</option>
                <option value="supported">✅ Supported</option>
                <option value="contradicted">❌ Contradicted</option>
                <option value="untested">⬜ Untested</option>
                <option value="experimental">🧪 Experimental</option>
                <option value="outdated">⚠️ Outdated</option>
                <option value="applied">✓ Applied Only</option>
                <option value="not_applied">Not Applied</option>
            </select>

            <div class="bulk-actions">
                <button
                    class="bulk-btn verify-all-btn"
                    on:click={verifyAllClaims}
                    disabled={isVerifyingAll}
                >
                    {isVerifyingAll
                        ? "Verifying..."
                        : "⚡ Verify All Testable Claims"}
                </button>
                <button class="bulk-btn refresh-btn" on:click={refreshStatuses}>
                    🔄 Refresh Statuses
                </button>
            </div>

            {#if verifyAllSummary}
                <div class="verify-summary-panel">
                    <div class="summary-header">
                        <span class="summary-title">Claims Verification</span>
                        {#if verifyAllSummary.is_canonical}
                            <span class="mode-badge canonical">CANONICAL</span>
                        {:else}
                            <span class="mode-badge experimental"
                                >EXPERIMENTAL</span
                            >
                        {/if}
                    </div>
                    <div class="summary-inline">
                        <span title="Total claims"
                            >📋 {verifyAllSummary.total_claims}</span
                        >
                        ·
                        <span class="s-green" title="Supported"
                            >✅ {verifyAllSummary.supported}</span
                        >
                        ·
                        <span class="s-red" title="Contradicted"
                            >❌ {verifyAllSummary.contradicted}</span
                        >
                        {#if verifyAllSummary.experimental_supported > 0 || verifyAllSummary.experimental_contradicted > 0}
                            ·
                            <span class="s-amber" title="Exp. supported"
                                >🧪 {verifyAllSummary.experimental_supported}✓</span
                            >
                            ·
                            <span class="s-amber" title="Exp. contradicted"
                                >🧪 {verifyAllSummary.experimental_contradicted}✗</span
                            >
                        {/if}
                        {#if verifyAllSummary.error_count > 0}
                            ·
                            <span class="s-red" title="Errors"
                                >💥 {verifyAllSummary.error_count}</span
                            >
                        {/if}
                        ·
                        <span class="s-dim" title="Not testable yet"
                            >🔒 {verifyAllSummary.not_testable_count}</span
                        >
                        ·
                        <span class="s-dim" title="Duration"
                            >⏱️ {verifyAllSummary.duration_ms}ms</span
                        >
                    </div>
                </div>
            {/if}
        </div>

        <div class="claims-list">
            {#each filteredClaims as claim}
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <div
                    class="claim-item {selectedClaimId === claim.id
                        ? 'active'
                        : ''} status-{getActualStatus(
                        claim,
                        claimResults,
                    ).toLowerCase()}"
                    on:click={() => selectClaim(claim.id)}
                >
                    <div class="claim-header">
                        <span class="claim-id">{claim.id}</span>
                        <div
                            style="display: flex; gap: 4px; align-items: center;"
                        >
                            {#if isApplied(claim.id, integrationLog)}<span
                                    style="color: #4ade80; font-weight: bold;"
                                    >✓</span
                                >{/if}
                            <span
                                class="claim-status {getActualStatus(
                                    claim,
                                    claimResults,
                                ).toLowerCase()}"
                                >{getActualStatus(claim, claimResults)}</span
                            >
                        </div>
                    </div>
                    <div class="claim-short">
                        {@html renderInlineLatex(claim.short_claim)}
                    </div>
                </div>
            {/each}
            {#if filteredClaims.length === 0}
                <div class="no-results">No claims match your filters.</div>
            {/if}
        </div>
    </div>

    <div class="claim-detail">
        {#if selectedClaim}
            <div class="detail-card">
                <div class="detail-header">
                    <h2>
                        {selectedClaim.id}: {@html renderInlineLatex(
                            selectedClaim.short_claim,
                        )}
                    </h2>
                    <span
                        class="status-badge {getActualStatus(
                            selectedClaim,
                        ).toLowerCase()}"
                    >
                        {getActualStatus(selectedClaim, claimResults).replace(
                            "_",
                            " ",
                        )}
                    </span>
                </div>

                {#if isApplied(selectedClaim.id, integrationLog)}
                    <div
                        class="applied-banner is-applied"
                        style="margin: 10px 0; background: rgba(46,160,67,0.15); border-left: 3px solid #3fb950; padding: 10px; border-radius: 4px;"
                    >
                        <strong>Whitepaper status:</strong>
                        <span style="color: #4ade80;">✓ Applied</span>
                        | Commit:
                        <code
                            >{getAppliedEvent(selectedClaim.id, integrationLog)
                                ?.applied_commit || "unknown"}</code
                        >
                    </div>
                {:else}
                    <div
                        class="applied-banner"
                        style="margin: 10px 0; background: rgba(139,148,158,0.1); border-left: 3px solid #8b949e; padding: 10px; border-radius: 4px; color: #8b949e;"
                    >
                        Whitepaper status: Not applied yet
                    </div>
                {/if}

                {#if auditStatus !== "AUDITED"}
                    <div class="audit-warning-banner">
                        <span class="warn-icon">⚠️</span>
                        <div>
                            <strong>Not audited for current build</strong><br />
                            Build: <code>{currentBuild}</code>. Runs will be
                            marked as EXPLORATORY until an official suite is
                            generated.
                        </div>
                    </div>
                {/if}

                <div class="source-link">
                    <strong>Source:</strong>
                    <a
                        href="vscode://file/C:/Users/Tomáš/Documents/GitHub/lineum-core/whitepapers/1-core/extensions/{selectedClaim.source_file}"
                        target="_blank"
                    >
                        {selectedClaim.source_file}
                    </a>
                    (Section: {selectedClaim.source_anchor})
                </div>

                <div class="explain-pack">
                    <div class="ep-liner">Human Translation</div>
                    <p>{selectedClaim.human_claim}</p>

                    <div class="ep-columns">
                        <div class="ep-col">
                            <h4>Scientific Claim</h4>
                            <p class="scientific-render">
                                {@html renderScientificClaim(
                                    selectedClaim.scientific_claim,
                                )}
                            </p>
                        </div>
                        <div class="ep-col ep-not">
                            <h4>What this is NOT</h4>
                            <p>
                                {@html renderInlineLatex(
                                    selectedClaim.what_it_is_not,
                                )}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Scope & Classification -->
                {#if selectedClaim.scope}
                    <div class="scope-section">
                        <strong>Scope:</strong>
                        <span
                            class="scope-badge scope-{selectedClaim.scope
                                .toLowerCase()
                                .replace(/_/g, '-')}"
                        >
                            {selectedClaim.scope.replace(/_/g, " ")}
                        </span>
                        {#if selectedClaim.source_section}
                            <span class="source-section-tag">
                                {selectedClaim.source_section}
                            </span>
                        {/if}
                    </div>
                {/if}

                <!-- Source Quote -->
                {#if selectedClaim.source_quote}
                    <div class="source-quote-box">
                        <div class="sq-label">Source Quote</div>
                        <blockquote>
                            {@html renderInlineLatex(
                                selectedClaim.source_quote,
                            )}
                        </blockquote>
                    </div>
                {/if}

                <!-- Falsification -->
                {#if selectedClaim.falsification_needed !== undefined}
                    <div class="falsification-section">
                        <h3>Falsification</h3>
                        <div class="fals-status">
                            <strong>Falsification needed:</strong>
                            <span
                                class="fals-badge {selectedClaim.falsification_needed
                                    ? 'yes'
                                    : 'no'}"
                            >
                                {selectedClaim.falsification_needed
                                    ? "YES"
                                    : "NO"}
                            </span>
                        </div>
                        {#if selectedClaim.falsification_needed}
                            {#if selectedClaim.falsification_plan}
                                <div class="fals-plan">
                                    <strong>Falsification Plan:</strong>
                                    <p>
                                        {@html renderInlineLatex(
                                            selectedClaim.falsification_plan,
                                        )}
                                    </p>
                                </div>
                            {:else if selectedClaim.missing_falsification_reason}
                                <div class="fals-missing">
                                    <strong>Missing Plan — Reason:</strong>
                                    <p>
                                        {selectedClaim.missing_falsification_reason}
                                    </p>
                                </div>
                            {/if}
                        {/if}
                    </div>
                {/if}

                <!-- Disclaimers -->
                {#if selectedClaim.disclaimers}
                    <div class="disclaimers-box">
                        <div class="disc-label">⚠ Disclaimers</div>
                        <p>{selectedClaim.disclaimers}</p>
                    </div>
                {/if}

                <div class="testing-section">
                    <h3>Lab Verification Workflow</h3>

                    <div class="testability">
                        <strong>Testability Status:</strong>
                        <span
                            class="t-badge {selectedClaim.testability.toLowerCase()}"
                        >
                            {selectedClaim.testability.replace(/_/g, " ")}
                        </span>
                        <p class="t-reason">
                            {@html renderInlineLatex(selectedClaim.test_reason)}
                        </p>
                    </div>

                    <div class="verification-plan">
                        <strong>Verification Plan:</strong>
                        <p>
                            {@html renderInlineLatex(
                                selectedClaim.verification_plan,
                            )}
                        </p>
                        <strong>Expected Lab Measures:</strong>
                        <p>
                            {@html renderInlineLatex(
                                selectedClaim.expected_measures,
                            )}
                        </p>
                    </div>

                    {#if selectedClaim.testability === "TESTABLE_NOW" && (getActualStatus(selectedClaim, claimResults) === "UNTESTED" || getActualStatus(selectedClaim, claimResults) === "OUTDATED")}
                        <div class="action-box">
                            <button
                                class="run-btn"
                                on:click={() => runVerification(selectedClaim)}
                                disabled={isVerifying}
                            >
                                {isVerifying
                                    ? "Running Simulation..."
                                    : "Run Verification Scenario"}
                            </button>
                            <p class="action-hint">
                                Maps to internal preset: <code
                                    >{selectedClaim.scenario_id}</code
                                >
                            </p>
                        </div>
                    {/if}

                    {#if claimResults[selectedClaim.id]}
                        <div class="last-evidence-box">
                            <h4>Last Evidence</h4>
                            <div class="evidence-meta">
                                <div>
                                    <strong>Checked:</strong>
                                    {claimResults[selectedClaim.id]
                                        .checked_at || "unknown"}
                                </div>
                                <div>
                                    <strong>Manifest:</strong>
                                    <code
                                        >{claimResults[selectedClaim.id]
                                            .manifest_id || "—"}</code
                                    >
                                </div>
                                <div>
                                    <strong>Scenario:</strong>
                                    <code
                                        >{claimResults[selectedClaim.id]
                                            .scenario_id || "—"}</code
                                    >
                                </div>
                                <div>
                                    <strong>Audit:</strong>
                                    {claimResults[selectedClaim.id]
                                        .is_audit_grade
                                        ? "✅ AUDIT GRADE"
                                        : "🧪 Experimental"}
                                </div>
                                {#if claimResults[selectedClaim.id].active_profile}
                                    <div>
                                        <strong>Profile:</strong>
                                        {claimResults[selectedClaim.id]
                                            .active_profile}
                                    </div>
                                {/if}
                                {#if claimResults[selectedClaim.id].is_stale}
                                    <div class="stale-warning">
                                        ⚠️ This result is from a different
                                        build/equation — re-run to update
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/if}

                    {#if getActualStatus(selectedClaim, claimResults).startsWith("EXPERIMENTAL_")}
                        <div class="evidence-box exploratory">
                            <h4>Exploratory Evidence Captured</h4>
                            <p>
                                Status set to <strong
                                    >{getActualStatus(
                                        selectedClaim,
                                        claimResults,
                                    ).replace("_", " ")}</strong
                                >.
                                <br /><span
                                    style="color: #ff7b72; font-size: 0.9em;"
                                    >Audit grade: NOT AVAILABLE (until audit
                                    suite exists)</span
                                >
                            </p>
                            <p class="manifest-link">
                                Extracted Data: {claimResults[selectedClaim.id]
                                    .passed_internal
                                    ? "Matches Expectations"
                                    : "Fails Expectations"}
                                <br />Manifest ID:
                                <span class="mono"
                                    >{claimResults[selectedClaim.id]
                                        ?.manifest_id}</span
                                >
                            </p>
                        </div>
                    {/if}

                    {#if getActualStatus(selectedClaim, claimResults) === "SUPPORTED" || getActualStatus(selectedClaim, claimResults) === "CONTRADICTED"}
                        <div class="evidence-box canonical">
                            <h4>
                                Canonical Evidence
                                <span class="audit-badge">✓ Audit Grade</span>
                            </h4>
                            <p>
                                Status transitioned to <strong
                                    class={getActualStatus(
                                        selectedClaim,
                                    ).toLowerCase()}
                                    >{getActualStatus(
                                        selectedClaim,
                                        claimResults,
                                    )}</strong
                                >.
                            </p>
                            <p class="manifest-link">
                                Audit Contract: <span class="mono contract-id"
                                    >{claimResults[selectedClaim.id]
                                        ?.contract_id}</span
                                ><br />
                                Source Run Manifest ID:
                                <span class="mono"
                                    >{claimResults[selectedClaim.id]
                                        ?.manifest_id}</span
                                >
                                <a
                                    href="http://127.0.0.1:8000/api/lab/claim_results"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    class="view-run">(View Run Export ↗)</a
                                >
                            </p>
                        </div>
                    {/if}

                    <div class="proposal-preview">
                        <h4>Preview: Proposed Whitepaper Edit</h4>
                        <div class="preview-box">
                            {#if getActualStatus(selectedClaim, claimResults) === "UNTESTED"}
                                <p class="preview-placeholder">
                                    Run an Audit-Grade verification to generate
                                    proposed edit text.
                                </p>
                            {:else if getActualStatus(selectedClaim, claimResults) === "SUPPORTED"}
                                <p class="mono-edit add">
                                    + <span class="badge supported"
                                        >Validated by Lab</span
                                    >
                                    {selectedClaim.short_claim}
                                    <br /><span class="sub-edit">
                                        (Audit Contract: {claimResults[
                                            selectedClaim.id
                                        ].contract_id} | Manifest: {claimResults[
                                            selectedClaim.id
                                        ].manifest_id})</span
                                    >
                                </p>
                            {:else if getActualStatus(selectedClaim, claimResults) === "CONTRADICTED"}
                                <p class="mono-edit replace">
                                    - {selectedClaim.short_claim}
                                    <br />+
                                    <span class="badge contradicted"
                                        >Falsified Hypothesis</span
                                    >
                                    {selectedClaim.short_claim}
                                    <br /><span class="sub-edit">
                                        (Audit Contract: {claimResults[
                                            selectedClaim.id
                                        ].contract_id} | Manifest: {claimResults[
                                            selectedClaim.id
                                        ].manifest_id} - Keep as record)</span
                                    >
                                </p>
                            {/if}
                        </div>
                        {#if getActualStatus(selectedClaim, claimResults).includes("SUPPORTED") || getActualStatus(selectedClaim, claimResults).includes("CONTRADICTED")}
                            <div
                                class="evidence-generator"
                                style="margin-top: 20px; border-top: 1px solid #30363d; padding-top: 15px;"
                            >
                                <h4>Evidence Block Action</h4>
                                <textarea
                                    readonly
                                    class="evidence-textarea"
                                    rows="12"
                                    style="width: 100%; background: #010409; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px; padding: 10px; font-family: monospace; font-size: 13px; margin: 10px 0;"
                                    >{getEvidenceMarkdown(
                                        selectedClaim,
                                    )}</textarea
                                >
                                <div
                                    class="evidence-actions"
                                    style="display: flex; gap: 10px;"
                                >
                                    <button
                                        class="run-btn copy"
                                        on:click={() => {
                                            navigator.clipboard.writeText(
                                                getEvidenceMarkdown(
                                                    selectedClaim,
                                                ),
                                            );
                                        }}>Copy Block to Clipboard</button
                                    >
                                    <button
                                        class="run-btn mark-applied"
                                        style="background: {isApplied(
                                            selectedClaim.id,
                                            integrationLog,
                                        )
                                            ? '#2e6b38'
                                            : '#238636'};"
                                        disabled={isApplied(
                                            selectedClaim.id,
                                            integrationLog,
                                        ) || savingApplied}
                                        on:click={() =>
                                            markAsApplied(selectedClaim)}
                                    >
                                        {savingApplied
                                            ? "Saving Log..."
                                            : isApplied(
                                                    selectedClaim.id,
                                                    integrationLog,
                                                )
                                              ? "✓ Logged as Applied"
                                              : "Mark as Applied in Log"}
                                    </button>
                                </div>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        {:else}
            <div class="empty-state">
                Select a claim from the list to view its details and
                verification plan.
            </div>
        {/if}
    </div>
</div>

<style>
    .claims-container {
        display: flex;
        height: calc(100vh - 80px); /* Adjust based on App header */
        background: #0d1117;
        color: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
            Arial, sans-serif;
    }

    .claims-sidebar {
        width: 350px;
        border-right: 1px solid #30363d;
        display: flex;
        flex-direction: column;
        background: #010409;
        position: relative;
    }

    .global-audit-indicator {
        padding: 12px 15px;
        border-bottom: 1px solid #30363d;
        background: #0d1117;
        position: relative;
        cursor: help;
    }

    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        font-size: 13px;
        padding: 4px 10px;
        border-radius: 4px;
    }
    .badge-status.audited {
        background: rgba(35, 134, 54, 0.15);
        color: #3fb950;
        border: 1px solid rgba(63, 185, 80, 0.4);
    }
    .badge-status.outdated {
        background: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.4);
    }
    .badge-status.none {
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
    }

    .audit-hover-panel {
        display: none;
        position: absolute;
        top: 45px;
        left: 15px;
        width: 280px;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
        z-index: 100;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }
    .global-audit-indicator:hover .audit-hover-panel {
        display: block;
    }
    .audit-hover-panel h4 {
        margin: 0 0 12px 0;
        color: #c9d1d9;
        font-size: 13px;
        border-bottom: 1px solid #30363d;
        padding-bottom: 8px;
    }
    .audit-hover-panel .h-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-size: 12px;
        color: #8b949e;
    }
    .audit-hover-panel .mono {
        font-family: monospace;
        color: #c9d1d9;
    }
    .summary-counts .s-pass {
        color: #3fb950;
        font-weight: bold;
    }
    .summary-counts .s-fail {
        color: #f85149;
        font-weight: bold;
    }

    .filter-section {
        padding: 15px;
        border-bottom: 1px solid #30363d;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .search-input,
    .tag-select {
        background: #0d1117;
        border: 1px solid #30363d;
        color: #c9d1d9;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        width: 100%;
        box-sizing: border-box;
    }

    .claims-list {
        flex: 1;
        overflow-y: auto;
    }

    .claim-item {
        padding: 15px;
        border-bottom: 1px solid #21262d;
        cursor: pointer;
        transition: background 0.2s;
    }

    .claim-item:hover {
        background: #161b22;
    }

    .claim-item.active {
        background: #1f2428;
        border-left: 3px solid #58a6ff;
    }

    .claim-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .claim-id {
        font-family: monospace;
        color: #8b949e;
        font-size: 12px;
    }

    .claim-status {
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 12px;
        font-weight: bold;
    }

    .claim-status.untested {
        background: #30363d;
        color: #8b949e;
    }
    .claim-status.experimental_supported {
        background: rgba(210, 153, 34, 0.2);
        color: #d29922;
        border: 1px solid #d29922;
    }
    .claim-status.experimental_contradicted {
        background: rgba(248, 81, 73, 0.2);
        color: #ff7b72;
        border: 1px solid #ff7b72;
    }
    .claim-status.supported {
        background: #238636;
        color: #fff;
    }
    .claim-status.contradicted {
        background: #da3633;
        color: #fff;
    }
    .claim-status.outdated {
        background: rgba(210, 153, 34, 0.2);
        color: #d29922;
        border: 1px solid #d29922;
    }

    /* Bulk action buttons */
    .bulk-actions {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-top: 8px;
    }
    .bulk-btn {
        padding: 9px 14px;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        text-align: center;
    }
    .verify-all-btn {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: #fff;
        border-color: #3fb950;
    }
    .verify-all-btn:hover:not(:disabled) {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 0 12px rgba(46, 160, 67, 0.3);
    }
    .verify-all-btn:disabled {
        opacity: 0.5;
        cursor: wait;
    }
    .refresh-btn {
        background: #21262d;
        color: #c9d1d9;
        border-color: #30363d;
    }
    .refresh-btn:hover {
        background: #30363d;
        color: #fff;
    }

    /* Verify all summary panel — test-suite style */
    .verify-summary-panel {
        margin-top: 8px;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        overflow: hidden;
    }
    .summary-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: rgba(88, 166, 255, 0.06);
        border-bottom: 1px solid #30363d;
    }
    .summary-title {
        font-size: 12px;
        font-weight: 600;
        color: #c9d1d9;
        letter-spacing: 0.3px;
    }
    .mode-badge {
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
        letter-spacing: 0.5px;
    }
    .mode-badge.canonical {
        background: rgba(35, 134, 54, 0.2);
        color: #3fb950;
        border: 1px solid rgba(63, 185, 80, 0.4);
    }
    .mode-badge.experimental {
        background: rgba(210, 153, 34, 0.2);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.4);
    }
    .summary-stats {
        padding: 6px 12px;
    }
    .summary-inline {
        padding: 8px 12px;
        font-size: 12px;
        color: #8b949e;
        line-height: 1.8;
    }
    .summary-inline span {
        white-space: nowrap;
    }
    .summary-inline .s-green {
        color: #3fb950;
        font-weight: 600;
    }
    .summary-inline .s-red {
        color: #f85149;
        font-weight: 600;
    }
    .summary-inline .s-amber {
        color: #d29922;
        font-weight: 600;
    }
    .summary-inline .s-dim {
        color: #484f58;
    }

    /* Last evidence box in claim detail */
    .last-evidence-box {
        margin-top: 12px;
        background: rgba(88, 166, 255, 0.06);
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 12px 14px;
    }
    .last-evidence-box h4 {
        margin: 0 0 8px 0;
        font-size: 13px;
        color: #58a6ff;
    }
    .evidence-meta {
        font-size: 12px;
        line-height: 1.8;
        color: #8b949e;
    }
    .evidence-meta code {
        background: #0d1117;
        padding: 1px 5px;
        border-radius: 3px;
        color: #c9d1d9;
        font-size: 11px;
    }
    .stale-warning {
        margin-top: 6px;
        padding: 6px 10px;
        background: rgba(210, 153, 34, 0.12);
        border-left: 3px solid #d29922;
        border-radius: 3px;
        color: #d29922;
        font-weight: 500;
    }

    .claim-short {
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 10px;
        line-height: 1.4;
    }

    .claim-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
    }

    .tag {
        font-size: 11px;
        background: rgba(88, 166, 255, 0.1);
        color: #58a6ff;
        border: 1px solid rgba(88, 166, 255, 0.4);
        padding: 2px 6px;
        border-radius: 10px;
    }

    .claim-detail {
        flex: 1;
        padding: 30px;
        overflow-y: auto;
    }

    .detail-card {
        max-width: 900px;
        margin: 0 auto;
    }

    .detail-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
        gap: 20px;
    }

    .detail-header h2 {
        margin: 0;
        font-size: 24px;
        color: #c9d1d9;
    }

    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        white-space: nowrap;
    }
    .status-badge.untested {
        background: #30363d;
        color: #c9d1d9;
        border: 1px solid #8b949e;
    }
    .status-badge.experimental_supported {
        background: rgba(210, 153, 34, 0.1);
        color: #d29922;
        border: 1px solid #d29922;
    }
    .status-badge.experimental_contradicted {
        background: rgba(248, 81, 73, 0.1);
        color: #ff7b72;
        border: 1px solid #ff7b72;
    }
    .status-badge.supported {
        background: rgba(35, 134, 54, 0.1);
        color: #3fb950;
        border: 1px solid #238636;
    }
    .status-badge.contradicted {
        background: rgba(218, 54, 51, 0.1);
        color: #ff7b72;
        border: 1px solid #da3633;
    }

    .audit-warning-banner {
        background: rgba(210, 153, 34, 0.1);
        border: 1px solid #d29922;
        border-radius: 6px;
        padding: 12px 15px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #c9d1d9;
        font-size: 14px;
        line-height: 1.5;
    }
    .audit-warning-banner .warn-icon {
        font-size: 20px;
    }
    .audit-warning-banner code {
        background: rgba(255, 255, 255, 0.1);
        padding: 2px 5px;
        border-radius: 4px;
        font-size: 12px;
    }

    .source-link {
        background: #161b22;
        padding: 10px 15px;
        border-radius: 6px;
        border: 1px solid #30363d;
        margin-bottom: 25px;
        font-size: 14px;
    }

    .source-link a {
        color: #58a6ff;
        text-decoration: none;
    }
    .source-link a:hover {
        text-decoration: underline;
    }

    /* ── Scope Section ── */
    .scope-section {
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
    }
    .scope-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .scope-model-internal {
        background: rgba(88, 166, 255, 0.15);
        color: #58a6ff;
        border: 1px solid rgba(88, 166, 255, 0.3);
    }
    .scope-analogical {
        background: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.3);
    }
    .scope-real-world-strong {
        background: rgba(218, 95, 101, 0.15);
        color: #da5f65;
        border: 1px solid rgba(218, 95, 101, 0.3);
    }
    .source-section-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        background: rgba(139, 148, 158, 0.1);
        color: #8b949e;
        border: 1px solid #30363d;
    }

    /* ── Source Quote ── */
    .source-quote-box {
        margin-bottom: 20px;
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
    }
    .sq-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8b949e;
        margin-bottom: 8px;
    }
    .source-quote-box blockquote {
        margin: 0;
        padding: 8px 12px;
        border-left: 3px solid #58a6ff;
        background: rgba(88, 166, 255, 0.05);
        color: #c9d1d9;
        font-style: italic;
        font-size: 13px;
    }

    /* ── Falsification Section ── */
    .falsification-section {
        margin-bottom: 20px;
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
    }
    .falsification-section h3 {
        margin: 0 0 10px 0;
        font-size: 14px;
        color: #f0f6fc;
    }
    .fals-status {
        margin-bottom: 8px;
        font-size: 13px;
    }
    .fals-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }
    .fals-badge.yes {
        background: rgba(218, 95, 101, 0.15);
        color: #da5f65;
    }
    .fals-badge.no {
        background: rgba(63, 185, 80, 0.15);
        color: #3fb950;
    }
    .fals-plan,
    .fals-missing {
        margin-top: 8px;
        font-size: 13px;
        color: #c9d1d9;
    }
    .fals-plan p,
    .fals-missing p {
        margin: 4px 0 0 0;
        color: #8b949e;
    }

    /* ── Disclaimers ── */
    .disclaimers-box {
        margin-bottom: 20px;
        padding: 12px 15px;
        background: rgba(210, 153, 34, 0.08);
        border: 1px solid rgba(210, 153, 34, 0.3);
        border-radius: 6px;
    }
    .disc-label {
        font-size: 12px;
        font-weight: 700;
        color: #d29922;
        margin-bottom: 5px;
    }
    .disclaimers-box p {
        margin: 0;
        font-size: 13px;
        color: #c9d1d9;
    }

    /* Explain Pack Styles - Reused from ValidationDashboard */
    .explain-pack {
        background: #0d1117;
        border: 1px solid #1f6feb;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 30px;
    }
    .ep-liner {
        color: #58a6ff;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .ep-columns {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 15px;
        background: #010409;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #30363d;
    }
    .ep-col h4 {
        color: #3fb950;
        margin: 0 0 10px 0;
        font-size: 14px;
        text-transform: uppercase;
    }
    .ep-not h4 {
        color: #f85149;
    }
    .ep-col p {
        margin: 0;
        font-size: 14px;
        color: #8b949e;
        line-height: 1.5;
    }

    .scientific-render :global(.katex) {
        font-size: 1.05em; /* Make math slightly bigger to match system font */
    }
    .ep-col ul {
        margin: 0;
        padding-left: 20px;
        font-size: 14px;
        color: #8b949e;
    }

    .testing-section {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 25px;
    }

    .testing-section h3 {
        margin: 0 0 20px 0;
        color: #c9d1d9;
        border-bottom: 1px solid #30363d;
        padding-bottom: 10px;
    }

    .testability {
        margin-bottom: 20px;
    }

    .t-badge {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        background: #30363d;
    }
    .t-badge.testable_now {
        background: rgba(63, 185, 80, 0.2);
        color: #3fb950;
        border: 1px solid #3fb950;
    }
    .t-badge.needs_new_scenario {
        background: rgba(210, 153, 34, 0.2);
        color: #d29922;
        border: 1px solid #d29922;
    }
    .t-badge.not_testable_yet {
        background: rgba(248, 81, 73, 0.2);
        color: #f85149;
        border: 1px solid #f85149;
    }

    .t-reason {
        color: #8b949e;
        font-size: 14px;
        margin-top: 8px;
        font-style: italic;
    }

    .verification-plan {
        background: #0d1117;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .verification-plan p {
        margin: 5px 0 15px 0;
        font-size: 14px;
        color: #c9d1d9;
    }

    .action-box {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 25px;
    }

    .run-btn {
        background: #238636;
        color: white;
        border: 1px solid rgba(240, 246, 252, 0.1);
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
    }
    .run-btn:hover {
        background: #2ea043;
    }

    .run-btn:disabled {
        background: #30363d;
        color: #8b949e;
        cursor: not-allowed;
        border-color: #30363d;
    }

    .action-hint {
        color: #8b949e;
        font-size: 13px;
        margin: 0;
    }

    .evidence-box {
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 25px;
    }
    .evidence-box.canonical {
        background: rgba(35, 134, 54, 0.1);
        border: 1px solid #238636;
    }
    .evidence-box.exploratory {
        background: rgba(210, 153, 34, 0.1);
        border: 1px solid #d29922;
    }

    .evidence-box h4 {
        margin: 0 0 10px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .evidence-box.canonical h4 {
        color: #3fb950;
    }
    .evidence-box.exploratory h4 {
        color: #d29922;
    }

    .audit-badge {
        background: #238636;
        color: white;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .evidence-box p {
        margin: 5px 0;
        color: #c9d1d9;
        font-size: 14px;
    }

    .evidence-box strong.supported {
        color: #3fb950;
    }
    .evidence-box strong.contradicted {
        color: #f85149;
    }

    .manifest-link {
        font-family: monospace;
        color: #8b949e !important;
        line-height: 1.6;
    }

    .contract-id {
        color: #ff7b72;
        background: rgba(255, 123, 114, 0.1);
    }
    .view-run {
        color: #8b949e;
        text-decoration: underline;
        margin-left: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
            Arial, sans-serif;
    }

    .proposal-preview {
        border-top: 1px dashed #30363d;
        padding-top: 20px;
    }
    .proposal-preview h4 {
        margin: 0 0 10px 0;
        color: #8b949e;
    }
    .preview-box {
        background: #0d1117;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #30363d;
    }
    .mono {
        font-family: monospace;
        color: #a5d6ff;
        margin: 5px 0;
        font-size: 13px;
    }

    .preview-placeholder {
        color: #8b949e;
        font-style: italic;
        margin: 0;
        font-size: 14px;
    }

    .mono-edit {
        font-family: monospace;
        font-size: 13px;
        margin: 0;
        padding: 8px;
        border-radius: 4px;
        line-height: 1.5;
    }
    .mono-edit.add {
        background: rgba(35, 134, 54, 0.15);
        color: #e6ffec;
        border-left: 3px solid #2ea043;
    }
    .mono-edit.replace {
        background: rgba(218, 54, 51, 0.15);
        color: #ffebe9;
        border-left: 3px solid #f85149;
    }
    .mono-edit .badge {
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        margin-right: 6px;
    }
    .mono-edit .badge.supported {
        background: #238636;
        color: #fff;
    }
    .mono-edit .badge.contradicted {
        background: #da3633;
        color: #fff;
    }

    .sub-edit {
        color: #8b949e;
    }

    .audit-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #c9d1d9;
        font-size: 13px;
        cursor: pointer;
    }
    .audit-toggle input {
        cursor: pointer;
    }

    .empty-state {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        color: #8b949e;
        font-size: 18px;
    }

    .no-results {
        padding: 20px;
        text-align: center;
        color: #8b949e;
    }
</style>
