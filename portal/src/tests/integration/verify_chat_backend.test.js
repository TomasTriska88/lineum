import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.resolve(__dirname, '../.env.local');

console.log("Reading .env.local from:", envPath);
const envContent = fs.readFileSync(envPath, 'utf-8');
const match = envContent.match(/GEMINI_API_KEY=(.*)/);

if (!match || !match[1]) {
    console.error("❌ GEMINI_API_KEY not found in .env.local");
    process.exit(1);
}

const API_KEY = match[1].trim();
console.log(`✅ API Key found: ${API_KEY.substring(0, 8)}...`);

async function verify() {
    console.log("Attempting to connect to Gemini API...");
    const genAI = new GoogleGenerativeAI(API_KEY);

    // Try gemini-1.5-flash first
    try {
        console.log("Testing model: gemini-1.5-flash...");
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
        const result = await model.generateContent("Hello! Are you operational?");
        const response = await result.response;
        console.log("✅ SUCCESS with gemini-1.5-flash!");
        console.log("Response:", response.text());
        return;
    } catch (error) {
        console.warn("⚠️ Failed with gemini-1.5-flash. Details:", error.message);
    }

    // Fallback to gemini-pro
    try {
        console.log("Testing model: gemini-pro...");
        const model = genAI.getGenerativeModel({ model: "gemini-pro" });
        const result = await model.generateContent("Hello! Are you operational?");
        const response = await result.response;
        console.log("✅ SUCCESS with gemini-pro!");
        console.log("Response:", response.text());
    } catch (error) {
        console.error("❌ FAILURE: Could not connect to Gemini with either model.");
        // console.error("Full Error:", JSON.stringify(error, null, 2));
        console.error("Error Message:", error.message);
        process.exit(1);
    }
}

verify();
