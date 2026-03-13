// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { load as loadSlug } from './[slug]/+page';
import { readdirSync, statSync } from 'fs';
import { join } from 'path';

function getValidWhitepaperSlugs(): string[] {
    const slugs: string[] = [];
    const wpDir = join(process.cwd(), 'src', 'lib', 'data', 'whitepapers');
    
    function scan(dir: string) {
        if (!statSync(dir).isDirectory()) return;
        const items = readdirSync(dir);
        for (const item of items) {
            const fullPath = join(dir, item);
            if (statSync(fullPath).isDirectory()) {
                scan(fullPath);
            } else if (item.endsWith('.md') && !item.toLowerCase().includes('readme') && !item.toLowerCase().includes('template') && !item.startsWith('.')) {
                slugs.push(item.replace('.md', ''));
            }
        }
    }
    
    scan(wpDir);
    return slugs;
}

describe('Wiki Dynamic Loading Logic', () => {
    it('should derive expected documents from the actual current manifest/source of truth and resolve successfully', async () => {
        const slugs = getValidWhitepaperSlugs();
        expect(slugs.length, 'No valid whitepapers found in source of truth manifest.').toBeGreaterThan(0);
        
        // Dynamically grab an actual existing paper
        const testSlug = slugs[0];
        const result = await loadSlug({ params: { slug: testSlug } } as any);
        expect(result).toBeDefined();
        expect(result.slug.toLowerCase()).toBe(testSlug.toLowerCase());
        expect(result.content).toBeDefined();
    });

    it('should be case-insensitive to slug matching using dynamic source', async () => {
        const slugs = getValidWhitepaperSlugs();
        const testSlugUpper = slugs[0].toUpperCase();
        const result = await loadSlug({ params: { slug: testSlugUpper } } as any);
        expect(result.slug.toLowerCase()).toBe(testSlugUpper.toLowerCase());
        expect(result.content).toBeDefined();
    });

    it('should throw 404 for non-existent paper', async () => {
        try {
            await loadSlug({ params: { slug: 'invalid-non-existent-123' } } as any);
            expect(false).toBe(true); // Should not reach
        } catch (e: any) {
            expect(e.status).toEqual(404);
        }
    });
});
