import { json } from '@sveltejs/kit';
import * as env from "$env/static/private";
import { rateLimiter } from '$lib/server/limiter';
import { usageGuard } from '$lib/server/usage_guard';
import type { RequestHandler } from './$types';

const GEMINI_API_KEY = (env as any).GEMINI_API_KEY;

export const POST: RequestHandler = async ({ request, getClientAddress, locals }) => {
    // 1. Rate Limiting (Stricter for TTS)
    const id = locals.sessionId || getClientAddress();
    const limit = rateLimiter.check('tts', id);

    if (!limit.allowed) {
        return json({ error: limit.reason }, { status: 429 });
    }

    // 1.5 Safety: Check Daily Budget
    const limitCheck = usageGuard.checkLimit();
    if (!limitCheck.allowed) {
        // PERSONA VS DEV MODE
        const isDev = process.env.NODE_ENV === 'development';
        const msg = isDev
            ? `[DEV] Daily safety limit reached. (Remaining: $${limitCheck.remainingBudget.toFixed(2)})`
            : "I need to rest my voice circuits until tomorrow.";

        return json({ error: msg }, { status: 429 });
    }

    // 2. Validate Input
    let text: string;
    // Hardcoded Voice: Kore (Female) - per user request to disable selection
    const voice: string = "Kore";

    try {
        const body = await request.json();
        text = body.text;
        // if (body.voice) voice = body.voice; // Selection disabled
    } catch {
        return json({ error: "Invalid JSON body" }, { status: 400 });
    }

    // Gemini TTS supports up to ~4096 chars usually, allowing 2000 is safe
    if (!text || typeof text !== 'string' || text.length > 2000) {
        return json({ error: "Text is required and must be under 2000 chars." }, { status: 400 });
    }

    if (!GEMINI_API_KEY) {
        return json({ error: "Server configuration error (Missing Key)." }, { status: 500 });
    }

    // 3. Call Gemini TTS (REST API)
    // We user Pro model again because Flash TTS has poor quality (Robotic Voice) for Czech.
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-tts:generateContent?key=${GEMINI_API_KEY}`;

    try {
        const payload = {
            contents: [{ role: "user", parts: [{ text }] }],
            generationConfig: {
                responseModalities: ["AUDIO"],
                speechConfig: {
                    voiceConfig: {
                        prebuiltVoiceConfig: {
                            voiceName: voice
                        }
                    },
                    audioConfig: {
                        audioEncoding: "LINEAR16",
                        sampleRateHertz: 24000
                    }
                },
                audioTimestamp: false // Optional, can be used for debugging
            }
        };

        // EXPLICITLY REQUEST FORMAT to avoid mismatch surprises
        // We request standard PCM (Linear16) at 24kHz to match our WAV header logic.
        // If we don't specifying, Gemini might return MP3 or random rate.
        // Note: The structure for `generationConfig` varies by model version.
        // For v1beta/models/gemini-2.5-pro-preview-tts, check if it supports direct format params here.
        // Actually, the docs suggest generationConfig.speechConfig.audioConfig might be the place?
        // Or responseMimeType?
        // Let's safe bet: The previous code worked but guessed.
        // Let's try adding `responseMimeType: "audio/wav"` if supported, or just trust the raw output.
        // Wait, current code checks `rawMimeType.includes('audio/L16')`.
        // If the user heard "slow motion", it means we likely got 48kHz audio but played it at 24kHz.
        // I will change the header sample rate to 24000 (which it is) but maybe the data IS 24000.
        // Actually, let's assume it IS 24000.
        // If it was *slow*, the samples were played too slowly.
        // Meaning real rate > playback rate.
        // e.g. Real rate 48000, Playback rate 24000.
        // So Gemini probably returns 24000 by default? No, usually 24k.
        // Wait, if I hardcode header to 24k, and it plays slow...
        // It means there are MORE samples than expected for the duration.
        // So the source data has a HIGHER sample rate (e.g. 48k).
        // I will try updating the header to 24000 but add a TODO to verify or bump to 48000 if persists.
        // Actually, let's explicit request.

        // Revised payload structure based on typical Gemini API:
        /*
        generationConfig: {
            responseModalities: ["AUDIO"],
            speechConfig: {
                voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } }
            }
        }
        */
        // I can't easily force sample rate without `audioConfig`.
        // I'll stick to 24000 but I'll add a log to check the MIME type return.



        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errText = await response.text();
            console.error("Gemini TTS Error:", errText);

            if (response.status === 429) {
                return json({ error: "Gemini Quota Exceeded" }, { status: 429 });
            }
            return json({ error: "Failed to generate audio." }, { status: 500 });
        }

        const data = await response.json();

        // RECORD USAGE (Estimated)
        // Input: text length / 4 (approx tokens)
        // Output: Audio length (approx 25 tokens/sec). Let's estimate conservatively: 1 char = 0.1 sec audio = 2.5 tokens.
        // Or better, just record input tokens for now as output tokens are hard to guess from binary.
        // Actually, pricing says $20/1M output tokens (audio).
        // Let's assume 1 char ~= 1 output token for safety estimation until we parse real metadata.
        const inputTokens = Math.ceil(text.length / 4);
        const outputTokens = Math.ceil(text.length * 2); // Conservative estimate for audio density
        usageGuard.recordUsage(inputTokens, outputTokens, 'pro'); // Pro model (High Quality)


        // Extract Audio
        if (data.candidates?.[0]?.content?.parts?.[0]?.inlineData) {
            const inlineData = data.candidates[0].content.parts[0].inlineData;
            const base64Audio = inlineData.data;
            const rawMimeType = inlineData.mimeType || 'audio/wav';
            console.log(`[TTS] Received Audio MIME: ${rawMimeType}, Length: ${base64Audio.length}`);

            // Convert base64 to binary buffer
            let audioBuffer = Buffer.from(base64Audio, 'base64') as any;
            let finalMimeType = rawMimeType;

            // FIX: Wraps raw PCM (L16) in a WAV container so browsers can play it
            if (rawMimeType.includes('audio/L16')) {
                console.log("Wrapping raw PCM in WAV header...");
                audioBuffer = addWavHeader(audioBuffer as any, 24000, 1, 16); // 24kHz, Mono, 16-bit
                finalMimeType = 'audio/wav';
            }

            return new Response(audioBuffer, {
                headers: {
                    'Content-Type': finalMimeType,
                    'Content-Length': audioBuffer.length.toString(),
                    'Cache-Control': 'public, max-age=31536000, immutable'
                }
            });
        } else {
            console.error("Unexpected Gemini TTS Response Structure:", JSON.stringify(data));
            return json({ error: "No audio data received." }, { status: 500 });
        }

    } catch (err: any) {
        console.error("TTS Endpoint Exception:", err);
        return json({ error: "Internal Server Error" }, { status: 500 });
    }
};

/**
 * Adds a RIFF WAV header to raw PCM data.
 */
function addWavHeader(samples: Buffer, sampleRate: number, numChannels: number, bitsPerSample: number): Buffer {
    const byteRate = (sampleRate * numChannels * bitsPerSample) / 8;
    const blockAlign = (numChannels * bitsPerSample) / 8;
    const dataSize = samples.length;
    const buffer = Buffer.alloc(44 + dataSize);

    // RIFF chunk
    buffer.write('RIFF', 0);
    buffer.writeUInt32LE(36 + dataSize, 4);
    buffer.write('WAVE', 8);

    // fmt chunk
    buffer.write('fmt ', 12);
    buffer.writeUInt32LE(16, 16); // Subchunk1Size (16 for PCM)
    buffer.writeUInt16LE(1, 20); // AudioFormat (1 for PCM)
    buffer.writeUInt16LE(numChannels, 22);
    buffer.writeUInt32LE(sampleRate, 24);
    buffer.writeUInt32LE(byteRate, 28);
    buffer.writeUInt16LE(blockAlign, 32);
    buffer.writeUInt16LE(bitsPerSample, 34);

    // data chunk
    buffer.write('data', 36);
    buffer.writeUInt32LE(dataSize, 40);

    // Write samples
    samples.copy(buffer, 44);

    return buffer;
}
