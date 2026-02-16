import { describe, it, expect } from 'vitest';

// Simulating the logic from ZetaScanner.svelte
function calculateRevolutionary(frameCorrelation, currentFrame) {
    const history = frameCorrelation.slice(0, currentFrame + 1);
    const avg = history.length > 0
        ? history.reduce((a, b) => a + b, 0) / history.length
        : 0.5;

    // Original logic: avgCorrelation > 0.85 && frame > 20
    const isRevolutionaryOld = avg > 0.85 && currentFrame > 20;

    // Proposed logic: window average or recent peak
    const window = frameCorrelation.slice(Math.max(0, currentFrame - 10), currentFrame + 1);
    const windowAvg = window.reduce((a, b) => a + b, 0) / window.length;
    const isRevolutionaryNew = windowAvg > 0.8;

    return { avg, isRevolutionaryOld, isRevolutionaryNew };
}

describe('Zeta Scanner Revolutionary Logic', () => {
    it('should fail to trigger with strictly global average on noisy data', () => {
        // Mock data: low correlation at start, high at end
        const data = new Array(30).fill(0.1).concat(new Array(10).fill(0.95));
        const frame = 39; // Last frame

        const result = calculateRevolutionary(data, frame);

        console.log(`Global Avg: ${result.avg.toFixed(3)}`);
        expect(result.isRevolutionaryOld).toBe(false); // Reproduces the "bug"
        expect(result.isRevolutionaryNew).toBe(true);  // Verifies the fix
    });

    it('should trigger correctly with actual audit-like data', () => {
        // Using real-world max correlation (0.99) and avg (0.4)
        const data = new Array(150).fill(0.2).concat(new Array(50).fill(0.99));
        const frame = 199;

        const result = calculateRevolutionary(data, frame);
        expect(result.isRevolutionaryOld).toBe(false);
        expect(result.isRevolutionaryNew).toBe(true);
    });
});
