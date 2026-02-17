import { json } from '@sveltejs/kit';
import * as env from "$env/static/private";
import { rateLimiter } from '$lib/server/limiter';
import type { RequestHandler } from './$types';

const GEMINI_API_KEY = (env as any).GEMINI_API_KEY;

export const POST: RequestHandler = async ({ request, getClientAddress, locals }) => {
    // 1. Rate Limiting (Stricter for TTS)
    const id = locals.sessionId || getClientAddress();
    const limit = rateLimiter.check('tts', id);

    if (!limit.allowed) {
        return json({ error: limit.reason }, { status: 429 });
    }

    // 2. Validate Input
    let text: string;
    let voice: string = "Aoede";

    try {
        const body = await request.json();
        text = body.text;
        if (body.voice) voice = body.voice;
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
    // We use direct REST because the SDK support for Audio Modality is experimental/undocumented
    // Using Pro because Flash TTS has strict 10 RPD limit. Pro has 1.5K RPD.
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
                    }
                }
            }
        };

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


        // Extract Audio
        if (data.candidates?.[0]?.content?.parts?.[0]?.inlineData) {
            const inlineData = data.candidates[0].content.parts[0].inlineData;
            const base64Audio = inlineData.data;
            const rawMimeType = inlineData.mimeType || 'audio/wav';

            // Convert base64 to binary buffer
            let audioBuffer = Buffer.from(base64Audio, 'base64');
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
