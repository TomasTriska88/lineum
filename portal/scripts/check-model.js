import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

async function listModels() {
    if (!process.env.GEMINI_API_KEY) {
        console.error("Error: GEMINI_API_KEY not found in environment.");
        process.exit(1);
    }

    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

    try {
        const candidates = [
            "gemini-3.0-pro-exp",
            "gemini-3.0-pro",
            "gemini-2.0-pro-exp",
            "gemini-2.0-flash-exp", // "Gemini 2 Flash Exp" in screenshot
            "gemini-2.0-flash",     // "Gemini 2 Flash" in screenshot
            "gemini-1.5-pro",       // "Gemini 2.5 Pro" might be a rebrand or latest 1.5? Unlikely.
            "gemini-exp-1206",      // Common experimental ID
        ];

        console.log("Checking model availability...");

        for (const modelName of candidates) {
            try {
                process.stdout.write(`Testing ${modelName}... `);
                const model = genAI.getGenerativeModel({ model: modelName });
                const result = await model.generateContent("Hi");
                await result.response;
                console.log("✅ OK");
            } catch (e) {
                console.log(`❌ FAILED`);
                console.log(`   Error: ${e.message}`);
            }
        }

    } catch (e) {
        console.error("Error accessing model:", e.message);
        if (e.message.includes("404") || e.message.includes("not found")) {
            console.error("Model appears to be unavailable.");
        }
    }
}

listModels();
