
import aiIndex from '$lib/data/ai_index.json';

interface ContextChunk {
    source: string;
    content: string;
    status: string;
    score: number;
}

export class ContextSelector {
    private chunks: ContextChunk[] = [];
    private isInitialized = false;

    constructor() {
        this.initialize();
    }

    private initialize() {
        if (this.isInitialized) return;

        console.log(`[ContextSelector] Indexing ${aiIndex.length} files...`);

        // Naive chunking: Split by double newlines or headers
        // In a real system, we'd use a proper text splitter.
        // For whitepapers, we verify specific files.

        for (const file of aiIndex) {
            // Access expanded to all files. Everything indexed is searchable.

            const sections = file.content.split(/\n#{1,3}\s/); // Split by headers H1-H3

            for (const section of sections) {
                if (section.length < 50) continue; // Skip tiny sections

                // SECURITY: Strip misleading epistemic tags from Legacy/Planning content
                // If a legacy file says [VALIDATED], it is "stolen valor". We remove it so Lina doesn't get confused.
                let cleanContent = section.trim();
                if (file.status.includes('LEGACY') || file.status.includes('Planning')) {
                    cleanContent = cleanContent.replace(/\[(VALIDATED|OBS|OBSERVED|HYPOTHESIS|DISPLAY)\]/g, '(legacy-claim)');
                }

                this.chunks.push({
                    source: file.path, // Use full relative path for citation (e.g. whitepaper-old/03-equation.md)
                    content: cleanContent,
                    status: file.status,
                    score: 0
                });
            }
        }

        console.log(`[ContextSelector] Created ${this.chunks.length} chunks from whitepapers.`);
        this.isInitialized = true;
    }

    public select(query: string, limit: number = 5): string {
        const queryTokens = this.tokenize(query);

        if (queryTokens.length === 0) return "";

        // Reset scores
        this.chunks.forEach(c => c.score = 0);

        // Score chunks
        for (const chunk of this.chunks) {
            const chunkTextLower = chunk.content.toLowerCase();
            let matches = 0;

            for (const token of queryTokens) {
                if (chunkTextLower.includes(token)) {
                    matches++;
                    // Bonus for exact phrase matching could be added here
                }
            }

            // Keyword density scoring
            // We use a simpler scoring now: Raw matches are good.
            if (matches > 0) {
                chunk.score = matches;
            }
        }

        // Sort and select
        // INCREASED LIMIT: With paid billing, we can afford ~50k tokens context.
        // Fetching top 20 chunks ensures we almost never miss context.
        const topChunks = this.chunks
            .filter(c => c.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 20);

        console.log(`[ContextSelector] Selected ${topChunks.length} chunks (Expanded Context) for query "${query}"`);

        return topChunks.map(c => `
---
Source: ${c.source}
Status: ${c.status} ${c.status.includes('LEGACY') ? '(WARNING: HISTORICAL/OBSOLETE DATA - DO NOT CITE AS FACT)' : '(CURRENT)'}
Content:
${c.content}
---
`).join('\n');
    }

    private tokenize(text: string): string[] {
        return text.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(w => w.length > 1) // Skip 1-char words but allow 2+ char acronyms (AI, LPL)
            .filter(w => !['what', 'how', 'why', 'who', 'the', 'and', 'are', 'you', 'when', 'where', 'which', 'that', 'this', 'have', 'from', 'about'].includes(w));
    }
}

// Singleton
export const contextSelector = new ContextSelector();
