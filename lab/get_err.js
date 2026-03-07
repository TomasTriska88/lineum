const fs = require('fs');
try {
    const text = fs.readFileSync('test_err.log', 'utf16le');
    const lines = text.split('\n');
    let printing = false;
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('Error:') || lines[i].includes('FAIL') || lines[i].includes('failed')) {
            printing = 15; // print 15 lines of context
        }
        if (printing > 0) {
            console.log(lines[i].trim());
            printing--;
        }
    }
} catch (e) {
    console.error(e.message);
}
