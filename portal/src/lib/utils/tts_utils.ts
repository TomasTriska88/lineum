
/**
 * Detects whether the text should be spoken in Czech or English.
 * 
 * Heuristic Refined:
 * 1. Strong Czech Chars (Almost never in English): (r, e, u, n, t, d with carons) -> Always Czech.
 * 2. Safe English Words (Strictly not Czech): the, this, that, ... -> Always English (overrides Czech chars).
 * 3. Weak Czech Chars (Could be names in English): (a, e, i, y, u with accutes, s, z, c with carons) -> Czech only if no Safe English.
 * 
 * @param text The text to analyze
 * @returns 'cs-CZ' or 'en-US'
 */
export function detectLanguage(text: string): 'cs-CZ' | 'en-US' {
    const hasStrongCzech = /[řěůňťď]/i.test(text);
    const hasWeakCzech = /[áéíýžšžčú]/i.test(text);

    // List of words that strongly indicate English and are unlikely to appear in a Czech sentence 
    // (except as loan words, but usually "the" or "is" implies English structure).
    const safeEnglishPattern = /\b(the|this|that|which|with|have|from|would|will|there|what|your|are|who|when|where|why|how|hello|hi|thanks|thank)\b/i;
    const hasSafeEnglish = safeEnglishPattern.test(text);

    // Logic:
    // - Safe English -> English (Overrides even strong Czech chars like "Hello Mr. Rerich")
    // - Otherwise -> Czech (if ANY Czech char found)
    // - Default -> English (if no Czech chars found)

    const isCzech = (hasStrongCzech || hasWeakCzech) && !hasSafeEnglish;

    return isCzech ? 'cs-CZ' : 'en-US';
}

/**
 * Selects the best available voice for the given language.
 * 
 * @param voices List of available SpeechSynthesisVoice objects
 * @param lang 'cs-CZ' or 'en-US'
 * @returns The selected SpeechSynthesisVoice or undefined
 */
export function selectVoice(voices: SpeechSynthesisVoice[], lang: 'cs-CZ' | 'en-US'): SpeechSynthesisVoice | undefined {
    if (lang === 'cs-CZ') {
        const czechVoice = voices.find(
            (v) =>
                v.lang.includes("cs") &&
                (v.name.includes("Vlasta") || // Windows Female
                    v.name.includes("Zuzana") || // Nuance Female
                    v.name.includes("Google") || // Google Czech (usually female)
                    v.name.toLowerCase().includes("female") // Generic fallback
                ),
        );
        // Generic Czech Fallback
        return czechVoice || voices.find((v) => v.lang.includes("cs"));
    } else {
        const englishVoice = voices.find(
            (v) =>
                v.lang.includes("en") &&
                (v.name.includes("Zira") ||       // Windows Female
                    v.name.includes("Google US") ||  // Google US (Female default)
                    v.name.includes("Samantha") ||   // Apple Female
                    v.name.toLowerCase().includes("female") // Generic fallback
                ),
        );
        // Generic English Fallback
        return englishVoice || voices.find((v) => v.lang.includes("en"));
    }
}
