export async function load() {
    // Statically bundle the codex directly so there are no File System issues in production
    const codexRaw = await import("$lib/data/docs/LINEUM_CODEX_v1.md?raw");

    return {
        content: codexRaw.default
    };
}
