const fs = require('fs');

try {
    const log = fs.readFileSync('test_output.txt', 'utf16le');
    const mainMatches = [...log.matchAll(/MAIN PAGE BOXES: (\{.*\})/g)];
    const subMatches = [...log.matchAll(/SUBPAGE BOXES: (\{.*\})/g)];

    console.log("--- Extracted Test Data ---");
    if (mainMatches.length > 0) console.log("MAIN:", mainMatches[mainMatches.length - 1][1]);
    if (subMatches.length > 0) console.log("SUB:", subMatches[subMatches.length - 1][1]);
} catch (e) {
    console.error(e);
}
