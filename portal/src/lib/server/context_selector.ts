
import aiIndex from '$lib/data/ai_index.json';

interface ContextChunk {
    source: string;
    content: string;
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
            // Filter only core whitepapers for now to keep quality high
            if (!file.path.includes('whitepapers')) continue;

            const sections = file.content.split(/\n#{1,3}\s/); // Split by headers H1-H3

            for (const section of sections) {
                if (section.length < 50) continue; // Skip tiny sections

                this.chunks.push({
                    source: file.name,
                    content: section.trim(),
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
Content:
${c.content}
---
`).join('\n');
    }

    private tokenize(text: string): string[] {
        return text.toLowerCase()
            .replace(/[^\w\sěščřžýáíéůúňťď]/g, ' ')
            .split(/\s+/)
            .filter(w => w.length > 3) // Skip short words
            .filter(w => !['what', 'how', 'when', 'where', 'which', 'that', 'this', 'have', 'from', 'about'].includes(w));
    }
}

// Singleton
export const contextSelector = new ContextSelector();
