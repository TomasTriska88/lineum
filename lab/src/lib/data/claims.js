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

export const whitepaperClaims = claimsData.map(c => {
    // Derive runability_status
    let runability_status = "BLOCKED_UNTIL_APPROVED";

    if (c.testability === "TESTABLE_NOW") {
        if (c.verification_spec_status === "APPROVED") {
            if (c.exact_scenario_id && c.exact_scenario_id !== "needs-new-scenario" && c.exact_scenario_id !== "None" && c.exact_scenario_id !== "") {
                runability_status = "RUNNABLE_NOW";
            } else {
                runability_status = "NEEDS_SCENARIO_CREATION";
            }
        }
    } else if (c.testability === "NEEDS_NEW_SCENARIO") {
        runability_status = "NEEDS_SCENARIO_CREATION";
    } else if (c.testability === "NOT_TESTABLE_YET") {
        runability_status = "NOT_TESTABLE_YET";
    }

    // Derive included_in_verify_all
    const included_in_verify_all = runability_status === "RUNNABLE_NOW" ? "YES" : "NO";

    return {
        ...c,
        runability_status,
        included_in_verify_all
    };
});
