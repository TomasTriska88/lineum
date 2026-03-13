import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { describe, it } from 'vitest';
import { assertEnglishOnly } from './test_utils';
import { globSync } from 'glob';

describe('Global English-Only Enforcement', () => {

    it('ensures project trackers (e.g., todo.md) are strictly in English', () => {
        const trackers = [
            join(process.cwd(), '../todo.md'),
            join(process.cwd(), '../task.md'),
            join(process.cwd(), 'src/lib/data/project/todo.md')
        ];

        for (const tracker of trackers) {
            if (existsSync(tracker)) {
                const content = readFileSync(tracker, 'utf-8');
                // Prose documents should have English structure
                assertEnglishOnly(content, ['Tomas Triska', 'Déjà', 'déjà'], true, tracker);
            }
        }
    });

    it('ensures all Vitest test suites are written strictly in English', () => {
        // Enforce rule 10.2: ALL tests (assertions, messages) must be English 
        const testFiles = globSync('src/**/*.test.ts', { cwd: process.cwd(), absolute: true });

        for (const file of testFiles) {
            if (existsSync(file)) {
                if (file.includes('tts_utils.test.ts') || file.includes('test_utils.ts') || file.includes('chatUtils.test.ts') || file.includes('i18n.test.ts') || file.includes('language-enforcement.test.ts') || file.includes('codex.test.ts') || file.includes('license.test.ts') || file.includes('chat_flow.test.ts') || file.includes('i18n_quality.test.ts')) continue;
                const content = readFileSync(file, 'utf-8');
                // Code files don't guarantee exact prose, so structure check is false
                assertEnglishOnly(content, ['Tomas Triska', 'Tomáš', 'Tříska', 'cs-CZ', 'Czech', 'Recha'], false, file);
            }
        }
    });

    it('ensures all Playwright E2E suites are written strictly in English', () => {
        const testFiles = globSync('src/**/*.spec.ts', { cwd: process.cwd(), absolute: true });

        for (const file of testFiles) {
            if (existsSync(file)) {
                if (file.includes('navigation') || file.includes('i18n') || file.includes('language') || file.includes('brand')) continue;
                const content = readFileSync(file, 'utf-8');
                // We allow exact language name strings because language switchers often use them
                assertEnglishOnly(content, ['Czech', 'Field Science', 'Breathe', 'O Nás', 'Čeština', '日本語'], false, file);
            }
        }
    });

});
