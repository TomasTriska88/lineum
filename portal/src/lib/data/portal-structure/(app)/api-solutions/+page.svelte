<script lang="ts">
    import { onMount } from "svelte";
    import * as m from "$lib/paraglide/messages.js";
    import LogoCloud from "$lib/components/LogoCloud.svelte";
    import { portal } from "$lib/actions/portal";
    import UrbanRoutingApp from "$lib/components/api-showcase/UrbanRoutingApp.svelte";
    import EvacRoutingApp from "$lib/components/api-showcase/EvacRoutingApp.svelte";
    import FastTrngApp from "$lib/components/api-showcase/FastTrngApp.svelte";
    import ZetaEntropyApp from "$lib/components/api-showcase/ZetaEntropyApp.svelte";
    import Web3VrfApp from "$lib/components/api-showcase/Web3VrfApp.svelte";
    import LineumHashApp from "$lib/components/api-showcase/LineumHashApp.svelte";
    import GamingRngApp from "$lib/components/api-showcase/GamingRngApp.svelte";

    // ... hydration tracking for Playwright tests ...
    let pageHydrated = false;
    onMount(() => {
        pageHydrated = true;
    });

    // --- ROI Calculator Logic ---
    let fleetSize = 500;
    let dailyOps = 100; // in thousands

    $: estimatedSavings = fleetSize * (dailyOps * 1000) * 365 * 0.0006; // $0.0006 saving per computation

    function formatCurrency(value: number) {
        if (value >= 1e6) {
            return "$" + (value / 1e6).toFixed(1) + "M";
        } else if (value >= 1e3) {
            return "$" + (value / 1e3).toFixed(0) + "k";
        }
        return "$" + value.toFixed(0);
    }

    // --- Dynamic Snippet Fetcher ---
    let snippetLanguage = "python";

    const SNIPPETS = {
        python: `import lineum

# 1. Initialize the AI LTM Field
solver = lineum.Client(api_key="lnm_enterprise_***")

# 2. Extract paths directly from the field
result = solver.route(
    map="urban_city_block.bin",
    agents=[{"start_x": 10, "start_y": 10}, {"start_x": 20, "start_y": 20}],
    target={"x": 60, "y": 110}
)
`,
        curl: `curl -X POST https://api.lineum.io/v1/compute/swarm \\
  -H "Authorization: Bearer lnm_enterprise_***" \\
  -H "Content-Type: application/json" \\
  -d '{
    "map": "urban_city_block.bin",
    "target": {"x": 60, "y": 110},
    "agents": [{"start_x": 10, "start_y": 10}, {"start_x": 20, "start_y": 20}]
  }'`,
    };

    $: apiSnippet = SNIPPETS[snippetLanguage as keyof typeof SNIPPETS];
</script>

<svelte:head>
    <title>{m.common_brand()} API Solutions | Swarm Routing Showcase</title>
</svelte:head>

<div
    data-hydrated={pageHydrated}
    class="min-h-screen text-slate-50 font-sans flex flex-col pt-[104px]"
