const fs = require('fs');
const path = require('path');
const { test, describe, expect, beforeAll, afterAll } = require('vitest');
const { generateMap } = require('../scripts/generate_whitepaper_map.js');

describe('generate_whitepaper_map.js', () => {
    const testDir = path.join(__dirname, '.test_whitepapers');
    const testRoot = path.join(__dirname, '..');
    
    beforeAll(() => {
        // Create a mock whitepapers directory
        fs.mkdirSync(testDir, { recursive: true });
        fs.mkdirSync(path.join(testDir, '1-core'), { recursive: true });
        
        fs.writeFileSync(path.join(testDir, '01-valid.md'), '# Valid');
        fs.writeFileSync(path.join(testDir, '1-core', '02-sub.md'), '# Nested');
        fs.writeFileSync(path.join(testDir, 'TODO.md'), '# Todo');
        fs.writeFileSync(path.join(testDir, 'TEMPLATE.md'), '# Template');
        fs.writeFileSync(path.join(testDir, 'notmarkdown.txt'), 'Not MD');
    });

    afterAll(() => {
        // Cleanup
        fs.rmSync(testDir, { recursive: true, force: true });
    });

    test('should exclude TODO.md, TEMPLATE.md, and non-md files', () => {
        const map = generateMap(testDir, testRoot);
        const keys = Object.keys(map);
        
        expect(keys).toContain('01-valid.md');
        expect(keys).toContain('02-sub.md');
        expect(keys).not.toContain('TODO.md');
        expect(keys).not.toContain('TEMPLATE.md');
        expect(keys).not.toContain('notmarkdown.txt');
    });

    test('should generate relative POSIX paths from repo root', () => {
        const map = generateMap(testDir, testRoot);
        
        // Output format should match 'tests/.test_whitepapers/01-valid.md' without hardcoded C: drives
        const expectedPrefix = path.relative(testRoot, testDir).split(path.sep).join('/');
        
        expect(map['01-valid.md']).toBe(`${expectedPrefix}/01-valid.md`);
        expect(map['02-sub.md']).toBe(`${expectedPrefix}/1-core/02-sub.md`);
    });
});
