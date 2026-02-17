import { json } from '@sveltejs/kit';
import { chat } from '$lib/server/chat';
import { rateLimiter } from '$lib/server/limiter';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, getClientAddress }) => {
    // 1. Rate Limiting
    const ip = getClientAddress();
    const limit = rateLimiter.check('chat', ip);

    if (!limit.allowed) {
        return json({ error: limit.reason }, { status: 429 });
    }

    try {
        const { messages, context } = await request.json();

        if (!messages || !Array.isArray(messages)) {
            return json({ error: "Invalid request format." }, { status: 400 });
        }

        // 2. Call Gemini
        const response = await chat(messages, context);

        return json({ text: response });
    } catch (err: any) {
        console.error("Detailed API Chat Error:", err);
        return json({
            error: err.message || "An unexpected error occurred."
        }, { status: 500 });
    }
};
