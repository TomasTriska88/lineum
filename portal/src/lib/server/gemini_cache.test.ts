
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getOrUpdateCache } from './gemini_cache';

// Mock the Google AI server SDK
const mockList = vi.fn();
const mockCreate = vi.fn();
const mockDelete = vi.fn();

vi.mock('@google/generative-ai/server', () => {
    return {
        GoogleAICacheManager: vi.fn(function () {
            return {
                list: mockList,
                create: mockCreate,
                delete: mockDelete
            };
        }),
        GoogleAIFileManager: vi.fn()
    };
});

// Mock environment variable
vi.mock('$env/static/private', () => ({
    GEMINI_API_KEY: 'mock-api-key'
}));

describe('gemini_cache', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Clear module-level cache if possible, or we might need to expose a reset function
        // For simplicity in this test pass, we assume isolation or just test the logic flow
    });

    it('should create a new cache if none exists', async () => {
        mockList.mockResolvedValue({}); // No existing caches
        mockCreate.mockResolvedValue({
            name: 'caches/new-cache-123',
            expireTime: new Date(Date.now() + 3600000).toISOString()
        });

        const cacheName = await getOrUpdateCache('Test Content');

        expect(mockList).toHaveBeenCalled();
        expect(mockCreate).toHaveBeenCalledWith(expect.objectContaining({
            displayName: 'lineum-core-whitepapers-v1',
            ttlSeconds: 3600,
            contents: expect.arrayContaining([
                expect.objectContaining({
                    parts: expect.arrayContaining([
                        expect.objectContaining({ text: 'Test Content' })
                    ])
                })
            ])
        }));
        expect(cacheName).toBe('caches/new-cache-123');
    });

    it('should return existing active cache if found', async () => {
        const futureDate = new Date(Date.now() + 3600000).toISOString();
        mockList.mockResolvedValue({
            cachedContents: [
                {
                    name: 'caches/existing-123',
                    displayName: 'lineum-core-whitepapers-v1',
                    expireTime: futureDate
                }
            ]
        });

        const cacheName = await getOrUpdateCache('Test Content');

        expect(mockList).toHaveBeenCalled();
        expect(mockCreate).not.toHaveBeenCalled(); // Should NOT create new
        expect(cacheName).toBe('caches/existing-123');
    });

    it('should delete expired cache and create new one', async () => {
        const pastDate = new Date(Date.now() - 1000).toISOString();
        mockList.mockResolvedValue({
            cachedContents: [
                {
                    name: 'caches/expired-123',
                    displayName: 'lineum-core-whitepapers-v1',
                    expireTime: pastDate
                }
            ]
        });

        mockCreate.mockResolvedValue({
            name: 'caches/new-cache-456',
            expireTime: new Date(Date.now() + 3600000).toISOString()
        });

        const cacheName = await getOrUpdateCache('Test Content');

        expect(mockDelete).toHaveBeenCalledWith('caches/expired-123');
        expect(mockCreate).toHaveBeenCalled();
        expect(cacheName).toBe('caches/new-cache-456');
    });
});
