<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
    import HashingDemo from "../HashingDemo.svelte";
</script>

<ShowcaseTemplate
    badge="4 / 5 API SUITE"
    title="LineumHash API"
    description="A physical, non-algorithmic hash function. Takes a user payload and maps it into initial disturbance drops in the simulation field. As the field collapses, its complex structural memory footprint serves as the impenetrable hash payload."
    traditionalTitle="Algorithmic Hashing (SHA-256)"
    traditionalDesc="Math-based algorithms vulnerable to theoretical inversion via Shor's algorithm on upcoming quantum computers."
    lineumTitle="Topological One-Way Function"
    lineumDesc="Quantum-inversion is impossible. The fracture is chaotic and must be strictly forward-simulated step by step; it cannot be mathematically short-circuited."
    language="curl / REST"
    codeSnippet={`curl -X POST https://api.lineum.io/v1/hash/topological \\
  -H "Authorization: Bearer lnm_enterprise_***" \\
  -H "Content-Type: application/json" \\
  -d '{
    "payload": "user_password_string_123",
    "pump_cycles": 1500,
    "avalanche_threshold": 0.01
  }'`}
>
    <!-- Visual -->
    <div slot="visual" class="w-full h-[500px]">
        <div
            class="h-full w-full overflow-hidden bg-slate-950 rounded-3xl border border-slate-800 relative z-0"
        >
            <div class="absolute inset-x-8 top-8 bottom-8">
                <HashingDemo />
            </div>
        </div>
    </div>

    <!-- Proof -->
    <div
        slot="proof"
        class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-center gap-4 text-xs font-mono text-slate-400"
    >
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>RESISTANCE</span>
            <span class="text-white font-bold text-rose-400"
                >Quantum (Shor's Algorithm) Immune</span
            >
        </div>
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>AVALANCHE EFFECT</span>
            <span class="text-emerald-400">> 50% bit flip per char</span>
        </div>
        <div class="flex justify-between">
            <span>TARGET COMPLIANCE</span>
            <span class="text-sky-400">HIPAA, High-Security Vaults</span>
        </div>
    </div>
</ShowcaseTemplate>
