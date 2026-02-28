import { expect } from 'vitest';

/**
 * Asserts that the provided string content is written in English
 * by checking for the absence of Czech diacritics and common structural words.
 * @param content The string text to validate
 * @param allowedExceptions Array of strings (e.g., author names) that are allowed to contain diacritics
 * @param requireEnglishStructure Boolean. If true, enforces presence of "the", "and", etc. (useful for prose, disable for code).
 * @param filePath The file path being verified (for debugging).
 */
export function assertEnglishOnly(content: string, allowedExceptions: string[] = [], requireEnglishStructure: boolean = true, filePath: string = 'Unknown') {
    let cleanContent = content;

    // Remove strictly allowed exceptions (like 'Tomáš Tříska') before checking
    for (const ex of allowedExceptions) {
        cleanContent = cleanContent.split(ex).join('');
    }

    // 1. Hard fail on common Czech-specific characters
    const czechChars = /[áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]/;
    const hasCzechChars = czechChars.test(cleanContent);
    if (hasCzechChars) {
        const match = cleanContent.match(czechChars);
        const index = match?.index || 0;
        const contextStart = Math.max(0, index - 20);
        const contextEnd = Math.min(cleanContent.length, index + 20);
        const errorContext = cleanContent.substring(contextStart, contextEnd);
        console.error(`[${filePath}] Found invalid character: '${match?.[0]}' in context: "...${errorContext}..."`);
    }
    expect(hasCzechChars, `[${filePath}] Content contains prohibited Czech diacritics`).toBe(false);

    // 2. Positive check: Should contain standard English structural words
    if (requireEnglishStructure) {
        const lowerContent = cleanContent.toLowerCase();
        expect(lowerContent.includes(' the ') || lowerContent.includes(' and ') || lowerContent.includes(' is ') || lowerContent.includes(' import '),
            "Content lacks foundational English structure").toBe(true);
    }
}
