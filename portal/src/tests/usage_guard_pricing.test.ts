
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock Modules BEFORE Import
vi.mock('fs', () => ({
    default: {
        existsSync: vi.fn(),
        readFileSync: vi.fn(),
        writeFileSync: vi.fn(),
    }
}));

vi.mock('$env/dynamic/private', () => ({
    env: { DAILY_BUDGET_USD: '1.0' }
}));

// Import AFTER mocking
import { UsageGuard } from '../lib/server/usage_guard';
import fs from 'fs';

describe('UsageGuard Multi-Model Pricing', () => {
    let guard: UsageGuard;

    beforeEach(() => {
        vi.resetAllMocks();
        // Mock fs to simulate no existing DB
        vi.mocked(fs.existsSync).mockReturnValue(false);
        guard = new UsageGuard();
    });

    it('should calculate cost correctly for Flash (default)', () => {
        // Flash: Input $0.10/1M, Output $0.40/1M
        // 1M input -> $0.10
        guard.recordUsage(1_000_000, 0, 'flash');
        expect(guard.getStats().estimatedCost).toBeCloseTo(0.10, 4);

        // 1M output -> $0.40 (Total $0.50)
        guard.recordUsage(0, 1_000_000, 'flash');
        expect(guard.getStats().estimatedCost).toBeCloseTo(0.50, 4);
    });

    it('should calculate cost correctly for Pro', () => {
        // Pro: Input $3.50/1M, Output $10.50/1M
        // 1M input -> $3.50
        guard.recordUsage(1_000_000, 0, 'pro');
        expect(guard.getStats().estimatedCost).toBeCloseTo(3.50, 4);
    });

    it('should default to Flash if no model specified', () => {
        // Create new instance to ensure clean state
        guard.recordUsage(1_000_000, 0); // Should use Flash input rate ($0.10)
        expect(guard.getStats().estimatedCost).toBeCloseTo(0.10, 4);
    });
});
