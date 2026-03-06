<script>
    import { onMount } from "svelte";

    export let auditStatus = "NONE";
    export let contractId = null;
    export let contractTimestamp = null;
    export let contractCommit = null;
    export let equationFingerprint = null;
    export let summaryPass = 0;
    export let summaryFail = 0;

    // Action functions passed from parent
    export let onRunGoldenSuite = () => {};
    export let isRunning = false;
    export let errorMsg = null;

    let isHoveringBadge = false;

    // Status visual mapping
    const getBadgeStyle = (status) => {
        if (status === "AUDITED")
            return "bg-green-500/20 text-green-400 border-green-500/50";
        if (status === "OUTDATED")
            return "bg-yellow-500/20 text-yellow-400 border-yellow-500/50";
        return "bg-red-500/20 text-red-400 border-red-500/50";
    };

    const getBadgeIcon = (status) => {
        if (status === "AUDITED") return "✅";
        if (status === "OUTDATED") return "⚠️";
        return "❌";
    };
</script>

<div class="bg-[#151520] border border-gray-800 rounded-xl p-6 shadow-2xl">
    <div class="hero-section">
        <h2 class="text-xl font-bold text-cyan-400 mb-4">
            Laboratory Scorecard
        </h2>

        <!-- Audit Badge & Tooltip Container -->
        <div
            class="relative w-max"
            role="group"
            on:mouseenter={() => (isHoveringBadge = true)}
            on:mouseleave={() => (isHoveringBadge = false)}
        >
            <div
                class="badge {getBadgeStyle(
                    auditStatus,
                )} border rounded-lg px-4 py-2 flex items-center gap-3 cursor-help shadow-lg transition-transform hover:scale-105"
            >
                <span class="text-2xl">{getBadgeIcon(auditStatus)}</span>
                <div class="flex flex-col">
                    <span class="font-bold tracking-wide"
                        >ACTIVE AUDIT CONTRACT</span
                    >
                    <span class="text-sm opacity-80">{auditStatus}</span>
                </div>
            </div>

            <!-- Hover Details -->
            {#if isHoveringBadge}
                <div
                    class="absolute left-0 top-full mt-2 w-80 p-4 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 text-sm animate-fade-in pointer-events-none"
                >
                    <h3
                        class="text-cyan-400 font-bold mb-2 border-b border-gray-700 pb-1"
                    >
                        Audit Details
                    </h3>
                    <div
                        class="grid grid-cols-[100px_1fr] gap-x-2 gap-y-1 text-gray-300"
                    >
                        <span class="text-gray-500">Contract ID:</span>
                        <span class="font-mono text-xs break-all"
                            >{contractId || "N/A"}</span
                        >

                        <span class="text-gray-500">Commit:</span>
                        <span class="font-mono text-xs"
                            >{contractCommit || "N/A"}</span
                        >

                        <span class="text-gray-500">Eq Fingerprint:</span>
                        <span
                            class="font-mono text-xs"
                            title={equationFingerprint}
                            >{equationFingerprint
                                ? equationFingerprint.substring(0, 8) + "..."
                                : "N/A"}</span
                        >

                        <span class="text-gray-500">Timestamp:</span>
                        <span class="text-xs">{contractTimestamp || "N/A"}</span
                        >

                        <span class="text-gray-500">Summary:</span>
                        <span>
                            <span class="text-green-400"
                                >{summaryPass} PASS</span
                            >
                            /
                            <span
                                class={summaryFail > 0
                                    ? "text-red-400"
                                    : "text-gray-400"}>{summaryFail} FAIL</span
                            >
                        </span>
                    </div>
                </div>
            {/if}
        </div>

        {#if auditStatus !== "AUDITED"}
            <div class="mt-3 text-sm text-yellow-400/80 max-w-lg">
                <strong>Warning:</strong> The current build's equation does not have
                an active Audit-Grade contract. Whitepaper claims cannot be verified
                canonically (EXPERIMENTAL mode only) until a new Audit Contract is
                generated.
            </div>
        {/if}
    </div>

    <!-- Actions Section -->
    <div class="actions-section mt-8 pt-6 border-t border-gray-800">
        <h3 class="text-lg font-bold text-gray-200 mb-4">Run Controls</h3>
        <div class="flex items-center gap-4">
            <button
                class="px-4 py-2 rounded font-bold bg-blue-600/20 text-blue-400 border border-blue-500/50 hover:bg-blue-600/40 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
                on:click={onRunGoldenSuite}
                disabled={isRunning}
            >
                {#if isRunning}
                    <span class="animate-pulse">Running Scenarios...</span>
                {:else}
                    Run Golden Suite (Experimental)
                {/if}
            </button>
        </div>

        {#if errorMsg}
            <div
                class="mt-4 p-3 bg-red-900/40 border border-red-500/50 rounded text-red-300 text-sm"
            >
                Error: {errorMsg}
            </div>
        {/if}
    </div>
</div>

<style>
    .animate-fade-in {
        animation: fadeIn 0.2s ease-out forwards;
    }
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
