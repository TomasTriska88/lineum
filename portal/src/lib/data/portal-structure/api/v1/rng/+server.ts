import { json } from '@sveltejs/kit';

// Simple in-memory rate limiting placeholder (until Directus/Redis is integrated)
const ipRequestCounts = new Map<string, number[]>();
const RATE_LIMIT_WINDOW_MS = 60000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 10;

export async function POST({ request, getClientAddress }) {
    try {
        const clientIp = getClientAddress();
        const now = Date.now();

        // 1. Rate Limiting Logic (Gatekeeper Placeholder)
        if (!ipRequestCounts.has(clientIp)) {
            ipRequestCounts.set(clientIp, []);
        }

        let timestamps = ipRequestCounts.get(clientIp) || [];
        timestamps = timestamps.filter(t => now - t < RATE_LIMIT_WINDOW_MS);

        if (timestamps.length >= MAX_REQUESTS_PER_WINDOW) {
            return json(
                { success: false, error: 'Too Many Requests. Rate limit exceeded.' },
                { status: 429 }
            );
        }

        timestamps.push(now);
        ipRequestCounts.set(clientIp, timestamps);

        // 2. Parse incoming params
        const body = await request.json().catch(() => ({}));

        // 3. Forward to the Python FastApi Worker
        const WORKER_URL = 'http://127.0.0.1:8000/api/v1/ai/true-rng';

        const workerResponse = await fetch(WORKER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Future: 'Authorization': `Bearer ${process.env.INTERNAL_API_KEY}`
            },
            body: JSON.stringify({
                resolution: body.resolution || 64,
                pump_cycles: body.pump_cycles || 1500
            })
        });

        if (!workerResponse.ok) {
            const errorData = await workerResponse.text();
            console.error("Python Worker Error:", workerResponse.status, errorData);
            return json(
                { success: false, error: 'Upstream compute provider failed.' },
                { status: 502 }
            );
        }

        const data = await workerResponse.json();

        // 4. Return the Hardware RNG payload to the frontend
        return json(data);

    } catch (err: any) {
        console.error("RNG Proxy Error:", err);
        return json(
            { success: false, error: 'Internal Server Error forwarding to RNG worker.' },
            { status: 500 }
        );
    }
}
