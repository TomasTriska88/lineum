// @vitest-environment node
import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Asset Serving Configuration', () => {
    it('should have the source directory in the correct location relative to portal', () => {
        const sourceDir = path.join(process.cwd(), '..', 'source');
        expect(fs.existsSync(sourceDir)).toBe(true);
        expect(fs.lstatSync(sourceDir).isDirectory()).toBe(true);
    });

    it('should contain the core icon.png', () => {
        const iconPath = path.join(process.cwd(), '..', 'source', 'icon.png');
        expect(fs.existsSync(iconPath)).toBe(true);
    });

    it('should contain the fields visualization', () => {
        const vizPath = path.join(process.cwd(), '..', 'source', 'lineum-fields-visualization.png');
        expect(fs.existsSync(vizPath)).toBe(true);
    });
});
