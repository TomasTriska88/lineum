<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
</script>

<ShowcaseTemplate
    badge="2 / 5 API SUITE"
    title="Extreme Zeta Entropy API"
    description="A premium B2B endpoint that artificially generates mathematically rare Riemann Zeta points by colliding massive structures. The Quantum Chaos."
    traditionalTitle="Odlyzko Analytical Algorithms"
    traditionalDesc="Calculating these values analytically requires supercomputers and days of processing time."
    lineumTitle="Lineum Oracle-as-a-Service"
    lineumDesc="Extracts Riemann Zeta patterns directly from simulated geometric collapse in milliseconds."
    language="bash"
    codeSnippet={`curl -X POST https://api.lineum.io/v1/entropy/zeta \\
  -H "Authorization: Bearer lnm_enterprise_***" \\
  -d '{"bytes": 64, "mixing_nodes": 1000}'`}
>
    <!-- Visual -->
    <div
        slot="visual"
        class="w-full flex items-center justify-center p-8 bg-slate-950/80 rounded-3xl border border-rose-500/20 shadow-[0_0_50px_rgba(244,63,94,0.1)] overflow-hidden h-[400px] relative"
    >
        <!-- CSS placeholder for geometric collapse -->
        <div
            class="absolute inset-0 flex items-center justify-center opacity-40"
        >
            <div
                class="w-64 h-64 border border-rose-500/30 rounded-full animate-ping [animation-duration:3s]"
            ></div>
            <div
                class="absolute w-48 h-48 border border-rose-400/50 rounded-full animate-pulse"
            ></div>
            <div
                class="absolute text-rose-500 font-mono text-sm tracking-widest font-bold"
            >
                GUE STRUCTURAL COLLAPSE
            </div>
        </div>
    </div>

    <!-- Proof -->
    <div
        slot="proof"
        class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-center gap-4 text-xs font-mono text-slate-400"
    >
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>TARGET AUDIENCE</span>
            <span class="text-white">National Security, ZK-Vaults</span>
        </div>
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>SECURITY ARCHITECTURE</span>
            <span class="text-rose-400">Topology Destroyed in Hashing</span>
        </div>
        <div class="flex justify-between">
            <span>STATISTICAL ENSEMBLE</span>
            <span class="text-sky-400">Gaussian Unitary (GUE)</span>
        </div>
    </div>
</ShowcaseTemplate>
