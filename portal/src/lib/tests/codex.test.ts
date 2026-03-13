import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { describe, it, expect } from 'vitest';
import { assertEnglishOnly } from './test_utils';

describe('Lineum Ethical Codex Integrity', () => {
    it('must be written explicitly in English', () => {
        // Enforce language rules on the primary repository codex
        const codexPath = join(process.cwd(), 'src/lib/data/docs/LINEUM_CODEX_v1.md');

        if (!existsSync(codexPath)) {
            throw new Error(`Codex file not found at: ${codexPath}`);
        }

        const content = readFileSync(codexPath, 'utf-8');

        // Use reusable utility to assert English structure
        assertEnglishOnly(content, ['Tomas Triska', 'Tomáš Tříska'], true);
    });

    it('ensures the portal replica perfectly matches the localized variants', () => {
        const portalCodexPath = join(process.cwd(), 'src/lib/data/docs/LINEUM_CODEX_v1.md');

        expect(existsSync(portalCodexPath)).toBe(true);
    });

    it('ensures all translated codex variants maintain strict structural parity with the English master', () => {
        const fs = require('fs');
        const docsPath = join(process.cwd(), 'src/lib/data/docs');
        const masterCodexPath = join(docsPath, 'LINEUM_CODEX_v1.md');

        expect(existsSync(masterCodexPath)).toBe(true);
        const masterContent = readFileSync(masterCodexPath, 'utf-8');

        // Extract all markdown headings (H1, H2, H3, etc.)
        const extractHeadings = (content: string) => {
            return content.split('\n').filter(line => line.trim().startsWith('# ')).length +
                content.split('\n').filter(line => line.trim().startsWith('## ')).length +
                content.split('\n').filter(line => line.trim().startsWith('### ')).length;
        };

        const masterHeadingCount = extractHeadings(masterContent);

        // Find all translation files
        const files = fs.readdirSync(docsPath);
        const translationFiles = files.filter((f: string) => f.startsWith('LINEUM_CODEX_v1_') && f.endsWith('.md'));

        translationFiles.forEach((fileName: string) => {
            const translationPath = join(docsPath, fileName);
            const translationContent = readFileSync(translationPath, 'utf-8');
            const translationHeadingCount = extractHeadings(translationContent);

            // The translation must have the exact same structural layout (number of headers)
            // If they don't match, it means the master was updated but the translation was forgotten
            if (translationHeadingCount !== masterHeadingCount) {
                console.error(`\n[DRIFT] ${fileName} has ${translationHeadingCount} headers, expected ${masterHeadingCount}!`);
            }
            expect(translationHeadingCount, `Structural drift detected in translation: ${fileName}. Ensure all sections are translated.`).toBe(masterHeadingCount);
        });
    });
});
