import { languageTag } from "$lib/paraglide/runtime.js";

export async function load() {
    // Determine the active language statically via Paraglide
    const lang = languageTag();
    let codexRaw;

    try {
        if (lang === 'cs') codexRaw = await import("$lib/data/docs/LINEUM_CODEX_v1_cs.md?raw");
        else codexRaw = await import("$lib/data/docs/LINEUM_CODEX_v1.md?raw");
    } catch (e) {
        // Fallback to strict base English if missing translation
        codexRaw = await import("$lib/data/docs/LINEUM_CODEX_v1.md?raw");
    }

    return {
        content: codexRaw.default
    };
}
