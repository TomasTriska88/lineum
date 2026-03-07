import claimsData from './claims.json' with { type: 'json' };

/**
 * Lineum Claims Registry — Full Ingest from All Whitepapers
 * 
 * Schema per claim:
 *   id, short_claim, human_claim, scientific_claim, what_it_is_not,
 *   source_file, source_section, source_anchor, source_quote,
 *   tags[], scope, status, testability, test_reason,
 *   verification_plan, expected_measures, scenario_id,
 *   disclaimers, falsification_needed, falsification_plan, missing_falsification_reason
 * 
 * Scope:        MODEL_INTERNAL | ANALOGICAL | REAL_WORLD_STRONG
 * Testability:  TESTABLE_NOW | NEEDS_NEW_SCENARIO | NOT_TESTABLE_YET
 * Status:       UNTESTED (default; resolved by backend at runtime)
 */

export const whitepaperClaims = claimsData;
