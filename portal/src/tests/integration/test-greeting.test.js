
import fetch from 'node-fetch';

async function getGreeting(i) {
    try {
        const response = await fetch('http://localhost:5173/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: [{ role: 'user', parts: [{ text: "Initialize session. Introduce yourself efficiently to a new user. 1-2 sentences max. Use your persona." }] }],
                context: '/lab/simulation'
            })
        });
        const data = await response.json();
        if (data.error) {
            console.log(`[${i + 1}] ERROR (${response.status}): ${data.error}\n`);
        } else {
            console.log(`[${i + 1}] ${data.text}\n`);
        }
    } catch (error) {
        console.error(`[${i + 1}] Error:`, error.message);
    }
}

async function run() {
    console.log("Generating 10 Lina Greetings...\n");
    for (let i = 0; i < 10; i++) {
        await getGreeting(i);
    }
}

run();
