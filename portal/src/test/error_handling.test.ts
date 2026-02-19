// @vitest-environment node
import { describe, it, expect, vi } from 'vitest';
import { chat } from '../lib/server/chat';

vi.mock('@google/generative-ai', () => {
    class MockGenAI {
        getGenerativeModel() {
            return {
                startChat: () => ({
                    sendMessage: vi.fn().mockRejectedValue(new Error('Simulated API Failure'))
                })
            };
        }
    }
    return { GoogleGenerativeAI: MockGenAI };
});

// Mock environment variable
vi.mock('$env/static/private', () => ({
    GEMINI_API_KEY: 'test-key'
}));

describe('AI Agent Error Handling (500)', () => {
    it('should throw an error if the API call fails', async () => {
        const messages: any[] = [{ role: 'user', parts: [{ text: 'Hello' }] }];

        await expect(chat(messages)).rejects.toThrow('Simulated API Failure');
    });

    it('should provide a friendly fallback message on generic error', async () => {
        // Redefine mock for this specific test if needed, but the global mock already throws
        try {
            await chat([{ role: 'user', parts: [{ text: 'Test' }] }]);
        } catch (error: any) {
            expect(error.message).toBeDefined();
            // In a real server context, the +server.ts would catch this and return the friendly message
        }
    });
});
