// @vitest-environment node

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { usageGuard } from '../lib/server/usage_guard';
import { POST as chatPOST } from '../routes/api/chat/+server';
import { POST as ttsPOST } from '../routes/api/tts/+server';
import { rateLimiter } from '../lib/server/limiter';

// Mock dependencies
vi.mock('../lib/data/ai_index.json', () => ({ default: [] }));
vi.mock('$env/dynamic/private', () => ({ env: { GEMINI_API_KEY: 'mock-key' } }));
vi.mock('$env/static/private', () => ({ GEMINI_API_KEY: 'mock-key' }));

// Mock GoogleGenerativeAI
const mockChatSession = {
    sendMessage: vi.fn().mockResolvedValue({
        response: {
            text: () => "Mock response",
            usageMetadata: { promptTokenCount: 10, candidatesTokenCount: 10 }
        }
    })
};

const mockGenAI = {
    getGenerativeModel: vi.fn().mockReturnValue({
        startChat: vi.fn().mockReturnValue(mockChatSession)
    })
};

vi.mock('@google/generative-ai', () => ({
    GoogleGenerativeAI: vi.fn(() => mockGenAI)
}));


describe('Global Token Limit Guard Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Reset usage guard state
        // usageGuard is a singleton, so we need to mock its checkLimit method or internals
        // But since we want to test IT, let's spy on it.
        // Actually, better to reset its internal state if possible, but it loads from file.
        // We will mock `fs` or just spy on `checkLimit` to simulate "Limit Reached".
    });

    it('should block CHAT requests when limit is reached', async () => {
        // Force limit reached
        vi.spyOn(usageGuard, 'checkLimit').mockReturnValue({ allowed: false, remainingBudget: 0 });

        const request = new Request('http://localhost/api/chat', {
            method: 'POST',
            body: JSON.stringify({ messages: [{ role: 'user', parts: [{ text: 'Hello' }] }] })
        });

        const locals = { sessionId: 'test-user' };
        const getClientAddress = () => '127.0.0.1';

        // Bypass Rate Limiter
        vi.spyOn(rateLimiter, 'check').mockReturnValue({ allowed: true });

        const response = await chatPOST({ request, locals, getClientAddress } as any);

        expect(response.status).toBe(429); // Too Many Requests (Limit Reached) (Wait, chat.ts throws Error which +server.ts catches? No, check +server.ts)
        // Wait, +server.ts calls chat(). chat() throws Error. +server.ts catches and returns 500?
        // Let's check chat/+server.ts: 
        // 53: } catch (err: any) { ... return json({ error: ... }, { status: 500 }); }
        // BUT checkLimit throws Error with specific message.
        // If chat() throws "Daily safety limit reached", +server.ts catches it and returns 500.
        // This might be a DESIGN FLAW or intended. The user wants to ensure it is guarded.
        // If it throws, it IS guarded (no API call made). 
        // Ideally it should be 429.

        const data = await response.json();
        // Expect error message about safety limit
        expect(data.error).toMatch(/Daily safety limit reached|recharge/i);
    });

    it('should block TTS requests when limit is reached', async () => {
        // Force limit reached
        vi.spyOn(usageGuard, 'checkLimit').mockReturnValue({ allowed: false, remainingBudget: 0 });

        const request = new Request('http://localhost/api/tts', {
            method: 'POST',
            body: JSON.stringify({ text: 'Hello' })
        });

        const locals = { sessionId: 'test-user' };
        const getClientAddress = () => '127.0.0.1';

        // Bypass Rate Limiter
        vi.spyOn(rateLimiter, 'check').mockReturnValue({ allowed: true });

        const response = await ttsPOST({ request, locals, getClientAddress } as any);

        expect(response.status).toBe(429); // TTS explicitly returns 429
        const data = await response.json();
        expect(data.error).toMatch(/Daily safety limit reached|rest my voice/i);
    });
});
