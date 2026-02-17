
import fs from 'fs';
import path from 'path';

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function chat(message, context = 'test') {
    const res = await fetch("http://localhost:5173/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            // Mock a session cookie if needed, but fetch usually handles cookies if jar is used.
            // Node fetch doesn't persist cookies by default across requests unless using a cookie jar.
            // For this test, relies on IP or if I can extract set-cookie.
        },
        body: JSON.stringify({
            messages: [{ role: 'user', parts: [{ text: message }] }],
            context
        })
    });

    const data = await res.json();
    return { status: res.status, data, headers: res.headers };
}

// Simple cookie jar
let cookie = "";

async function chatWithCookie(message) {
    const headers = { "Content-Type": "application/json" };
    if (cookie) headers["Cookie"] = cookie;

    const res = await fetch("http://localhost:5175/api/chat", { // Port 5175 from dev update
        method: "POST",
        headers,
        body: JSON.stringify({
            messages: [{ role: 'user', parts: [{ text: message }] }],
            context: 'test'
        })
    });

    // Capture cookie
    const setCookie = res.headers.get('set-cookie');
    if (setCookie) {
        cookie = setCookie.split(';')[0];
    }

    const data = await res.json();
    console.log(`[${res.status}] Msg: "${message.substring(0, 20)}..." -> Reply:`, data.text ? data.text.substring(0, 50) + "..." : (data.error || "Unknown"));
    if (data.retryAfter) console.log(`   -> Queue Challenge: Wait ${data.retryAfter}s`);
    return { status: res.status, data };
}

async function run() {
    console.log("--- Starting Verification (Port 5175) ---");

    // 1. Success (Consumes Quota)
    console.log("\n1. Sending 'Hello' (Should be 200 OK)");
    await chatWithCookie("Hello");

    // 2. Offline Fallback (Rate Limited but found answer)
    console.log("\n2. Sending 'What is the core?' (Should be 200 OK via Offline Fallback)");
    await chatWithCookie("What is the core?");

    // 3. Queue Trigger (Rate Limited and NO answer)
    console.log("\n3. Sending 'Random nonsense 123' (Should be 429 Queue)");
    await chatWithCookie("Random nonsense 123");

    // 4. Czech Query (Offline Optimization Check)
    console.log("\n4. Sending Czech Query 'úplně laicky mi vysvětli zkráceně celý projekt' (Should be 200 OK via Offline Fallback)");
    await chatWithCookie("úplně laicky mi vysvětli zkráceně celý projekt");
}

run();
