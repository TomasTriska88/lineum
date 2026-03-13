<script>
    import { onMount } from "svelte";

    export let auditStatus = "NONE";
    export let auditBannerKind = "not_audited";
    export let isCanonicalAudit = false;
    export let isCurrentBuildAudited = false;
    export let contractId = null;
    export let contractTimestamp = null;
    export let contractCommit = null;
    export let currentBuildCommit = null;
    export let equationFingerprint = null;
    export let auditCodeFingerprint = null;
    export let summaryPass = 0;
    export let summaryFail = 0;
    export let activeProfile = null;

    // Action functions passed from parent
    export let onRunGoldenSuite = () => {};
    export let isRunning = false;
    export let errorMsg = null;

    // Status visual mapping
    const getBadgeColor = (isCanonical, isCurrentBlock) => {
        if (isCanonical && isCurrentBlock)
            return {
                bg: "rgba(34,197,94,0.12)",
                border: "rgba(34,197,94,0.4)",
                text: "#4ade80",
                glow: "0 0 20px rgba(34,197,94,0.15)",
            };
        if (isCanonical && !isCurrentBlock)
            return {
                bg: "rgba(234,179,8,0.12)",
                border: "rgba(234,179,8,0.4)",
                text: "#facc15",
                glow: "0 0 20px rgba(234,179,8,0.15)",
            };
        if (auditStatus === "BUILD_NEWER") // Legacy fallback if needed
            return {
                bg: "rgba(59,130,246,0.12)",
                border: "rgba(59,130,246,0.4)",
                text: "#60a5fa",
                glow: "0 0 20px rgba(59,130,246,0.15)",
            };
        return {
            bg: "rgba(239,68,68,0.12)",
            border: "rgba(239,68,68,0.4)",
            text: "#f87171",
            glow: "0 0 20px rgba(239,68,68,0.15)",
        };
    };

    const getBadgeIcon = (isCanonical, isCurrentBlock) => {
        if (isCanonical && isCurrentBlock) return "✅";
        if (isCanonical && !isCurrentBlock) return "⚠️";
        if (auditStatus === "BUILD_NEWER") return "ℹ️";
        return "❌";
    };

    $: colors = getBadgeColor(isCanonicalAudit, isCurrentBuildAudited);
    $: hasContract = contractId && contractId !== "N/A";
</script>

