import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

describe('Simulacrum Link Contract', () => {
    it('Should use PUBLIC_SIMULACRUM_URL in Home Page instead of hardcoding', () => {
        const fileContent = fs.readFileSync(path.resolve(__dirname, '../routes/+page.svelte'), 'utf-8');

        // Ensure PUBLIC_SIMULACRUM_URL is imported from environment
        expect(fileContent).toMatch(/import\s+\{\s*PUBLIC_SIMULACRUM_URL\s*\}\s+from\s+["']\$env\/static\/public["']/);

        // Ensure the variable is used for the href
        expect(fileContent).toMatch(/href=\{PUBLIC_SIMULACRUM_URL\}/);

        // Ensure 'https://simulacrum.lineum.io' is NOT hardcoded directly in the HTML anymore
        expect(fileContent).not.toMatch(/href=["']https:\/\/simulacrum\.lineum\.io["']/);
    });
});
