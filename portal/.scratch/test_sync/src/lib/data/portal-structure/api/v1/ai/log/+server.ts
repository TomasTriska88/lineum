import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export async function POST({ request }) {
    try {
        const { sessionId, queryText, responseText } = await request.json();

        // This is a placeholder backend logic. 
        // Once Directus is deployed, this API route will relay the data securely directly to the DB.

        // Ensure logs directory exists at the project root
        const logDir = path.resolve('..', 'logs');
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }

        const logEntry = {
            timestamp: new Date().toISOString(),
            sessionId,
            query: queryText,
            response: responseText
        };

        const logFilePath = path.join(logDir, 'ai_interactions.jsonl');
        fs.appendFileSync(logFilePath, JSON.stringify(logEntry) + "\n");

        return json({ success: true });
    } catch (err) {
        console.error("Failed to log telemetry", err);
        return json({ success: false, error: 'Failed to log telemetry' }, { status: 500 });
    }
}
