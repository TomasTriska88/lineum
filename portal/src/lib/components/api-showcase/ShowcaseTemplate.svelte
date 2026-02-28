<script lang="ts">
    export let badge = "USE CASE";
    export let title = "Product Title";
    export let description =
        "Customer Explanation: Immediate, jargon-free explanation of 'what this solves'.";

    // Comparison
    export let traditionalTitle = "Traditional Method";
    export let traditionalDesc = "O(N) algorithms.";
    export let lineumTitle = "Lineum Capability";
    export let lineumDesc = "O(1) tensor fields.";

    // Integration
    export let codeSnippet = "";
    export let language = "typescript";
</script>

<div class="w-full flex flex-col gap-16 items-center mb-32">
    <!-- Header: A) Customer Explanation -->
    <div class="w-full max-w-4xl text-center px-4">
        <div
            class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-xs font-bold font-mono w-fit mx-auto mb-6"
        >
            <span class="w-2 h-2 rounded-full bg-violet-500 animate-pulse"
            ></span>
            {badge}
        </div>
        <h2
            class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight"
        >
            {@html title}
        </h2>
        <p
            class="text-slate-400 text-xl font-light leading-relaxed max-w-3xl mx-auto"
        >
            {@html description}
        </p>
    </div>

    <!-- B) Visual Immediacy -->
    <div class="w-full max-w-6xl px-4">
        <slot name="visual">
            <div
                class="w-full aspect-video md:aspect-[21/9] bg-slate-900/50 border border-slate-800 rounded-3xl flex items-center justify-center shadow-xl overflow-hidden relative group"
            >
                <div
                    class="absolute inset-0 bg-violet-500/5 opacity-0 group-hover:opacity-100 transition-opacity"
                ></div>
                <!-- Visual Component Placeholder -->
                <span class="text-slate-600 font-mono text-sm"
                    >[Interactive Visualization Placeholder]</span
                >
            </div>
        </slot>
    </div>

    <!-- Details Grid -->
    <div class="w-full max-w-6xl px-4 grid grid-cols-1 lg:grid-cols-2 gap-12">
        <!-- C) Head-to-Head Comparison -->
        <div class="flex flex-col gap-6">
            <h3 class="text-2xl font-bold text-white">Head-to-Head</h3>

            <div class="flex flex-col gap-4">
                <!-- Traditional -->
                <div
                    class="p-6 rounded-2xl bg-slate-900 border border-slate-800"
                >
                    <div class="flex items-center gap-3 mb-3">
                        <div
                            class="w-8 h-8 rounded-full bg-rose-500/10 flex items-center justify-center text-rose-500"
                        >
                            ✕
                        </div>
                        <h4 class="text-white font-bold">{traditionalTitle}</h4>
                    </div>
                    <p class="text-slate-400 text-sm leading-relaxed">
                        {@html traditionalDesc}
                    </p>
                </div>

                <!-- Lineum -->
                <div
                    class="p-6 rounded-2xl bg-emerald-500/5 border border-emerald-500/20"
                >
                    <div class="flex items-center gap-3 mb-3">
                        <div
                            class="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400"
                        >
                            ✓
                        </div>
                        <h4 class="text-emerald-400 font-bold">
                            {lineumTitle}
                        </h4>
                    </div>
                    <p class="text-slate-300 text-sm leading-relaxed">
                        {@html lineumDesc}
                    </p>
                </div>
            </div>
        </div>

        <!-- Right Side: Proof & Code -->
        <div class="flex flex-col gap-8">
            <!-- D) The Proof -->
            <div class="flex flex-col gap-4">
                <h3 class="text-2xl font-bold text-white mb-2">The Proof</h3>
                <slot name="proof">
                    <div
                        class="w-full h-48 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-center"
                    >
                        <span
                            class="text-slate-600 font-mono text-xs text-center px-6"
                        >
                            [Benchmark Logs & Performance Bounds]
                        </span>
                    </div>
                </slot>
            </div>

            <!-- E) Integration Code -->
            <div class="flex flex-col gap-4">
                <div class="flex items-center justify-between mt-4 mb-2">
                    <h3 class="text-xl font-bold text-white">Integration</h3>
                    <span class="text-xs font-mono text-slate-500 uppercase"
                        >{language}</span
                    >
                </div>
                <div
                    class="bg-[#0d1117] border border-slate-800 rounded-2xl p-6 overflow-x-auto shadow-inner"
                >
                    <pre class="text-sm text-sky-400 font-mono"><code
                            >{codeSnippet}</code
                        ></pre>
                </div>
            </div>
        </div>
    </div>
</div>
