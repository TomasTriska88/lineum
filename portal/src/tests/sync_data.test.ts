// @vitest-environment node
import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import fs from 'fs';
import path from 'path';
import { sync } from '../../scripts/sync-data.js';

const PROJECT_ROOT = process.cwd();
const SOURCE_DIR = path.join(PROJECT_ROOT, '../whitepapers'); // Assuming standard structure
const TARGET_DIR = path.join(PROJECT_ROOT, 'src/lib/data/whitepapers');
const AI_INDEX_PATH = path.join(PROJECT_ROOT, 'src/lib/data/ai_index.json');

const TEST_FILE_NAME = '_test_sync_automated.md';
const TEST_FILE_CONTENT = '# STATUS: Hypothesis\n\nThis is a temporary test file for sync verification.';
const SOURCE_FILE_PATH = path.join(SOURCE_DIR, TEST_FILE_NAME);

describe('Data Synchronization', () => {
    // Only run this suite if we can access the source directories
    const canRun = fs.existsSync(SOURCE_DIR);

    if (!canRun) {
        it.skip('Skipping sync tests: Source directory not found', () => { });
        return;
    }

    beforeAll(() => {
        // Create a dummy file in the source directory
        if (!fs.existsSync(SOURCE_DIR)) fs.mkdirSync(SOURCE_DIR, { recursive: true });
        fs.writeFileSync(SOURCE_FILE_PATH, TEST_FILE_CONTENT);
    });

    afterAll(() => {
        // Cleanup
        if (fs.existsSync(SOURCE_FILE_PATH)) fs.unlinkSync(SOURCE_FILE_PATH);
        const targetFile = path.join(TARGET_DIR, TEST_FILE_NAME);
        if (fs.existsSync(targetFile)) fs.unlinkSync(targetFile);
    });

    it('should copy new files from source to target', () => {
        console.log('Running sync function direct import...');

        // Mock console.log to avoid clutter, or keep it to see progress
        const logSpy = vi.spyOn(console, 'log').mockImplementation(() => { });
        const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => { });

        try {
            sync();
        } finally {
            logSpy.mockRestore();
            warnSpy.mockRestore();
        }

        // Check if file exists in target
        const targetFile = path.join(TARGET_DIR, TEST_FILE_NAME);
        expect(fs.existsSync(targetFile), `File ${targetFile} should exist`).toBe(true);

        const content = fs.readFileSync(targetFile, 'utf-8');
        expect(content).toBe(TEST_FILE_CONTENT);
    });

    it('should update ai_index.json with new file metadata', () => {
        expect(fs.existsSync(AI_INDEX_PATH), 'ai_index.json should exist').toBe(true);

        const index = JSON.parse(fs.readFileSync(AI_INDEX_PATH, 'utf-8'));
        const entry = index.find((i: any) => i.name === TEST_FILE_NAME);

        expect(entry, 'Entry for test file should exist in ai_index.json').toBeDefined();
        expect(entry.status).toBe('Hypothesis'); // Based on content header
        expect(entry.type).toBe('documentation');
    });

    it('should track robust context files (LINA_PERSONA.md)', () => {
        // Verify that critical context files are present in the synced data/core
        const CORE_TARGET = path.join(PROJECT_ROOT, 'src/lib/data/core');
        const PERSONA = path.join(CORE_TARGET, 'LINA_PERSONA.md');
        const DESIGN = path.join(CORE_TARGET, 'DESIGN_GUIDE.md');

        expect(fs.existsSync(PERSONA), 'LINA_PERSONA.md should be synced to core').toBe(true);
        expect(fs.existsSync(DESIGN), 'DESIGN_GUIDE.md should be synced to core').toBe(true);
    });
});
