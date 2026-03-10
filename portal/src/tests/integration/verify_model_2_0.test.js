import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.resolve(__dirname, '../.env.local');
const envContent = fs.readFileSync(envPath, 'utf-8');
const match = envContent.match(/GEMINI_API_KEY=(.*)/);
const API_KEY = match[1].trim();

async function verify() {
    console.log("Attempting to connect with gemini-2.0-flash...");
    const genAI = new GoogleGenerativeAI(API_KEY);

    try {
        const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
        const result = await model.generateContent("Hello! Are you operational?");
        const response = await result.response;
        console.log("✅ SUCCESS with gemini-2.0-flash!");
        console.log("Response:", response.text());
    } catch (error) {
        console.error("❌ FAILURE with gemini-2.0-flash:", error.message);
    }
}

verify();
