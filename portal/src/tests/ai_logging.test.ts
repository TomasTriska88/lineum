import { describe, it, expect } from 'vitest';
import { POST } from '../routes/api/v1/ai/log/+server';
import fs from 'fs';
import path from 'path';

describe('AI Logging Endpoint Completeness', () => {
    it('Should successfully write a 10,000 character conversation without truncation', async () => {
        const largeString = 'A'.repeat(10000);

        const mockRequest = new Request('http://127.0.0.1:5173/api/v1/ai/log', {
            method: 'POST',
            body: JSON.stringify({
                sessionId: 'test-session-huge',
                queryText: 'Tell me a long story',
                responseText: largeString
            })
        });

        const response = await POST({ request: mockRequest } as any);
        const data = await response.json();

        expect(response.status).toBe(200);
        expect(data.success).toBe(true);

        // Verify it was actually written to the file
        const logPath = path.resolve('..', 'logs', 'ai_interactions.jsonl');

        // Wait briefly for file system
        await new Promise(resolve => setTimeout(resolve, 100));

        const content = fs.readFileSync(logPath, 'utf-8');
        const lines = content.trim().split('\n');
        const lastLog = JSON.parse(lines[lines.length - 1]);

        expect(lastLog.sessionId).toBe('test-session-huge');
        expect(lastLog.response.length).toBe(10000);
        expect(lastLog.response).toBe(largeString);
    });
});
