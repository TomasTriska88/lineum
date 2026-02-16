// @vitest-environment node
import { describe, it, expect, vi } from 'vitest';
import { load } from './+page';

describe('Wiki Dynamic Loader', () => {
    it('should find lineum-core paper', async () => {
        // We mock the glob for the test or use the correct relative path
        // In Vitest, the code runs from the file location
        const result = await load({ params: { slug: 'lineum-core' } });
        expect(result).toHaveProperty('content');
        expect(result).toHaveProperty('title');
        expect(result.slug).toBe('lineum-core');
        // lineum-core should have a version extracted
        expect(result.title).toContain('lineum-core'); // Based on current Document ID
    });

    it('should throw 404 for non-existent paper', async () => {
        try {
            await load({ params: { slug: 'non-existent' } });
            // Should not reach here
            expect(true).toBe(false);
        } catch (e: any) {
            expect(e.status).toBe(404);
        }
    });

    it('should be case-insensitive to slug matching', async () => {
        const result = await load({ params: { slug: 'LINEUM-CORE' } });
        expect(result.slug).toBe('LINEUM-CORE');
        expect(result).toHaveProperty('content');
    });
});
