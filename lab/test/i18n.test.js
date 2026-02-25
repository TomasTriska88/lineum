import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { locale, t, resolveKey, translations } from '../src/lib/i18n';

describe('i18n Translation System', () => {
    it('resolves top-level keys correctly', () => {
        locale.set('cs');
        const translate = get(t);
        expect(translate('simulakrum')).toBe(translations.cs.simulakrum);
    });

    it('resolves nested namespace keys correctly', () => {
        locale.set('cs');
        const translate = get(t);
        // We will add a 'test_namespace' to translations in i18n.js for testing
        expect(translate('test_ns.hello')).toBe(translations.cs.test_ns.hello);
    });

    it('falls back to English when a key is missing in Czech', () => {
        locale.set('cs');
        const translate = get(t);
        expect(translate('test_ns.only_english')).toBe('English Only');
    });

    it('returns a placeholder with [MISSING] prefix when the key is not found in any locale', () => {
        locale.set('cs');
        const translate = get(t);
        expect(translate('nonexistent.key')).toBe('[MISSING: nonexistent.key]');
    });

    it('correctly resolves a key using the resolveKey helper directly', () => {
        const obj = { level1: { level2: { value: 'success' } } };
        expect(resolveKey(obj, 'level1.level2.value')).toBe('success');
        expect(resolveKey(obj, 'level1.missing')).toBe(undefined);
    });
});
