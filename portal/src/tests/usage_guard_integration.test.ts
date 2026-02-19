// @vitest-environment node

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { usageGuard } from '../lib/server/usage_guard';
import { chat } from '../lib/server/chat';

// Mock dependencies
vi.mock('$env/dynamic/private', () => ({
    env: {
        GEMINI_API_KEY: 'test-key',
        DAILY_BUDGET_USD: '0.000001' // Ultra-low limit for testing
    }
}));

// Mock GoogleGenerativeAI to avoid real network calls
const mockSendMessage = vi.fn().mockResolvedValue({
    response: {
        text: () => "Response",
        usageMetadata: { promptTokenCount: 10, candidatesTokenCount: 10 }
    }
});
const mockStartChat = vi.fn().mockReturnValue({
    sendMessage: mockSendMessage
});
const mockGetGenerativeModel = vi.fn().mockReturnValue({
    startChat: mockStartChat
});

vi.mock('@google/generative-ai', () => ({
    GoogleGenerativeAI: class {
        getGenerativeModel = mockGetGenerativeModel;
        constructor(apiKey: string) { }
    }
}));

// Mock other dependencies to isolate chat logic
vi.mock('../lib/server/context_selector', () => ({
    contextSelector: {
        select: vi.fn().mockReturnValue("Mock Context")
    }
}));

describe('UsageGuard Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should block chat when daily limit is exceeded', async () => {
        // Arrange: Force UsageGuard to return allowed: false
        const spy = vi.spyOn(usageGuard, 'checkLimit').mockReturnValue({
            allowed: false,
            remainingBudget: 0
        });

        // Act & Assert
        await expect(chat([{ role: 'user', parts: [{ text: "Hello" }] }]))
            .rejects
            .toThrow(/safety circuits indicate I need to recharge/); // Use loose matching

        expect(spy).toHaveBeenCalled();
    });

    it('should record usage after successful chat', async () => {
        // Arrange: Allow request
        vi.spyOn(usageGuard, 'checkLimit').mockReturnValue({
            allowed: true,
            remainingBudget: 10
        });
        const recordSpy = vi.spyOn(usageGuard, 'recordUsage');

        // Mock successful API response
        mockSendMessage.mockResolvedValue({
            response: {
                text: () => "Response",
                usageMetadata: { promptTokenCount: 10, candidatesTokenCount: 10 }
            }
        });

        // Act
        await chat([{ role: 'user', parts: [{ text: "Hello" }] }]);

        // Assert
        expect(recordSpy).toHaveBeenCalledWith(10, 10);
    });
});
