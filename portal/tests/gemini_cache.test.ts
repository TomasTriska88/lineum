// @ts-nocheck

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getOrUpdateCache, resetLocalRefCache } from '../scripts/gemini_cache.js';

// Mock the Google AI server SDK
const mocks = vi.hoisted(() => ({
    mockList: vi.fn(),
    mockCreate: vi.fn(),
    mockDelete: vi.fn()
}));

vi.mock('@google/generative-ai/server', () => {
    return {
        GoogleAICacheManager: vi.fn(function () {
            return {
                list: mocks.mockList,
                create: mocks.mockCreate,
                delete: mocks.mockDelete
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
        resetLocalRefCache();
    });

    it('should create a new cache if none exists', async () => {
        mocks.mockList.mockResolvedValue({}); // No existing caches
        mocks.mockCreate.mockResolvedValue({
            name: 'caches/new-cache-123',
            expireTime: new Date(Date.now() + 3600000).toISOString()
        });

        const cacheName = await getOrUpdateCache('Test Content');

        expect(mocks.mockList).toHaveBeenCalled();
        expect(mocks.mockCreate).toHaveBeenCalledWith(expect.objectContaining({
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
        mocks.mockList.mockResolvedValue({
            cachedContents: [
                {
                    name: 'caches/existing-123',
                    displayName: 'lineum-core-whitepapers-v1',
                    expireTime: futureDate
                }
            ]
        });

        const cacheName = await getOrUpdateCache('Test Content');

        expect(mocks.mockList).toHaveBeenCalled();
        expect(mocks.mockCreate).not.toHaveBeenCalled(); // Should NOT create new
        expect(cacheName).toBe('caches/existing-123');
    });

    it('should delete expired cache and create new one', async () => {
        const pastDate = new Date(Date.now() - 1000).toISOString();
        mocks.mockList.mockResolvedValue({
            cachedContents: [
                {
                    name: 'caches/expired-123',
                    displayName: 'lineum-core-whitepapers-v1',
                    expireTime: pastDate
                }
            ]
        });

        mocks.mockCreate.mockResolvedValue({
            name: 'caches/new-cache-456',
            expireTime: new Date(Date.now() + 3600000).toISOString()
        });

        const cacheName = await getOrUpdateCache('Test Content');

        expect(mocks.mockDelete).toHaveBeenCalledWith('caches/expired-123');
        expect(mocks.mockCreate).toHaveBeenCalled();
        expect(cacheName).toBe('caches/new-cache-456');
    });
});
