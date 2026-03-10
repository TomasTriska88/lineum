import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.resolve(__dirname, '../.env.local');
const envContent = fs.readFileSync(envPath, 'utf-8');
const match = envContent.match(/GEMINI_API_KEY=(.*)/);
const API_KEY = match[1].trim();

async function listModels() {
    console.log("Fetching available models...");
    // We can't use the SDK to list models easily in all versions, 
    // so we'll use a direct fetch which is reliable.
    const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${API_KEY}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        fs.writeFileSync('models.json', JSON.stringify(data, null, 2));
        console.log("✅ Models saved to models.json");

        if (data.models) {
            const names = data.models.map(m => m.name);
            console.log("Found models:", names.join(', '));

            const has15Flash = names.some(n => n.includes('gemini-1.5-flash'));
            console.log("Has gemini-1.5-flash?", has15Flash);
        } else {
            console.log("No models found in response:", data);
        }

    } catch (e) {
        console.error("Error fetching models:", e);
    }
}

listModels();
