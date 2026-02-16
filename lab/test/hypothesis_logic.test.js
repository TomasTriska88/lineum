import { describe, it, expect } from 'vitest';

// Simulating the derived metrics logic from HypothesisTester.svelte
function calculateMetrics(discoveryData) {
    if (!discoveryData) return { alignment: "0.00%", stability: "0.0%" };

    const alignment = (discoveryData.pearson_r * 100).toFixed(2) + "%";
    const stability = (1 / (1 + discoveryData.euclidean_dist) * 100).toFixed(1) + "%";

    return { alignment, stability };
}

describe('Hypothesis Discovery Logic', () => {
    it('should correctly derive Alignment from Pearson R (spec6 real-world data)', () => {
        const mockData = {
            pearson_r: 0.9961,
            euclidean_dist: 0.05
        };

        const result = calculateMetrics(mockData);

        expect(result.alignment).toBe("99.61%");
    });

    it('should correctly derive Stability from Euclidean Distance', () => {
        const mockData = {
            pearson_r: 0.9961,
            euclidean_dist: 0.05 // Very close alignment
        };

        const result = calculateMetrics(mockData);

        // 1 / (1 + 0.05) = 1 / 1.05 = ~0.9523
        expect(result.stability).toBe("95.2%");
    });

    it('should handle zero or high distance (chaos)', () => {
        const mockData = {
            pearson_r: 0.1,
            euclidean_dist: 1.5 // High distance
        };

        const result = calculateMetrics(mockData);

        expect(result.alignment).toBe("10.00%");
        // 1 / (1 + 1.5) = 1 / 2.5 = 0.4
        expect(result.stability).toBe("40.0%");
    });

    it('should handle null data gracefully', () => {
        const result = calculateMetrics(null);
        expect(result.alignment).toBe("0.00%");
        expect(result.stability).toBe("0.0%");
    });
});
