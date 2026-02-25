// @vitest-environment node
import { describe, it, expect, vi } from 'vitest';
import { load } from './+page';

describe('Wiki Dynamic Loader', () => {
    it('should find 01-core-lineum paper', async () => {
        const result = await load({ params: { slug: '01-core-lineum' } });
        expect(result).toHaveProperty('content');
        expect(result).toHaveProperty('title');
        expect(result).toHaveProperty('status');
        expect(result.slug).toBe('01-core-lineum');
        expect(result.status).toBe('Draft');
        expect(result.title).toContain('lineum');
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
        const result = await load({ params: { slug: '01-CORE-LINEUM' } });
        expect(result.slug).toBe('01-CORE-LINEUM');
        expect(result).toHaveProperty('content');
    });
});
