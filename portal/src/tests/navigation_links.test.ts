import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Navigation Link Integrity', () => {
    it('should strictly prohibit dead links (href="#" or empty) across all Svelte routes', () => {
        const routesPath = path.resolve(__dirname, '../routes');
        const recurse = (dir: string) => {
            const files = fs.readdirSync(dir, { withFileTypes: true });
            for (const file of files) {
                const fullPath = path.join(dir, file.name);
                if (file.isDirectory()) {
                    recurse(fullPath);
                } else if (file.name.endsWith('.svelte')) {
                    const content = fs.readFileSync(fullPath, 'utf8');

                    const hasEmptyHref = /href=""/.test(content);
                    const hasHashHref = /href="#"/.test(content);

                    expect(
                        hasEmptyHref,
                        `Navigation Violation: ${file.name} contains an empty href="" link.`
                    ).toBe(false);

                    expect(
                        hasHashHref,
                        `Navigation Violation: ${file.name} contains a dead href="#" anchor.`
                    ).toBe(false);
                }
            }
        };
        recurse(routesPath);
    });
});
