interface RequestLog {
    timestamp: number;
    ip: string;
}

interface LimitConfig {
    globalLimit: number; // Max requests per minute globally
    userLimit: number;   // Max requests per minute per IP
    windowMs: number;    // Time window in milliseconds
}

const DEFAULT_CONFIG: LimitConfig = {
    globalLimit: 15,
    userLimit: 5,
    windowMs: 60 * 1000
};

// Distinct configurations for different actions
export const LIMITS: Record<string, LimitConfig> = {
    chat: {
        globalLimit: 100, // Safe buffer (API limit is 360 RPM)
        userLimit: 20,    // Allow heavy user testing
        windowMs: 60 * 1000
    },
    tts: {
        globalLimit: 100,
        userLimit: 50,
        windowMs: 60 * 1000
    }
};

export class RateLimiter {
    private logs: Record<string, RequestLog[]> = {
        chat: [],
        tts: []
    };

    /**
     * Checks if a request is allowed for a specific action bucket.
     * @param action 'chat' | 'tts'
     * @param ip User IP address
     */
    check(action: string, ip: string): { allowed: boolean; reason?: string } {
        const config = LIMITS[action] || DEFAULT_CONFIG;
        const now = Date.now();

        // Ensure bucket exists
        if (!this.logs[action]) {
            this.logs[action] = [];
        }

        // 1. Clean up old logs (sliding window)
        this.logs[action] = this.logs[action].filter(log => now - log.timestamp < config.windowMs);

        const logs = this.logs[action];

        // 2. Global Limit Check
        if (logs.length >= config.globalLimit) {
            console.warn(`[LIMITER] Global limit reached for ${action}. Current: ${logs.length}, Max: ${config.globalLimit}`);
            return { allowed: false, reason: "System is busy (Global Rate Limit). Please wait a moment." };
        }

        // 3. User Limit Check
        const userLogs = logs.filter(log => log.ip === ip);
        if (userLogs.length >= config.userLimit) {
            console.warn(`[LIMITER] User limit reached for ${action} by ${ip}. Current: ${userLogs.length}, Max: ${config.userLimit}`);
            return { allowed: false, reason: "You are sending requests too fast. Please slow down." };
        }

        // 4. Record Request
        this.logs[action].push({ timestamp: now, ip });
        return { allowed: true };
    }
}

// Export a singleton instance
export const rateLimiter = new RateLimiter();
