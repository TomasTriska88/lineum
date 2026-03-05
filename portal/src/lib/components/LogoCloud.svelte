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
            class="flex flex-col items-center justify-center max-w-2xl text-center mx-auto mt-4 px-4"
        >
            <div
                class="w-14 h-14 bg-sky-500/10 border border-sky-500/30 rounded-full flex flex-col items-center justify-center mx-auto mb-6 shadow-[0_0_30px_rgba(56,189,248,0.15)]"
            >
                <svg
                    class="w-7 h-7 text-sky-400"
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
            <h4
                class="text-2xl md:text-3xl text-slate-100 font-bold tracking-tight mb-4"
            >
                Be the first to step into the future.
            </h4>
            <p
                class="text-[16px] md:text-lg text-slate-400 font-light mb-8 max-w-xl mx-auto"
            >
                Become our pioneer partner and secure lifetime access to all our
                enterprise products at cost.
            </p>
            <a
                href="mailto:hello@lineum.io"
                class="inline-flex items-center gap-2 px-8 py-3.5 bg-sky-500 hover:bg-sky-400 font-bold text-sm md:text-base rounded-full transition-all hover:scale-105 shadow-[0_0_20px_rgba(56,189,248,0.3)]"
                style="color: #020617 !important; text-decoration: none;"
            >
                Become an Early Adopter
            </a>
        </div>
    {/if}
</div>
