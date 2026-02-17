import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { POST } from './+server';

// Mock env
vi.mock('$env/static/private', () => ({
    GEMINI_API_KEY: 'mock-key'
}));

// Mock limiter - we need to spy on it or mock it
// Since rateLimiter is a singleton exported from a module, we can spy on its method if we import it.
import { rateLimiter } from '$lib/server/limiter';

describe('TTS Endpoint', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
        // Reset limiter logs if possible or mock the check method
        vi.spyOn(rateLimiter, 'check').mockReturnValue({ allowed: true });

        // Mock global fetch
        global.fetch = vi.fn();
    });

    it('should return 400 if text is missing', async () => {
        const request = {
            json: async () => ({})
        } as Request;

        const response = await POST({ request, getClientAddress: () => '127.0.0.1' } as any);
        expect(response.status).toBe(400);
    });

    it('should return audio buffer on success', async () => {
        const mockAudioData = Buffer.from('mock-audio').toString('base64');
        const mockApiResponse = {
            candidates: [{
                content: {
                    parts: [{
                        inlineData: {
                            mimeType: 'audio/wav',
                            data: mockAudioData
                        }
                    }]
                }
            }]
        };

        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => mockApiResponse
        });

        const request = {
            json: async () => ({ text: 'Hello' })
        } as Request;

        const response = await POST({ request, getClientAddress: () => '127.0.0.1' } as any);

        expect(response.status).toBe(200);
        expect(response.headers.get('Content-Type')).toBe('audio/wav');

        const buffer = await response.arrayBuffer();
        expect(Buffer.from(buffer).toString()).toBe('mock-audio');
    });

    it('should return 429 if rate limited by internal limiter', async () => {
        vi.spyOn(rateLimiter, 'check').mockReturnValue({ allowed: false, reason: 'Test Limit' });

        const request = {
            json: async () => ({ text: 'Hello' })
        } as Request;

        const response = await POST({ request, getClientAddress: () => '127.0.0.1' } as any);
        expect(response.status).toBe(429);
        const body = await response.json();
        expect(body.error).toBe('Test Limit');
    });

    it('should handle API errors gracefully', async () => {
        (global.fetch as any).mockResolvedValue({
            ok: false,
            status: 500,
            text: async () => 'Google Error'
        });

        const request = {
            json: async () => ({ text: 'Hello' })
        } as Request;

        const response = await POST({ request, getClientAddress: () => '127.0.0.1' } as any);
        expect(response.status).toBe(500);
    });
});
