import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Whitepaper Formatting Standard Enforcement', () => {
    it('should strictly prohibit consecutive blank lines (3+) in all Markdown readmes', () => {
        const basePath = path.resolve(__dirname, '../../../whitepapers');
        const allDirs = fs.readdirSync(basePath, { recursive: true, withFileTypes: true });

        const readmes = allDirs
            .filter(dirent => dirent.isFile() && dirent.name === 'README.md')
            .map(dirent => path.join(dirent.parentPath, dirent.name));

        for (const file of readmes) {
            const content = fs.readFileSync(file, 'utf8');
            const hasRunawayWhitespace = /\n{3,}/.test(content);

            expect(hasRunawayWhitespace).toBeFalsy({
                message: `Formatting Violation: ${path.basename(path.dirname(file))}/README.md contains 3 or more consecutive blank lines. This breaks canonical script parsers.`
            });
        }
    });
});
