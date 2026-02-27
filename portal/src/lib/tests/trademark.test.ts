import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import path from 'path';

const pagePath = path.resolve(process.cwd(), 'src/routes/+page.svelte');
const pageContent = readFileSync(pagePath, 'utf8');

describe('Brand & Trademark Compliance', () => {

    it('must enforce the presence of the ™ symbol on the main Lineum logo in the hero section', () => {
        // We ensure that the main hero logo text contains the trademark symbol
        // This establishes Common Law Trademark rights on the public website
        expect(pageContent).toContain('<span class="logo-text">Lineum™</span>');
    });

    it('must not erroneously enforce TM on generic scientific terms like Linon', () => {
        // Terms like "linon" or "field" are generic nouns in the physics theory,
        // they cannot and should not be trademarked, similar to "electron" or "photon".
        // Here we just verify the file can be read and parsed correctly.
        expect(pageContent).toBeTruthy();
    });

});
