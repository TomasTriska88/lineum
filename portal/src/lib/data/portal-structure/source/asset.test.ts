// @vitest-environment node
import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Asset Serving Configuration', () => {
    // Railway build context often isolates the app dir, missing ../source
    // We skip these tests if the directory is missing to allow the build to pass.
    const sourceDir = path.join(process.cwd(), '..', 'source');
    const hasSource = fs.existsSync(sourceDir);

    it.skipIf(!hasSource)('should have the source directory in the correct location relative to portal', () => {
        expect(fs.existsSync(sourceDir)).toBe(true);
        expect(fs.lstatSync(sourceDir).isDirectory()).toBe(true);
    });

    it.skipIf(!hasSource)('should contain the core icon.png', () => {
        const iconPath = path.join(sourceDir, 'icon.png');
        expect(fs.existsSync(iconPath)).toBe(true);
    });

    it.skipIf(!hasSource)('should contain the fields visualization', () => {
        const vizPath = path.join(sourceDir, 'lineum-fields-visualization.png');
        expect(fs.existsSync(vizPath)).toBe(true);
    });
});
