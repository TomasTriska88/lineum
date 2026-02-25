import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync, statSync, existsSync } from 'fs';
import { join } from 'path';

function getReadmeFiles(dir: string, fileList: string[] = []) {
    if (!existsSync(dir)) return fileList;

    const files = readdirSync(dir);
    for (const file of files) {
        const filePath = join(dir, file);
        if (statSync(filePath).isDirectory()) {
            getReadmeFiles(filePath, fileList);
        } else if (file === 'README.md') {
            fileList.push(filePath);
        }
    }
    return fileList;
}

describe('Markdown Syntax Integrity for SvelteKit', () => {
    it('All README.md files must have properly closed HTML comments', () => {
        // Collect readmes from the Portal data directory and the original Source Root
        const portalReadmes = getReadmeFiles('src/lib/data/whitepapers');
        const sourceReadmes = getReadmeFiles('../../whitepapers');

        // Deduplicate in case paths overlap
        const allReadmes = Array.from(new Set([...portalReadmes, ...sourceReadmes]));

        let malformedComments: string[] = [];

        for (const file of allReadmes) {
            const content = readFileSync(file, 'utf-8');
            const lines = content.split('\n');

            lines.forEach((line, index) => {
                // If a line opens an HTML comment '<!--' but does not close it '-->'
                // This will crash mdsvex/Svelte compiler exactly as shown in the screenshot.
                if (line.includes('<!--') && !line.includes('-->')) {
                    malformedComments.push(`${file}:${index + 1} -> ${line.trim()}`);
                }
            });
        }

        expect(malformedComments, `Found malformed HTML comments that will break Vite/Svelte compilation:\n${malformedComments.join('\n')}`).toEqual([]);
    });
});
