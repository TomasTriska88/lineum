import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

describe('Simulacrum Link Contract', () => {
    it('Should dynamically switch Simulacrum URLs in Layout based on dev flag', () => {
        const fileContent = fs.readFileSync(path.resolve(__dirname, '../routes/+layout.svelte'), 'utf-8');

        // Ensure $app/environment dev flag is imported
        expect(fileContent).toMatch(/import\s+\{\s*dev\s*\}\s+from\s+["']\$app\/environment["']/);

        // Ensure the ternary conditional for URLs exists
        expect(fileContent).toMatch(/dev\s*\?\s*["']http:\/\/localhost:5174["']\s*:\s*["']https:\/\/simulacrum\.lineum\.io["']/);

        // Ensure 'https://simulacrum.lineum.io' is NOT hardcoded directly in the HTML anymore
        expect(fileContent).not.toMatch(/href=["']https:\/\/simulacrum\.lineum\.io["']/);
    });

    it('Should dynamically switch Simulacrum URLs in Home Page based on dev flag', () => {
        const fileContent = fs.readFileSync(path.resolve(__dirname, '../routes/+page.svelte'), 'utf-8');

        // Ensure $app/environment dev flag is imported
        expect(fileContent).toMatch(/import\s+\{\s*dev\s*\}\s+from\s+["']\$app\/environment["']/);

        // Ensure the ternary conditional for URLs exists
        expect(fileContent).toMatch(/dev\s*\?\s*["']http:\/\/localhost:5174["']\s*:\s*["']https:\/\/simulacrum\.lineum\.io["']/);

        // Ensure 'https://simulacrum.lineum.io' is NOT hardcoded directly in the HTML anymore
        expect(fileContent).not.toMatch(/href=["']https:\/\/simulacrum\.lineum\.io["']/);
    });
});
