
import { json } from '@sveltejs/kit';
import { chat, getOfflineFallback } from '$lib/server/chat';
import { rateLimiter } from '$lib/server/limiter';
import { usageGuard } from '$lib/server/usage_guard';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, getClientAddress, locals }) => {
    // 0. Parse Body First
    let body;
    try {
        body = await request.json();
    } catch (e) {
        return json({ error: "Invalid JSON" }, { status: 400 });
    }
    const { messages, context } = body;

    if (!messages || !Array.isArray(messages)) {
        return json({ error: "Invalid request format." }, { status: 400 });
    }

    // 1. Rate Limiting
    const id = locals.sessionId || getClientAddress();
    const limit = rateLimiter.check('chat', id);

    if (!limit.allowed) {
        // Try Offline Fallback (RAG-lite)
        const lastMsg = messages[messages.length - 1]?.parts?.[0]?.text || "";
        const fallback = getOfflineFallback(lastMsg);

        if (fallback) {
            return json({ text: fallback });
        }

        return json({
            error: limit.reason,
            retryAfter: 60,
            friendly: "I'm processing too many requests. Please wait a moment.",
            usage: { totalTokenCount: 0 }
        }, { status: 429 });
    }

    try {
        // 2. Call Gemini
        const result = await chat(messages, context);

        // Forward Smart 429s from Gemini
        if ((result as any).error) {
            return json(result, { status: 429 });
        }

        return json(result);
    } catch (err: any) {
        console.error("Detailed API Chat Error:", err);

        // Check for usage guard error messages
        const errMsg = err.message || "";
        if (errMsg.includes("Daily safety limit reached") || errMsg.includes("safety circuits indicate I need to recharge")) {
            return json({
                error: errMsg
            }, { status: 429 });
        }

        return json({
            error: errMsg || "An unexpected error occurred."
        }, { status: 500 });
    }
};

export const GET: RequestHandler = async () => {
    // Simple endpoint to get current usage stats for UI initialization
    const stats = usageGuard.getStats();
    return json(stats);
};
