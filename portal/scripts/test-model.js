
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';

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

const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash-001" });

async function run() {
    try {
        console.log("Testing gemini-2.0-flash-001...");
        const result = await model.generateContent("Hello, are you there?");
        console.log("Response:", result.response.text());
    } catch (e) {
        console.error("Error Details:", e);
        if (e.response) {
            console.error("Response:", await e.response.text());
        }
    }
}

run();
