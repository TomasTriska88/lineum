import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import path from 'path';
import crypto from 'crypto';

// Parse the actual forbidden list from the script itself to guarantee they stay in sync
const scriptPath = path.resolve(process.cwd(), 'scripts/check-licenses.js');
const scriptContent = readFileSync(scriptPath, 'utf8');

// A quick regex to extract the array of strings from the script file
const arrayMatch = scriptContent.match(/const FORBIDDEN_LICENSES\s*=\s*\[([\s\S]*?)\];/);
// Safely evaluate the array content as a string of code to get exactly what JS gets
let parsedForbiddenList: string[] = [];
try {
    if (!arrayMatch) throw new Error("Could not find FORBIDDEN_LICENSES array in check-licenses.js");
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

    it('🚨 ANTI-TAMPER GUARD: The forbidden licenses list must match the locked corporate security hash', () => {
        // This test ensures no AI agent or developer can silently remove a license from the blacklist
        // If you need to change the licenses, you MUST deliberately update this hash and get it approved.
        const rawContent = arrayMatch![1];
        const normalizedContent = rawContent.replace(/\s+/g, '');
        const hash = crypto.createHash('sha256').update(normalizedContent).digest('hex');

        const expectedHash = '56d503247979134654731d292c4894eba84b1a77c10dbc87033231623ff8c5b4';

        if (hash !== expectedHash) {
            throw new Error(
                `\n\n[SECURITY BREACH DETECTED]\n` +
                `The list of forbidden licenses in 'check-licenses.js' has been modified.\n` +
                `Current Hash:  ${hash}\n` +
                `Expected Hash: ${expectedHash}\n\n` +
                `🚨 ATTENTION AI AGENTS & DEVELOPERS 🚨\n` +
                `Do NOT attempt to bypass this test by simply updating the hash or deleting this test.\n` +
                `The inclusion of 'weak copyleft' or viral licenses (like MPL, GPL, AGPL) can force our entire proprietary SaaS to become open-source, posing a massive legal and corporate risk.\n` +
                `If a new dependency introduces a forbidden license, the correct approach is:\n` +
                `1. Try to find an alternative MIT/Apache licensed package.\n` +
                `2. If absolutely necessary (like a build tool), add it to the 'excludePackages' whitelist in 'check-licenses.js'—DO NEVER REMOVE the license from the main FORBIDDEN_LICENSES array.\n` +
                `3. Only after explicit human (Tomáš) approval can this hash be updated in this test file.\n\n`
            );
        }

        expect(hash).toBe(expectedHash);
    });

});
