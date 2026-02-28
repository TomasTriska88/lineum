import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('i18n Translation Quality & Completeness', () => {
    const langs = ['en', 'cs', 'de', 'ja'];
    const messagesPath = path.resolve(__dirname, '../../messages');

    // Load all dictionaries
    const dicts: Record<string, Record<string, string>> = {};
    for (const lang of langs) {
        const fileContent = fs.readFileSync(path.join(messagesPath, `${lang}.json`), 'utf-8');
        dicts[lang] = JSON.parse(fileContent);
    }

    // Get all keys from English (base)
    const baseKeys = Object.keys(dicts['en']);

    it('all languages should have exactly the same keys as English source', () => {
        for (const lang of langs) {
            if (lang === 'en') continue;

            const currentKeys = Object.keys(dicts[lang]);

            // Find missing keys
            const missing = baseKeys.filter(k => !currentKeys.includes(k));
            if (missing.length > 0) {
                console.error(`Missing keys in ${lang}: ${missing}`);
            }

            // Find extra extra
            const extra = currentKeys.filter(k => !baseKeys.includes(k));
            if (extra.length > 0) {
                console.error(`Extra unused keys in ${lang}: ${extra}`);
            }

            expect(missing.length).toBe(0);
            expect(extra.length).toBe(0);
        }
    });

    it('all interpolation variables {name} should match exactly across all languages', () => {
        const variableRegex = /\{([^}]+)\}/g;

        for (const key of baseKeys) {
            const baseText = dicts['en'][key];
            const baseVarsSet = new Set<string>();
            let match;

            // Extract EN variables
            while ((match = variableRegex.exec(baseText)) !== null) {
                baseVarsSet.add(match[1]);
            }

            // Check other languages
            for (const lang of langs) {
                if (lang === 'en') continue;

                const langText = dicts[lang][key];
                if (!langText) continue; // Missing keys are caught by previous test

                const langVarsSet = new Set<string>();
                let langMatch;
                while ((langMatch = variableRegex.exec(langText)) !== null) {
                    langVarsSet.add(langMatch[1]);
                }

                // Compare sets
                const baseVarsArr = Array.from(baseVarsSet).sort();
                const langVarsArr = Array.from(langVarsSet).sort();

                expect(langVarsArr, `Mismatch in interpolation variables for key "${key}" in language "${lang}"`).toEqual(baseVarsArr);
            }
        }
    });

    it('ensure no placeholder AI artifacts like [Insert Translation Here] exist', () => {
        const artifactPhrases = [
            '[insert',
            'translate this',
            '[todo]',
            '[to do]',
            'todo:',
            'lorem ipsum',
        ];

        for (const lang of langs) {
            for (const key of baseKeys) {
                const text = dicts[lang][key];
                if (!text) continue;

                const lowerText = text.toLowerCase();
                for (const artifact of artifactPhrases) {
                    expect(lowerText).not.toContain(artifact);
                }
            }
        }
    });

    it('ensure translations are not identical to english (detect missing localization)', () => {
        // Some words might naturally be identical (like "API", "Lineum", etc.)
        // We'll skip keys that are too short to accurately judge
        for (const lang of langs) {
            if (lang === 'en') continue;

            let identicalCount = 0;
            let totalChecked = 0;

            for (const key of baseKeys) {
                const enText = dicts['en'][key];
                const langText = dicts[lang][key];

                if (!enText || !langText) continue;
                if (enText.length < 15) continue; // Skip short strings like "Back", "API", etc.
                if (enText.includes('Lineum') && enText.length < 20) continue; // Brand names

                totalChecked++;
                if (enText === langText) {
                    identicalCount++;
                }
            }

            // For a mature dictionary, identical long strings should be rare
            // If more than 5% of long strings are identical to english, it's highly suspicious
            const identicalRatio = identicalCount / totalChecked;
            if (identicalRatio > 0.05) {
                console.warn(`Suspiciously high ratio of identical english strings in ${lang}: ${Math.round(identicalRatio * 100)}% (${identicalCount}/${totalChecked})`);
            }

            // Setting a generous threshold, but enforcing it
            expect(identicalRatio).toBeLessThan(0.15);
        }
    });
});
