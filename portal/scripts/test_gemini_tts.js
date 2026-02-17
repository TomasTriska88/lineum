import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.resolve(__dirname, '../.env.local');
const envContent = fs.readFileSync(envPath, 'utf-8');
const match = envContent.match(/GEMINI_API_KEY=(.*)/);
const API_KEY = match[1].trim();

async function testTTS() {
    console.log("Testing REST API for Gemini TTS...");
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=${API_KEY}`;

    // According to recent Gemini docs, generating audio might require specific payload structure.
    // Let's try requesting RESPONSE MODALITIES.
    const payload = {
        contents: [{ role: "user", parts: [{ text: "Mluvím česky. Jsem Lineum Explorer." }] }],
        generationConfig: {
            responseModalities: ["AUDIO"]
        }
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.candidates && data.candidates[0].content && data.candidates[0].content.parts[0].inlineData) {
            console.log("✅ SUCCESS! Audio data received.");
            console.log("MIME Type:", data.candidates[0].content.parts[0].inlineData.mimeType);
            const audioData = data.candidates[0].content.parts[0].inlineData.data;
            console.log("Data Length:", audioData.length);

            // Save to file to verify
            fs.writeFileSync('test_audio_base64.txt', audioData);
            console.log("Saved base64 audio to test_audio_base64.txt");
        } else {
            console.log("❌ Response received but no audio inlineData:");
            console.log(JSON.stringify(data, null, 2));
        }

    } catch (error) {
        console.error(`❌ Fetch Error:`, error.message);
    }
}

testTTS();
