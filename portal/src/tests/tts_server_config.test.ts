
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { POST } from '../routes/api/tts/+server';
import { json } from '@sveltejs/kit';

// Mock dependencies
vi.mock('$env/static/private', () => ({
    GEMINI_API_KEY: 'mock-key'
}));

vi.mock('../lib/server/limiter', () => ({
    rateLimiter: { check: () => ({ allowed: true }) }
}));

vi.mock('../lib/server/usage_guard', () => ({
    usageGuard: {
        checkLimit: () => ({ allowed: true, remainingBudget: 10 }),
        recordUsage: vi.fn()
    }
}));

// Mock global fetch
const fetchMock = vi.fn();
global.fetch = fetchMock;

describe('TTS Server Configuration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        fetchMock.mockResolvedValue({
            ok: true,
            json: async () => ({ candidates: [] }) // Dummy response
        });
    });

    it('should request explicit audio configuration (LINEAR16, 24kHz)', async () => {
        const locals = { sessionId: 'test-session' };
        const request = {
            json: async () => ({ text: "Hello" })
        };

        await POST({ request, getClientAddress: () => '127.0.0.1', locals } as any);

        // Verify fetch was called
        expect(fetchMock).toHaveBeenCalledTimes(1);

        // Inspect payload
        const callArgs = fetchMock.mock.calls[0];
        const payload = JSON.parse(callArgs[1].body);

        // Assertions for critical config
        expect(payload.generationConfig).toBeDefined();

        // This is what we EXPECT to see once fixed:
        // generationConfig: {
        //     speechConfig: {
        //         voiceConfig: { ... },
        //         audioConfig: { audioEncoding: "LINEAR16", sampleRateHertz: 24000 }
        //     }
        // }
        // However, the current code structure handles config differently.
        // Wait, Gemini API usually puts audioConfig INSIDE speechConfig? Or separate?
        // Docs say: generationConfig.speechConfig.voiceConfig
        // BUT audioConfig is often top-level or sibling?
        // Actually, for `generateContent` with `responseModalities: ["AUDIO"]`, the parameters are passed in `generationConfig`.
        // Let's assume standard `speechConfig` structure:
        // speechConfig: { voiceConfig: {...} } 
        // AND usually `audioEncoding` is not part of `speechConfig` in `generateContent`, it might be.
        // BUT `google-cloud/text-to-speech` uses `audioConfig`.
        // Gemini `generateContent` API for audio uses `responseMimeType` or similar?
        // Actually, let's stick to what we WANT to implement: `speechConfig.audioConfig`.
        // If the API rejects it, we'll know. But for now, we test that we SENT it.

        // Expectation:
        const speechConfig = payload.generationConfig.speechConfig;

        // We expect audioConfig to be present
        // (Note: This assertion will FAIL until we implement the fix)
        expect(speechConfig).toHaveProperty('audioConfig');
        expect(speechConfig.audioConfig).toEqual({
            audioEncoding: "LINEAR16",
            sampleRateHertz: 24000
        });
    });
});
