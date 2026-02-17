async function verify() {
    console.log("Testing full stack integration at http://localhost:5173/api/chat...");
    try {
        const res = await fetch('http://localhost:5173/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: [{ role: 'user', parts: [{ text: 'System check. Respond with "Operational".' }] }]
            })
        });

        if (!res.ok) {
            console.error(`❌ HTTP Error: ${res.status} ${res.statusText}`);
            const text = await res.text();
            console.error("Response body:", text);
            process.exit(1);
        }

        const data = await res.json();
        console.log("✅ API Responded!");
        if (data.text) {
            console.log("Response text:", data.text);
            if (data.text.includes("Operational") || data.text.length > 0) {
                console.log("✅ Verification successful.");
            } else {
                console.warn("⚠️ Response received but unexpected content.");
            }
        } else if (data.error) {
            console.error("❌ API returned logical error:", data.error);
            process.exit(1);
        } else {
            console.error("❌ Unexpected JSON structure:", data);
            process.exit(1);
        }

    } catch (e) {
        console.error("❌ Connection failed:", e.message);
        process.exit(1);
    }
}

verify();
