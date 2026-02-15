export const palette = {
    psi: '#00d2ff',  // ψ Phase — cyan
    kappa: '#1a3a5a',  // κ Stability — deep blue
    phi: '#818cf8',  // φ Memory — ghost indigo
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
                label: 'Emergent Life (ψ-Phase)',
                description: 'The primary entities of the field. These <b>Point Singularities</b> wander through the vacuum, shifting colors based on their internal phase state (Cyan: Stable, Magenta: Transition, Yellow: Peak).',
                color: palette.psi
            },
            {
                id: 'kappa',
                label: 'Safe Zones (κ-Field)',
                description: 'Regions of high vacuum stability. These appear as a <b>blue-to-magenta spectral mist</b> where Linons are less likely to experience rapid phase shifts.',
                color: palette.kappa
            },
            {
                id: 'phi',
                label: 'Ghost Trails (φ-Memory)',
                description: 'The <span style="color: #818cf8">compact spectral wake</span> trailing *behind* moving particles. It acts as a subtle companion, showing the **Memory (φ)** of recent movement without disrupting the primary field.',
                color: palette.phi
            },
            {
                id: 'warp',
                label: 'Space Warp (Curvature)',
                description: 'Dynamic **contour lines** (resembling "rubber bands") and magenta halos surrounding clusters. These are ripples in the κ-field created as mass-like particles bend space around them.',
                color: palette.warp
            },
            {
                id: 'tension',
                label: 'Tension Vectors',
                description: 'Digital pointers showing the direction of field attraction. These represent **Geodetic Tension**—the force of field geometry pulling on each Linon.',
                color: '#ff00ff'
            },
            {
                id: 'coupling',
                label: 'Interaction Filaments (Coupling)',
                description: 'Transient links between particles. These represent **quantum entanglement** or phase-coupling, where the movement of one Linon instantaneously affects the other through the field.',
                color: palette.coupling
            }
        ],
        faq: [
            {
                q: 'Kde je vidět "strukturální uzavření" (Structural Closure)?',
                a: 'Uzavření se projevuje těmi <b>ostrými barevnými hranicemi</b> a prstenci kolem Linonů. Jsou to matematické hranice, kde se lineum-pole vrací samo do sebe (auto-referenční smyčka), což dává částicím jejich stabilitu.'
            },
            {
                q: 'Proč Linony obíhají pořád stejně?',
                a: 'Nejde o gravitaci, ale o <b>fázové uzamčení</b> ke geometrii vakua. Linony neobíhají "něco", ale následují fixní topografické vlny v poli, které jsou dány základní rovnicí Lineum.'
            },
            {
                q: 'Proč se Linony nikdy nesrazí?',
                a: 'Linony nejsou pevná tělesa, ale vlnové interference. Když se k sobě přiblíží, jejich fázové gradienty vytvoří <b>nepřekonatelnou topologickou bariéru</b>, která je odrazí dříve, než by došlo ke kontaktu.'
            },
            {
                q: 'Proč se Linony navzájem nepřitahují?',
                a: 'V tomto poli neexistuje náboj ani hmotnost v klasickém smyslu. Jejich interakce je čistě <b>informační a geometrická</b> — reagují na zakřivení pole (Warp), nikoliv na sebe navzájem.'
            }
        ]
    },
    footer: {
        copy: '© 2026 Lineum Project • lineum.io',
        support: 'Podpořit projekt (Revolut)',
        github: 'GitHub'
    }
};
