
import { GoogleAICacheManager, GoogleAIFileManager } from '@google/generative-ai/server';
import { GEMINI_API_KEY } from '$env/static/private';
import { createHash } from 'crypto';

// Cache configuration
const CACHE_BASE_NAME = 'lineum-core-v1';
const CACHE_TTL_SECONDS = 3600; // 1 hour (Free tier limit usually)
const MODEL_NAME = 'models/gemini-1.5-flash-002'; // Stable 1.5 works with caching on Free Tier

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
 * Automatically invalidates if content changes (via hash in displayName).
 */
export async function getOrUpdateCache(content: string, mimeType = 'text/plain'): Promise<string> {
    const mgr = getCacheManager();

    // Generate hash of content to detect changes
    const hash = createHash('sha256').update(content).digest('hex').substring(0, 8);
    const currentDisplayName = `${CACHE_BASE_NAME}-${hash}`;

    // 1. Check local ref first (fast path)
    const now = Date.now();
    if (localRefCache[currentDisplayName]) {
        if (localRefCache[currentDisplayName].expires > now + 300000) { // 5 mins safety buffer
            return localRefCache[currentDisplayName].name;
        } else {
            // Expired or close to expiry, clear local ref
            delete localRefCache[currentDisplayName];
        }
    }

    try {
        // 2. List existing caches to find ours
        // Note: list() is paginated but we assume we don't have thousands
        const listResult = await mgr.list();

        let existingCache = null;

        if (listResult.cachedContents) {
            for (const c of listResult.cachedContents) {
                if (c.displayName === currentDisplayName) {
                    // Start strict: Matches content hash AND not expired
                    if (c.name && c.expireTime) {
                        const expiryTime = new Date(c.expireTime).getTime();
                        if (expiryTime > now + 300000) {
                            existingCache = c;
                            break;
                        } else {
                            // Expired exact match
                            console.log(`[GeminiCache] Deleting expired: ${c.name}`);
                            try { await mgr.delete(c.name); } catch (e) { }
                        }
                    }
                } else if (c.displayName && c.displayName.startsWith(CACHE_BASE_NAME)) {
                    // Old version of our cache (different hash) -> Cleanup
                    // We only clean up if we are sure it's ours and old
                    console.log(`[GeminiCache] Cleanup old version: ${c.displayName}`);
                    try { await mgr.delete(c.name); } catch (e) { }
                }
            }
        }

        if (existingCache && existingCache.name && existingCache.expireTime) {
            console.log(`[GeminiCache] Found active cache: ${existingCache.name} (${currentDisplayName})`);
            localRefCache[currentDisplayName] = {
                name: existingCache.name,
                expires: new Date(existingCache.expireTime).getTime()
            };
            return existingCache.name;
        }

        // 3. Create new cache
        console.log(`[GeminiCache] Creating new cache '${currentDisplayName}'...`);
        const newCache = await mgr.create({
            model: MODEL_NAME,
            displayName: currentDisplayName,
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
        localRefCache[currentDisplayName] = {
            name: newCache.name,
            expires: new Date(newCache.expireTime).getTime()
        };

        return newCache.name;

    } catch (error) {
        console.error("[GeminiCache] Error managing cache:", error);
        throw error;
    }
}

export function resetLocalRefCache() {
    for (const key in localRefCache) {
        delete localRefCache[key];
    }
}
