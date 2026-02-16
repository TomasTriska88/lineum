import { describe, it, expect } from 'vitest';

// Simulating the logic from TidalAnalyzer.svelte
function analyzeTidalStretching(data) {
    if (!data || !data.variances || data.variances.length === 0) {
        return { isConfirmed: false, ratio: 0 };
    }

    const minVar = Math.min(...data.variances);
    const maxVar = Math.max(...data.variances);
    const ratio = maxVar / (minVar || 1);

    // Hypothesis: Stretching occurs if variance increases by more than 100x near phi-trap
    const isConfirmed = ratio > 100;

    return { isConfirmed, ratio, minVar, maxVar };
}

describe('Tidal Stretching Logic', () => {
    it('should confirm stretching on cluster approach data', () => {
        const mockData = {
            times: [0, 10, 20, 30],
            variances: [6.1, 275.0, 3135.0, 7128.0],
            distances: [30.0, 15.0, 5.0, 0.5]
        };

        const result = analyzeTidalStretching(mockData);

        expect(result.isConfirmed).toBe(true);
        expect(result.ratio).toBeGreaterThan(1000);
        expect(result.maxVar).toBe(7128.0);
    });

    it('should not confirm stretching on stable cluster data', () => {
        const mockData = {
            times: [0, 10, 20, 30],
            variances: [6.1, 6.2, 5.9, 6.0],
            distances: [30.0, 28.0, 26.0, 24.0]
        };

        const result = analyzeTidalStretching(mockData);

        expect(result.isConfirmed).toBe(false);
        expect(result.ratio).toBeLessThan(2);
    });

    it('should handle empty or malformed data gracefully', () => {
        expect(analyzeTidalStretching(null).isConfirmed).toBe(false);
        expect(analyzeTidalStretching({}).isConfirmed).toBe(false);
        expect(analyzeTidalStretching({ variances: [] }).isConfirmed).toBe(false);
    });
});
