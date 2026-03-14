<script>
    import { t } from "../i18n.js";
    import { whitepaperClaims } from "../data/claims.js";
    import whitepaperMap from "../data/whitepaper_map.json";
    import { marked } from "marked";
    import katex from "katex";
    import "katex/dist/katex.min.css";
    import { onMount } from "svelte";
    import CollapsibleBox from "./CollapsibleBox.svelte";

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

    export const manifestHistory = []; // Array of { id, preset, passed, mode }
    export let isGeneratingAudit = false;

    let searchQuery =
        typeof window !== "undefined"
            ? localStorage.getItem("wc_search") || ""
            : "";
    let selectedTag = "all";
    let statusFilter =
        typeof window !== "undefined"
            ? localStorage.getItem("wc_status") || "all"
            : "all";
    let testabilityFilter =
        typeof window !== "undefined"
            ? localStorage.getItem("wc_testability") || "all"
            : "all";
    let scopeFilter =
        typeof window !== "undefined"
            ? localStorage.getItem("wc_scope") || "all"
            : "all";
    let falsificationFilter =
        typeof window !== "undefined"
            ? localStorage.getItem("wc_falsification") || "all"
            : "all";

    let selectedWhitepaper =
        typeof window !== "undefined"
            ? localStorage.getItem("wc_whitepaper") || "all"
            : "all";
            
    let isFiltersExpanded = false;

    $: hasActiveFilters =
        searchQuery !== "" ||
        selectedTag !== "all" ||
        statusFilter !== "all" ||
        testabilityFilter !== "all" ||
        scopeFilter !== "all" ||
        falsificationFilter !== "all" ||
        selectedWhitepaper !== "all";

    function clearFilters() {
        searchQuery = "";
        selectedTag = "all";
        statusFilter = "all";
        testabilityFilter = "all";
        scopeFilter = "all";
        falsificationFilter = "all";
        selectedWhitepaper = "all";
    }

    let integrationLog = [];
    let savingApplied = false;
    let isPromotionBlockExpanded = false;

    // Derived tags list
    $: allTags = [
        "all",
        ...new Set(whitepaperClaims.flatMap((c) => c.tags)),
    ].sort();

    // Derived whitepapers list
    $: allWhitepapers = [
        "all",
        ...new Set(whitepaperClaims.map((c) => c.source_file).filter(Boolean)),
    ].sort();

    // Filter claims
    $: filteredClaims = whitepaperClaims.filter((claim) => {
        const matchesSearch =
            (claim.id || "").toLowerCase().includes((searchQuery || "").toLowerCase()) ||
            (claim.short_claim || "").toLowerCase().includes((searchQuery || "").toLowerCase()) ||
            (claim.human_claim || "").toLowerCase().includes((searchQuery || "").toLowerCase());
        const matchesTag =
            selectedTag === "all" || claim.tags.includes(selectedTag);

        const appliedState = isApplied(claim.id, integrationLog);
        const status = getActualStatus(claim, claimResults);
        let matchesStatus = true;
        if (statusFilter === "applied") matchesStatus = appliedState;
        else if (statusFilter === "not_applied") matchesStatus = !appliedState;
        else if (statusFilter === "supported")
            matchesStatus = status === "SUPPORTED";
        else if (statusFilter === "contradicted")
            matchesStatus = status === "CONTRADICTED";
        else if (statusFilter === "untested")
            matchesStatus = status === "UNTESTED";
        else if (statusFilter === "experimental")
            matchesStatus = status.startsWith("EXPERIMENTAL_");
        else if (statusFilter === "outdated")
            matchesStatus = status === "OUTDATED";

        const matchesTestability =
            testabilityFilter === "all" ||
            claim.testability === testabilityFilter;
        const matchesScope =
            scopeFilter === "all" || claim.scope === scopeFilter;
        const matchesFalsification =
            falsificationFilter === "all" ||
            (falsificationFilter === "needed"
                ? claim.falsification_needed === true
                : true);
        const matchesWhitepaper =
            selectedWhitepaper === "all" || claim.source_file === selectedWhitepaper;

        return (
            matchesSearch &&
            matchesTag &&
            matchesStatus &&
            matchesTestability &&
            matchesScope &&
            matchesFalsification &&
            matchesWhitepaper
        );
    });

    // SINGLE SOURCE OF TRUTH for Claim Verdict (Pure pass/fail constraint, no provenance)
    function getActualStatus(claim, results, isActive) {
        if (
            claim.testability === "NOT_TESTABLE_YET" ||
            claim.testability === "NEEDS_NEW_SCENARIO"
        ) {
            return "UNTESTED";
        }
        if (isActive) {
            return "AUDIT_RUNNING";
        }

        const cr = (results || {})[claim.id] || {};
        
        // Return raw verdict from API (SUPPORTED, CONTRADICTED, UNTESTED)
        let verdict = cr.verdict;
        if (!verdict) return "UNTESTED";

        // Enforce provenance requirement for positive experimental results natively here if API failed to drop it
        if (verdict === "SUPPORTED" || verdict === "CONTRADICTED") {
            if (cr.evidence_provenance === "EXPERIMENTAL_RUN" || cr.evidence_provenance === "NONE" || cr.evidence_provenance === "STALE_EVIDENCE") {
                 if (!cr.manifest_id || cr.manifest_id === "error-fallback" || !cr.scenario_id) {
                     return "UNTESTED";
                 }
            }
        }
        return verdict;
    }

    // SINGLE SOURCE OF TRUTH for Claim Provenance Tier
    function getProvenanceStatus(claim, results, isActive) {
        if (isActive) return "";
        if (
            claim.testability === "NOT_TESTABLE_YET" ||
            claim.testability === "NEEDS_NEW_SCENARIO"
        ) {
            return "";
        }
        const cr = (results || {})[claim.id] || {};
        return cr.evidence_provenance || "NONE";
    }

    function formatProvenance(provString) {
        if (!provString || provString === "NONE") return "";
        if (provString === "STALE_EVIDENCE") return "(STALE EVIDENCE)";
        if (provString === "EXPERIMENTAL_RUN") return "(EXPERIMENTAL DRAFT)";
        if (provString === "CANONICAL_SUITE") return ""; // Canonical is implicit if there's no warning
        return `(${provString.replace("_", " ")})`;
    }

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

    let selectedClaimId =
        typeof window !== "undefined"
            ? localStorage.getItem("wc_selected_claim") || null
            : null;

    $: if (typeof window !== "undefined") {
        localStorage.setItem("wc_search", searchQuery);
        localStorage.setItem("wc_status", statusFilter);
        localStorage.setItem("wc_testability", testabilityFilter);
        localStorage.setItem("wc_scope", scopeFilter);
        localStorage.setItem("wc_falsification", falsificationFilter);
        localStorage.setItem("wc_whitepaper", selectedWhitepaper);
        if (selectedClaimId) {
            localStorage.setItem("wc_selected_claim", selectedClaimId);
        } else {
            localStorage.removeItem("wc_selected_claim");
        }
    }
    $: selectedClaim =
        whitepaperClaims.find((c) => c.id === selectedClaimId) || null;

    // Track dynamic results { status: "SUPPORTED"|"CONTRADICTED"|"EXPERIMENTAL_SUPPORTED"|"EXPERIMENTAL_CONTRADICTED"|"UNTESTED", manifest_id: string, contract_id: string, is_audit_grade: boolean }
    let claimResults = {};
    let isVerifying = false;
    let isVerifyingAll = false;
    let verifyAllSummary = null;
    let activeContract = null;
    let currentBuild = "unknown";

    let auditStatus = "NONE";
    let auditBannerKind = "not_audited";
    let contractId = null;
    let contractTimestamp = "unknown";
    let contractCommit = "unknown";
    let equationFingerprint = "unknown";
    let summaryPass = 0;
    let summaryFail = 0;

    let productionSafety = {
        is_production: false,
        can_generate_audit: true,
        can_verify_all: true,
        reason: "",
    };
    let canonicalPromotion = {
        canonical_promotion_status: "NOT_READY",
        missing_requirements: [],
        required_claims_status: [],
    };

    async function fetchHealth() {
        try {
            const res = await fetch("/api/lab/health");
            if (res.ok) {
                const data = await res.json();
                activeContract = data.contract_id || null;
                currentBuild =
                    data.commit_hash || data.current_build || "unknown";

                auditStatus = data.audit_status || "NONE";
                auditBannerKind = data.audit_banner_kind || "not_audited";
                contractId = data.contract_id || null;
                contractTimestamp = data.contract_timestamp || "unknown";
                contractCommit =
                    data.contract_commit || data.commit_hash || "unknown";
                equationFingerprint = data.equation_fingerprint || "unknown";
                summaryPass = data.summary_pass || 0;
                summaryFail = data.summary_fail || 0;
                if (data.production_safety)
                    productionSafety = data.production_safety;
                if (data.canonical_promotion)
                    canonicalPromotion = data.canonical_promotion;
            }
        } catch (e) {
            console.error("Health check failed:", e);
        }
    }

    onMount(() => {
        const init = async () => {
            await fetchHealth();
            await refreshStatuses();
            try {
                const logRes = await fetch("/integration_log");
                if (logRes.ok) {
                    const logData = await logRes.json();
                    integrationLog = logData.events || [];
                }
            } catch (e) {
                console.error("Integration log fetch failed:", e);
            }
        };
        init();

        window.addEventListener("audit-completed", fetchHealth);
        return () => window.removeEventListener("audit-completed", fetchHealth);
    });

    async function refreshStatuses() {
        try {
            const res = await fetch(
                "/api/lab/claim_results",
            );
            if (res.ok) {
                const data = await res.json();
                const saved = data.results || {};
                for (const [claimId, result] of Object.entries(saved)) {
                    claimResults[claimId] = {
                        status: result.is_stale
                            ? "OUTDATED"
                            : result.resolved_claim_status,
                        verdict: result.verdict,
                        evidence_provenance: result.evidence_provenance,
                        manifest_id: result.manifest_id,
                        contract_id: result.contract_id,
                        is_audit_grade: result.is_current_build_audited ?? (result.audit_status === "AUDITED" || result.audit_status === "CANONICAL_AUDITED"),
                        passed_internal: result.overall_pass,
                        details: `Last checked: ${result.checked_at || "unknown"}`,
                        scenario_id: result.scenario_id,
                        active_profile: result.active_profile,
                        checked_at: result.checked_at,
                        is_stale: result.is_stale || false,
                        traceability: result.traceability,
                    };
                }
                claimResults = { ...claimResults };
                console.log(
                    "DEBUG SVELTE: refreshStatuses claimResults =",
                    claimResults,
                );
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
                "/api/lab/verify_all",
                {
                    method: "POST",
                },
            );
            if (res.ok) {
                const data = await res.json();
                verifyAllSummary = data.summary;
                await fetchHealth();
                await refreshStatuses();
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

        // Match audit_status logic to the single source of truth downgrade
        let bAuditStatus = auditStatus;
        if (auditBannerKind === "not_audited" || auditBannerKind === "stale_for_current_build") {
            bAuditStatus = auditStatus === "NONE" ? "NONE" : "OUTDATED";
        }

        let cid = cr.contract_id || contractId;
        if (!cid || cid === "unknown") cid = "none";

        let finger = equationFingerprint;
        if (!finger || finger === "unknown") finger = "null";

        let com = contractCommit;
        if (!com || com === "unknown") com = "none";

        // Use full currentBuild Git hash string minus branch
        let fallbackCom = currentBuild ? currentBuild.split(" ")[0] : "none";
        if (com === "none" && fallbackCom.length > 5) {
            com = fallbackCom;
        }

        const anchor = claim.source_anchor
            ? `#${claim.source_anchor.replace(/^#+/, "")}`
            : "";

        let target = "none (core registry only)";
        if (claim.source_file && !claim.source_file?.includes("claims.js")) {
            const mappedPath = whitepaperMap[claim.source_file] || `whitepapers/missing/${claim.source_file}`;
            target = `${mappedPath}${anchor}`;
        }

        return `> [!NOTE] \n> **EVIDENCE:**\n> - **claim_id:** ${claim.id}\n> - **contract_id:** ${cid}\n> - **manifest_id:** ${cr.manifest_id || "none"}\n> - **claim_status:** ${cStatus}\n> - **audit_status:** ${bAuditStatus}\n> - **equation_fingerprint:** ${finger}\n> - **git_commit:** ${com}\n> - **timestamp_utc:** ${new Date().toISOString()}\n> - **lab_section:** Claims\n> - **whitepaper_target:** ${target}`;
    }

    function getAssistantPacketMarkdown(claim) {
        const cr = claimResults[claim.id] || {};
        let actualStatus = getActualStatus(claim, claimResults);

        // Normalization rule: If it's a canonically tested claim that is editorially ready on cpu deterministically, treat it as fully SUPPORTED/CONTRADICTED in the packet
        if (
            claim.project_packet?.project_integration_status === "READY_FOR_EDITORIAL_REVIEW" &&
            claim.falsification_evidence_source === "CANONICAL_SUITE" &&
            cr.traceability?.deterministic_mode === true &&
            cr.traceability?.execution_device === "cpu"
        ) {
            if (actualStatus === "EXPERIMENTAL_SUPPORTED") actualStatus = "SUPPORTED";
            if (actualStatus === "EXPERIMENTAL_CONTRADICTED") actualStatus = "CONTRADICTED";
        }

        // Single coherent readiness rule: Must be explicitly READY_FOR_EDITORIAL_REVIEW *AND* actual status must be supportive/contradictive (including experimental)
        const isReady =
            claim.project_packet?.project_integration_status ===
                "READY_FOR_EDITORIAL_REVIEW" &&
            (actualStatus === "SUPPORTED" || actualStatus === "CONTRADICTED" || actualStatus === "EXPERIMENTAL_SUPPORTED" || actualStatus === "EXPERIMENTAL_CONTRADICTED");
            
        const isSupported = actualStatus === "SUPPORTED" || actualStatus === "EXPERIMENTAL_SUPPORTED";

        const isCanonical =
            claim.canonical_claim_set === "REQUIRED_FOR_PROMOTION" ||
            claim.canonical_claim_set === "SUPPORTING_ONLY" ||
            claim.id.includes("CORE");
            
        // Fix evidence_level logic to align strictly with test provenance
        let evidenceLevel = "MISSING_EVIDENCE";
        if (actualStatus === "SUPPORTED" || actualStatus === "CONTRADICTED") {
            if (cr.evidence_provenance === "CANONICAL_SUITE") {
                evidenceLevel = "CANONICAL_EVIDENCE";
            } else if (cr.evidence_provenance === "EXPERIMENTAL_RUN" || cr.evidence_provenance === "STALE_EVIDENCE") {
                evidenceLevel = "EXPERIMENTAL_EVIDENCE";
            } else {
                evidenceLevel = "CANONICAL_EVIDENCE";
            }
        } else if (cr.is_audit_grade === false && cr.checked_at) {
             evidenceLevel = "AUDIT_FAILED";
        }

        let isCanonicalDisplay = isCanonical ? "CANONICAL" : "EXPERIMENTAL";
        let evidenceSourceDisplay = claim.falsification_evidence_source || "N/A";

        if (evidenceLevel === "MISSING_EVIDENCE") {
            isCanonicalDisplay = isCanonical ? "UNKNOWN" : "EXPERIMENTAL";
            evidenceSourceDisplay = "NONE / MISSING_EVIDENCE";
        }

        let metricsList = "(No data)";
        let verdict = "No mathematical proof executed yet.";

        if (cr.traceability?.metrics?.length > 0) {
            metricsList = cr.traceability.metrics
                .map(
                    (m) =>
                        `- name: ${m.metric_name}\n  actual_value: ${m.actual_value !== null ? Number(m.actual_value).toExponential(4) : "—"}\n  threshold_rule: ${m.comparison_operator} ${m.threshold_rule}\n  why_status_changed: ${m.why_status_changed || "N/A"}`,
                )
                .join("\n\n");
            verdict = cr.traceability.overall_pass
                ? "SUPPORTED"
                : "CONTRADICTED";
        }

        let editorialConstraints = "";
        if (claim.editorial_guidance) {
            const ed = claim.editorial_guidance;
            let suggestedUse = ed.suggested_whitepaper_use || "MISSING";
            if (evidenceLevel !== "CANONICAL_EVIDENCE" && suggestedUse === "CANONICAL_EVIDENCE_ONLY") {
                suggestedUse = "EXPERIMENTAL_USE_ONLY";
            }
            editorialConstraints = `- what_it_means: ${ed.what_it_means || "MISSING"}\n- what_it_does_not_mean: ${ed.what_it_does_not_mean || "MISSING"}\n- forbidden_overclaims:\n${(ed.forbidden_overclaims || []).length > 0 ? ed.forbidden_overclaims.map((o) => `  - ${o}`).join("\n") : "  - (None defined)"}\n- safe_wording:\n${(ed.safe_wording || []).length > 0 ? ed.safe_wording.map((s) => `  - ${s}`).join("\n") : "  - (None defined)"}\n- suggested_whitepaper_use: ${suggestedUse}`;
        } else {
            editorialConstraints = `- what_it_means: MISSING_EDITORIAL_GUIDANCE\n- what_it_does_not_mean: MISSING_EDITORIAL_GUIDANCE\n- forbidden_overclaims:\n  - MISSING_EDITORIAL_GUIDANCE\n- safe_wording:\n  - MISSING_EDITORIAL_GUIDANCE\n- suggested_whitepaper_use: MISSING_EDITORIAL_GUIDANCE`;
        }

        let projectStatus =
            claim.project_packet?.project_integration_status || "MISSING_PROJECT_INTEGRATION_STATUS";
        let targetTopicId = claim.target_topic_id || "MISSING_TOPIC_ID";

        let candidateTargets = "None specified";
        if (claim.project_packet?.candidate_whitepaper_targets?.length > 0) {
            candidateTargets = claim.project_packet.candidate_whitepaper_targets
                .map(
                    (t) => {
                        const relativePath = whitepaperMap[t.file] || `whitepapers/missing/${t.file}`;
                        return `- file: ${relativePath}\n  target_topic_id: ${t.target_topic_id || t.topic_id || "UNKNOWN"}\n  current_anchor_if_known: ${t.current_anchor_if_known || "UNKNOWN"}\n  confidence: ${t.confidence}\n  rationale: ${t.rationale}`;
                    }
                )
                .join("\n\n");
        }

        let implementationNotes =
            claim.project_packet?.implementation_notes || "None";
        let escalate = false;

        let projectNextStepsBlock = `- project_integration_status: ${projectStatus}\n- missing_prerequisites: None_pending\n- recommended_next_step: ${claim.project_packet?.recommended_next_step || "-"}\n- implementation_notes: ${implementationNotes}`;

        if (!isReady) {
            let missingArr = claim.project_packet?.missing_prerequisites?.length > 0 
                ? claim.project_packet.missing_prerequisites 
                : ["Missing preconditions to be resolved by engineering."];
            
            let missingStr = "\n" + missingArr.map(x => `  - ${x}`).join("\n");

            let recArr = claim.project_packet?.recommended_next_step && !["Resolve missing prerequisites.", "-"].includes(claim.project_packet.recommended_next_step)
                ? [claim.project_packet.recommended_next_step]
                : [
                    "Create a real scenario_id in the project",
                    "Implement metrics in the project codepath",
                    "Propagate traceability into claim_results and UI",
                    "Add tests",
                    "If intended for canonical use later, define suite-contract integration",
                    "Scratch script alone is not sufficient"
                  ];
            
            let recStr = "\n" + recArr.map(x => `  - ${x}`).join("\n");

            projectNextStepsBlock = `- project_integration_status: ${projectStatus}\n- missing_prerequisites:${missingStr}\n- recommended_next_step:${recStr}\n- implementation_notes: ${implementationNotes}`;
            
            escalate = true;
        }

        return `# LINEUM HANDOFF PROTOCOL [v1.0.0]
packet_schema_version: v1.0.0

A) META-INSTRUCTIONS FOR PRIMARY AGENT
- Treat this packet as the current source of truth for Lineum.
- Do not rely on prior memory of equations, whitepapers, audits, claims, or historical project state.
- You are the Primary Agent. Your job is to review evidence strength, propose safe wording when allowed, and prevent overclaims.
- If anything important is missing, do not fill gaps from memory.
- If evidence is missing, do not accept scratch-only proof as sufficient.
- The Assistant must review first. If the claim is NOT READY, the Assistant must formulate concrete project-side instructions for Antigravity (the Secondary / Project Agent) based on the structured fields in Section E.
- The Assistant must output these Secondary Agent instructions as a clearly copyable block so the user can pass it on without rewriting it.

B) CLAIM DEFINITION
- claim_id: ${claim.id}
- short_claim: ${claim.short_claim}
- scope: ${claim.scope}
- current_status: ${actualStatus}
- evidence_level: ${evidenceLevel}
- canonical_or_experimental: ${isCanonicalDisplay}
- active_profile: ${cr.active_profile || "unknown"}
- equation_fingerprint: ${cr.traceability?.equation_fingerprint || "unknown"}
- scenario_id: ${claim.scenario_id || "None"}
- target_topic_id: ${targetTopicId}

C) ENGINEERING TRACEABILITY
- evidence_source: ${evidenceSourceDisplay}
- execution_device: ${cr.traceability?.execution_device || "unknown"}
- deterministic_mode: ${cr.traceability?.deterministic_mode !== undefined ? (cr.traceability.deterministic_mode ? "true" : "false") : "unknown"}
- overall_verdict: ${verdict}

Metrics:
${metricsList}

D) EDITORIAL CONSTRAINTS
${editorialConstraints}

E) PROJECT STATUS & NEXT STEPS
- This section provides the structured information the Primary Agent needs to generate the right secondary-agent handoff.
- If prerequisites are missing, the claim is not ready for final wording.
- Missing project work must be requested from Antigravity and completed in the repository/runtime, not only in scratch scripts or side artifacts.
${projectNextStepsBlock}

Candidate Whitepaper Targets:
${candidateTargets}

F) AUTOMATION ROUTING
- Is this ready for wording proposal now? ${isReady ? "YES" : "NO"}
- Primary agent action: ${isReady ? "Propose safe wording now." : "Review the missing prerequisites and instruct the user exactly what concrete project-side tasks Antigravity must do next. The instruction must be clearly formatted as a copyable block so the user can pass it directly to Antigravity without rewriting it."}
- wording_proposal_allowed_now: ${isReady ? "true" : "false"}
- claim_ready_for_editorial_use: ${isReady ? "true" : "false"}
- escalate_to_secondary_agent: ${escalate ? "true" : "false"}
`;
    }

    let copyStates = {};
    function copyToClipboard(claimId, type, text) {
        const key = `${claimId}-${type}`;
        copyStates[key] = "copying";
        copyStates = { ...copyStates };
        navigator.clipboard
            .writeText(text)
            .then(() => {
                copyStates[key] = "copied";
                copyStates = { ...copyStates };
                setTimeout(() => {
                    copyStates[key] = "idle";
                    copyStates = { ...copyStates };
                }, 2000);
            })
            .catch((err) => {
                console.error("Copy failed", err);
                copyStates[key] = "failed";
                copyStates = { ...copyStates };
                setTimeout(() => {
                    copyStates[key] = "idle";
                    copyStates = { ...copyStates };
                }, 2000);
            });
    }

    async function markAsApplied(claim) {
        savingApplied = true;
        const cr = claimResults[claim.id];
        const isApp = isApplied(claim.id, integrationLog);
        const payload = {
            event: isApp ? "REVERTED" : "APPLIED",
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
            const res = await fetch("/integration_log", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                const newLogRes = await fetch(
                    "/integration_log",
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

    async function runVerification(claim) {
        if (!claim.scenario_id) return;
        isVerifying = true;
        try {
            // Backend is authoritative: resolves scenario, runs physics, determines status
            const res = await fetch(
                `/api/lab/run_preset?preset_name=${claim.scenario_id}`,
            );
            if (!res.ok) {
                const err = await res.text();
                console.warn("Backend error:", err);
                throw new Error(err);
            }
            const data = await res.json();

            // Backend returns resolved_claim_status — immediately synchronize the single source of truth matrix
            await fetchHealth();
            await refreshStatuses();
            
            // Re-select actual resolved text for UX details overlay
            claimResults[claim.id] = {
                ...claimResults[claim.id],
                details: data.message || "Executed.",
            };
        } catch (e) {
            console.warn("Verification error:", e);
            claimResults[claim.id] = {
                status: "ERROR",
                manifest_id: null,
                contract_id: null,
                is_audit_grade: false,
                passed_internal: false,
                details: `Execution Failed: ${e.message}`,
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
        {#if canonicalPromotion.canonical_promotion_status !== "NOT_READY"}
            <CollapsibleBox
                title={$t('claims.wave_core_promo')}
                badgeText={canonicalPromotion.canonical_promotion_status.replace(/_/g, " ")}
                badgeStyle={canonicalPromotion.canonical_promotion_status === 'CANONICAL_AUDITED' ? 'background: #238636; color: white;' : canonicalPromotion.canonical_promotion_status === 'READY_FOR_CANONICAL_PROMOTION' ? 'background: #9e6a03; color: white;' : 'background: #1f6feb; color: white;'}
                bind:isExpanded={isPromotionBlockExpanded}
            >
                <div slot="header-meta" style="font-size: 12px; color: #8b949e; padding-left: 20px;">
                    {canonicalPromotion.required_claims_status.filter((r) => r.is_ready).length} / {canonicalPromotion.required_claims_status.length} {$t('claims.required_claims')}
                </div>
                    <div
                        style="margin-top: 15px; border-top: 1px solid #30363d; padding-top: 15px;"
                    >
                        <div
                            style="font-size: 13px; color: #8b949e; margin-bottom: 15px;"
                        >
                            {$t('claims.goal_elevating')} <span
                                style="font-family: monospace;">{$t('wc_wave_core')}</span
                            > {$t('claims.from_prov_to_canon')}
                        </div>

                        <div style="font-size: 13px;">
                            <strong style="display: block; margin-bottom: 8px;"
                                >{$t('claims.req_status')}</strong
                            >
                            <ul
                                style="list-style: none; padding: 0; margin: 0 0 15px 0; border: 1px solid #30363d; border-radius: 4px; overflow: hidden; max-height: 200px; overflow-y: auto;"
                            >
                                {#each canonicalPromotion.required_claims_status as req}
                                    <li
                                        style="padding: 8px 10px; border-bottom: 1px solid #30363d; background: {req.is_ready
                                            ? '#051d14'
                                            : '#161b22'}; display: flex; justify-content: space-between; align-items: center;"
                                    >
                                        <span
                                            title={req.id}
                                            style="font-family: monospace; font-size: 12px; color: {req.is_ready
                                                ? '#3fb950'
                                                : '#c9d1d9'}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 60%;"
                                        >
                                            {req.is_ready ? "✓" : "○"}
                                            {req.id}
                                        </span>
                                        <span
                                            style="font-size: 10px; color: #8b949e; text-align: right; line-height: 1;"
                                            >{req.evidence_source.replace(
                                                /_/g,
                                                " ",
                                            )}</span
                                        >
                                    </li>
                                {/each}
                            </ul>
                        </div>

                        {#if canonicalPromotion.missing_requirements.length > 0}
                            <div style="font-size: 13px; color: #ff7b72;">
                                <strong
                                    style="display: block; margin-bottom: 4px;"
                                    >{$t('claims.blockers')}</strong
                                >
                                <ul style="padding-left: 20px; margin: 0;">
                                    {#each canonicalPromotion.missing_requirements as blocker}
                                        <li>{blocker}</li>
                                    {/each}
                                </ul>
                            </div>
                        {/if}

                        {#if canonicalPromotion.canonical_promotion_status === "READY_FOR_CANONICAL_PROMOTION"}
                            <div
                                style="font-size: 13px; color: #3fb950; margin-top: 15px; padding-top: 15px; border-top: 1px solid #30363d;"
                            >
                                <strong>{$t('claims.ready')}</strong> {$t('claims.please_run')}
                                <span style="font-family: monospace;"
                                    >{$t('claims.gen_audit_contract')}</span
                                > {$t('claims.to_finalize')}
                            </div>
                        {/if}
            </CollapsibleBox>
        {/if}

        <!-- Vyjmutý CollapsibleBox volně v parent divu -->
        <CollapsibleBox
            title={$t('claims.filter_claims')}
            badgeText={hasActiveFilters ? $t('claims.showing_x_claims').replace('{count}', filteredClaims.length.toString()) : ""}
            testId="filters-toggle"
            bind:isExpanded={isFiltersExpanded}
        >
            <div slot="header-actions">
                {#if hasActiveFilters}
                    <button
                        class="clear-filters-btn"
                        on:click|stopPropagation={clearFilters}
                        style="background: transparent; color: #ff7b72; border: 1px solid rgba(255,123,114,0.3); border-radius: 4px; padding: 2px 8px; cursor: pointer; font-size: 0.65rem; z-index: 10;"
                        data-tooltip={$t('claims.clear_title')}
                    >
                        {$t('claims.clear_filters')}
                    </button>
                {/if}
            </div>
            <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 15px;">
                <div style="flex: 1; min-width: 150px; display: flex; flex-direction: column; gap: 4px;">
                    <label for="filter-search" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">{$t('claims.search_query')}</label>
                    <input
                        id="filter-search"
                        type="text"
                        placeholder="Search claims..."
                        bind:value={searchQuery}
                        class="search-input"
                    />
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <label for="filter-tags" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">{$t('claims.tags')}</label>
                    <select
                        id="filter-tags"
                        bind:value={selectedTag}
                        class="tag-select"
                        style="width: 100%;"
                    >
                        {#each allTags as tag}
                            <option value={tag}
                                >{tag === "all" ? $t('claims.all_tags') : tag}</option
                            >
                        {/each}
                    </select>
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <label for="filter-state" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">{$t('claims.audit_state')}</label>
                    <select
                        id="filter-state"
                        bind:value={statusFilter}
                        class="tag-select"
                        style="width: 100%;"
                    >
                        <option value="all">{$t('claims.state_all')}</option>
                        <option value="supported">{$t('claims.state_supported')}</option>
                        <option value="contradicted">{$t('claims.state_contradicted')}</option>
                        <option value="untested">{$t('claims.state_untested')}</option>
                        <option value="experimental">{$t('claims.state_experimental')}</option>
                        <option value="outdated">{$t('claims.state_outdated')}</option>
                        <option value="applied">{$t('claims.state_applied')}</option>
                        <option value="not_applied">{$t('claims.state_not_applied')}</option>
                    </select>
                </div>
            </div>

            <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 5px;">
                <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <label for="filter-testability" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">{$t('claims.testability')}</label>
                    <select
                        id="filter-testability"
                        bind:value={testabilityFilter}
                        class="tag-select"
                        style="width: 100%;"
                    >
                        <option value="all">{$t('claims.testability_all')}</option>
                        <option value="TESTABLE_NOW">{$t('claims.test_now')}</option>
                        <option value="NEEDS_NEW_SCENARIO"
                            >{$t('claims.test_needs_scenario')}</option
                        >
                        <option value="NOT_TESTABLE_YET">{$t('claims.test_not_yet')}</option>
                    </select>
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <label for="filter-scope" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">{$t('claims.model_scope')}</label>
                    <select
                        id="filter-scope"
                        bind:value={scopeFilter}
                        class="tag-select"
                        style="width: 100%;"
                    >
                        <option value="all">{$t('claims.scope_all')}</option>
                        <option value="MODEL_INTERNAL">{$t('claims.scope_internal')}</option>
                        <option value="ANALOGICAL">{$t('claims.scope_analogical')}</option>
                        <option value="REAL_WORLD_STRONG">{$t('claims.scope_strong')}</option>
                    </select>
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <label for="filter-falsification" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">{$t('claims.falsification')}</label>
                    <select
                        id="filter-falsification"
                        bind:value={falsificationFilter}
                        class="tag-select"
                        style="width: 100%;"
                    >
                        <option value="all">{$t('claims.false_all')}</option>
                        <option value="needed">{$t('claims.false_needed')}</option>
                    </select>
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <label for="filter-whitepaper" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">{$t('claims.doc_source')}</label>
                    <select
                        id="filter-whitepaper"
                        bind:value={selectedWhitepaper}
                        class="tag-select"
                        style="width: 100%;"
                    >
                        <option value="all">{$t('claims.doc_all')}</option>
                        {#each allWhitepapers as wp}
                            {#if wp !== "all"}
                                <option value={wp}>{wp}</option>
                            {/if}
                        {/each}
                    </select>
                </div>
            </div>
        </CollapsibleBox>

        <div class="filter-section">
            <div class="bulk-actions">
                <button
                    class="bulk-btn verify-all-btn"
                    on:click={verifyAllClaims}
                    disabled={isVerifyingAll ||
                        !productionSafety.can_verify_all}
                    data-tooltip={!productionSafety.can_verify_all
                        ? productionSafety.reason
                        : $t('claims.verify_all_testable')}
                >
                    {isVerifyingAll
                        ? $t('claims.verification_in_progress')
                        : $t('claims.verify_all_testable')}
                </button>
                <button class="bulk-btn refresh-btn" on:click={refreshStatuses}>
                    {$t('claims.refresh_statuses')}
                </button>
            </div>

            {#if verifyAllSummary}
                <div class="verify-summary-panel">
                    <div class="summary-header">
                        <span class="summary-title">{$t('claims.claims_verification')}</span>
                        {#if verifyAllSummary.is_canonical}
                            <span class="mode-badge canonical">{$t('wc_canonical')}</span>
                        {:else}
                            <span class="mode-badge experimental"
                                >{$t('wc_experimental')}</span
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
                            >⏱️ {verifyAllSummary.duration_ms}{$t('wc_ms')}</span
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
                    role="button"
                    tabindex="0"
                    on:click={() => selectClaim(claim.id)}
                    on:keydown={(e) =>
                        e.key === "Enter" && selectClaim(claim.id)}
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
                                >{getActualStatus(claim, claimResults, isGeneratingAudit)}</span>
                            {#if getProvenanceStatus(claim, claimResults, isGeneratingAudit) === "STALE_EVIDENCE"}
                                <span class="claim-status outdated" style="font-size: 0.75em; padding: 2px 6px; background: rgba(227,100,20,0.15); color: #e36414; border: 1px solid rgba(227,100,20,0.3);">
                                    {formatProvenance(getProvenanceStatus(claim, claimResults, isGeneratingAudit))}
                                </span>
                            {:else if getProvenanceStatus(claim, claimResults, isGeneratingAudit) === "EXPERIMENTAL_RUN"}
                                <span class="claim-status experimental" style="font-size: 0.75em; padding: 2px 6px; opacity: 0.8;">
                                    {formatProvenance(getProvenanceStatus(claim, claimResults, isGeneratingAudit))}
                                </span>
                            {/if}
                        </div>
                    </div>
                    <div class="claim-short">
                        {@html renderInlineLatex(claim.short_claim)}
                    </div>
                </div>
            {/each}
            {#if filteredClaims.length === 0}
                <div class="no-results">{$t('claims.no_results')}</div>
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
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span
                            class="status-badge {getActualStatus(
                                selectedClaim,
                                claimResults,
                                isGeneratingAudit
                            ).toLowerCase()}"
                        >
                            {getActualStatus(selectedClaim, claimResults, isGeneratingAudit).replace("_", " ")}
                        </span>
                        {#if getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit) === "STALE_EVIDENCE"}
                            <span class="status-badge outdated" style="font-size: 0.8em; padding: 2px 8px; background: rgba(227,100,20,0.15); color: #e36414; border: 1px solid rgba(227,100,20,0.3);">
                                {formatProvenance(getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit))}
                            </span>
                        {:else if getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit) === "EXPERIMENTAL_RUN"}
                            <span class="status-badge experimental" style="font-size: 0.8em; padding: 2px 8px; opacity: 0.8;">
                                {formatProvenance(getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit))}
                            </span>
                        {/if}
                    </div>
                </div>

                {#if isApplied(selectedClaim.id, integrationLog)}
                    <div
                        class="applied-banner is-applied"
                        style="margin: 10px 0; background: rgba(46,160,67,0.15); border-left: 3px solid #3fb950; padding: 10px; border-radius: 4px;"
                    >
                        <strong>{$t('claims.whitepaper_status')}</strong>
                        <span style="color: #4ade80;">{$t('claims.applied')}</span>
                        {$t('claims.commit_label')}
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
                        {$t('claims.whitepaper_status')} {$t('claims.not_applied_yet')}
                    </div>
                {/if}

                {#if auditBannerKind === "not_audited"}
                    <div class="audit-warning-banner">
                        <span class="warn-icon">⚠️</span>
                        <div>
                            <strong>{$t('claims.not_audited_build')}</strong><br />
                            {$t('claims.build_label')} <code>{currentBuild}</code>. {$t('claims.runs_marked_exploratory')}
                        </div>
                    </div>
                {:else if auditBannerKind === "stale_for_current_build"}
                    <div class="audit-warning-banner" style="background-color: var(--lineum-amber-dark, #bd561d); color: white;">
                        <span class="warn-icon">⏳</span>
                        <div>
                            <strong>{$t('claims.audit_stale')}</strong><br />
                            {$t('claims.build_label')} <code>{currentBuild}</code> {$t('claims.stale_desc')}
                        </div>
                    </div>
                {:else if auditBannerKind === "running"}
                    <div class="audit-warning-banner" style="background-color: var(--lineum-wave, #1dbdbd); border-color: var(--lineum-wave); color: #0a0a0a;">
                        <span class="warn-icon">⏳</span>
                        <div>
                            <strong>{$t('audit_running')}</strong><br />
                            {$t('claims.audit_in_progress')}
                        </div>
                    </div>
                {/if}

                <div class="source-link">
                    <strong>{$t('claims.source')}</strong>
                    <a
                        href="/wiki/{selectedClaim.source_file.replace(
                            /\.md$/,
                            '',
                        )}"
                        target="_blank"
                    >
                        {selectedClaim.source_file}
                    </a>
                    ({$t('claims.section')} {selectedClaim.source_anchor})
                </div>

                <div class="explain-pack">
                    <div class="ep-liner">{$t('claims.human_translation')}</div>
                    <p>{selectedClaim.human_claim}</p>

                    <div class="ep-columns">
                        <div class="ep-col">
                            <h4>{$t('claims.scientific_claim')}</h4>
                            <p class="scientific-render">
                                {@html renderScientificClaim(
                                    selectedClaim.scientific_claim,
                                )}
                            </p>
                        </div>
                        <div class="ep-col ep-not">
                            <h4>{$t('claims.what_this_is_not')}</h4>
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
                        <strong>{$t('claims.scope_label')}</strong>
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
                        <div class="sq-label">{$t('claims.source_quote')}</div>
                        <blockquote>
                            {@html renderInlineLatex(
                                selectedClaim.source_quote,
                            )}
                        </blockquote>
                    </div>
                {/if}

                <!-- Falsification -->
                {#if selectedClaim.falsification_mode || selectedClaim.falsification_needed !== undefined}
                    <div class="falsification-section">
                        <div
                            style="display: flex; justify-content: space-between; align-items: baseline;"
                        >
                            <h3>{$t('claims.falsification_state')}</h3>
                            {#if selectedClaim.falsification_mode}
                                <span
                                    style="font-size: 11px; padding: 2px 6px; background: rgba(31, 111, 235, 0.15); color: #58a6ff; border: 1px solid rgba(31, 111, 235, 0.3); border-radius: 12px; font-family: monospace;"
                                >
                                    {selectedClaim.falsification_mode}
                                </span>
                            {/if}
                        </div>

                        {#if selectedClaim.falsification_mode}
                            <div
                                class="fals-meta-grid"
                                style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; font-size: 13px; background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid #30363d;"
                            >
                                <div>
                                    <strong
                                        style="color: #8b949e; display: block; font-size: 11px; text-transform: uppercase;"
                                        >{$t('claims.status')}</strong
                                    >
                                    <span
                                        class="mono"
                                        style="font-weight: bold; color: {selectedClaim.falsification_status ===
                                        'FAILED'
                                            ? '#f85149'
                                            : selectedClaim.falsification_status ===
                                                'PASSED'
                                              ? '#3fb950'
                                              : '#d29922'};"
                                    >
                                        {selectedClaim.falsification_status ||
                                            $t('claims.not_run')}
                                    </span>
                                </div>
                                <div>
                                    <strong
                                        style="color: #8b949e; display: block; font-size: 11px; text-transform: uppercase;"
                                        >{$t('claims.evidence_source')}</strong
                                    >
                                    <span class="mono"
                                        >{selectedClaim.falsification_evidence_source?.replace(
                                            /_/g,
                                            " ",
                                        ) || $t('claims.none')}</span
                                    >
                                </div>
                                {#if selectedClaim.last_falsification_run_id}
                                    <div
                                        style="grid-column: 1 / -1; margin-top: 4px; padding-top: 8px; border-top: 1px solid #21262d;"
                                    >
                                        <strong
                                            style="color: #8b949e; display: inline-block; width: 60px; font-size: 11px;"
                                            >{$t('claims.run_id')}</strong
                                        >
                                        <span
                                            class="mono"
                                            style="color: #c9d1d9; font-size: 11px;"
                                            >{selectedClaim.last_falsification_run_id}</span
                                        >
                                    </div>
                                {/if}
                            </div>
                        {/if}

                        <div class="fals-status">
                            <strong>{$t('claims.falsification_needed')}</strong>
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
                                    <strong>{$t('claims.falsification_plan')}</strong>
                                    <p>
                                        {@html renderInlineLatex(
                                            selectedClaim.falsification_plan,
                                        )}
                                    </p>
                                </div>
                            {:else if selectedClaim.missing_falsification_reason}
                                <div class="fals-missing">
                                    <strong>{$t('claims.missing_plan')}</strong>
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
                        <div class="disc-label">{$t('claims.disclaimers_title')}</div>
                        <p>{selectedClaim.disclaimers}</p>
                    </div>
                {/if}

                <div class="testing-section">
                    <h3>{$t('claims.lab_verify_workflow')}</h3>

                    <div class="testability">
                        <strong>{$t('claims.testability_status')}</strong>
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
                        <strong>{$t('claims.verify_plan')}</strong>
                        <p>
                            {@html renderInlineLatex(
                                selectedClaim.verification_plan,
                            )}
                        </p>
                        <strong>{$t('claims.expected_measures')}</strong>
                        <p>
                            {@html renderInlineLatex(
                                selectedClaim.expected_measures,
                            )}
                        </p>
                    </div>

                    {#if selectedClaim.testability === "TESTABLE_NOW"}
                        <div class="action-box">
                            <button
                                class="run-btn"
                                on:click={() => runVerification(selectedClaim)}
                                disabled={isVerifying}
                            >
                                {isVerifying
                                    ? $t('claims.run_sim_btn')
                                    : $t('claims.run_verify_scenario')}
                            </button>
                            <p class="action-hint">
                                {$t('claims.maps_preset')} <code
                                    >{selectedClaim.scenario_id}</code
                                >
                            </p>
                        </div>
                    {/if}

                    {#if claimResults[selectedClaim.id]}
                        <div class="last-evidence-box">
                            <h4>{$t('claims.last_evidence')}</h4>
                            <div class="evidence-meta">
                                <div>
                                    <strong>{$t('claims.checked_label')}</strong>
                                    {claimResults[selectedClaim.id]
                                        .checked_at || $t('claims.unknown')}
                                </div>
                                <div>
                                    <strong>{$t('claims.manifest_label')}</strong>
                                    <code
                                        >{claimResults[selectedClaim.id]
                                            .manifest_id || "—"}</code
                                    >
                                </div>
                                <div>
                                    <strong>{$t('claims.scenario_label')}</strong>
                                    <code
                                        >{claimResults[selectedClaim.id]
                                            .scenario_id || "—"}</code
                                    >
                                </div>
                                <div>
                                    <strong>{$t('claims.audit_label')}</strong>
                                    {claimResults[selectedClaim.id]
                                        .is_audit_grade
                                        ? $t('claims.audit_grade')
                                        : "🧪 Experimental"}
                                </div>
                                {#if claimResults[selectedClaim.id].active_profile}
                                    <div>
                                        <strong>{$t('claims.profile_label')}</strong>
                                        {claimResults[selectedClaim.id]
                                            .active_profile}
                                    </div>
                                {/if}
                                {#if claimResults[selectedClaim.id].is_stale}
                                    <div class="stale-warning">
                                        {$t('claims.stale_warning')}
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/if}

                    {#if claimResults[selectedClaim.id] && claimResults[selectedClaim.id].traceability}
                        <div class="traceability-box">
                            <h4>{$t('claims.comp_traceability')}</h4>

                            <div class="trace-grid">
                                <strong>{$t('claims.exec_device_label')}</strong>
                                <span
                                    >{claimResults[selectedClaim.id]
                                        .traceability.execution_device}</span
                                >

                                <strong>{$t('claims.determ_mode_label')}</strong>
                                <span
                                    >{claimResults[selectedClaim.id]
                                        .traceability.deterministic_mode
                                        ? $t('claims.yes_enforced')
                                        : $t('claims.no')}</span
                                >

                                <strong>{$t('claims.eq_fingerprint')}</strong>
                                <span class="mono small breakable"
                                    >{claimResults[selectedClaim.id]
                                        .traceability
                                        .equation_fingerprint}</span
                                >

                                <strong>{$t('claims.overall_result')}</strong>
                                <span
                                    class="verdict {claimResults[
                                        selectedClaim.id
                                    ].traceability.overall_pass
                                        ? 'pass'
                                        : 'fail'}"
                                >
                                    {claimResults[selectedClaim.id].traceability
                                        .overall_pass
                                        ? $t('claims.supported_upper')
                                        : $t('claims.contradicted_upper')}
                                </span>
                            </div>

                            {#if claimResults[selectedClaim.id].traceability.metrics && claimResults[selectedClaim.id].traceability.metrics.length > 0}
                                <h5>{$t('claims.eval_rules_metrics')}</h5>
                                <div class="trace-table-container">
                                    <table class="trace-table">
                                        <thead>
                                            <tr>
                                                <th>{$t('claims.col_metric')}</th>
                                                <th>{$t('claims.col_actual')}</th>
                                                <th>{$t('claims.col_rule')}</th>
                                                <th>{$t('claims.col_verdict')}</th>
                                                <th>{$t('claims.col_source')}</th>
                                                <th>{$t('claims.col_reason')}</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {#each claimResults[selectedClaim.id].traceability.metrics as metricObj}
                                                <tr>
                                                    <td class="mono"
                                                        >{metricObj.metric_name}</td
                                                    >
                                                    <td class="mono">
                                                        {metricObj.actual_value !==
                                                        null
                                                            ? Number(
                                                                  metricObj.actual_value,
                                                              ).toExponential(4)
                                                            : "—"}
                                                    </td>
                                                    <td class="mono"
                                                        >{metricObj.comparison_operator}
                                                        {metricObj.threshold_rule}</td
                                                    >
                                                    <td
                                                        class="verdict-col {metricObj.passed
                                                            ? 'pass'
                                                            : 'fail'}"
                                                    >
                                                        {metricObj.passed
                                                            ? $t('claims.pass')
                                                            : $t('claims.fail')}
                                                    </td>
                                                    <td class="mono small"
                                                        >{metricObj.source_file_or_field}</td
                                                    >
                                                    <td class="reason-cell"
                                                        >{metricObj.why_status_changed}</td
                                                    >
                                                </tr>
                                            {/each}
                                        </tbody>
                                    </table>
                                </div>
                            {/if}
                        </div>
                    {/if}

                    {#if getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit) === "EXPERIMENTAL_RUN" || getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit) === "STALE_EVIDENCE"}
                        <div class="evidence-box exploratory">
                            <h4>{$t('claims.exploratory_evidence')}</h4>
                            <p>
                                {$t('claims.status_set_to')} <strong
                                    >{getActualStatus(
                                        selectedClaim,
                                        claimResults,
                                    ).replace("_", " ")}</strong
                                >.
                                <br /><span
                                    style="color: #ff7b72; font-size: 0.9em;"
                                    >{$t('claims.audit_grade_na')}</span
                                >
                            </p>
                            <p class="manifest-link">
                                {$t('claims.extracted_data')} {claimResults[selectedClaim.id]
                                    .passed_internal
                                    ? $t('claims.matches_exp')
                                    : $t('claims.fails_exp')}
                                <br />{$t('claims.manifest_label')}
                                <span class="mono"
                                    >{claimResults[selectedClaim.id]
                                        ?.manifest_id}</span
                                >
                            </p>
                        </div>
                    {/if}

                    {#if (getActualStatus(selectedClaim, claimResults, isGeneratingAudit) === "SUPPORTED" || getActualStatus(selectedClaim, claimResults, isGeneratingAudit) === "CONTRADICTED") && getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit) === "CANONICAL_SUITE"}
                        <div class="evidence-box canonical">
                            <h4>
                                {$t('claims.canonical_evidence')}
                                <span class="audit-badge">{$t('claims.audit_grade')}</span>
                            </h4>
                            <p>
                                {$t('claims.status_transitioned')} <strong
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
                                {$t('claims.audit_contract')} <span class="mono contract-id"
                                    >{claimResults[selectedClaim.id]
                                        ?.contract_id}</span
                                ><br />
                                {$t('claims.source_run_manifest')}
                                <span class="mono"
                                    >{claimResults[selectedClaim.id]
                                        ?.manifest_id}</span
                                >
                                <a
                                    href="http://127.0.0.1:8000/api/lab/claim_results"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    class="view-run">{$t('claims.view_run_export')}</a
                                >
                            </p>
                        </div>
                    {/if}

                    <div class="proposal-preview">
                        <h4>{$t('claims.preview_proposed')}</h4>
                        <div class="preview-box">
                            {#if getActualStatus(selectedClaim, claimResults, isGeneratingAudit) === "UNTESTED"}
                                <p class="preview-placeholder">
                                    {$t('claims.run_audit_generate')}
                                </p>
                            {:else if getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit) === "EXPERIMENTAL_RUN"}
                                <p class="preview-placeholder">
                                    {$t('claims.lab_sim_completed_audit_req')}
                                </p>
                            {:else if getProvenanceStatus(selectedClaim, claimResults, isGeneratingAudit) === "STALE_EVIDENCE" || getActualStatus(selectedClaim, claimResults, isGeneratingAudit) === "OUTDATED"}
                                <p class="preview-placeholder">
                                    {$t('claims.prev_lab_sim_outdated')}
                                </p>
                            {:else if getActualStatus(selectedClaim, claimResults, isGeneratingAudit) === "SUPPORTED"}
                                <p class="mono-edit add">
                                    + <span class="badge supported"
                                        >{$t('claims.validated_by_lab')}</span
                                    >
                                    {selectedClaim.short_claim}
                                    <br /><span class="sub-edit">
                                        ({$t('claims.audit_contract')} {claimResults[
                                            selectedClaim.id
                                        ].contract_id} | {$t('claims.manifest_label')} {claimResults[
                                            selectedClaim.id
                                        ].manifest_id})</span
                                    >
                                </p>
                            {:else if getActualStatus(selectedClaim, claimResults, isGeneratingAudit) === "CONTRADICTED"}
                                <p class="mono-edit replace">
                                    - {selectedClaim.short_claim}
                                    <br />+
                                    <span class="badge contradicted"
                                        >{$t('claims.falsified_hypothesis')}</span
                                    >
                                    {selectedClaim.short_claim}
                                    <br /><span class="sub-edit">
                                        ({$t('claims.audit_contract')} {claimResults[
                                            selectedClaim.id
                                        ].contract_id} | {$t('claims.manifest_label')} {claimResults[
                                            selectedClaim.id
                                        ].manifest_id} {$t('claims.keep_as_record')})</span
                                    >
                                </p>
                            {/if}
                        </div>

                        <div
                            class="evidence-generator"
                            style="margin-top: 20px; border-top: 1px solid #30363d; padding-top: 15px;"
                        >
                            <h4>{$t('claims.evidence_actions')}</h4>
                            <textarea
                                readonly
                                class="evidence-textarea assistant-textarea"
                                rows="12"
                                style="width: 100%; background: #010409; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px; padding: 10px; font-family: monospace; font-size: 13px; margin: 10px 0;"
                                >{getAssistantPacketMarkdown(
                                    selectedClaim,
                                )}</textarea
                            >
                            <div
                                class="evidence-actions"
                                style="display: flex; gap: 10px;"
                            >
                                <button
                                    class="assistant-copy-btn"
                                    style="padding: 8px 16px; font-weight: bold; font-family: monospace; border-radius: 4px; border: 1px solid #30363d; background: #1f6feb; color: white; cursor: pointer; display: flex; align-items: center; gap: 6px; flex-grow: 1; justify-content: center;"
                                    on:click={() =>
                                        copyToClipboard(
                                            selectedClaim.id,
                                            "assistant",
                                            getAssistantPacketMarkdown(
                                                selectedClaim,
                                            ),
                                        )}
                                >
                                    {copyStates[
                                        `${selectedClaim.id}-assistant`
                                    ] === "copying"
                                        ? $t('claims.copy_assistant_copying')
                                        : copyStates[
                                                `${selectedClaim.id}-assistant`
                                            ] === "copied"
                                          ? $t('claims.copy_assistant_copied')
                                          : copyStates[
                                                  `${selectedClaim.id}-assistant`
                                              ] === "failed"
                                            ? $t('claims.copy_assistant_failed')
                                            : $t('claims.copy_assistant')}
                                </button>
                                <button
                                    class="run-btn copy"
                                    on:click={() =>
                                        copyToClipboard(
                                            selectedClaim.id,
                                            "block",
                                            getEvidenceMarkdown(selectedClaim),
                                        )}
                                >
                                    {copyStates[`${selectedClaim.id}-block`] ===
                                    "copying"
                                        ? $t('claims.copy_evidence_copying')
                                        : copyStates[
                                                `${selectedClaim.id}-block`
                                            ] === "copied"
                                          ? $t('claims.copy_evidence_copied')
                                          : copyStates[
                                                  `${selectedClaim.id}-block`
                                              ] === "failed"
                                            ? $t('claims.copy_evidence_failed')
                                            : $t('claims.copy_evidence')}
                                </button>
                                <button
                                    class="run-btn mark-applied"
                                    style="background: {isApplied(
                                        selectedClaim.id,
                                        integrationLog,
                                    )
                                        ? '#2e6b38'
                                        : '#238636'};"
                                    disabled={savingApplied ||
                                        selectedClaim.editorial_guidance
                                            ?.suggested_whitepaper_use ===
                                            "DO_NOT_USE_IN_WHITEPAPER_YET"}
                                    on:click={() =>
                                        markAsApplied(selectedClaim)}
                                >
                                    {savingApplied
                                        ? $t('claims.saving_log')
                                        : isApplied(
                                                selectedClaim.id,
                                                integrationLog,
                                            )
                                          ? $t('claims.unmark_applied')
                                          : $t('claims.mark_applied')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {:else}
            <div class="empty-state">
                {$t('claims.empty_state')}
            </div>
        {/if}
    </div>
</div>

<!-- Trigger Hot Module Reload -->

<style>
    .claims-container {
        display: flex;
        height: calc(100vh - 80px); /* Adjust based on App header */
        background: #0d1117;
        color: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
            Arial, sans-serif;
    }

    @media (max-width: 768px) {
        .claims-container {
            flex-direction: column;
            height: auto;
            min-height: calc(100vh - 80px);
        }
    }

    .claims-sidebar {
        width: 350px;
        border-right: 1px solid #30363d;
        display: flex;
        flex-direction: column;
        background: #010409;
        position: relative;
    }

    @media (max-width: 768px) {
        .claims-sidebar {
            width: 100%;
            height: 400px;
            border-right: none;
            border-bottom: 1px solid #30363d;
        }
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
        background: #0d1117 url('data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" width="16" height="16" stroke="gray" stroke-width="2" fill="none" class="feather feather-chevron-down" xmlns="http://www.w3.org/2000/svg"><polyline points="6 9 12 15 18 9"></polyline></svg>') no-repeat right 10px center;
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        border: 1px solid #30363d;
        color: #c9d1d9;
        font-size: 13px;
        border-radius: 6px;
        padding: 8px 30px 8px 12px;
        outline: none;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .tag-select:hover {
        border-color: #8b949e;
    }
    .tag-select:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3);
    }
    .search-input,
    .tag-select {
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
    .claim-status.audit_running {
        background: rgba(47, 129, 247, 0.2);
        color: #58a6ff;
        border: 1px solid rgba(88, 166, 255, 0.4);
        animation: pulse-audit 2s infinite;
    }
    @keyframes pulse-audit {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
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
        font-size: 0.8rem;
        line-height: 1.5;
        color: #a0aec0;
    }

    .traceability-box {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid #1f1f35;
        border-radius: 6px;
        padding: 12px;
        margin-top: 12px;
    }
    .traceability-box h4 {
        margin: 0 0 10px 0;
        color: #8b949e;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .traceability-box h5 {
        margin: 12px 0 6px 0;
        color: #c9d1d9;
        font-size: 0.8rem;
    }
    .trace-grid {
        display: grid;
        grid-template-columns: max-content 1fr;
        gap: 4px 12px;
        font-size: 0.8rem;
        color: #c9d1d9;
    }
    .trace-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        margin-top: 6px;
    }
    .trace-table th {
        text-align: left;
        color: #8b949e;
        padding: 4px 8px;
        border-bottom: 1px solid #1f1f35;
        font-weight: 500;
    }
    .trace-table td {
        padding: 4px 8px;
        border-bottom: 1px solid #1f1f35;
        color: #c9d1d9;
    }

    .verdict {
        font-weight: 700;
        font-size: 0.8rem;
        padding: 1px 6px;
        border-radius: 4px;
        display: inline-block;
    }
    .verdict.pass {
        background: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(63, 185, 80, 0.4);
    }
    .verdict.fail {
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
    }

    .verdict-col {
        font-weight: 700;
    }
    .verdict-col.pass {
        color: #3fb950;
    }
    .verdict-col.fail {
        color: #f85149;
    }

    .reason-cell {
        font-size: 0.75rem;
        color: #8b949e;
        max-width: 250px;
        white-space: normal;
        line-height: 1.3;
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
