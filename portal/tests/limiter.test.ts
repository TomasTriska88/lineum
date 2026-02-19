import { describe, it, expect, beforeEach, vi } from 'vitest';
import { RateLimiter, LIMITS } from './limiter';

describe('RateLimiter', () => {
    let limiter: RateLimiter;

    beforeEach(() => {
        limiter = new RateLimiter();
        vi.useFakeTimers();
    });

    it('should allow requests within limit', () => {
        const ip = '127.0.0.1';
        for (let i = 0; i < LIMITS.chat.userLimit; i++) {
            const result = limiter.check('chat', ip);
            expect(result.allowed).toBe(true);
        }
    });

    it('should block requests over user limit', () => {
        const ip = '127.0.0.1';
        // Fill bucket
        for (let i = 0; i < LIMITS.chat.userLimit; i++) {
            limiter.check('chat', ip);
        }
        // Next one should fail
        const result = limiter.check('chat', ip);
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain('too fast');
    });

    it('should reset after window expires', () => {
        const ip = '127.0.0.1';
        // Exhaust limit
        for (let i = 0; i < LIMITS.chat.userLimit + 1; i++) {
            limiter.check('chat', ip);
        }

        // Confirm blocked
        expect(limiter.check('chat', ip).allowed).toBe(false);

        // Advance time past window (60s + 1s)
        vi.advanceTimersByTime(LIMITS.chat.windowMs + 1000);

        // Should be allowed again
        expect(limiter.check('chat', ip).allowed).toBe(true);
    });

    it('should handle global limits', () => {
        // Fill global bucket with distinct IPs
        for (let i = 0; i < LIMITS.chat.globalLimit; i++) {
            limiter.check('chat', `192.168.1.${i}`);
        }

        // Next request from ANY IP should fail
        const result = limiter.check('chat', '10.0.0.1');
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain('Global Rate Limit');
    });
});
