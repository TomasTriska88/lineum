import { describe, it, expect, vi } from 'vitest';
import { checkRateLimit } from '../lib/server/limiter';

describe('AI Agent Logic & Security', () => {
    it('should respect user rate limits (5 RPM)', () => {
        const ip = '1.2.3.4';
        for (let i = 0; i < 5; i++) {
            expect(checkRateLimit(ip).allowed).toBe(true);
        }
        const result = checkRateLimit(ip);
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain("too many messages");
    });

    it('should respect global rate limits (15 RPM)', () => {
        const ipPrefix = '10.0.0.';
        // Global limit is 15. We already used 5 in previous test.
        for (let i = 0; i < 10; i++) {
            checkRateLimit(`${ipPrefix}${i}`);
        }

        const result = checkRateLimit('11.11.11.11');
        expect(result.allowed).toBe(false);
        expect(result.reason).toContain("Global limit");
    });
});
