<script lang="ts">
    import partnersData from "$lib/data/content/partners.json";

    type Partner = { name: string; logo: string };
    const partners: Partner[] = partnersData as Partner[];
</script>

<div class="py-12 md:py-16 w-full flex flex-col items-center">
    <h3
        class="text-xs uppercase tracking-widest font-bold text-slate-500 mb-8 text-center"
    >
        Trusted By Enterprise Leaders
    </h3>

    {#if partners && partners.length > 0}
        <div
            class="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-70"
        >
            {#each partners as partner}
                <img
                    src={partner.logo}
                    alt={partner.name}
                    class="h-8 md:h-10 object-contain grayscale hover:grayscale-0 transition-all duration-300"
                />
            {/each}
        </div>
    {:else}
        <div
            class="bg-slate-900/50 border border-slate-800 rounded-2xl p-8 max-w-2xl text-center shadow-lg"
        >
            <div
                class="w-12 h-12 bg-sky-500/10 border border-sky-500/30 rounded-full flex flex-col items-center justify-center mx-auto mb-4"
            >
                <svg
                    class="w-6 h-6 text-sky-400"
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
            <p class="text-lg text-slate-300 font-semibold mb-2">
                Buďte první, předběhněte svou konkurenci.
            </p>
            <p class="text-sm text-slate-400 mb-6">
                Staňte se naším prvním partnerem a získejte všechny naše
                produkty doživotně jen za cenu nákladů.
            </p>
            <a
                href="mailto:partners@lineum.io"
                class="inline-flex items-center gap-2 px-6 py-2.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-sm rounded-lg transition-colors shadow-[0_0_20px_rgba(56,189,248,0.2)]"
            >
                Become an Early Adopter
            </a>
        </div>
    {/if}
</div>
