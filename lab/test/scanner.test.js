import { describe, it, expect } from 'vitest';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

describe('Laboratory Data Synchronization', () => {
    const dataDir = join(process.cwd(), 'public', 'data');

    const readJson = (file) => {
        const path = join(dataDir, file);
        if (!existsSync(path)) return null;
        return JSON.parse(readFileSync(path, 'utf8'));
    };

    it('should have consistent frame counts across all audit data', () => {
        const phiData = readJson('phi_frames.json');
        const resonanceData = readJson('resonance.json');
        const trajData = readJson('trajectories.json');

        expect(phiData).not.toBeNull();
        expect(resonanceData).not.toBeNull();
        expect(trajData).not.toBeNull();

        const phiFrames = phiData.metadata.frame_count;
        const resSamples = resonanceData.phi_evolution.length;

        console.log(`Verifying sync: Phi Frames=${phiFrames}, Resonance Samples=${resSamples}`);

        expect(resSamples).toBe(phiFrames);

        // Verify each trajectory has the correct number of points
        trajData.forEach(traj => {
            expect(traj.path.length).toBe(phiFrames);
        });
    });
});
