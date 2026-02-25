import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Performance Standard Enforcement', () => {
    it('should force any Svelte component calling requestAnimationFrame to use the intersect action', () => {
        // Enforce the rule so developers don't forget to optimize continuous rendering loops.
        const basePath = path.resolve(__dirname, '..');
        const allFiles = fs.readdirSync(basePath, { recursive: true, encoding: 'utf8' }) as string[];
        const svelteFiles = allFiles
            .filter(f => f.endsWith('.svelte'))
            .map(f => path.join(basePath, f));

        for (const file of svelteFiles) {
            const content = fs.readFileSync(file, 'utf8');

            if (content.includes('requestAnimationFrame')) {
                const hasIntersectImport = content.includes('import { intersect } from') || content.includes('import { intersect }');
                const hasIntersectAction = content.includes('use:intersect');

                expect(
                    hasIntersectImport && hasIntersectAction,
                    `Component "${path.basename(file)}" uses "requestAnimationFrame" but lacks the "use:intersect" performance optimization wrapper. Always constrain infinite render loops to the viewport!`
                ).toBe(true);
            }
        }
    });
});