<div class="scorecard-root">
    <!-- Hero Badge -->
    <div
        class="badge-row"
        style="background:{colors.bg}; border-color:{colors.border}; box-shadow:{colors.glow}"
    >
        <span class="badge-icon">{getBadgeIcon(isCanonicalAudit, isCurrentBuildAudited)}</span>
        <div class="badge-text">
            <span class="badge-label" style="color:{colors.text}"
                >AUDIT CONTRACT</span
            >
            <span class="badge-status" style="color:{colors.text}"
                >{auditStatus}</span
            >
        </div>
        {#if activeProfile}
            <span class="profile-tag">{activeProfile}</span>
        {/if}
    </div>

    <!-- Audit Details Grid — always visible -->
    <div class="details-card">
        <h3 class="details-title">Audit Details</h3>
        <div class="details-grid">
            <span class="label">Contract ID</span>
            <span class="value mono">{contractId || "N/A"}</span>

            <span class="label">Build Commit</span>
            <span class="value mono small breakable"
                >{currentBuildCommit || "unknown"}</span
            >

            <span class="label">Audit Commit</span>
            <span class="value mono small breakable"
                >{contractCommit || "unknown"}</span
            >

            <span class="label">Eq Fingerprint</span>
            <span class="value mono small breakable">
                {equationFingerprint || "unknown"}
            </span>

            <span class="label">Code Fingerprint</span>
            <span class="value mono small breakable">
                {auditCodeFingerprint || "unknown"}
            </span>

            <span class="label">Timestamp</span>
            <span class="value small truncate" title={contractTimestamp}
                >{contractTimestamp
                    ? String(contractTimestamp).substring(0, 19)
                    : "N/A"}</span
            >

            <span class="label">Summary</span>
            <span class="value">
                <span class="pass-count">{summaryPass} PASS</span>
                <span class="separator">/</span>
                <span class={summaryFail > 0 ? "fail-count" : "zero-fail"}
                    >{summaryFail} FAIL</span
                >
            </span>

            {#if activeProfile}
                <span class="label">Profile</span>
                <span class="value">
                    <span class="profile-inline">{activeProfile}</span>
                </span>
            {/if}
        </div>
    </div>

    {#if auditBannerKind === "stale_for_current_build"}
        <div class="warning-box">
            <strong>⚠ Warning:</strong> A canonical baseline pass exists for an older build, but this current build has un-audited changes.
        </div>
    {:else if !isCanonicalAudit && auditStatus !== "BUILD_NEWER"}
        <div class="warning-box red-warning">
            <strong>⚠ Warning:</strong> A canonical metric-backed audit is not complete. Claims remain in an experimental state.
        </div>
    {/if}

    <!-- Actions Section -->
    <div class="actions-section">
        <h3 class="actions-title">Run Controls</h3>
        <div class="actions-row">
            <button
                class="run-btn"
                on:click={onRunGoldenSuite}
                disabled={isRunning}
            >
                {#if isRunning}
                    <span class="pulse">Running Scenarios…</span>
                {:else}
                    Run Golden Suite (Experimental)
                {/if}
            </button>
        </div>

        {#if errorMsg}
            <div class="error-box">
                Error: {errorMsg}
            </div>
        {/if}
    </div>
</div>

<style>
    .scorecard-root {
        background: linear-gradient(135deg, #0f0f1a 0%, #151525 100%);
        border: 1px solid #2a2a40;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    }

    .badge-row {
        display: flex;
        align-items: center;
        gap: 12px;
        border: 1px solid;
        border-radius: 10px;
        padding: 12px 18px;
        transition: transform 0.2s;
    }
    .badge-row:hover {
        transform: scale(1.02);
    }

    .badge-icon {
        font-size: 1.75rem;
    }

    .badge-text {
        display: flex;
        flex-direction: column;
    }
    .badge-label {
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .badge-status {
        font-size: 0.75rem;
        opacity: 0.85;
    }

    .profile-tag {
        margin-left: auto;
        background: rgba(6, 182, 212, 0.15);
        border: 1px solid rgba(6, 182, 212, 0.35);
        color: #22d3ee;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        font-family: "JetBrains Mono", "Fira Code", monospace;
    }

    .details-card {
        margin-top: 16px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid #1f1f35;
        border-radius: 8px;
        padding: 16px 16px 20px;
    }
    .details-title {
        color: #06b6d4;
        font-weight: 700;
        font-size: 0.8rem;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid #1f1f35;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .details-grid {
        display: grid;
        grid-template-columns: 100px minmax(0, 1fr);
        gap: 4px 10px;
        align-items: baseline;
    }
    .label {
        color: #6b7280;
        font-size: 0.72rem;
        font-weight: 500;
        white-space: nowrap;
    }
    .truncate {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 100%;
    }
    .breakable {
        word-break: break-all;
        line-height: 1.3;
    }
    .value {
        color: #d1d5db;
        font-size: 0.8rem;
    }
    .mono {
        font-family: "JetBrains Mono", "Fira Code", monospace;
    }
    .small {
        font-size: 0.7rem;
    }

    .pass-count {
        color: #4ade80;
        font-weight: 600;
    }
    .fail-count {
        color: #f87171;
        font-weight: 600;
    }
    .zero-fail {
        color: #6b7280;
    }
    .separator {
        color: #4b5563;
        margin: 0 4px;
    }

    .profile-inline {
        background: rgba(6, 182, 212, 0.12);
        border: 1px solid rgba(6, 182, 212, 0.3);
        color: #22d3ee;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: "JetBrains Mono", "Fira Code", monospace;
        display: inline-block;
        line-height: 1.4;
    }

    .warning-box {
        margin-top: 14px;
        padding: 10px 14px;
        background: rgba(234, 179, 8, 0.08);
        border: 1px solid rgba(234, 179, 8, 0.25);
        border-radius: 8px;
        color: rgba(250, 204, 21, 0.85);
        font-size: 0.8rem;
        line-height: 1.5;
    }
    .red-warning {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.35);
        color: #fca5a5;
    }

    .actions-section {
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid #1f1f35;
    }
    .actions-title {
        color: #e5e7eb;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 12px;
    }
    .actions-row {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .run-btn {
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85rem;
        background: rgba(59, 130, 246, 0.12);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.35);
        cursor: pointer;
        transition: all 0.2s;
    }
    .run-btn:hover:not(:disabled) {
        background: rgba(59, 130, 246, 0.25);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
    }
    .run-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.6;
        }
    }

    .error-box {
        margin-top: 12px;
        padding: 10px 14px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 8px;
        color: #fca5a5;
        font-size: 0.8rem;
    }
</style>
