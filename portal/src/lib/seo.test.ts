import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('SEO & Virality Guards', () => {
    it('should have a sitemap.xml endpoint generation file', () => {
        const sitemapPath = path.resolve(__dirname, '../routes/sitemap.xml/+server.ts');
        expect(fs.existsSync(sitemapPath)).toBe(true);
    });

    it('should have OpenGraph logic injected into the layout head', () => {
        const layoutPath = path.resolve(__dirname, '../routes/+layout.svelte');
        const content = fs.readFileSync(layoutPath, 'utf8');
        expect(content).toContain('og:title');
        expect(content).toContain('og:description');
        expect(content).toContain('twitter:card');
    });

    it('should inject structured JSON-LD data for crawler indexing', () => {
        const layoutPath = path.resolve(__dirname, '../routes/+layout.svelte');
        const content = fs.readFileSync(layoutPath, 'utf8');
        expect(content).toContain('application/ld+json');
        expect(content).toContain('SoftwareApplication');
    });
});
