<script lang="ts" context="module">
    // Import the params to access them in the template
    import { page } from "$app/stores";
</script>

<script lang="ts">
    import * as m from "$lib/paraglide/messages.js";
    import TrueRng from "$lib/components/TrueRng.svelte";
    import type { PageData } from "./$types";

    export let data: PageData;
</script>

<svelte:head>
    <title>
        {m[
            `api_solutions_scenarios_${data.scenarioKey}_title` as keyof typeof m
        ]()} | {m.common_brand()} API
    </title>
</svelte:head>

<div class="min-h-screen bg-black text-white selection:bg-{data.accent}/30">
    <!-- Navigation Gradient Overlap -->
    <div
        class="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b {data.heroColor} opacity-50 pointer-events-none"
    ></div>

    <div class="container mx-auto px-6 lg:px-12 pt-48 pb-24 relative z-10">
        <!-- Breadcrumbs -->
        <a
            href="/api-solutions"
            class="text-slate-400 hover:text-white flex items-center gap-2 mb-12 text-sm font-medium transition-colors w-fit"
        >
            <svg
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
            </svg>
            {m.api_solutions_slug_back()}
        </a>

        <!-- Hero -->
        <div class="max-w-4xl mb-24">
            <div
                class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-{data.accent}/10 border border-{data.accent}/20 text-{data.accent} text-xs font-bold font-mono w-fit mb-6"
            >
                <span
                    class="w-2 h-2 rounded-full bg-{data.accent} animate-pulse"
                ></span>
                SPECIALIZED DOMAIN
            </div>
            <h1 class="text-5xl md:text-7xl font-bold tracking-tight mb-8">
                {m[
                    `api_solutions_scenarios_${data.scenarioKey}_title` as keyof typeof m
                ]()}
            </h1>
            <p
                class="text-xl md:text-2xl text-slate-300 leading-relaxed max-w-3xl"
            >
                <strong class="text-white"
                    >{m[
                        `api_solutions_scenarios_${data.scenarioKey}_subtitle` as keyof typeof m
                    ]()}</strong
                ><br /><br />
                {m[
                    `api_solutions_scenarios_${data.scenarioKey}_description` as keyof typeof m
                ]()}
            </p>
        </div>

        <!-- Domain Specific WebGL Demo -->
        {#if data.slug === "true-rng"}
            <div class="mb-32">
                <TrueRng />
            </div>
        {:else}
            <!-- Placeholder for Domain Specific WebGL Demo -->
            <div
                class="w-full aspect-video md:aspect-[21/9] bg-slate-900/50 border border-slate-800 rounded-3xl mb-32 flex items-center justify-center relative overflow-hidden group"
            >
                <div
                    class="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay"
                ></div>
                <div class="flex flex-col items-center gap-4">
                    <svg
                        class="w-12 h-12 text-slate-600"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="1.5"
                            d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"
                        />
                    </svg>
                    <span
                        class="text-slate-500 font-mono text-sm tracking-widest uppercase"
                        >{m.api_solutions_slug_demo_title()}</span
                    >
                </div>
            </div>
        {/if}

        <!-- The Paradigm Shift -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-16 mb-32">
            <!-- Discrete Failure -->
            <div class="p-8 rounded-3xl bg-slate-900 border border-slate-800">
                <div
                    class="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-6"
                >
                    <svg
                        class="w-6 h-6 text-red-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                </div>
                <h3 class="text-2xl font-bold mb-4">
                    {m.api_solutions_slug_fail_title()}
                </h3>
                <p class="text-slate-400 leading-relaxed text-lg">
                    {m[
                        `api_solutions_scenarios_${data.scenarioKey}_problem` as keyof typeof m
                    ]()}
                </p>
            </div>

            <!-- Field Success -->
            <div
                class="p-8 rounded-3xl border border-{data.accent}/30 bg-gradient-to-b from-{data.accent}/5 to-transparent relative overflow-hidden"
            >
                <div
                    class="absolute top-0 right-0 w-64 h-64 bg-{data.accent}/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2"
                ></div>

                <div class="relative z-10">
                    <div
                        class="w-12 h-12 rounded-xl bg-{data.accent}/20 flex items-center justify-center mb-6"
                    >
                        <svg
                            class="w-6 h-6 text-{data.accent}"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M13 10V3L4 14h7v7l9-11h-7z"
                            />
                        </svg>
                    </div>
                    <h3 class="text-2xl font-bold mb-4">
                        {m.api_solutions_slug_success_title()}
                    </h3>
                    <p class="text-slate-300 leading-relaxed text-lg">
                        {m[
                            `api_solutions_scenarios_${data.scenarioKey}_solution` as keyof typeof m
                        ]()}
                    </p>
                </div>
            </div>
        </div>

        <!-- Integration & API -->
        <div class="max-w-4xl mb-32">
            <h2 class="text-3xl font-bold mb-8">
                {m.api_solutions_slug_integration()}
            </h2>
            <div
                class="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl"
            >
                <div
                    class="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between"
                >
                    <div class="flex gap-2">
                        <div class="w-3 h-3 rounded-full bg-slate-700"></div>
                        <div class="w-3 h-3 rounded-full bg-slate-700"></div>
                        <div class="w-3 h-3 rounded-full bg-slate-700"></div>
                    </div>
                    <span class="text-xs font-mono text-slate-500"
                        >api.lineum-core.com</span
                    >
                </div>
                <div class="p-6 bg-[#0d1117] overflow-x-auto text-sm">
                    <div
                        class="text-xs text-slate-500 mb-4 font-mono select-none border-b border-slate-800 pb-2"
                    >
                        lineum_{$page.params.slug}.example
                    </div>
                    <pre><code class="language-typescript text-emerald-400"
                            >{data.apiSnippet}</code
                        ></pre>
                </div>
            </div>
        </div>

        <!-- CTA -->
        <div
            class="w-full rounded-3xl p-12 relative overflow-hidden flex flex-col items-center text-center border border-white/10 bg-gradient-to-b from-slate-900 to-black"
        >
            <!-- Glow background -->
            <div
                class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl h-[300px] bg-{data.accent}/20 rounded-full blur-[100px] opacity-50 pointer-events-none"
            ></div>

            <h2
                class="text-3xl md:text-5xl font-bold text-white mb-6 relative z-10"
            >
                {m.api_solutions_cta_title()}
            </h2>
            <p class="text-slate-400 text-lg mb-10 max-w-xl relative z-10">
                {m.api_solutions_cta_desc()}
            </p>
            <div class="flex gap-4 relative z-10">
                <a
                    href="#sales"
                    class="px-8 py-4 bg-white text-black font-bold rounded-xl hover:bg-slate-200 transition-colors"
                >
                    {m.api_solutions_cta_sales()}
                </a>
                <a
                    href="/docs"
                    class="px-8 py-4 border border-white/20 text-white font-bold rounded-xl hover:bg-white/5 transition-colors"
                >
                    {m.api_solutions_cta_docs()}
                </a>
            </div>
        </div>
    </div>
</div>
