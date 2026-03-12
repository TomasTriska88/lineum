import { describe, it, expect } from 'vitest';
import claimsData from '../src/lib/data/claims.json';

describe('Claims Metadata Language Integrity', () => {
    // Regex matching specific Czech diacritics to strictly forbid Czech language artifacts
    const czechCharsRegex = /[ěščřžýáíéúůóďťňĚŠČŘŽÝÁÍÉÚŮÓĎŤŇ]/;

    it('should not contain any Czech diacritics in any textual claim field', () => {
        const textFieldsToCheck = [
            'short_claim',
            'human_claim',
            'scientific_claim',
            'what_it_is_not',
            'source_section',
            'source_anchor',
            'source_quote',
            'test_reason',
            'verification_plan',
            'expected_measures',
            'disclaimers',
            'falsification_plan',
            'missing_falsification_reason',
            'rationale'
        ];

        let failedClaims = [];

        for (const claim of claimsData) {
            for (const field of textFieldsToCheck) {
                if (claim[field] && typeof claim[field] === 'string') {
                    if (czechCharsRegex.test(claim[field])) {
                        failedClaims.push(`[${claim.id}] Field '${field}' contains forbidden Czech characters: "${claim[field]}"`);
                    }
                }
            }
        }

        // We expect the array of failures to be completely empty
        expect(failedClaims, "Found Czech phrases in English-only claims database!").toEqual([]);
    });
});
