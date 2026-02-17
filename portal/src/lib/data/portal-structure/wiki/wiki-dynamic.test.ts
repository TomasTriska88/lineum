// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { load as loadSlug } from './[slug]/+page';

describe('Wiki Dynamic Loading Logic', () => {
    it('should correctly resolve lineum-core whitepaper', async () => {
        const result = await loadSlug({ params: { slug: 'lineum-core' } });
        expect(result).toBeDefined();
        expect(result.slug).toBe('lineum-core');
        expect(result.content).toContain('**Document ID:**');
        // Check if title extraction works (fixed regex)
        expect(result.title).toContain('lineum-core');
    });

    it('should be case-insensitive to slug matching', async () => {
        const result = await loadSlug({ params: { slug: 'LINEUM-CORE' } });
        expect(result.slug).toBe('LINEUM-CORE');
        expect(result.content).toBeDefined();
    });

    it('should handle extension papers', async () => {
        const result = await loadSlug({ params: { slug: 'lineum-extension-spectral-structure' } });
        expect(result.title).toBeDefined();
    });

    it('should throw 404 for non-existent paper', async () => {
        try {
            await loadSlug({ params: { slug: 'missing-paper-123' } });
            expect(false).toBe(true); // Should not reach
        } catch (e: any) {
            expect(e.status).toEqual(404);
        }
    });
});
