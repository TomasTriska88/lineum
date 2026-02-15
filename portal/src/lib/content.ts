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
                label: 'Emergent Life',
                description: 'The <span style="color: #00d2ff">cyan</span> points of light. Not solid matter, but waves of energy. They pulse and cycle colors as they "breathe" in their own rhythm.',
                color: palette.psi
            },
            {
                id: 'kappa',
                label: 'Safe Zones',
                description: 'The <span style="color: #7eb8ff">deep blue</span> background. It forms a landscape of stability—particles slide off the <span style="color: #fff">lighter</span> hills and settle in the safe, dark valleys.',
                color: palette.kappa
            },
            {
                id: 'phi',
                label: 'Ghost Trails',
                description: 'The <span style="color: #8a2be2">violet</span> streaks leaving a trace behind moving dots. Like the wake behind a boat, showing exactly where the particle has been.',
                color: palette.phi
            },
            {
                id: 'warp',
                label: 'Space Warp',
                description: 'The <span style="color: #ff00ff">magenta</span> distortion. When many particles cluster together, they bend the space around them, creating gravity-like wells.',
                color: palette.warp
            },
            {
                id: 'coupling',
                label: 'Binding Forces',
                description: 'Faint <span style="color: #ff007f">rose</span> lines. Invisible energy filaments that form connections between particles to hold complex structures together.',
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
