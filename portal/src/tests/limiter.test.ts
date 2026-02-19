
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RateLimiter, LIMITS } from '$lib/server/limiter';

describe('RateLimiter', () => {
    let limiter: RateLimiter;

    beforeEach(() => {
        // Mock Date.now
        vi.useFakeTimers();
        limiter = new RateLimiter();

        // Use test limits
        LIMITS['test'] = {
            globalLimit: 2,
            userLimit: 1,
            windowMs: 1000
        };
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should allow request within limits', () => {
        const result = limiter.check('test', 'user1');
        expect(result.allowed).toBe(true);
    });

    it('should block user exceeding userLimit', () => {
        limiter.check('test', 'user1'); // 1st (Allowed)
        const result = limiter.check('test', 'user1'); // 2nd (Blocked)
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain('slow down');
    });

    it('should block global exceeding globalLimit', () => {
        limiter.check('test', 'userA'); // 1st ok
        limiter.check('test', 'userB'); // 2nd ok
        const result = limiter.check('test', 'userC'); // 3rd (Global limit 2 exceeded)
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain('System is busy');
    });

    it('should reset after window', () => {
        limiter.check('test', 'user1');
        expect(limiter.check('test', 'user1').allowed).toBe(false);

        // Advance time by windowMs + 100
        vi.advanceTimersByTime(1100);

        expect(limiter.check('test', 'user1').allowed).toBe(true);
    });
});
