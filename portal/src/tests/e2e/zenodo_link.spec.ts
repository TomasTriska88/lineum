import { test, expect } from './base';
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

test.describe('Zenodo Citation Link', () => {
    test('homepage Zenodo link matches CITATION.cff', async ({ page }) => {
        // 1. Read the expected DOI from CITATION.cff
        const cffPath = path.resolve('src/lib/data/project/CITATION.cff');
        const fileContents = fs.readFileSync(cffPath, 'utf8');
        const data = yaml.load(fileContents) as any;
        const expectedDoi = data.doi;

        expect(expectedDoi).toBeTruthy();

        // 2. Go to homepage
        await page.goto('/');

        // 3. Find the Zenodo link in the Scientist section
        // We look for the link containing the DOI
        const zenodoLink = page.locator(`a[href="https://doi.org/${expectedDoi}"]`);

        // Wait for it to be visible/attached
        await expect(zenodoLink).toBeAttached();

        // 4. Verify the href matches
        const actualHref = await zenodoLink.getAttribute('href');
        expect(actualHref).toBe(`https://doi.org/${expectedDoi}`);
    });
});
