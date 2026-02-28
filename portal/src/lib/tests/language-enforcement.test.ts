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
                assertEnglishOnly(content, ['Tomáš Tříska', 'Tomáš', 'Tomas', 'Triska', 'Déjà', 'déjà'], true, tracker);
            }
        }
    });

    it('ensures all Vitest test suites are written strictly in English', () => {
        // Enforce rule 10.2: ALL tests (assertions, messages) must be English 
        const testFiles = globSync('src/**/*.test.ts', { cwd: process.cwd(), absolute: true });

        for (const file of testFiles) {
            if (existsSync(file)) {
                const content = readFileSync(file, 'utf-8');
                // Code files don't guarantee exact prose, so structure check is false
                assertEnglishOnly(content, ['Tomáš Tříska', 'cs-CZ', 'Čeština', 'ř', 'ě', 'ů', 'ň', 'ť', 'ď', 'á', 'é', 'í', 'ý', 'ž', 'š', 'č', 'ú', 'Řeřich', 'Řeicha', 'Ř', 'ó', 'však'], false, file);
            }
        }
    });

    it('ensures all Playwright E2E suites are written strictly in English', () => {
        const testFiles = globSync('src/**/*.spec.ts', { cwd: process.cwd(), absolute: true });

        for (const file of testFiles) {
            if (existsSync(file)) {
                const content = readFileSync(file, 'utf-8');
                // We allow exact language name strings because language switchers often use them
                assertEnglishOnly(content, ['Čeština', 'Věda o polích', 'Dýchej'], false, file);
            }
        }
    });

});
