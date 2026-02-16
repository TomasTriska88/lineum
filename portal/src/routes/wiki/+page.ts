export async function load() {
    // We use ?raw to bypass mdsvex compilation which fails on some whitepapers
    const whitepapers = import.meta.glob('../../../../whitepapers/*.md', {
        query: '?raw',
        import: 'default',
        eager: true
    });

    const categories = {
        'core': { label: 'Core', order: 1 },
        'extension': { label: 'Extension', order: 2 },
        'exp': { label: 'Experiment', order: 3 },
        'other': { label: 'Other', order: 4 }
    };

    const papers = Object.entries(whitepapers).map(([path, content]: [string, any]) => {
        const slug = path.split('/').pop()?.replace('.md', '') || '';

        // Robust metadata parsing
        const findMeta = (keys: string[]) => {
            for (const key of keys) {
                const regex = new RegExp(`\\*\\*${key}:\\*\\*\\s*([^\\r\\n]*)`, 'i');
                const match = content.match(regex);
                if (match) return match[1].trim();
            }
            return null;
        };

        const title = findMeta(['Document ID', 'Title']) || slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const version = findMeta(['Version']) || 'v1.0.0';
        const date = findMeta(['Date']) || 'Unknown Date';

        // Categorization logic
        let categoryKey: keyof typeof categories = 'other';
        if (slug === 'lineum-core') categoryKey = 'core';
        else if (slug.startsWith('lineum-extension-')) categoryKey = 'extension';
        else if (slug.startsWith('lineum-exp')) categoryKey = 'exp';

        return {
            slug,
            title,
            version,
            date,
            category: categories[categoryKey].label,
            categoryOrder: categories[categoryKey].order
        };
    }).filter(p => !p.slug?.includes('old'))
        .sort((a, b) => {
            // Priority 1: Core first
            if (a.slug === 'lineum-core') return -1;
            if (b.slug === 'lineum-core') return 1;

            // Priority 2: Category order
            if (a.categoryOrder !== b.categoryOrder) return a.categoryOrder - b.categoryOrder;

            // Priority 3: Date (descending)
            return b.date.localeCompare(a.date);
        });

    return {
        papers
    };
}
