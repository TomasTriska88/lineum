// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { load as loadSlug } from './[slug]/+page';

describe('Wiki Dynamic Loading Logic', () => {
    it('should correctly resolve 01-core-lineum whitepaper', async () => {
        const result = await loadSlug({ params: { slug: '01-core-lineum' } });
        expect(result).toBeDefined();
        expect(result.slug).toBe('01-core-lineum');
        expect(result.content).toContain('**Document ID:**');
        // Check if title extraction works (fixed regex)
        expect(result.title).toContain('lineum');
    });

    it('should be case-insensitive to slug matching', async () => {
        const result = await loadSlug({ params: { slug: '01-CORE-LINEUM' } });
        expect(result.slug).toBe('01-CORE-LINEUM');
        expect(result.content).toBeDefined();
    });

    it('should handle extension papers', async () => {
        const result = await loadSlug({ params: { slug: '06-core-ext-silentgravity' } });
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
