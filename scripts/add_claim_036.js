const fs = require('fs');
const path = require('path');

const claimsFile = path.join(__dirname, '../lab/src/lib/data/claims.json');
const data = JSON.parse(fs.readFileSync(claimsFile, 'utf8'));

const newClaim = {
    "id": "CL-COSMO-036",
    "short_claim": "Quantum microscopy atom captures structurally match Lineum's \u03BC\u2080 wave vortices.",
    "human_claim": "The first clear pictures of single atoms look exactly like the math-generated whirlpools in our simulation, reinforcing that matter is trapped waves.",
    "scientific_claim": "The visual topographies of empirically trapped atoms map to the LAP4/LAP8 stabilized \u03A8/\u03A6 interference patterns of Linon vortices.",
    "what_it_is_not": "This claims correspondence in foundational topology, not that we simulated the exact identical element structure.",
    "source_file": "36-cosmo-hyp-quantum-microscopy.md",
    "source_section": "\u00A73 Dynamika dvou pol\u00ED",
    "source_anchor": "#dynamika-dvou-pol",
    "source_quote": "Sn\u00EDmek atomu je tedy v terminologii Linea statick\u00FDm \u0159ezem momentu, kdy se nespoutan\u00E1 vlna \u00FAsp\u011B\u0161n\u011B chytne...",
    "tags": ["cosmology", "quantum", "microscopy", "linon", "vortex", "draft"],
    "scope": "ANALOGICAL",
    "status": "UNTESTED",
    "testability": "NOT_TESTABLE_YET",
    "test_reason": "Requires algorithmic structural similarity index cross-referencing between empirical microscopy data and mathematically simulated \u03BC\u2080 fields from Lineum.",
    "verification_plan": "1. Run stable Linon vortex preset. 2. Export \u03A8/\u03A6 distribution. 3. Assess with empirical structures via SSIM.",
    "expected_measures": "SSIM metric > 0.85.",
    "scenario_id": null,
    "disclaimers": "This relies on philosophical and topographic interpretation of current state-of-the-art physics imagery.",
    "falsification_needed": true,
    "falsification_plan": "If future higher resolution topological maps of atomic boundaries fundamentally violate LAP4/LAP8 symmetry patterns, the explicit analogy fails.",
    "missing_falsification_reason": null,
    "verification_spec_status": "NOT_PREPARED",
    "canonical_claim_set": "NOT_PART_OF_PROMOTION",
    "falsification_mode": "MANUAL_PLAN_ONLY",
    "falsification_status": "NOT_IMPLEMENTED",
    "last_falsification_run_id": null
};

// Only add if it doesn't exist
if (!data.some(c => c.id === 'CL-COSMO-036')) {
    data.push(newClaim);
    fs.writeFileSync(claimsFile, JSON.stringify(data, null, 4));
    console.log('✅ Successfully added CL-COSMO-036 to claims.json');
} else {
    console.log('CL-COSMO-036 already exists.');
}
