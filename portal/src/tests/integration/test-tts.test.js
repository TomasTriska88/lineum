
import fs from 'fs';

async function testTTS() {
    const response = await fetch("http://localhost:5173/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "Hello, this is a test of the new voice model." })
    });

    if (response.ok) {
        const buffer = await response.arrayBuffer();
        fs.writeFileSync("test_audio.wav", Buffer.from(buffer));
        console.log("Success! Audio saved to test_audio.wav");
    } else {
        console.error("Error:", response.status, await response.text());
    }
}

testTTS();
