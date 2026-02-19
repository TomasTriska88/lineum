
import { describe, it, expect } from 'vitest';
import { detectLanguage, selectVoice } from '$lib/utils/tts_utils';

describe('detectLanguage', () => {
    it('detects Czech with strong characters', () => {
        expect(detectLanguage('Ahoj, jak se máš?')).toBe('cs-CZ'); // š, á
        expect(detectLanguage('Řeřicha')).toBe('cs-CZ'); // Ř, ř
        expect(detectLanguage('Kůň')).toBe('cs-CZ'); // ů, ň
    });

    it('detects English with standard words', () => {
        expect(detectLanguage('Hello there')).toBe('en-US');
        expect(detectLanguage('This is a test')).toBe('en-US');
        expect(detectLanguage('What are you doing?')).toBe('en-US');
    });

    it('prioritizes English words even if Czech characters are present', () => {
        expect(detectLanguage('Hello Tomáš')).toBe('en-US'); // Tomáš has á, š but Hello is safe
        expect(detectLanguage('This is for Řeřich')).toBe('en-US'); // Řeřich has ř but This/is/for are safe
        expect(detectLanguage('Where is Lukáš?')).toBe('en-US');
    });

    it('defaults to English if no strong/weak Czech characters are found', () => {
        // "To je pes" has no accents. It will be treated as English 
        // because we can't be sure it's Czech without a dictionary lookup.
        expect(detectLanguage('To je pes')).toBe('en-US');
        expect(detectLanguage('No accents here')).toBe('en-US');
    });

    it('detects Czech for weak characters if no English words are present', () => {
        expect(detectLanguage('Běží liška k táboru')).toBe('cs-CZ'); // ě, ž, š, á
        expect(detectLanguage('Mám hlad')).toBe('cs-CZ'); // á
    });
});

describe('selectVoice', () => {
    // Mock basic voice objects
    const mockVoices: any[] = [
        { name: 'Microsoft Jakub', lang: 'cs-CZ' },
        { name: 'Microsoft Vlasta', lang: 'cs-CZ' },
        { name: 'Google US English', lang: 'en-US' },
        { name: 'Microsoft Zira', lang: 'en-US' },
        { name: 'Microsoft David', lang: 'en-US' }
    ];

    it('selects Vlasta for Czech if available', () => {
        const voice = selectVoice(mockVoices, 'cs-CZ');
        expect(voice?.name).toContain('Vlasta');
    });

    it('selects Zira or Google for English if available', () => {
        const voice = selectVoice(mockVoices, 'en-US');
        expect(voice?.name).toMatch(/Zira|Google/);
    });

    it('falls back to any voice of language if preferred not found', () => {
        const limitedVoices: any[] = [
            { name: 'Microsoft Jakub', lang: 'cs-CZ' }, // Only Jakub
            { name: 'Microsoft David', lang: 'en-US' }  // Only David
        ];

        expect(selectVoice(limitedVoices, 'cs-CZ')?.name).toBe('Microsoft Jakub');
        expect(selectVoice(limitedVoices, 'en-US')?.name).toBe('Microsoft David');
    });
});
