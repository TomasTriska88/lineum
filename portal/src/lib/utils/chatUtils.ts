
export function stripMarkdown(text: string): string {
    let clean = text
        .replace(/\*\*(.*?)\*\*/g, "$1") // Bold
        .replace(/\*(.*?)\*/g, "$1") // Italic
        .replace(/`+(.*?)`+/g, "$1") // Code
        .replace(/\[(.*?)\]\(.*?\)/g, "$1") // Links
        .replace(/[*#_`]/g, ""); // Cleanup leftovers

    return transliterateSymbols(clean);
}

export function transliterateSymbols(text: string, lang: string = "cs"): string {
    if (!lang.startsWith("cs")) return text;

    return (
        text
            // 1. Decimals: 0.012 -> 0,012 (Czech standard)
            .replace(/(\d+)\.(\d+)/g, "$1,$2")
            // 2. Asterisk Handling
            // "space * space" or "number * number" -> krat
            .replace(/(\d|\w)\s*\*\s*(\d|\w)/g, "$1 krat $2")
            // formatted bold/italic was already stripped in stripMarkdown, so remaining * are symbols
            .replace(/\*/g, "hvezdicka")
            // 3. Greek & Special Symbols
            .replace(/φ/g, "fi")
            .replace(/ψ/g, "psi")
            .replace(/Ω/g, "omega")
            .replace(/κ/g, "kappa")
            .replace(/=/g, "rovna se")
            .replace(/λ/g, "lambda")
            .replace(/Σ/g, "suma")
            .replace(/α/g, "alfa")
            .replace(/β/g, "beta")
            .replace(/γ/g, "gama")
            .replace(/Δ/g, "delta")
            .replace(/π/g, "pi")
            .replace(/μ/g, "mikro")
    );
}
