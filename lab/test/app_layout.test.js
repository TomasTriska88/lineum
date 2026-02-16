import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Lab UI Structural Integrity (Invariant Test)', () => {
    // We read the file directly to check for CSS and HTML invariants 
    // This is a robust way to prevent the "oops I deleted a class" regression
    const appSveltePath = path.resolve(__dirname, '../src/App.svelte');
    const content = fs.readFileSync(appSveltePath, 'utf8');

    it('should contain essential CSS classes for the Stats panel', () => {
        const requiredClasses = [
            '.stats-panel',
            '.stat',
            '.label',
            '.value',
            '.jump-btn',
            '.speed-control',
            '.toggle-btn',
            '.run-selector',
            '.header-controls'
        ];

        requiredClasses.forEach(cls => {
            expect(content).toContain(cls);
        });
    });

    it('should have the correct HTML structure for the Stats panel', () => {
        // Check for specific HTML patterns that define the stats layout
        expect(content).toContain('class="stats-panel"');
        expect(content).toContain('class="stat"');
        expect(content).toContain('class="label"');
        expect(content).toContain('class="value"');
    });

    it('should have the tab buttons defined', () => {
        expect(content).toContain('on:click={() => (activeTab = "stats")}');
        expect(content).toContain('on:click={() => (activeTab = "scanner")}');
        expect(content).toContain('on:click={() => (activeTab = "tidal")}');
    });

    it('should have the TidalAnalyzer component imported and used', () => {
        expect(content).toContain('import TidalAnalyzer from "./lib/components/TidalAnalyzer.svelte"');
        expect(content).toContain('<TidalAnalyzer {dataRoot} />');
    });
});
