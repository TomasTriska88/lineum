
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// ES Module fix for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const envPath = path.resolve(__dirname, '../.env'); // Check root .env first
const envLocalPath = path.resolve(__dirname, '../.env.local');

let apiKey = "";

console.log("Checking for API Key...");

// Try .env.local
if (fs.existsSync(envLocalPath)) {
    console.log("Found .env.local");
    const envContent = fs.readFileSync(envLocalPath, 'utf-8');
    const match = envContent.match(/GEMINI_API_KEY=(.*)/);
    if (match) {
        apiKey = match[1].trim();
    }
}

// Try .env if not found
if (!apiKey && fs.existsSync(envPath)) {
    console.log("Found .env");
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const match = envContent.match(/GEMINI_API_KEY=(.*)/);
    if (match) {
        apiKey = match[1].trim();
    }
}

// Try process.env
if (!apiKey) {
    apiKey = process.env.GEMINI_API_KEY;
}

if (!apiKey) {
    console.error("CRITICAL: No GEMINI_API_KEY found in .env, .env.local, or process.env");
    process.exit(1);
}

const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });

async function run() {
    try {
        console.log("--------------------------------------------------");
        console.log("Testing Model: gemini-2.5-flash");
        console.log("--------------------------------------------------");

        const prompt = "Hello! Please reply with 'System Online: Gemini 2.5 Flash is operational.' if you can read this.";
        console.log(`Sending Prompt: "${prompt}"`);

        const result = await model.generateContent(prompt);
        const response = result.response.text();

        console.log("--------------------------------------------------");
        console.log("Response Received:");
        console.log(response);
        console.log("--------------------------------------------------");
        console.log("✅ VERIFICATION SUCCESSFUL: 'gemini-2.5-flash' is available.");
    } catch (e) {
        console.error("--------------------------------------------------");
        console.error("❌ VERIFICATION FAILED");
        console.error("Error Details:", e.message);
        if (e.response) {
            // console.error("API Response:", JSON.stringify(await e.response.json(), null, 2));
        }
        process.exit(1);
    }
}

run();
