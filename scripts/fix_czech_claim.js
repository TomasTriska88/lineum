const fs = require('fs');
const path = require('path');

const claimsFile = path.resolve(__dirname, '../lab/src/lib/data/claims.json');
const claims = JSON.parse(fs.readFileSync(claimsFile, 'utf8'));

let updated = false;

for (const claim of claims) {
    if (claim.id === 'CL-COSMO-036') {
        claim.source_section = "§3 Dynamics of Two Fields";
        claim.source_anchor = "#3-dynamics-of-two-fields-stopping-and-capturing-reality";
        claim.source_quote = "The image of an atom is thus, in Lineum terminology, a static slice of the moment when the untamed wave successfully catches...";
        updated = true;
        break;
    }
}

if (updated) {
    fs.writeFileSync(claimsFile, JSON.stringify(claims, null, 4));
    console.log("✅ Fixed metadata for CL-COSMO-036 to English.");
} else {
    console.log("❌ Could not find CL-COSMO-036");
}
