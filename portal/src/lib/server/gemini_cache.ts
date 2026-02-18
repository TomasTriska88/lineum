
import { GoogleAICacheManager, GoogleAIFileManager } from '@google/generative-ai/server';
import { GEMINI_API_KEY } from '$env/static/private';

// Cache configuration
const CACHE_DISPLAY_NAME = 'lineum-core-whitepapers-v1';
const CACHE_TTL_SECONDS = 3600; // 1 hour (Free tier limit usually)
const MODEL_NAME = 'models/gemini-1.5-flash-001'; // Or 2.0 if available for caching

// Singleton instance
let cacheManager: GoogleAICacheManager | null = null;
let fileManager: GoogleAIFileManager | null = null;

function getCacheManager() {
    if (!cacheManager) {
        if (!GEMINI_API_KEY) throw new Error("GEMINI_API_KEY not found");
        cacheManager = new GoogleAICacheManager(GEMINI_API_KEY);
    }
    return cacheManager;
}

// In-memory cache of the active cache name to avoid API calls on every request
// keys: displayName -> { name: string, expires: number }
const localRefCache: Record<string, { name: string, expires: number }> = {};

/**
 * Gets a valid cache name (resource ID) for the given content.
 * If a valid cache exists, returns it.
 * If not, creates a new one.
 */
export async function getOrUpdateCache(content: string, mimeType = 'text/plain'): Promise<string> {
    const mgr = getCacheManager();

    // 1. Check local ref first (fast path)
    const now = Date.now();
    if (localRefCache[CACHE_DISPLAY_NAME]) {
        if (localRefCache[CACHE_DISPLAY_NAME].expires > now + 300000) { // 5 mins safety buffer
            return localRefCache[CACHE_DISPLAY_NAME].name;
        } else {
            // Expired or close to expiry, clear local ref
            delete localRefCache[CACHE_DISPLAY_NAME];
        }
    }

    try {
        // 2. List existing caches to find ours
        // Note: list() is paginated but we assume we don't have thousands
        const listResult = await mgr.list();

        let existingCache = null;

        // Find the most recent valid cache with our display name
        if (listResult.cachedContents) {
            for (const c of listResult.cachedContents) {
                if (c.displayName === CACHE_DISPLAY_NAME) {
                    // Check expiry
                    if (c.name && c.expireTime) {
                        const expiryTime = new Date(c.expireTime).getTime();
                        if (expiryTime > now + 300000) {
                            existingCache = c;
                            break;
                        } else {
                            // Cleanup expired/old caches with same name
                            console.log(`[GeminiCache] Deleting expired cache: ${c.name}`);
                            try { await mgr.delete(c.name); } catch (e) { }
                        }
                    }
                }
            }
        }

        if (existingCache && existingCache.name && existingCache.expireTime) {
            console.log(`[GeminiCache] Found active cache: ${existingCache.name}`);
            localRefCache[CACHE_DISPLAY_NAME] = {
                name: existingCache.name,
                expires: new Date(existingCache.expireTime).getTime()
            };
            return existingCache.name;
        }

        // 3. Create new cache
        console.log(`[GeminiCache] Creating new cache '${CACHE_DISPLAY_NAME}'...`);
        const newCache = await mgr.create({
            model: MODEL_NAME,
            displayName: CACHE_DISPLAY_NAME,
            ttlSeconds: CACHE_TTL_SECONDS,
            contents: [
                {
                    role: 'user',
                    parts: [{ text: content }]
                }
            ]
        });

        if (!newCache.name || !newCache.expireTime) {
            throw new Error("Cache created but missing name or expiry");
        }

        console.log(`[GeminiCache] Created: ${newCache.name}`);
        localRefCache[CACHE_DISPLAY_NAME] = {
            name: newCache.name,
            expires: new Date(newCache.expireTime).getTime()
        };

        return newCache.name;

    } catch (error) {
        console.error("[GeminiCache] Error managing cache:", error);
        throw error;
    }
}
