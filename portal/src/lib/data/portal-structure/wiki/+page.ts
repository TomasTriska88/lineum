export async function load() {
    // Use deep glob to find whitepapers in subdirectories
    const whitepapers = import.meta.glob('$whitepapers/**/*.md', {
        query: '?raw',
        import: 'default',
        eager: true
    });

    const categories = {
        'core': { label: 'Core', order: 1 },
        'cosmology': { label: 'Cosmology', order: 2 },
        'ontology': { label: 'Ontology', order: 3 },
        'extension': { label: 'Extension', order: 4 },
        'exp': { label: 'Experiment', order: 5 },
        'other': { label: 'Other', order: 6 }
    };

    const papers = Object.entries(whitepapers).map(([path, content]) => {
        const textContent = (content as string) || '';
        const slug = path.split('/').pop()?.replace('.md', '') || '';

        // Robust metadata parsing
        const findMeta = (keys: string[]) => {
            for (const key of keys) {
                const regex = new RegExp(`\\*\\*${key}:\\*\\*\\s*([^\\r\\n]*)`, 'i');
                const match = textContent.match(regex);
                if (match) return match[1].trim();
            }
            return null;
        };

        const title = findMeta(['Document ID', 'Title']) || slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const version = findMeta(['Version']) || 'v1.0.0';
        const date = findMeta(['Date']) || 'Unknown Date';
        const status = findMeta(['Status']) || 'Draft';

        // Categorization logic based on folder path or filename
        let categoryKey: keyof typeof categories = 'other';
        if (path.includes('/1-core/')) {
            categoryKey = path.includes('/experiments/') ? 'exp' : 'core';
        } else if (path.includes('/2-cosmology/')) {
            categoryKey = 'cosmology';
        } else if (path.includes('/3-ontology/')) {
            categoryKey = 'ontology';
        } else if (slug.startsWith('lineum-extension-')) {
            categoryKey = 'extension';
        } else if (slug.startsWith('lineum-exp')) {
            categoryKey = 'exp';
        }

        return {
            slug,
            title,
            version,
            date,
            status,
            category: categories[categoryKey].label,
            categoryOrder: categories[categoryKey].order
        };
    }).filter(p => {
        const safeSlug = p.slug?.toLowerCase() || '';
        const safeTitle = p.title?.toLowerCase() || '';
        return !safeSlug.includes('old') &&
            !safeSlug.includes('readme') &&
            !safeSlug.includes('template') &&
            !safeSlug.includes('stale') &&
            !safeTitle.includes('lowercase-kebab');
    })
        .sort((a, b) => {
            // Priority 1: Category order
            if (a.categoryOrder !== b.categoryOrder) return a.categoryOrder - b.categoryOrder;

            // Priority 2: Slug alphabetical (respects 01-, 02- prefixes)
            return a.slug.localeCompare(b.slug);
        });

    return {
        papers
    };
}
