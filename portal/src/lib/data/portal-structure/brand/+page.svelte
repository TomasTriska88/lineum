<script lang="ts">
    import * as m from "$lib/paraglide/messages.js";
</script>

<svelte:head>
    <title>{m.brand_hero_title() + " | " + m.common_brand()}</title>
    <meta name="description" content={m.brand_hero_subtitle()} />
</svelte:head>

<div
    class="relative min-h-[80vh] overflow-hidden px-6 lg:px-8"
    style="padding-top: 8rem; padding-bottom: 6rem;"
>
    <!-- Abstract Tech Visuals (adapted from other pages for consistent look) -->
    <div
        class="pointer-events-none absolute inset-0 mix-blend-screen opacity-20"
    >
        <div
            class="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(0,255,255,0.1),transparent_50%)]"
        ></div>
        <div
            class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[rgba(0,255,255,0.3)] to-transparent"
        ></div>
    </div>

    <!-- Main Content Container with Glassmorphism -->
    <div class="relative max-w-5xl mx-auto z-10">
        <!-- Hero Header -->
        <header class="text-center mb-16">
            <h1
                class="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight mb-4 drop-shadow-lg"
            >
                <span
                    class="text-transparent bg-clip-text bg-gradient-to-br from-white to-gray-400"
                >
                    {m.brand_hero_title()}
                </span>
            </h1>
            <p
                class="text-xl md:text-2xl text-[var(--accent-cyan)] font-light max-w-2xl mx-auto drop-shadow-md"
            >
                {m.brand_hero_subtitle()}
            </p>
        </header>

        <!-- Color Palette Grid -->
        <section class="mb-16">
            <h2
                class="text-2xl font-bold mb-6 text-gray-200 border-b border-gray-800 pb-2"
            >
                {m.brand_colors_title()}
            </h2>
            <div
                class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 relative"
            >
                <!-- Cyber-Cyan (Wave) -->
                <div class="tech-card overflow-hidden group">
                    <div
                        class="h-32 w-full bg-[#00ffff] transition-transform duration-500 group-hover:scale-105"
                    ></div>
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-2">
                            <h3
                                class="text-xl font-bold tracking-tight text-white"
                            >
                                {m.brand_color_cyan_name()}
                            </h3>
                            <span
                                class="text-xs font-mono px-2 py-1 rounded bg-white/10 text-cyan-400"
                                >#00FFFF</span
                            >
                        </div>
                        <p
                            class="text-sm text-white/60 font-mono flex items-center gap-1 mb-3"
                        >
                            <span class="text-cyan-400">∂ₜψ = ∇²ψ</span>
                            <span class="opacity-50">•</span> Wave/Light
                        </p>
                        <p class="text-sm text-white/50">
                            {m.brand_color_cyan_desc()}
                        </p>
                    </div>
                </div>

                <!-- Purple (Memory) -->
                <div class="tech-card overflow-hidden group">
                    <div
                        class="h-32 w-full bg-[#c026d3] transition-transform duration-500 group-hover:scale-105"
                    ></div>
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-2">
                            <h3
                                class="text-xl font-bold tracking-tight text-white"
                            >
                                {m.brand_color_purple_title()}
                            </h3>
                            <span
                                class="text-xs font-mono px-2 py-1 rounded bg-white/10 text-fuchsia-400"
                                >#C026D3</span
                            >
                        </div>
                        <p
                            class="text-sm text-white/60 font-mono flex items-center gap-1 mb-3"
                        >
                            <span class="text-fuchsia-400">φψ + ∇φ</span>
                            <span class="opacity-50">•</span> Gravilon
                        </p>
                        <p class="text-sm text-white/50">
                            {m.brand_color_purple_desc()}
                        </p>
                    </div>
                </div>

                <!-- Amber (Identity) -->
                <div class="tech-card overflow-hidden group">
                    <div
                        class="h-32 w-full bg-[#ffaa00] transition-transform duration-500 group-hover:scale-105"
                    ></div>
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-2">
                            <h3
                                class="text-xl font-bold tracking-tight text-white"
                            >
                                {m.brand_color_amber_title()}
                            </h3>
                            <span
                                class="text-xs font-mono px-2 py-1 rounded bg-white/10 text-amber-400"
                                >#FFAA00</span
                            >
                        </div>
                        <p
                            class="text-sm text-white/60 font-mono flex items-center gap-1 mb-3"
                        >
                            <span class="text-amber-400">ΔQ = mcΔT</span>
                            <span class="opacity-50">•</span> Thermo/HDD
                        </p>
                        <p class="text-sm text-white/50">
                            {m.brand_color_amber_desc()}
                        </p>
                    </div>
                </div>

                <!-- Simulacrum Dark -->
                <div
                    class="tech-card overflow-hidden group border border-white/5"
                >
                    <div
                        class="h-32 w-full bg-[#050505] transition-transform duration-500 group-hover:scale-105 relative"
                    >
                        <!-- Subtle pattern for dark bg to not look empty -->
                        <div
                            class="absolute inset-0"
                            style="background-image: radial-gradient(rgba(255,255,255,0.1) 1px, transparent 1px); background-size: 8px 8px; opacity: 0.3;"
                        ></div>
                    </div>
                    <div class="p-6">
                        <div class="flex items-center justify-between mb-2">
                            <h3
                                class="text-xl font-bold tracking-tight text-white"
                            >
                                {m.brand_color_dark_title()}
                            </h3>
                            <span
                                class="text-xs font-mono px-2 py-1 rounded bg-white/5 text-white/40"
                                >#050505</span
                            >
                        </div>
                        <p
                            class="text-sm text-white/60 font-mono flex items-center gap-1 mb-3"
                        >
                            <span class="text-white/40">Ω = 0</span>
                            <span class="opacity-50">•</span> Void
                        </p>
                        <p class="text-sm text-white/50">
                            {m.brand_color_dark_desc()}
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Official Assets Downloads -->
        <section class="mb-16">
            <h2
                class="text-2xl font-bold mb-6 text-gray-200 border-b border-gray-800 pb-2"
            >
                {m.brand_downloads_title()}
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Static Logo SVG -->
                <div
                    class="bg-[#0a0a0f]/60 backdrop-blur-lg border border-white/10 rounded-2xl p-6 flex flex-col items-center text-center transition-all duration-300 hover:bg-[#0a0a0f]/80"
                >
                    <div
                        class="w-16 h-16 mb-4 flex justify-center items-center"
                    >
                        <img
                            src="/branding/lineum-logo-static.svg"
                            alt="Lineum Logo Static"
                            class="w-full h-full"
                        />
                    </div>
                    <h4 class="text-lg font-bold text-white leading-tight mb-1">
                        {m.brand_downloads_static_title()}
                    </h4>
                    <p class="text-xs text-gray-400 mb-4">
                        {m.brand_downloads_static_desc()}
                    </p>
                    <a
                        href="/branding/lineum-logo-static.svg"
                        download
                        class="mt-auto inline-flex items-center justify-center px-4 py-2 border border-[var(--accent-cyan)]/30 rounded-lg text-sm font-medium text-[var(--accent-cyan)] hover:bg-[var(--accent-cyan)] hover:text-black transition-colors"
                    >
                        <svg
                            class="w-4 h-4 mr-2"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                            ></path></svg
                        >
                        {m.brand_download_btn()}
                    </a>
                </div>

                <!-- Animated Logo SVG -->
                <div
                    class="bg-[#0a0a0f]/60 backdrop-blur-lg border border-white/10 rounded-2xl p-6 flex flex-col items-center text-center transition-all duration-300 hover:bg-[#0a0a0f]/80 relative overflow-hidden"
                >
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-[var(--accent-cyan)]/5 to-transparent pointer-events-none"
                    ></div>
                    <div
                        class="w-16 h-16 mb-4 flex justify-center items-center"
                    >
                        <img
                            src="/branding/lineum-logo-animated.svg"
                            alt="Lineum Logo Animated"
                            class="w-full h-full drop-shadow-[0_0_8px_rgba(0,255,255,0.4)]"
                        />
                    </div>
                    <h4 class="text-lg font-bold text-white leading-tight mb-1">
                        {m.brand_downloads_animated_title()}
                    </h4>
                    <p class="text-xs text-gray-400 mb-4">
                        {m.brand_downloads_animated_desc()}
                    </p>
                    <a
                        href="/branding/lineum-logo-animated.svg"
                        download
                        class="relative z-10 mt-auto inline-flex items-center justify-center px-4 py-2 border border-[var(--accent-cyan)]/30 rounded-lg text-sm font-medium text-[var(--accent-cyan)] hover:bg-[var(--accent-cyan)] hover:text-black transition-colors"
                    >
                        <svg
                            class="w-4 h-4 mr-2"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                            ></path></svg
                        >
                        {m.brand_download_btn()}
                    </a>
                </div>

                <!-- Social Cover Raster PNG -->
                <div
                    class="bg-[#0a0a0f]/60 backdrop-blur-lg border border-white/10 rounded-2xl p-6 flex flex-col items-center text-center transition-all duration-300 hover:bg-[#0a0a0f]/80"
                >
                    <div
                        class="w-full h-24 mb-4 flex justify-center items-center overflow-hidden rounded-lg bg-black border border-white/5"
                    >
                        <img
                            src="/branding/lineum-social-cover-1200x630.png"
                            alt="Lineum Social Cover"
                            class="w-full object-cover"
                        />
                    </div>
                    <h4 class="text-lg font-bold text-white leading-tight mb-1">
                        {m.brand_downloads_raster_title()}
                    </h4>
                    <p class="text-xs text-gray-400 mb-4">
                        {m.brand_downloads_raster_desc()}
                    </p>
                    <a
                        href="/branding/lineum-social-cover-1200x630.png"
                        download
                        class="mt-auto inline-flex items-center justify-center px-4 py-2 border border-white/20 rounded-lg text-sm font-medium text-white hover:bg-white hover:text-black transition-colors"
                    >
                        <svg
                            class="w-4 h-4 mr-2"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                            ></path></svg
                        >
                        {m.brand_download_btn()}
                    </a>
                </div>
            </div>
        </section>

        <!-- Brand Philosophy -->
        <section
            class="bg-[#0a0a0f]/60 backdrop-blur-xl border border-[var(--accent-cyan)]/20 rounded-2xl p-8 relative overflow-hidden"
        >
            <div
                class="absolute -top-32 -right-32 w-64 h-64 bg-[var(--accent-cyan)]/10 rounded-full blur-[100px] pointer-events-none"
            ></div>

            <h2 class="text-2xl font-bold mb-4 text-white flex items-center">
                <span
                    class="w-2 h-2 rounded-full bg-[var(--accent-cyan)] mr-3 shadow-[0_0_8px_rgba(0,255,255,0.8)]"
                ></span>
                {m.brand_philosophy_title()}
            </h2>
            <p class="text-gray-300 leading-relaxed text-lg max-w-4xl">
                {m.brand_philosophy_desc()}
            </p>
        </section>
    </div>
</div>
