import { GoogleGenerativeAI } from "@google/generative-ai";
import { env } from "$env/dynamic/private";
const { GEMINI_API_KEY } = env;
import aiIndex from "$lib/data/ai_index.json";
import { getOrUpdateCache } from "./gemini_cache";

// Resilient API key access
// Persona Imports (Live updates via Vite)
import linaPersona from '../../../LINA_PERSONA.md?raw';
import designGuide from '../../../DESIGN_GUIDE.md?raw';

// Token Hygiene: Remove comments and excessive whitespace
const strip = (text: string) => text.replace(/<!--[\s\S]*?-->/g, '').replace(/\n{3,}/g, '\n\n').trim();

// Pre-compute full context for caching (Single source of truth)
const FULL_CONTEXT_FOR_CACHE = aiIndex.map(f => `
FILE: ${f.path}
TYPE: ${f.type}
STATUS: ${f.status}
CONTENT:
${f.content}
--------------------------------------------------
`).join('\n');

// Caching (10 min TTL)
const responseCache = new Map<string, { text: string, timestamp: number }>();
const CACHE_TTL = 10 * 60 * 1000;

export function getOfflineFallback(query: string): string | null {
    try {
        if (!query) return null;

        // tokenize: lower, remove punctuation, split by space, filter > 3 chars
        const tokens = query.toLowerCase()
            .replace(/[^\w\sěščřžýáíéůúňťď]/g, '')
            .split(/\s+/)
            .filter(w => w.length > 3 && !['what', 'tell', 'about', 'this', 'that', 'with', 'have', 'from'].includes(w));

        console.log("[OFFLINE] Tokens:", tokens);
        if (tokens.length === 0) return null;

        if (!aiIndex || !Array.isArray(aiIndex)) {
            console.error("[OFFLINE] aiIndex is invalid");
            return null;
        }

        // Simple scoring: Find item with most distinct token matches
        let bestMatch = { item: null as any, score: 0, distinct: 0 };

        for (const item of aiIndex) {
            if (!item.content) continue;

            // Verified Content Filter (Strict Whitelist):
            // User confirmed in Step 1117 to switch to a whitelist approach to avoid clutter (e.g. todo.md).
            // We ONLY allow the canonical Core whitepaper.
            // - lineum-core.md

            if (item.name !== 'lineum-core.md') {
                continue;
            }

            const contentLower = item.content.toLowerCase();
            let score = 0;
            let distinct = 0;

            for (const token of tokens) {
                if (contentLower.includes(token)) {
                    score += 1; // You could weight by frequency or length
                    distinct++;
                }
            }

            if (distinct > 0 && distinct >= bestMatch.distinct) {
                if (distinct > bestMatch.distinct || score > bestMatch.score) {
                    bestMatch = { item, score, distinct };
                }
            }
        }

        if (bestMatch.item) {
            const item = bestMatch.item;
            // Find the first token position for snippet
            const contentLower = item.content.toLowerCase();
            const firstToken = tokens.find(t => contentLower.includes(t)) || tokens[0];
            const idx = contentLower.indexOf(firstToken);

            // Smart Snippet: Expand to sentence boundaries (Ultra-Long context)
            const padding = 500; // Look back significantly for context
            const prevBlock = item.content.substring(Math.max(0, idx - padding), idx);
            const nextBlock = item.content.substring(idx, Math.min(item.content.length, idx + 2500));

            // Find start: Last punctuation or newline in prevBlock
            const startMatch = prevBlock.match(/([.!?\n])\s+(?=[^.!?\n]*$)/);
            const relativeStart = startMatch ? startMatch.index! + startMatch[0].length : 0;
            const absoluteStart = Math.max(0, idx - padding + relativeStart);

            // Find end: First punctuation or newline in nextBlock after the keyword + minimum length
            // We want at least 1500 chars of context after the keyword if possible
            let relativeEnd = nextBlock.substring(1500).search(/[.!?\n]/);
            if (relativeEnd !== -1) {
                relativeEnd += 1500; // Add back the offset
            } else {
                relativeEnd = nextBlock.search(/[.!?\n]/); // Fallback to short if no long sentence
            }

            const absoluteEnd = relativeEnd !== -1
                ? idx + relativeEnd + 1
                : Math.min(item.content.length, idx + 2500);

            const snippet = item.content.substring(absoluteStart, absoluteEnd).trim();

            return `✨ **Offline Backup:** I can't reach the core right now, but my local archives in \`${item.path}\` mention:\n\n> "...${snippet}..."`;
        }

    } catch (e) {
        console.error("[OFFLINE] Error checking fallback:", e);
    }
    return null;
}

