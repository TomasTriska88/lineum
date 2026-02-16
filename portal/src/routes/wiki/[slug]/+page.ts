import { error } from '@sveltejs/kit';

export async function load({ params }) {
    try {
        const whitepapers = import.meta.glob('../../../../../whitepapers/*.md', {
            query: '?raw',
            import: 'default',
            eager: true
        });

        const keys = Object.keys(whitepapers);
        const slugMatch = `${params.slug}.md`.toLowerCase();

        const match = keys.find(path => {
            const fileName = path.split(/[/\\]/).pop()?.toLowerCase();
            return fileName === slugMatch;
        });

        if (!match) {
            throw error(404, `Whitepaper "${params.slug}" not found`);
        }

        const content = whitepapers[match] as string;

        const titleMatch = content.match(/\*\*(?:Document ID|Title):\*\*\s*([^\r\n]*)/i);
        const title = titleMatch ? titleMatch[1].trim() : params.slug;

        return {
            content,
            title,
            slug: params.slug
        };
    } catch (e) {
        if (e && typeof e === 'object' && 'status' in e) throw e;
        throw error(404, 'Whitepaper not found');
    }
}
