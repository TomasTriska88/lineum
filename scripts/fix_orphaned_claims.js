const fs = require('fs');
const path = require('path');

const claimsFile = path.resolve(__dirname, '../lab/src/lib/data/claims.json');
const mapFile = path.resolve(__dirname, '../lab/src/lib/data/whitepaper_map.json');

try {
    const claims = JSON.parse(fs.readFileSync(claimsFile, 'utf8'));
    const map = JSON.parse(fs.readFileSync(mapFile, 'utf8'));

    const initialLength = claims.length;
    const validClaims = claims.filter(c => map.hasOwnProperty(c.source_file));

    const removed = initialLength - validClaims.length;
    
    if (removed > 0) {
        fs.writeFileSync(claimsFile, JSON.stringify(validClaims, null, 4));
        console.log(`✅ Removed ${removed} claims that referenced dead whitepaper links.`);
    } else {
        console.log(`✅ No dead claims found.`);
    }
} catch (e) {
    console.error("Error processing files:", e);
}