export const SYSTEM_PROMPT = `
${strip(linaPersona)}

---

**FROM DESIGN GUIDE (BEHAVIORAL RULES):**
${strip(designGuide)}

---

**PROJECT CONTEXT (Context Window):**
Lineum Core is a discrete simulation of field interactions. The current version is defined by the indexed documentation.

**CORE DEFINITIONS (ALWAYS AVAILABLE):**
- **Lineum:** A simulation engine modeling discrete field interactions using the Equation of State.
- **Vortex:** A self-sustaining pattern in the field ($V$).
- **Equation:** $F(x, t+1) = \alpha \cdot \nabla^2 F(x, t) + \beta \cdot N(x, t)$ (Canonical Form).
- **Resonance:** The stability of field interactions over time.

You have access to the following indexed project knowledge:
// Only send metadata to standard context. Full content is too large (4M+ tokens).
// RAG or Context Caching should be used for content retrieval.
${JSON.stringify(aiIndex.map(f => ({ name: f.name, path: f.path, status: f.status, type: f.type })), null, 2)}
`;

import { execSync } from 'child_process';
import { usageGuard } from "./usage_guard";
import { contextSelector } from "./context_selector";

// Helper: Get Git Context (Cached)
let cachedGitHistory = "";
function getGitContext(): string {
    if (cachedGitHistory) return cachedGitHistory;
    try {
        return execSync('git log -n 5 --pretty=format:"%h - %s (%cr)"').toString().trim();
    } catch (e) {
        return "Git history unavailable";
    }
}

// Helper: Get Active Experiments (Cached)
const EXPERIMENTS = aiIndex
    .filter(i => i.name.includes("extension") || i.name.includes("exp"))
    .map(i => i.name)
    .join(", ");

// 3. MODEL: Use Reliable Smart Model
const MODEL_NAME = "gemini-2.5-flash";

