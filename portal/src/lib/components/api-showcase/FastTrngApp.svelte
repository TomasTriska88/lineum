<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import TrueRng from "../TrueRng.svelte";
</script>

<ShowcaseTemplate
    badge="1 / 5 API SUITE"
    title="Fast Edge-of-Chaos TRNG API"
    description="Harvest mathematically pure, highly volatile entropy from the vacuum noise of simulated chaotic fields. Ideal for low-latency session keys and web cryptography."
    traditionalTitle="Traditional PRNGs / Hardware Sources"
    traditionalDesc="Predictable algorithms (Mersenne Twister) or slow external hardware devices bottlenecking at high throughput."
    lineumTitle="Lineum Simulated Vacuum"
    lineumDesc="Generates millions of unpredictable states trivially by reading the microscopic phase fluctuations in the fluid."
    language="JSON / REST"
    codeSnippet={`{
  "status": "success",
  "source": "lineum_quantum_chaos_trng",
  "requested_bytes": 32,
  "entropy_hex": "e7b9a23f8c01d4a9...9f1a",
  "certification": "FIPS 140-3 compliant signature"
}`}
>
    <div
        slot="visual"
        class="w-full flex items-center justify-center p-8 bg-slate-950/80 rounded-3xl border border-slate-800 overflow-hidden h-[500px]"
    >
        <div class="transform scale-90 md:scale-100">
            <TrueRng />
        </div>
    </div>

    <div
        slot="proof"
        class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-center gap-4 text-xs font-mono text-slate-400"
    >
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>ENTROPY SOURCE</span>
            <span class="text-white">ψ/φ COORDINATES SCRUBBED</span>
        </div>
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>NIST SUITE PASS RATE</span>
            <span class="text-emerald-400">100.00%</span>
        </div>
        <div class="flex justify-between">
            <span>OUTPUT THROUGHPUT</span>
            <span class="text-sky-400">140 MB/s per core</span>
        </div>
    </div>
</ShowcaseTemplate>
