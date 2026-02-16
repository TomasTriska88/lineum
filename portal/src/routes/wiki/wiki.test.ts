import { describe, it, expect } from 'vitest';
import { load } from './+page';

describe('Wiki Loader: Advanced Features', () => {
    it('should extract metadata and assign correct categories', async () => {
        const result = await load();
        expect(result).toHaveProperty('papers');
        const papers = result.papers;

        // Check for Core categorization
        const corePaper = papers.find((p: any) => p.slug === 'lineum-core');
        expect(corePaper).toBeDefined();
        if (corePaper) {
            expect(corePaper.category).toBe('Core');
        }

        // Check for Extensions
        const extension = papers.find((p: any) => p.slug.startsWith('lineum-extension-'));
        if (extension) expect(extension.category).toBe('Extension');

        // Check for Experiments
        const experiment = papers.find((p: any) => p.slug.startsWith('lineum-exp'));
        if (experiment) expect(experiment.category).toBe('Experiment');
    });

    it('should sort Lineum Core as the first item', async () => {
        const result = await load();
        const papers = result.papers;
        if (papers.length > 0) {
            expect(papers[0].slug).toBe('lineum-core');
        }
    });

    it('should avoid "Unknown" for metadata if possible', async () => {
        const result = await load();
        const core = result.papers.find((p: any) => p.slug === 'lineum-core');
        expect(core).toBeDefined();
        if (core) {
            expect(core.version).not.toBe('Unknown');
            expect(core.date).not.toBe('Unknown');
        }
    });
});
