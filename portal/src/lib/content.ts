export const palette = {
    psi: '#00d2ff',  // ψ Phase — cyan
    kappa: '#1a3a5a',  // κ Stability — deep blue
    phi: '#8a2be2',  // φ Memory — violet
    warp: '#ff00ff',  // Field Curvature — magenta
    coupling: '#ff007f',  // Interaction Filaments — rose
    bg: '#0a0a0f',  // Background
    text: '#e0e0e8',  // Primary text
    muted: '#888',     // Muted text
    accent: '#7eb8ff',  // Accent
};

export const content = {
    hero: {
        symbol: 'Λ',
        title: 'Věda o polích, která dýchají.',
        subtitle: 'Odkrýváme vznik stabilních excitací (Linonů) v diskrétních polích. Bez globálních konstant. Bez předdefinované metrické geometrie. Jen čistá lokální kauzalita.',
        cta_wiki: 'Lineum Core v1.0.18',
        cta_audit: 'Auditní Důkazy'
    },
    sections: {
        layman: {
            label: 'Pro laiky',
            title: 'Co je to Lineum?',
            p1: 'Představte si vesmír ne jako prázdnotu, ale jako jemnou digitální mřížku. Lineum je model, který ukazuje, jak se v tomto prostředí mohou "samy od sebe" vytvořit stabilní vlny, které se chovají jako částice.',
            p2: 'Není to jen simulace; je to hledání základních pravidel, ze kterých vzniká hmota.',
            visual_label: 'Vizuální metafora'
        },
        scientist: {
            label: 'Pro vědce',
            title: 'Deep Science & Auditable Reality',
            whitepaper: {
                title: 'Bílá Kniha (v1.0.18)',
                desc: 'Kompletní derivace rovnice, numerické schéma a interpretace výsledků.',
                link: 'Otevřít Wiki →'
            },
            zenodo: {
                title: 'Zenodo (DOI)',
                desc: 'Oficiální vědecký archiv s garantovanou dohledatelností dat.',
                link: '10.5281/zenodo...'
            },
            audit: {
                title: 'Audit Hub',
                desc: 'Každý run je ověřitelný. Transparentnost od prvního seedu.',
                link: 'Prohlédnout audity →'
            }
        }
    },
    legend: {
        trigger_label: 'Physics Reference',
        title: 'Physics Reference',
        subtitle: 'Emergent phenomena in Lineum',
        items: [
            {
                id: 'psi',
                label: 'ψ Phase Colors',
                description: 'The rotating hue in linon cores represents the complex phase angle arg(ψ).',
                color: palette.psi
            },
            {
                id: 'kappa',
                label: 'Stability Islands',
                description: 'Voronoi geometry showing regions of localized stability in the κ map substrate.',
                color: palette.kappa
            },
            {
                id: 'phi',
                label: 'Field Memory',
                description: 'The "Return Echo" (trailing ghosts) visualizes the persistence of the interaction field φ.',
                color: palette.phi
            },
            {
                id: 'warp',
                label: 'Field Curvature',
                description: 'Topological warping of the background represents the singular nature of vortex clusters.',
                color: palette.warp
            },
            {
                id: 'coupling',
                label: 'Interaction Filaments',
                description: 'Lines of tension between linons representing non-linear interaction coupling.',
                color: palette.coupling
            }
        ]
    },
    footer: {
        copy: '© 2026 Lineum Project • lineum.io',
        support: 'Podpořit projekt (Revolut)',
        github: 'GitHub'
    }
};
