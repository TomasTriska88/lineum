
const { GoogleGenerativeAI } = require("@google/generative-ai");
const fs = require('fs');
const path = require('path');

// 1. Manually parse .env.local because dotenv might not be standard here
let apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
    try {
        const envPath = path.resolve(__dirname, '../.env.local');
        if (fs.existsSync(envPath)) {
            const content = fs.readFileSync(envPath, 'utf-8');
            // Basic parser handling quotes
            const match = content.match(/GEMINI_API_KEY=["']?(.*?)["']?$/m);
            if (match) apiKey = match[1].trim();
        }
    } catch (e) {
        console.error("Failed to read .env.local", e);
    }
}

if (!apiKey) {
    console.error("❌ No GEMINI_API_KEY found in .env.local");
    process.exit(1);
}

console.log("✅ GEMINI_API_KEY found (length: " + apiKey.length + ")");

async function test() {
    try {
        const genAI = new GoogleGenerativeAI(apiKey);
        // Test specifically the model used in chat.ts
        const modelName = "gemini-2.0-flash-001";
        const model = genAI.getGenerativeModel({ model: modelName });

        console.log(`Testing model: ${modelName}...`);
        const result = await model.generateContent("Respond with 'OK' if you can read this.");
        const response = await result.response;
        console.log("✅ Success! Response:", response.text());
    } catch (error) {
        console.error("❌ Error:", error.message);
        if (error.message.includes("404") || error.message.includes("not found")) {
            console.log("💡 The model 'gemini-2.0-flash-001' might not be enabled or valid for this API key.");
            console.log("   Try changing to 'gemini-1.5-flash' in src/lib/server/chat.ts");
        }
    }
}

test();
