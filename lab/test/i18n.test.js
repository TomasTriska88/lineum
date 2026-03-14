import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { locale, t, resolveKey, translations } from '../src/lib/i18n';

describe('i18n Translation System (Lab Flat Dict)', () => {
    it('resolves top-level keys correctly', () => {
        const translate = get(t);
        expect(translate('simulakrum')).toBe(translations.simulakrum);
    });

    it('resolves nested namespace keys correctly', () => {
        const translate = get(t);
        expect(translate('test_ns.hello')).toBe(translations.test_ns.hello);
    });

    it('returns a placeholder with [MISSING] prefix when the key is not found', () => {
        const translate = get(t);
        expect(translate('nonexistent.key')).toBe('[MISSING: nonexistent.key]');
    });

    it('correctly resolves a key using the resolveKey helper directly', () => {
        const obj = { level1: { level2: { value: 'success' } } };
        expect(resolveKey(obj, 'level1.level2.value')).toBe('success');
        expect(resolveKey(obj, 'level1.missing')).toBe(undefined);
    });
});

import fs from 'fs';
import path from 'path';

describe('i18n Hardcoded Text Enforcement', () => {
    it('enforces no hardcoded English navigation labels in App.svelte', () => {
        const appSveltePath = path.resolve(__dirname, '../src/App.svelte');
        const code = fs.readFileSync(appSveltePath, 'utf-8');
        
        // Assert that the i18n translations are being used
        expect(code).toContain('$t("nav_simulator")');
        expect(code).toContain('$t("nav_claims")');
        expect(code).toContain('$t("nav_validation")');
        expect(code).toContain('$t("nav_lpl")');
        
        // Assert that the old hardcoded strings are removed
        expect(code).not.toContain('label: "3D Simulator"');
        expect(code).not.toContain('label: "Validation Core"');
        expect(code).not.toContain('label: "Claims"');
        expect(code).not.toContain('label: "LPL Compiler"');
    });
});

describe('i18n Key Existence Validation', () => {
    it('ensures every $t("key") referenced in Svelte components actually exists in i18n.js', () => {
        const srcDir = path.resolve(__dirname, '../src');
        const svelteFiles = [];

        function findSvelteFiles(dir) {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const fullPath = path.join(dir, file);
                if (fs.statSync(fullPath).isDirectory()) {
                    findSvelteFiles(fullPath);
                } else if (fullPath.endsWith('.svelte')) {
                    svelteFiles.push(fullPath);
                }
            }
        }
        findSvelteFiles(srcDir);

        const missingKeys = [];
        // Match $t('key') or $t("key")
        const tRegex = /\$t\(['"]([^'"]+)['"]\)/g;

        for (const file of svelteFiles) {
            const content = fs.readFileSync(file, 'utf-8');
            let match;
            while ((match = tRegex.exec(content)) !== null) {
                const key = match[1];
                const resolved = resolveKey(translations, key);
                if (resolved === undefined) {
                    missingKeys.push(`[${path.basename(file)}] Missing translation key: '${key}'`);
                }
            }
        }

        expect(missingKeys, "Found Svelte components referencing non-existent i18n keys!").toEqual([]);
    });
});
