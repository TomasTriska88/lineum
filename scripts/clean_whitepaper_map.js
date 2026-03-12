const fs = require('fs');
const path = require('path');

const mapFile = path.join(__dirname, '../lab/src/lib/data/whitepaper_map.json');
const mapData = JSON.parse(fs.readFileSync(mapFile, 'utf8'));

let cleanedData = {};
let removedCount = 0;

for (const [key, filepath] of Object.entries(mapData)) {
    // Check if file actually exists
    if (fs.existsSync(filepath)) {
        cleanedData[key] = filepath;
    } else {
        console.log(`❌ Removed dead link: ${key} -> ${filepath}`);
        removedCount++;
    }
}

// Check for duplicates by path (keep the first seen key)
const seenPaths = new Set();
const finalData = {};
for (const [key, filepath] of Object.entries(cleanedData)) {
    if (!seenPaths.has(filepath)) {
        seenPaths.add(filepath);
        finalData[key] = filepath;
    } else {
        console.log(`❌ Removed duplicate path: ${key} -> ${filepath}`);
        removedCount++;
    }
}


if (removedCount > 0) {
    fs.writeFileSync(mapFile, JSON.stringify(finalData, null, 2));
    console.log(`\n✅ whitepaper_map.json cleaned. Removed ${removedCount} stale/duplicate entries.`);
} else {
    console.log('\n✅ whitepaper_map.json is already clean. No stale entries found.');
}
