import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const claimsPath = path.resolve(__dirname, '../src/lib/data/claims.json');
const mapPath = path.resolve(__dirname, '../src/lib/data/whitepaper_map.json');

try {
    const claims = JSON.parse(fs.readFileSync(claimsPath, 'utf8'));
    const whitepaperMap = JSON.parse(fs.readFileSync(mapPath, 'utf8'));
    let errors = [];

    for (const claim of claims) {
        if (!claim.id) {
            errors.push('Claim missing ID');
        }
        if (!claim.short_claim) {
            errors.push(`Claim ${claim.id || 'Unknown'} is missing 'short_claim'`);
        }
        if (!claim.human_claim) {
            errors.push(`Claim ${claim.id || 'Unknown'} is missing 'human_claim'`);
        }
        if (!claim.source_file) {
            errors.push(`Claim ${claim.id || 'Unknown'} is missing 'source_file'`);
        } else if (!whitepaperMap[claim.source_file]) {
            errors.push(`Claim ${claim.id} references source_file '${claim.source_file}' which is not in whitepaper_map.json`);
        }
    }

    if (errors.length > 0) {
        console.error('Validation failed with ' + errors.length + ' errors:');
        console.error(JSON.stringify(errors, null, 2));
        process.exit(1);
    } else {
        console.log(`Successfully validated ${claims.length} claims.`);
    }
} catch (e) {
    console.error('Failed to read or parse claims.json / whitepaper_map.json:', e);
    process.exit(1);
}
