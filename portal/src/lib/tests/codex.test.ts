import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { describe, it, expect } from 'vitest';
import { assertEnglishOnly } from './test_utils';

describe('Lineum Ethical Codex Integrity', () => {
    it('must be written explicitly in English', () => {
        // Enforce language rules on the primary repository codex
        const codexPath = join(process.cwd(), '../docs/LINEUM_CODEX_v1.md');

        if (!existsSync(codexPath)) {
            throw new Error(`Codex file not found at: ${codexPath}`);
        }

        const content = readFileSync(codexPath, 'utf-8');

        // Use reusable utility to assert English structure
        assertEnglishOnly(content, ['Tomáš Tříska'], true);
    });

    it('ensures the portal replica perfectly matches the core root repository codex', () => {
        const rootCodexPath = join(process.cwd(), '../docs/LINEUM_CODEX_v1.md');
        const portalCodexPath = join(process.cwd(), 'src/lib/data/docs/LINEUM_CODEX_v1.md');

        expect(existsSync(rootCodexPath)).toBe(true);
        expect(existsSync(portalCodexPath)).toBe(true);

        const rootContent = readFileSync(rootCodexPath, 'utf-8');
        const portalContent = readFileSync(portalCodexPath, 'utf-8');

        // The text on the portal must be the exact same canonical truth
        expect(portalContent).toStrictEqual(rootContent);
    });
});
