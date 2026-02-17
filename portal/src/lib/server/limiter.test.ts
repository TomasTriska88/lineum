import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RateLimiter, LIMITS } from './limiter';

describe('RateLimiter', () => {
    let limiter: RateLimiter;

    beforeEach(() => {
        limiter = new RateLimiter();
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should allow requests properly within limits', () => {
        const res = limiter.check('chat', '127.0.0.1');
        expect(res.allowed).toBe(true);
    });

    it('should enforce user limits for chat', () => {
        const ip = '1.2.3.4';
        const limit = LIMITS.chat.userLimit;

        // Fill up to limit
        for (let i = 0; i < limit; i++) {
            expect(limiter.check('chat', ip).allowed).toBe(true);
        }

        // Exceed limit
        const blocked = limiter.check('chat', ip);
        expect(blocked.allowed).toBe(false);
        expect(blocked.reason).toContain('too fast');
    });

    it('should enforce global limits for chat', () => {
        const limit = LIMITS.chat.globalLimit;

        // Fill up global limit with unique IPs
        for (let i = 0; i < limit; i++) {
            expect(limiter.check('chat', `10.0.0.${i}`).allowed).toBe(true);
        }

        // Exceed global limit
        const blocked = limiter.check('chat', '10.0.0.999');
        expect(blocked.allowed).toBe(false);
        expect(blocked.reason).toContain('System is busy');
    });

    it('should maintain independent buckets for chat and tts', () => {
        const ip = '5.5.5.5';

        // Exhaust Chat Limit
        for (let i = 0; i < LIMITS.chat.userLimit; i++) {
            limiter.check('chat', ip);
        }
        expect(limiter.check('chat', ip).allowed).toBe(false);

        // TTS should still be allowed
        expect(limiter.check('tts', ip).allowed).toBe(true);
    });

    it('should enforce stricter limits for TTS', () => {
        const ip = '6.6.6.6';
        const ttsLimit = LIMITS.tts.userLimit;

        for (let i = 0; i < ttsLimit; i++) {
            expect(limiter.check('tts', ip).allowed).toBe(true);
        }

        expect(limiter.check('tts', ip).allowed).toBe(false);
    });

    it('should reset limits after window expiration', () => {
        const ip = '7.7.7.7';

        // Block user
        for (let i = 0; i < LIMITS.chat.userLimit; i++) {
            limiter.check('chat', ip);
        }
        expect(limiter.check('chat', ip).allowed).toBe(false);

        // Fast forward time past window
        vi.advanceTimersByTime(LIMITS.chat.windowMs + 1000);

        // Should be allowed again
        expect(limiter.check('chat', ip).allowed).toBe(true);
    });
});
