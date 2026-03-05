const fs = require('fs');

try {
    const raw = fs.readFileSync('.scratch/report2.json', 'utf8');
    const data = JSON.parse(raw);

    data.errors.forEach(e => {
        console.log("================ ERROR ================");
        console.log(e.message || JSON.stringify(e));
        console.log("\n");
    });
} catch (e) {
    console.error("Failed to parse", e);
}
