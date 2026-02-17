
import fs from 'fs';
import path from 'path';
import https from 'https';

const envPath = path.resolve(process.cwd(), '.env.local');
let apiKey = "";

try {
    if (fs.existsSync(envPath)) {
        const envContent = fs.readFileSync(envPath, 'utf-8');
        const match = envContent.match(/GEMINI_API_KEY=(.*)/);
        if (match) {
            apiKey = match[1].trim();
        }
    }
} catch (e) {
    console.error("Could not read .env.local");
    process.exit(1);
}

if (!apiKey) {
    apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        console.error("No API Key found.");
        process.exit(1);
    }
}

const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;

https.get(url, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
        try {
            const json = JSON.parse(data);
            fs.writeFileSync('models.json', JSON.stringify(json, null, 2));
            console.log("Saved models to models.json");
        } catch (e) {
            console.error("Parse Error:", e);
        }
    });
}).on('error', (err) => console.error("Error:", err));
