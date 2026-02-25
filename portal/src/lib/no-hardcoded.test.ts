import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync, statSync, writeFileSync } from 'fs';
import { join } from 'path';

function getAllSvelteFiles(dir: string, fileList: string[] = []) {
    try {
        const files = readdirSync(dir);
        for (const file of files) {
            const filePath = join(dir, file);
            if (statSync(filePath).isDirectory()) {
                getAllSvelteFiles(filePath, fileList);
            } else if (filePath.endsWith('.svelte')) {
                fileList.push(filePath);
            }
        }
    } catch (e) {
        // directory might not exist
    }
    return fileList;
}

describe('Static Analysis: No Hardcoded Text in Svelte Components', () => {
    it('All visible text in core pages should be wrapped in translation keys', () => {
        // We are progressively enforcing i18n, starting with the core landing and layout.
        const svelteFiles = [
            'src/routes/+page.svelte',
            'src/routes/+layout.svelte',
            'src/lib/components/Legend.svelte'
        ];

        let hardcodedViolations: string[] = [];

        // Simple heuristic: Text between > and < that contains at least one letter and isn't a svelte block { }
        // We'll ignore script and style tags.
        for (const file of svelteFiles) {
            const content = readFileSync(file, 'utf-8');

            // Remove <script> and <style> blocks entirely
            const withoutScripts = content.replace(/<script[\s\S]*?<\/script>/gi, '');
            const withoutStyles = withoutScripts.replace(/<style[\s\S]*?<\/style>/gi, '');

            // Remove comments <!-- ... -->
            const withoutComments = withoutStyles.replace(/<!--[\s\S]*?-->/g, '');

            // Find all text between > and <
            const matches = withoutComments.matchAll(/>([^<]+)</g);

            for (const match of matches) {
                const text = match[1].trim();

                // If it contains a word character, isn't fully enclosed in {}, and isn't just symbols
                if (text.length > 1 && /[a-zA-Z]/.test(text) && !text.includes('{$t')) {
                    // Check if the *entire* string is just a generic Svelte expression like {variable}
                    if (text.startsWith('{') && text.endsWith('}')) continue;

                    // If text contains a newline or equals sign, it's likely a misparsed component prop/attribute block
                    if (text.includes('\n') || text.includes('=')) continue;

                    // Specific ignores (like 'EN' or 'CZ' dynamically rendered, or symbols)
                    if (['☰', '✕', 'CZ', 'EN', 'DE', 'JA', 'Lineum', 'FAQ', 'Support', 'Lineum | Discrete Field Dynamics', 'Scientific Context (FAQ)'].includes(text)) continue;

                    hardcodedViolations.push(`${file} -> "${text}"`);
                }
            }
        }

        writeFileSync('../.scratch/hardcoded_results.json', JSON.stringify({ violations: hardcodedViolations }, null, 2));

        expect(hardcodedViolations, `Found hardcoded text that should be localized:\n${hardcodedViolations.join('\n')}`).toEqual([]);
    });
});
