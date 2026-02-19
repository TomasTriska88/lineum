import { describe, it, expect } from 'vitest';
import { RateLimiter } from '../lib/server/limiter';

describe('AI Agent Logic & Security', () => {
    it('should respect user rate limits (5 RPM)', () => {
        const ip = '1.2.3.4';
        const limiter = new RateLimiter();
        limiter['logs']['chat'] = []; // Reset logs

        // We need to inject a test config or mock LIMITS, but LIMITS is exported constant.
        // For now, let's just check the logic with default or mocked behavior.
        // Actually, LIMITS['test'] is not defined, so it falls back to DEFAULT_CONFIG (userLimit: 5)

        for (let i = 0; i < 5; i++) {
            expect(limiter.check('test', ip).allowed).toBe(true);
        }
        const result = limiter.check('test', ip);
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain("requests too fast");
    });

    it('should respect global rate limits (15 RPM)', () => {
        const ipPrefix = '10.0.0.';
        const limiter = new RateLimiter();
        // Global limit is 15 in DEFAULT_CONFIG

        for (let i = 0; i < 15; i++) {
            expect(limiter.check('test', `${ipPrefix}${i}`).allowed).toBe(true);
        }

        const result = limiter.check('test', '11.11.11.11');
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain("Global Rate Limit");
    });
});
