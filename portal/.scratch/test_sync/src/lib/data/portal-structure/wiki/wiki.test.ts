// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { load } from './+page';

describe('Wiki Loader: Advanced Features', () => {
    it('should extract metadata and assign correct categories', async () => {
        const result = await load();
        expect(result).toHaveProperty('papers');
        const papers = result.papers;

        // Check for Core categorization (now uses numerical prefixes)
        const corePaper = papers.find((p: any) => p.slug === '01-core-lineum');
        expect(corePaper).toBeDefined();
        if (corePaper) {
            expect(corePaper.track).toBe('Core');
            expect(corePaper.status).toBe('Draft');
        }

        // Check for Cosmology
        const cosmologyPaper = papers.find((p: any) => p.slug === '01-cosmo-base');
        if (cosmologyPaper) {
            expect(cosmologyPaper.track).toBe('Cosmology');
            expect(cosmologyPaper.status).toBe('Draft');
        }

        // Check for Extensions (if any remain in mock data)
        const extension = papers.find((p: any) => p.slug.includes('-ext-'));
        if (extension) expect(extension.track).toBe('Core');
    });

    it('should sort Lineum Core as the first item via category order and numerical prefix', async () => {
        const result = await load();
        const papers = result.papers;
        if (papers.length > 0) {
            expect(papers[0].slug).toBe('01-core-lineum');
        }
    });

    it('should extract correct metadata and avoid Unknowns', async () => {
        const result = await load();
        const core = result.papers.find((p: any) => p.slug === '01-core-lineum');
        expect(core).toBeDefined();
        if (core) {
            expect(core.version).not.toBe('Unknown');
            expect(core.date).not.toBe('Unknown Date');
            expect(core.status).toBe('Draft');
        }
    });
});