>
    <!-- Main Content -->
    <main class="flex-1 w-full flex flex-col items-center">
        <!-- VERCEL-STYLE HERO SECTION (Centered, Clean, Massive) -->
        <div
            class="w-full flex flex-col items-center justify-center text-center px-4 pt-16 pb-16 max-w-5xl mx-auto"
            style="margin-top: 180px;"
        >
            <div class="flex items-center gap-3 mb-8">
                <span
                    class="px-3 py-1 bg-white/5 border border-white/10 text-slate-300 text-xs font-bold rounded-full uppercase tracking-wider backdrop-blur-md"
                >
                    {m.api_solutions_hero_domain()}
                </span>
                <span
                    class="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full uppercase tracking-wider flex items-center gap-2 backdrop-blur-md"
                >
                    <span
                        class="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"
                    ></span>
                    {m.common_beta()}
                </span>
            </div>

            <h1
                class="text-5xl sm:text-7xl font-extrabold tracking-tight mb-8 leading-[1.05]"
                style="font-family: var(--font-sans);"
            >
                {@html m.api_solutions_hero_title_full({
                    highlight_span: "<span class='text-gradient-multi'>",
                    highlight_span_end: "</span>",
                })}
            </h1>

            <p class="text-slate-400 text-xl max-w-2xl font-light mb-12">
                {m.api_solutions_hero_subtitle()}
            </p>

            <div class="cta-group">
                <a
                    href="#roi"
                    class="btn btn-primary"
                    style="background-color: var(--accent-cyan); color: #020617;"
                    >{m.api_solutions_hero_cta_build()}</a
                >
                <a
                    href="/wiki"
                    class="btn btn-outline"
                    style="border-color: rgba(255,255,255,0.2); color: white;"
                    >{m.api_solutions_hero_cta_docs()}</a
                >
            </div>

            <div class="mt-8 md:mt-16 w-full">
                <LogoCloud />
            </div>
        </div>

        <!-- Core Paradigm Shift (B2B Marketing) -->
        <div
            id="roi"
            class="w-full max-w-5xl mx-auto px-4 mb-32 flex flex-col items-center"
        >
            <div class="text-center mb-16">
                <h2 class="text-3xl md:text-5xl font-bold text-white mb-6">
                    {m.api_solutions_roi_title()}
                </h2>
                <p class="text-slate-400 text-xl font-light max-w-3xl mx-auto">
                    {@html m.api_solutions_roi_subtitle()}
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
                <!-- Feature 1: Scaling -->
                <div
                    class="group relative bg-slate-950 border border-slate-800 rounded-2xl p-8 flex flex-col items-center text-center overflow-hidden hover:border-violet-500/50 hover:shadow-[0_0_40px_rgba(139,92,246,0.15)] transition-all"
                >
                    <!-- Background Glow -->
                    <div
                        class="absolute -top-24 -left-24 w-48 h-48 bg-violet-500/20 rounded-full blur-[80px] pointer-events-none group-hover:bg-violet-500/30 transition-all"
                    ></div>

                    <!-- Massive Callout -->
                    <div
                        class="text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-b from-white to-violet-500/50 drop-shadow-[0_0_15px_rgba(139,92,246,0.3)] select-none uppercase"
                    >
                        ENTROPY
                    </div>
                    <h4 class="text-lg font-bold text-white mb-3">
                        {m.api_solutions_features_rng_title()}
                    </h4>
                    <p
                        class="text-slate-400 text-sm leading-relaxed max-w-[200px]"
                    >
                        {m.api_solutions_features_rng_desc()}
                    </p>
                </div>

                <!-- Feature 2: Latency -->
                <div
                    class="group relative bg-slate-950 border border-slate-800 rounded-2xl p-8 flex flex-col items-center text-center overflow-hidden hover:border-emerald-500/50 hover:shadow-[0_0_40px_rgba(16,185,129,0.15)] transition-all"
                >
                    <!-- Background Glow -->
                    <div
                        class="absolute -top-24 -left-24 w-48 h-48 bg-emerald-500/20 rounded-full blur-[80px] pointer-events-none group-hover:bg-emerald-500/30 transition-all"
                    ></div>

                    <!-- Massive Callout -->
                    <div
                        class="text-4xl sm:text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-b from-white to-emerald-500/50 drop-shadow-[0_0_15px_rgba(16,185,129,0.3)] select-none uppercase"
                    >
                        AVALANCHE
                    </div>
                    <h4 class="text-xl font-bold text-white mb-3">
                        {m.api_solutions_features_hash_title()}
                    </h4>
                    <p
                        class="text-slate-400 text-sm leading-relaxed max-w-[200px]"
                    >
                        {m.api_solutions_features_hash_desc()}
                    </p>
                </div>

                <!-- Feature 3: DevOps -->
                <div
                    class="group relative bg-slate-950 border border-slate-800 rounded-2xl p-8 flex flex-col items-center text-center overflow-hidden hover:border-sky-500/50 hover:shadow-[0_0_40px_rgba(56,189,248,0.15)] transition-all"
                >
                    <!-- Background Glow -->
                    <div
                        class="absolute -top-24 -left-24 w-48 h-48 bg-sky-500/20 rounded-full blur-[80px] pointer-events-none group-hover:bg-sky-500/30 transition-all"
                    ></div>

                    <!-- Massive Callout -->
                    <div
                        class="text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-b from-white to-sky-500/50 drop-shadow-[0_0_15px_rgba(56,189,248,0.3)] select-none uppercase"
                    >
                        LOGIC
                    </div>
                    <h4 class="text-xl font-bold text-white mb-3">
                        {m.api_solutions_features_lpl_title()}
                    </h4>
                    <p
                        class="text-slate-400 text-sm leading-relaxed max-w-[200px]"
                    >
                        {m.api_solutions_features_lpl_desc()}
                    </p>
                </div>
            </div>
        </div>

        <!-- Scroll Anchor & Navigation Tabs -->
        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-12 max-w-4xl mx-auto"
        ></div>

        <!-- Floating Side Navigation (Desktop) -->
        <nav
            use:portal
            class="hidden xl:flex fixed left-8 top-1/2 -translate-y-1/2 z-50 flex-col gap-3 bg-slate-900/60 backdrop-blur-xl border border-slate-800 p-4 rounded-3xl shadow-2xl"
        >
            <a
                href="#routing"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-sky-400 group-hover:shadow-[0_0_15px_rgba(56,189,248,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Routing</span
                >
            </a>
            <a
                href="#fast_trng"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-violet-400 group-hover:shadow-[0_0_15px_rgba(139,92,246,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Fast TRNG</span
                >
            </a>
            <a
                href="#zeta"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-rose-400 group-hover:shadow-[0_0_15px_rgba(244,63,94,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Zeta Entropy</span
                >
            </a>
            <a
                href="#web3"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-sky-400 group-hover:shadow-[0_0_15px_rgba(56,189,248,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Web3 Oracle</span
                >
            </a>
            <a
                href="#hash"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-emerald-400 group-hover:shadow-[0_0_15px_rgba(16,185,129,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >LineumHash</span
                >
            </a>
            <a
                href="#gaming"
                class="group flex items-center gap-4 px-2 py-2 rounded-xl transition-all hover:bg-slate-800"
            >
                <div
                    class="w-2.5 h-2.5 rounded-full bg-slate-600 group-hover:bg-emerald-400 group-hover:shadow-[0_0_15px_rgba(16,185,129,0.8)] transition-all"
                ></div>
                <span
                    class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest hidden lg:block pr-2"
                    >Gaming RNG</span
                >
            </a>
        </nav>

        <!-- Mobile/Tablet Top Navigation (Hidden on Large Screens) -->
        <div
            class="w-full max-w-6xl mx-auto px-4 mb-24 sticky top-[100px] z-[110] xl:hidden"
        >
            <div
                class="flex items-center gap-3 bg-slate-900/90 backdrop-blur-xl border border-slate-700 p-3 rounded-2xl shadow-xl overflow-x-auto overflow-y-hidden snap-x snap-mandatory"
            >
                <a
                    href="#routing"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Routing</a
                >
                <a
                    href="#fast_trng"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Fast TRNG</a
                >
                <a
                    href="#zeta"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Zeta</a
                >
                <a
                    href="#web3"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Web3</a
                >
                <a
                    href="#hash"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Hash</a
                >
                <a
                    href="#gaming"
                    class="snap-start px-5 py-3 rounded-full text-base font-bold transition-all !text-slate-300 hover:!text-white hover:bg-slate-800 whitespace-nowrap !no-underline flex-shrink-0"
                    >Gaming</a
                >
            </div>
        </div>

        <!-- content wrapped -->
        <div
            id="routing"
            class="w-full flex-col flex items-center scroll-mt-48"
        >
            <UrbanRoutingApp />

            <div
                class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent my-32 max-w-4xl mx-auto"
            ></div>

            <div id="evac" class="scroll-mt-48 w-full">
                <EvacRoutingApp />
            </div>
        </div>
        <!-- End of routing section div -->

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="fast_trng" class="scroll-mt-48 w-full">
            <FastTrngApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="zeta" class="scroll-mt-48 w-full">
            <ZetaEntropyApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="web3" class="scroll-mt-48 w-full">
            <Web3VrfApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="hash" class="scroll-mt-48 w-full">
            <LineumHashApp />
        </div>

        <div
            class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-32 max-w-4xl mx-auto"
        ></div>

        <div id="gaming" class="scroll-mt-48 w-full">
            <GamingRngApp />
        </div>

        <!-- Explore Specialized Domains (Grid to Subpages) -->
        <div class="w-full max-w-7xl mx-auto mb-32 flex flex-col items-center">
            <div class="text-center mb-12">
                <h3 class="text-3xl md:text-4xl font-bold text-white mb-4">
                    {m.api_solutions_domains_title()}
                </h3>
                <p class="text-slate-400 text-lg max-w-2xl mx-auto">
                    {m.api_solutions_domains_desc()}
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
                <!-- Hardware & Circuits -->
                <a
                    href="/api-solutions/hardware-routing"
                    class="group relative bg-slate-900/40 border border-slate-800 rounded-2xl p-6 overflow-hidden transition-all hover:bg-slate-900/60 hover:border-violet-500/50 hover:shadow-[0_0_30px_rgba(139,92,246,0.15)] flex flex-col h-full"
                >
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                    ></div>
                    <div class="relative z-10 flex flex-col h-full">
                        <div
                            class="w-10 h-10 rounded-lg bg-violet-500/20 border border-violet-500/30 flex items-center justify-center mb-4 shrink-0 text-violet-400"
                        >
                            <svg
                                class="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                                ></path></svg
                            >
                        </div>
                        <h4
                            class="text-xl font-bold text-white mb-2 group-hover:text-violet-300 transition-colors"
                        >
                            {m.api_solutions_domains_hardware_title()}
                        </h4>
                        <p class="text-sm text-slate-400 mb-6 flex-grow">
                            {m.api_solutions_domains_hardware_desc()}
                        </p>
                        <div
                            class="flex items-center text-violet-400 text-sm font-bold mt-auto"
                        >
                            {m.api_solutions_domains_hardware_link()}
                            <span
                                class="ml-2 group-hover:translate-x-1 transition-transform"
                                >→</span
                            >
                        </div>
                    </div>
                </a>

                <!-- Generative Antennas -->
                <a
                    href="/api-solutions/generative-antennas"
                    class="group relative bg-slate-900/40 border border-slate-800 rounded-2xl p-6 overflow-hidden transition-all hover:bg-slate-900/60 hover:border-sky-500/50 hover:shadow-[0_0_30px_rgba(56,189,248,0.15)] flex flex-col h-full"
                >
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-sky-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                    ></div>
                    <div class="relative z-10 flex flex-col h-full">
                        <div
                            class="w-10 h-10 rounded-lg bg-sky-500/20 border border-sky-500/30 flex items-center justify-center mb-4 shrink-0 text-sky-400"
                        >
                            <svg
                                class="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"
                                ></path></svg
                            >
                        </div>
                        <h4
                            class="text-xl font-bold text-white mb-2 group-hover:text-sky-300 transition-colors"
                        >
                            {m.api_solutions_domains_antennas_title()}
                        </h4>
                        <p class="text-sm text-slate-400 mb-6 flex-grow">
                            {m.api_solutions_domains_antennas_desc()}
                        </p>
                        <div
                            class="flex items-center text-sky-400 text-sm font-bold mt-auto"
                        >
                            {m.api_solutions_domains_antennas_link()}
                            <span
                                class="ml-2 group-hover:translate-x-1 transition-transform"
                                >→</span
                            >
                        </div>
                    </div>
                </a>

                <!-- Medical / Vasculature -->
                <a
                    href="/api-solutions/vascular-medicine"
                    class="group relative bg-slate-900/40 border border-slate-800 rounded-2xl p-6 overflow-hidden transition-all hover:bg-slate-900/60 hover:border-emerald-500/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.15)] flex flex-col h-full"
                >
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                    ></div>
                    <div class="relative z-10 flex flex-col h-full">
                        <div
                            class="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mb-4 shrink-0 text-emerald-400"
                        >
                            <svg
                                class="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                                ></path></svg
                            >
                        </div>
                        <h4
                            class="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors"
                        >
                            {m.api_solutions_domains_fluid_title()}
                        </h4>
                        <p class="text-sm text-slate-400 mb-6 flex-grow">
                            {m.api_solutions_domains_fluid_desc()}
                        </p>
                        <div
                            class="flex items-center text-emerald-400 text-sm font-bold mt-auto"
                        >
                            {m.api_solutions_domains_fluid_link()}
                            <span
                                class="ml-2 group-hover:translate-x-1 transition-transform"
                                >→</span
                            >
                        </div>
                    </div>
                </a>
            </div>

            <div class="mt-8 text-center">
                <button
                    class="px-6 py-2 rounded-full border border-slate-700 bg-slate-800/50 text-slate-300 text-sm font-bold hover:bg-slate-800 hover:text-white transition-all flex items-center gap-2 mx-auto"
                >
                    <svg
                        class="w-4 h-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        ></path></svg
                    >
                    {m.api_solutions_domains_btn_download()}
                </button>
            </div>
        </div>

        <!-- The True Potential Explainer -->
        <div class="w-full max-w-5xl mx-auto mb-32 px-4">
            <div
                class="bg-slate-900 border border-slate-800 rounded-3xl p-8 md:p-12 relative overflow-hidden"
            >
                <!-- Background Glow -->
                <div
                    class="absolute top-0 right-0 w-[500px] h-[500px] bg-sky-500/5 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3"
                ></div>

                <div
                    class="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-12 items-center"
                >
                    <div>
                        <div
                            class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-bold font-mono w-fit mb-6"
                        >
                            {m.api_solutions_vision_tag()}
                        </div>
                        <h2
                            class="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight"
                        >
                            {@html m.api_solutions_vision_title()}
                        </h2>
                        <p class="text-slate-400 text-lg leading-relaxed mb-6">
                            {m.api_solutions_vision_p1()}
                        </p>
                        <p class="text-slate-400 text-lg leading-relaxed mb-6">
                            {@html m.api_solutions_vision_p2()}
                        </p>
                        <p
                            class="text-slate-400 text-lg leading-relaxed font-medium"
                        >
                            {m.api_solutions_vision_p3()}
                        </p>
                    </div>

                    <div class="flex flex-col gap-4">
                        <div
                            class="p-6 rounded-2xl bg-black/50 border border-slate-800 backdrop-blur-sm"
                        >
                            <h4
                                class="text-white font-bold mb-2 flex items-center gap-2"
                            >
                                {@html m.api_solutions_vision_f1_title()}
                            </h4>
                            <p class="text-sm text-slate-500">
                                {m.api_solutions_vision_f1_desc()}
                            </p>
                        </div>
                        <div
                            class="p-6 rounded-2xl bg-black/50 border border-slate-800 backdrop-blur-sm"
                        >
                            <h4
                                class="text-white font-bold mb-2 flex items-center gap-2"
                            >
                                {@html m.api_solutions_vision_f2_title()}
                            </h4>
                            <p class="text-sm text-slate-500">
                                {m.api_solutions_vision_f2_desc()}
                            </p>
                        </div>
                        <div
                            class="p-6 rounded-2xl bg-black/50 border border-slate-800 backdrop-blur-sm"
                        >
                            <h4
                                class="text-white font-bold mb-2 flex items-center gap-2"
                            >
                                {@html m.api_solutions_vision_f3_title()}
                            </h4>
                            <p class="text-sm text-slate-500">
                                {m.api_solutions_vision_f3_desc()}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ROI & Integration Section -->
        <div
            class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6 w-full max-w-7xl"
        >
            <!-- ROI Calculator -->
            <div
                class="border border-emerald-500/30 bg-emerald-950/20 backdrop-blur-sm rounded-2xl p-6 lg:p-8 flex flex-col justify-between shadow-[0_0_30px_rgba(16,185,129,0.05)]"
            >
                <div>
                    <h3 class="text-xl font-bold text-white mb-2">
                        {m.api_solutions_calculator_title()}
                    </h3>
                    <p class="text-slate-400 text-sm mb-8">
                        {m.api_solutions_calculator_desc()}
                    </p>

                    <div class="flex flex-col gap-6">
                        <div class="flex flex-col gap-3">
                            <div class="flex justify-between items-end">
                                <label
                                    for="fleetSizeInput"
                                    class="text-xs font-bold text-slate-300 uppercase tracking-wider"
                                    >{m.api_solutions_calculator_fleet_label()}</label
                                >
                                <span
                                    class="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded"
                                    >{fleetSize}</span
                                >
                            </div>
                            <input
                                id="fleetSizeInput"
                                type="range"
                                bind:value={fleetSize}
                                class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                                min="10"
                                max="5000"
                                step="10"
                            />
                        </div>

                        <div class="flex flex-col gap-3">
                            <div class="flex justify-between items-end">
                                <label
                                    for="dailyOpsInput"
                                    class="text-xs font-bold text-slate-300 uppercase tracking-wider"
                                    >{m.api_solutions_calculator_ops_label()}</label
                                >
                                <span
                                    class="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded"
                                    >{dailyOps}k</span
                                >
                            </div>
                            <input
                                id="dailyOpsInput"
                                type="range"
                                bind:value={dailyOps}
                                class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                                min="1"
                                max="1000"
                                step="5"
                            />
                        </div>
                    </div>
                </div>

                <div
                    class="mt-8 pt-6 border-t border-emerald-900/50 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4"
                >
                    <div>
                        <div
                            class="text-[10px] text-emerald-500/70 uppercase tracking-widest font-bold mb-1"
                        >
                            {m.api_solutions_calculator_savings_label()}
                        </div>
                        <div
                            class="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200"
                        >
                            {formatCurrency(estimatedSavings)}
                        </div>
                    </div>
                    <button
                        class="btn btn-primary"
                        style="background-color: var(--accent-color); color: white;"
                    >
                        {m.api_solutions_calculator_btn_sales()}
                    </button>
                </div>
            </div>

            <!-- API Code Snippet & Paywall -->
            <div
                class="border border-slate-800 bg-slate-900/40 backdrop-blur-sm rounded-2xl flex flex-col overflow-hidden"
            >
                <div
                    class="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between"
                >
                    <div class="flex items-center gap-2">
                        <span
                            class="w-3 h-3 rounded-full bg-red-400/20 border border-red-500/50"
                        ></span>
                        <span
                            class="w-3 h-3 rounded-full bg-amber-400/20 border border-amber-500/50"
                        ></span>
                        <span
                            class="w-3 h-3 rounded-full bg-emerald-400/20 border border-emerald-500/50"
                        ></span>
                    </div>
                    <div class="text-xs font-mono text-slate-500">
                        POST /api/v1/compute/swarm
                    </div>
                    <div class="flex gap-2">
                        <button
                            class="text-xs font-bold {snippetLanguage === 'curl'
                                ? 'text-sky-400 bg-sky-500/10 border border-sky-500/30'
                                : 'text-slate-400 bg-slate-800 hover:text-white border-transparent'} px-3 py-1 rounded transition-colors"
                            on:click={() => (snippetLanguage = "curl")}
                            >cURL</button
                        >
                        <button
                            class="text-xs font-bold {snippetLanguage ===
                            'python'
                                ? 'text-sky-400 bg-sky-500/10 border border-sky-500/30'
                                : 'text-slate-400 bg-slate-800 hover:text-white border-transparent'} px-3 py-1 rounded transition-colors"
                            on:click={() => (snippetLanguage = "python")}
                            >Python</button
                        >
                    </div>
                </div>
                <!-- Code Snippet Body -->
                <div
                    class="p-6 relative flex-1 text-sm font-mono text-slate-300 overflow-hidden leading-relaxed"
                >
                    <pre class="whitespace-pre-wrap font-mono text-sm">
                            {apiSnippet}
                        </pre>

                    <!-- Paywall Overlay -->
                    <div
                        class="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-slate-900 via-slate-900/90 to-transparent flex flex-col items-center justify-end pb-8 px-6 text-center z-10"
                    >
                        <div
                            class="flex items-center justify-center w-12 h-12 bg-slate-800 rounded-full mb-3 shadow-lg border border-slate-700"
                        >
                            <svg
                                class="w-5 h-5 text-sky-400"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                ></path></svg
                            >
                        </div>
                        <h4 class="font-bold text-white mb-1">
                            Production Access Locked
                        </h4>
                        <p class="text-xs text-slate-400 max-w-xs mx-auto mb-4">
                            Export raw datasets, upload custom floorplans, and
                            access real-time WebSockets with an Enterprise plan.
                        </p>
                        <button
                            class="btn btn-outline"
                            style="border-color: var(--accent-cyan); color: white;"
                        >
                            Upgrade to Lineum Enterprise
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-8 border-t border-slate-800/80 pt-12">
            <LogoCloud />
        </div>
    </main>
</div>

<style>
    :global(:root) {
        --nav-height: 0px;
    }
    :global(body) {
        /* Ensure normal scroll behavior and background for the new B2B layout */
        background-color: #020617; /* tailwind text-slate-950 */
        margin: 0;
    }
</style>
