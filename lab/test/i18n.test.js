import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { locale, t, resolveKey, translations } from '../src/lib/i18n';

describe('i18n Translation System (Lab Flat Dict)', () => {
    it('resolves top-level keys correctly', () => {
        const translate = get(t);
        expect(translate('simulakrum')).toBe(translations.simulakrum);
    });

    it('resolves nested namespace keys correctly', () => {
        const translate = get(t);
        expect(translate('test_ns.hello')).toBe(translations.test_ns.hello);
    });

    it('returns a placeholder with [MISSING] prefix when the key is not found', () => {
        const translate = get(t);
        expect(translate('nonexistent.key')).toBe('[MISSING: nonexistent.key]');
    });

    it('correctly resolves a key using the resolveKey helper directly', () => {
        const obj = { level1: { level2: { value: 'success' } } };
        expect(resolveKey(obj, 'level1.level2.value')).toBe('success');
        expect(resolveKey(obj, 'level1.missing')).toBe(undefined);
    });
});
