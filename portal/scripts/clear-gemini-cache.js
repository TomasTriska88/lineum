import { GoogleAICacheManager } from '@google/generative-ai/server';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

async function clearCache() {
    if (!process.env.GEMINI_API_KEY) {
        console.error("Error: GEMINI_API_KEY not found in environment.");
        process.exit(1);
    }

    const cacheManager = new GoogleAICacheManager(process.env.GEMINI_API_KEY);

    try {
        console.log("Listing all caches...");
        const result = await cacheManager.list();

        if (!result.cachedContents || result.cachedContents.length === 0) {
            console.log("No caches found.");
            return;
        }

        console.log(`Found ${result.cachedContents.length} caches. Deleting...`);

        for (const c of result.cachedContents) {
            console.log(`Deleting ${c.name} (${c.displayName || 'unnamed'})...`);
            await cacheManager.delete(c.name);
        }

        console.log("All caches cleared successfully.");
    } catch (e) {
        console.error("Error clearing caches:", e);
    }
}

clearCache();
