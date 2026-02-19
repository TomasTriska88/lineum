
import { env } from '$env/dynamic/private';
import fs from 'fs';
import path from 'path';

const DB_FILE = 'usage_db.json';

// Pricing for Gemini 2.0 (Estimated conservative blended rate)
// Input: $0.10 / 1M
// Output: $0.40 / 1M
// RAG Input is small (~10k), Output is ~500.
// Avg cost per request ~ $0.0015.

const COST_FLASH_INPUT = 0.10; // $0.10 / 1M
const COST_FLASH_OUTPUT = 0.40; // $0.40 / 1M

// Gemini 1.5 Pro Pricing (Approximation for 2.5 Pro Preview if billed)
// Input: $3.50 / 1M
// Output: $10.50 / 1M
const COST_PRO_INPUT = 3.50;
const COST_PRO_OUTPUT = 10.50;

interface UsageStats {
    date: string; // YYYY-MM-DD
    tokensInput: number;
    tokensOutput: number;
    estimatedCost: number;
}

export class UsageGuard {
    private stats: UsageStats = { date: '', tokensInput: 0, tokensOutput: 0, estimatedCost: 0 };
    private budgetLimitUsd: number;

    constructor() {
        // Default to $1.00 per day if not set (approx 25 CZK)
        this.budgetLimitUsd = parseFloat(env.DAILY_BUDGET_USD || '1.00');
        this.load();
    }

    private getToday(): string {
        return new Date().toISOString().split('T')[0];
    }

    private load() {
        try {
            if (fs.existsSync(DB_FILE)) {
                this.stats = JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
            }
        } catch (e) {
            console.error("[UsageGuard] Failed to load DB:", e);
        }

        // Reset if new day
        const today = this.getToday();
        if (this.stats.date !== today) {
            console.log("[UsageGuard] New day detected. Resetting counters.");
            this.stats = { date: today, tokensInput: 0, tokensOutput: 0, estimatedCost: 0 };
            this.save();
        }
    }

    private save() {
        try {
            fs.writeFileSync(DB_FILE, JSON.stringify(this.stats, null, 2));
        } catch (e) {
            console.error("[UsageGuard] Failed to save DB:", e);
        }
    }

    public checkLimit(): { allowed: boolean; remainingBudget: number } {
        this.load(); // Sync state
        if (this.stats.estimatedCost >= this.budgetLimitUsd) {
            console.warn(`[UsageGuard] BLOCKED: Daily limit $${this.budgetLimitUsd} exceeded (Current: $${this.stats.estimatedCost.toFixed(4)})`);
            return { allowed: false, remainingBudget: 0 };
        }
        return { allowed: true, remainingBudget: this.budgetLimitUsd - this.stats.estimatedCost };
    }

    public recordUsage(inputTokens: number, outputTokens: number, model: 'flash' | 'pro' = 'flash') {
        // SAFETY: Do not record usage in test environment or if key is poisoned
        if ((process.env.NODE_ENV === 'test' && !process.env.FORCE_USAGE_RECORDING) || process.env.GEMINI_API_KEY === 'INVALID_TEST_KEY') {
            console.log(`[UsageGuard] TEST MODE: Ignoring usage record (${inputTokens}/${outputTokens})`);
            return;
        }

        this.stats.tokensInput += inputTokens;
        this.stats.tokensOutput += outputTokens;

        const inputRate = model === 'pro' ? COST_PRO_INPUT : COST_FLASH_INPUT;
        const outputRate = model === 'pro' ? COST_PRO_OUTPUT : COST_FLASH_OUTPUT;

        const cost = (inputTokens / 1_000_000 * inputRate) +
            (outputTokens / 1_000_000 * outputRate);

        this.stats.estimatedCost += cost;
        this.save();
        console.log(`[UsageGuard] Recorded (${model}): ${inputTokens} in / ${outputTokens} out. Cost: +$${cost.toFixed(6)}. Total: $${this.stats.estimatedCost.toFixed(4)}`);
    }

    public getStats() {
        // Calculate percentage of budget used
        const percentage = Math.min(100, (this.stats.estimatedCost / this.budgetLimitUsd) * 100);
        return {
            ...this.stats,
            budgetLimit: this.budgetLimitUsd,
            percentage: percentage
        };
    }
}

export const usageGuard = new UsageGuard();
