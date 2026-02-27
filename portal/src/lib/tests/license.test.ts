import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import path from 'path';

// Parse the actual forbidden list from the script itself to guarantee they stay in sync
const scriptPath = path.resolve(process.cwd(), 'scripts/check-licenses.js');
const scriptContent = readFileSync(scriptPath, 'utf8');

// A quick regex to extract the array of strings from the script file
const arrayMatch = scriptContent.match(/const FORBIDDEN_LICENSES\s*=\s*\[([\s\S]*?)\];/);
// Safely evaluate the array content as a string of code to get exactly what JS gets
let parsedForbiddenList: string[] = [];
try {
    const rawContent = arrayMatch[1];
    // Split by comma, extract anything between quotes, ignore comments
    const quotesRegex = /(?:'|")([^'"]+)(?:'|")/g;
    let match;
    while ((match = quotesRegex.exec(rawContent)) !== null) {
        parsedForbiddenList.push(match[1]);
    }
} catch (e) {
    console.error("Failed to parse FORBIDDEN_LICENSES", e);
}


describe('Automated License Compliance Engine', () => {

    it('must successfully parse the forbidden licenses array from the source script', () => {
        expect(parsedForbiddenList).toBeInstanceOf(Array);
        expect(parsedForbiddenList.length).toBeGreaterThan(15);
    });

    it('must explicitly block all core GPL-family viral licenses', () => {
        const viralFamily = ['GPL', 'GPL-2.0', 'GPL-3.0', 'AGPL', 'AGPL-1.0', 'AGPL-3.0', 'LGPL', 'LGPL-3.0'];
        viralFamily.forEach(license => {
            expect(parsedForbiddenList).toContain(license);
        });
    });

    it('must explicitly block non-commercial and source-available traps', () => {
        const commercialTraps = ['SSPL-1.0', 'BSL-1.1', 'Commons-Clause'];
        commercialTraps.forEach(license => {
            expect(parsedForbiddenList).toContain(license);
        });
    });

    it('must explicitly block ambiguous, undocumented, and joke licenses that pose corporate liability', () => {
        const liabilityTraps = ['UNLICENSED', 'WTFPL', 'Public Domain', 'Beerware'];
        liabilityTraps.forEach(license => {
            expect(parsedForbiddenList).toContain(license);
        });
    });

    it('must explicitly block file-level weak copyleft licenses unacceptable for SaaS', () => {
        const fileLevelCopyleft = ['CDDL-1.1', 'EPL-2.0', 'MPL-2.0'];
        fileLevelCopyleft.forEach(license => {
            expect(parsedForbiddenList).toContain(license);
        });
    });

});
