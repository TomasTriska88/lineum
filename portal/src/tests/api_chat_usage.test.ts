
// @vitest-environment node
import { describe, it, expect, vi } from 'vitest';
import { GET } from '../routes/api/chat/+server';
import { usageGuard } from '../lib/server/usage_guard';
import { json } from '@sveltejs/kit';

// Mock UsageGuard
vi.mock('../lib/server/usage_guard', () => ({
    usageGuard: {
        getStats: vi.fn().mockReturnValue({
            date: '2026-02-19',
            tokensInput: 100,
            tokensOutput: 50,
            estimatedCost: 0.05,
            percentage: 10.0
        })
    }
}));

describe('Chat API - GET Endpoint', () => {
    it('should return current usage stats', async () => {
        // Act
        const response = await GET({} as any);
        const data = await response.json();

        // Assert
        expect(response.status).toBe(200); // Defaults to 200 for json() check implicitly
        expect(usageGuard.getStats).toHaveBeenCalled();
        expect(data).toHaveProperty('estimatedCost', 0.05);
        expect(data).toHaveProperty('percentage', 10.0);
    });
});