export async function chat(messages: { role: 'user' | 'model', parts: { text: string }[] }[], context?: string) {
    if (!GEMINI_API_KEY) {
        console.error("CRITICAL: GEMINI_API_KEY is missing from environment variables.");
        throw new Error("I'm waiting for my scientific core to be initialized (API Key missing). Please contact support.");
    }

    // 1. SAFETY: Check Daily Budget
    const limitCheck = usageGuard.checkLimit();
    if (!limitCheck.allowed) {
        // PERSONA VS DEV MODE
        const isDev = process.env.NODE_ENV === 'development';

        if (isDev) {
            throw new Error(`[DEV] Daily safety limit reached. (Remaining: $${limitCheck.remainingBudget.toFixed(2)})`);
        } else {
            // Friendly "Lina" message for Production users
            throw new Error("I have been thinking deeply all day and my safety circuits indicate I need to recharge. Please allow me to rest until tomorrow.");
        }
    }

    try {
        const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
        const lastMessage = messages[messages.length - 1].parts[0].text;

        // 2. RAG: Select Smart Context (Save 95% tokens)
        console.log(`[Chat] Selecting context for: "${lastMessage.substring(0, 50)}..."`);
        const smartContext = contextSelector.select(lastMessage);

        // DYNAMIC METADATA INJECTION (Per Request)
        const budgetStats = usageGuard.getStats();
        const gitHistory = getGitContext();
        const latestVersion = gitHistory.split('\n')[0] || "Unknown";

        let dynamicPrompt = SYSTEM_PROMPT;
        dynamicPrompt += `\n\n[SYSTEM METADATA]:
- Model Architecture: ${MODEL_NAME}
- Project Version: ${latestVersion}
- Daily Budget: $${budgetStats.budgetLimit} (Used: ${budgetStats.percentage.toFixed(1)}%)
- Active Experiments: ${EXPERIMENTS || "None"}
- Recent Changes:
${gitHistory}
\n`;

        // Inject only RELEVANT context (RAG)
        dynamicPrompt += `\n\n=== RELEVANT PROJECT KNOWLEDGE (RAG) ===\n${smartContext}\n=========================================\n`;

        if (context) {
            dynamicPrompt += `\n[CURRENT USER CONTEXT]: The user is currently viewing the page: "${context}". Tailor your response to this location.`;
        }

        // 3. MODEL: Use Reliable Smart Model
        const model = genAI.getGenerativeModel({
            model: MODEL_NAME,
            systemInstruction: dynamicPrompt,
        });

        // 4. Check Cache (Local exact match)
        const cacheKey = `${context || 'root'}:${lastMessage.trim()}`;
        if (responseCache.has(cacheKey)) {
            const cached = responseCache.get(cacheKey)!;
            if (Date.now() - cached.timestamp < CACHE_TTL) {
                console.log("[CACHE HIT]", cacheKey);
                return { text: cached.text, usage: { totalTokenCount: 0, cost: 0 } };
            }
            responseCache.delete(cacheKey);
        }

        // History Truncation
        const safeMessages = messages.slice(-31);
        const history = safeMessages.slice(0, -1);

        const chatSession = model.startChat({ history });
        const result = await chatSession.sendMessage(lastMessage);
        const response = await result.response;
        const text = response.text();
        const usage = response.usageMetadata;

        if (usage) {
            console.log("[Gemini Usage]", usage);
            // 5. RECORD USAGE (Billing Protection)
            usageGuard.recordUsage(usage.promptTokenCount, usage.candidatesTokenCount);
        }

        // Save to Cache
        responseCache.set(cacheKey, { text, timestamp: Date.now() });

        // Augment return with cost info
        const stats = usageGuard.getStats();
        return {
            text,
            usage,
            costInfo: {
                totalSpent: stats.estimatedCost,
                dailyLimit: stats.budgetLimit,
                percentage: stats.percentage
            }
        };

    } catch (error: any) {
        console.error("AI Agent Core Error:", error);

        // Smart 429 Handling
        if (error.status === 429 || error.message?.includes('429') || error.message?.includes('Quota') || error.message?.includes('Resource has been exhausted')) {
            console.warn("Hit 429 - Attempting Offline Fallback");

            // 3. Offline Fallback (Attached to 429)
            let fallbackMsgs = messages;
            let fallbackQuery = "";
            try {
                fallbackQuery = messages[messages.length - 1].parts[0].text;
            } catch (e) { }

            const fallback = getOfflineFallback(fallbackQuery);

            // Try to extract retry delay from error message or headers if available
            // Google often sends "retryDelay": "12.34s" in error details
            let retryAfter = 60; // Default 1 min
            const match = error.message?.match(/retryDelay[:\s]+"?(\d+(\.\d+)?)s"?/);
            if (match) {
                retryAfter = Math.ceil(parseFloat(match[1]));
            }

            return {
                error: "Core is recharging.",
                retryAfter,
                friendly: "My connection to the core is saturating. I need a moment to recharge.",
                fallback: fallback, // Attach fallback if available
                usage: { totalTokenCount: 0 }
            };
        }

        throw new Error(error.message || "I had a small glitch in my simulation logic. Could you try asking that again?");
    }
}

