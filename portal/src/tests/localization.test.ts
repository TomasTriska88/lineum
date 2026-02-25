import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Localization Completeness', () => {
    it('should never contain hardcoded string literals for <title> attributes across pages', () => {
        const routesPath = path.resolve(__dirname, '../routes');
        const recurse = (dir: string) => {
            const files = fs.readdirSync(dir, { withFileTypes: true });
            for (const file of files) {
                const fullPath = path.join(dir, file.name);
                if (file.isDirectory()) {
                    recurse(fullPath);
                } else if (file.name === '+page.svelte' || file.name === '+layout.svelte') {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    // Find all <title> tags.
                    const titleMatches = content.match(/<title>(.*?)<\/title>/g);
                    if (titleMatches) {
                        for (const title of titleMatches) {
                            // Enforce that $t is present. No hardcoded global static titles.
                            expect(title.includes('$t')).toBeTruthy({
                                message: `Translation Violation: ${file.name} contains a hardcoded <title> block instead of using Svelte $t(...) i18n variables.`
                            });
                        }
                    }
                }
            }
        };
        recurse(routesPath);
    });

    it('should ensure all MarginShard tooltips are dynamically translated using $t variables', () => {
        const shardsPath = path.resolve(__dirname, '../lib/components/MarginShards.svelte');
        if (fs.existsSync(shardsPath)) {
            const content = fs.readFileSync(shardsPath, 'utf8');
            expect(content).toContain('{$t(');
            expect(content).not.toContain('EXPLORER INSIGHT'); // Ensuring the hardcode is removed.
        }
    });
});
