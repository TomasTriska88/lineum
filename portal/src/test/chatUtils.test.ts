
import { describe, it, expect } from 'vitest';
import { stripMarkdown, transliterateSymbols } from '../lib/utils/chatUtils';

describe('Chat Utils', () => {
    describe('stripMarkdown', () => {
        it('should remove bold and italic', () => {
            expect(stripMarkdown('**Bold** and *Italic*')).toBe('Bold and Italic');
        });

        it('should remove code blocks', () => {
            expect(stripMarkdown('Code `var x = 1`')).toBe('Code var x = 1');
        });

        it('should remove links', () => {
            expect(stripMarkdown('[Link](http://example.com)')).toBe('Link');
        });

        it('should cleanup leftovers', () => {
            expect(stripMarkdown('Leftover * symbols #')).toBe('Leftover  symbols ');
        });

        it('should transliterate symbols', () => {
            expect(stripMarkdown('Value is φ')).toBe('Value is fí');
        });
    });

    describe('transliterateSymbols', () => {
        it('should handle decimals', () => {
            expect(transliterateSymbols('0.012')).toBe('0,012');
        });

        it('should handle multiplication', () => {
            expect(transliterateSymbols('5 * 5')).toBe('5 krát 5');
        });

        it('should handle greek letters', () => {
            expect(transliterateSymbols('Ω and κ')).toBe('omega and kappa');
        });

        it('should ignore non-czech lang', () => {
            expect(transliterateSymbols('0.12', 'en-US')).toBe('0.12');
        });
    });
});
