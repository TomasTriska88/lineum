import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as lib from '../helpers/check-czech-lib.js';
import fs from 'fs';

vi.mock('fs');

describe('check-czech-lib', () => {
    let consoleErrorSpy;

    beforeEach(() => {
        consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
    });

    afterEach(() => {
        consoleErrorSpy.mockRestore();
        vi.clearAllMocks();
    });

    it('returns true when Czech characters are present', () => {
        fs.readFileSync.mockReturnValue('Zde je nějaký text s háčky a čárkami.\nTo je špatně.');
        const result = lib.checkFile('dummy.js');
        expect(result).toBe(true);
        expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('returns false when only English text is present', () => {
        fs.readFileSync.mockReturnValue('This is a pure English string.\nNo special characters here.');
        const result = lib.checkFile('dummy.js');
        expect(result).toBe(false);
        expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('ignores whitelisted words like Čeština', () => {
        fs.readFileSync.mockReturnValue('This word Čeština should be ignored.\nBut this š is bad.');
        const result = lib.checkFile('dummy.js');
        expect(result).toBe(true); // Fails because of 'š'

        fs.readFileSync.mockReturnValue('This word Čeština should be ignored alone.');
        const result2 = lib.checkFile('dummy.js');
        expect(result2).toBe(false); // Passes because 'Čeština' is whitelisted
    });
});
