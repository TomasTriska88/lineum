import { describe, it, expect } from 'vitest';
import { translations, resolveKey } from './i18n';

describe('Lab i18n Dictionary Parity', () => {

    // Recursive function to get all flattened key paths
    function getFlattenedKeys(obj, prefix = '') {
        let keys = [];
        for (const key in obj) {
            if (typeof obj[key] === 'object' && obj[key] !== null) {
                keys = keys.concat(getFlattenedKeys(obj[key], `${prefix}${key}.`));
            } else {
                keys.push(`${prefix}${key}`);
            }
        }
        return keys;
    }

    const enKeys = getFlattenedKeys(translations.en);
    const csKeys = getFlattenedKeys(translations.cs);
    const deKeys = getFlattenedKeys(translations.de);
    const jaKeys = getFlattenedKeys(translations.ja);

    const checkCoverage = (targetLang, ObjectKeys) => {
        const missing = enKeys.filter(key => !ObjectKeys.includes(key));
        expect(missing, `Missing translations in ${targetLang}: \n${missing.join('\n')}`).toEqual([]);

        const orphans = ObjectKeys.filter(key => !enKeys.includes(key));
        expect(orphans, `Orphaned translations in ${targetLang} (not in EN): \n${orphans.join('\n')}`).toEqual([]);
    };

    it('Czech dictionary has parity with English', () => {
        checkCoverage('CS', csKeys);
    });

    it('German dictionary has parity with English', () => {
        checkCoverage('DE', deKeys);
    });

    it('Japanese dictionary has parity with English', () => {
        checkCoverage('JA', jaKeys);
    });

    it('Resolves deeply nested keys correctly', () => {
        const dummyObj = { a: { b: { c: "test string" } } };
        expect(resolveKey(dummyObj, 'a.b.c')).toBe("test string");
        expect(resolveKey(dummyObj, 'a.x.y')).toBeUndefined();
    });
});
