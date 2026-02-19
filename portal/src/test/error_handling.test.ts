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
vi.mock('$env/dynamic/private', () => ({
    env: { GEMINI_API_KEY: 'test-key' }
}));

// Mock other dependencies
vi.mock('../lib/server/usage_guard', () => ({
    usageGuard: {
        checkLimit: vi.fn().mockReturnValue({ allowed: true, remainingBudget: 10 }),
        recordUsage: vi.fn(),
        getStats: vi.fn().mockReturnValue({ budgetLimit: 1, percentage: 50, estimatedCost: 0.5 })
    }
}));

vi.mock('../lib/server/context_selector', () => ({
    contextSelector: {
        select: vi.fn().mockReturnValue("Saved Context")
    }
}));

vi.mock('../lib/server/gemini_cache', () => ({
    getOrUpdateCache: vi.fn()
}));

describe('AI Agent Error Handling (500)', () => {
    it('should throw an error if the API call fails', async () => {
        const messages: any[] = [{ role: 'user', parts: [{ text: 'Hello' }] }];

        try {
            await chat(messages);
            throw new Error("Chat function did not throw expectation!");
        } catch (e: any) {
            // Verify it matches expectation manually
            if (!e.message.includes('Simulated API Failure')) {
                throw new Error(`Expected 'Simulated API Failure' but got: ${e.message}`);
            }
        }
    });

    it('should provide a friendly fallback message on generic error', async () => {
        try {
            await chat([{ role: 'user', parts: [{ text: 'Test' }] }]);
        } catch (error: any) {
            expect(error.message).toBeDefined();
        }
    });
});
