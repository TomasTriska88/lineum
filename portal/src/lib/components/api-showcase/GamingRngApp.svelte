<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
</script>

<ShowcaseTemplate
    badge="5 / 5 API SUITE"
    title="Provably-Fair Gaming API"
    description="High-precision bounded number generation algorithms tailored for statistical audits in gambling and state lotteries. The Zeta-Certified RNG."
    traditionalTitle="Pseudo-RNG Functions"
    traditionalDesc="Standard rand() functions are cyclical, algorithmic and subject to underlying OS seed manipulation patterns."
    lineumTitle="Simulation Mathematical Log"
    lineumDesc="Output includes the exact simulation log, proving the bounded number was derived from a simulated topological interaction."
    language="python"
    codeSnippet={`import lineum

solver = lineum.Client(api_key="lnm_enterprise_***")

# Bounded extraction for lotteries [1, 49]
result = solver.gaming.generate_bounded(
    min=1, 
    max=49,
    count=6,
    certified_log=True
)

print(f"Drawn numbers: {result.numbers}")
print(f"Audit log id: {result.audit_log.id}")`}
>
    <!-- Visual -->
    <div
        slot="visual"
        class="w-full flex items-center justify-center p-8 bg-slate-950/80 rounded-3xl border border-emerald-500/20 shadow-[0_0_40px_rgba(16,185,129,0.1)] overflow-hidden h-[400px] relative"
    >
        <div class="absolute inset-0 flex flex-col items-center justify-center">
            <div
                class="w-32 h-32 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mb-6"
            >
                <span
                    class="text-5xl font-black text-emerald-400 font-mono text-transparent bg-clip-text bg-gradient-to-b from-white to-emerald-500"
                    >42</span
                >
            </div>
            <div
                class="text-emerald-400/50 font-mono text-xs max-w-sm text-center"
            >
                CERTIFICATE LOG: <br />
                <span class="opacity-50"
                    >0x8f7a9d... derived from interaction matrix topology
                    [1024x1024]. Zeta collapse validated by Lineum Engine Core.</span
                >
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
            <span class="text-white">Online Casinos, State Lotteries</span>
        </div>
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>CERTIFICATION</span>
            <span class="text-emerald-400">Provably Fair Mathematics</span>
        </div>
        <div class="flex justify-between">
            <span>BIAS DISTRIBUTION</span>
            <span class="text-sky-400">Uniform &lt; 0.0000001% Variance</span>
        </div>
    </div>
</ShowcaseTemplate>
