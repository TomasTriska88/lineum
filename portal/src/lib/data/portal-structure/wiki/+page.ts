export async function load() {
    // Use deep glob to find whitepapers in subdirectories
    const whitepapers = import.meta.glob('$whitepapers/**/*.md', {
        query: '?raw',
        import: 'default',
        eager: true
    });

    const tracks = {
        'core': { label: 'Core', order: 1 },
        'cosmology': { label: 'Cosmology', order: 2 },
        'ontology': { label: 'Ontology', order: 3 },
        'archive': { label: 'Archive', order: 4 },
        'other': { label: 'Other', order: 5 }
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

        const docType = findMeta(['Document Type', 'Type']) || 'Documentation';

        // Track & Subtype Categorization logic based on folder paths or filename
        let trackKey: keyof typeof tracks = 'other';
        let subType = 'Canonical'; // default to Canonical unless overridden

        // Track Mapping
        if (path.includes('/1-core/') || slug.includes('-core-') || slug.startsWith('01-core') || slug.startsWith('02-core') || slug.startsWith('lineum-core')) {
            trackKey = 'core';
        } else if (path.includes('/2-cosmology/') || slug.includes('cosmo-')) {
            trackKey = 'cosmology';
        } else if (path.includes('/3-ontology/') || slug.includes('ontology-')) {
            trackKey = 'ontology';
        } else if (path.includes('/4-archive/')) {
            trackKey = 'archive';
            subType = 'Retracted';
        }

        // SubType Mapping (Override Canonical with specific logic)
        if (slug.includes('-exp-') || docType.toLowerCase() === 'experiment') {
            subType = 'Experiment';
        } else if (slug.includes('-ext-') || docType.toLowerCase() === 'extension') {
            subType = 'Extension';
        } else if (slug.includes('-hyp-') || docType.toLowerCase() === 'hypothesis') {
            subType = 'Hypothesis';
        }

        return {
            slug,
            title,
            version,
            date,
            status,
            track: tracks[trackKey].label,
            trackOrder: tracks[trackKey].order,
            subType
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
            // Priority 1: Track order
            if (a.trackOrder !== b.trackOrder) return a.trackOrder - b.trackOrder;

            // Priority 2: Subtype order (Canonical first, then others, then Hypotheses)
            const subTypeOrder = { 'Canonical': 1, 'Hypothesis': 2, 'Extension': 3, 'Experiment': 4, 'Retracted': 5, 'Documentation': 6 };
            const aSub = subTypeOrder[a.subType as keyof typeof subTypeOrder] || 99;
            const bSub = subTypeOrder[b.subType as keyof typeof subTypeOrder] || 99;
            if (aSub !== bSub) return aSub - bSub;

            // Priority 3: Slug alphabetical (respects 01-, 02- prefixes)
            return a.slug.localeCompare(b.slug);
        });

    return {
        papers
    };
}
