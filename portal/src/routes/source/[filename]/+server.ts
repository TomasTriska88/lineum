import { error } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export async function GET({ params }) {
    const { filename } = params;

    // Security check: prevent directory traversal
    if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
        throw error(400, 'Invalid filename');
    }

    // Path in monorepo: we are in portal/src/routes/source/[filename]/+server.ts
    // Project root (portal/) is usually current working directory
    const filePath = path.join(process.cwd(), '..', 'source', filename);

    if (!fs.existsSync(filePath)) {
        console.error(`Asset not found: ${filePath}`);
        throw error(404, 'Asset not found');
    }

    const fileBuffer = fs.readFileSync(filePath);
    const ext = path.extname(filename).toLowerCase();

    const contentTypes: Record<string, string> = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp'
    };

    return new Response(fileBuffer, {
        headers: {
            'Content-Type': contentTypes[ext] || 'application/octet-stream',
            'Cache-Control': 'public, max-age=3600'
        }
    });
}
