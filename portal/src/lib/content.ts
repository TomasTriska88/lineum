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
        title: 'Science of fields that breathe.',
        subtitle: 'Exploring the emergence of stable excitations (Linons) in discrete fields. No global constants. No predefined metric geometry. Just pure local causality.',
        cta_wiki: 'Lineum Core v1.0.18',
        cta_audit: 'Audit Evidence'
    },
    sections: {
        layman: {
            label: 'For laymen',
            title: 'What is Lineum?',
            p1: 'Imagine the universe not as a vacuum, but as a fine digital grid. Lineum is a model that shows how stable waves can "self-assemble" in this environment, behaving like particles.',
            p2: 'It is not just a simulation; it is a search for the fundamental rules from which matter emerges.',
            visual_label: 'Visual metaphor'
        },
        scientist: {
            label: 'For scientists',
            title: 'Deep Science & Auditable Reality',
            whitepaper: {
                title: 'Whitepaper (v1.0.18)',
                desc: 'Complete derivation of the equation, numerical scheme, and interpretation of results.',
                link: 'Open Wiki →'
            },
            zenodo: {
                title: 'Zenodo (DOI)',
                desc: 'Official scientific archive with guaranteed data traceability.',
                link: '10.5281/zenodo...'
            },
            simulacrum: {
                title: 'Simulacrum',
                desc: 'Interactive laboratory and audit data browser. Track phase shifts in real time.',
                link: 'Enter Laboratory →'
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
                q: 'Where can "Structural Closure" be seen?',
                a: 'Closure is manifested by those <b>sharp color boundaries</b> and rings around Linons. They are mathematical boundaries where the lineum-field returns to itself (auto-referential loop), giving particles their stability.'
            },
            {
                q: 'Why do Linons orbit the same way?',
                a: 'It is not about gravity, but <b>phase locking</b> to the vacuum geometry. Linons do not orbit "something", but follow fixed topographic waves in the field, which are given by the fundamental Lineum equation.'
            },
            {
                q: 'Why do Linons never collide?',
                a: 'Linons are not solid bodies, but wave interferences. When they approach each other, their phase gradients create an <b>impassable topological barrier</b> that repels them before contact occurs.'
            },
            {
                q: 'Why do Linons not attract each other?',
                a: 'In this field, there is no charge or mass in the classic sense. Their interaction is purely <b>informational and geometric</b> — they respond to the curvature of the field (Warp), not to each other.'
            }
        ]
    },
    footer: {
        copy: '© 2026 Lineum Project • lineum.io',
        support: 'Support the project (Revolut)',
        github: 'GitHub'
    },
    support: {
        title: 'Support the Lineum Project',
        subtitle: 'Pushing the boundaries of discrete field dynamics through open research.',
        description: 'Lineum is an independent research project dedicated to discovering the fundamental rules of emergent stable excitations. Your support helps cover the computational costs of long-running simulations, maintain our open-source infrastructure, and provide more time for deep scientific analysis.',
        goals: [
            {
                title: 'Computational Infrastructure',
                desc: 'Funding high-uptime servers for audit runs and long-term simulation archiving.'
            },
            {
                title: 'Open Source Development',
                desc: 'Supporting the development of tools like Simulacrum and the Lineum Core engine.'
            },
            {
                title: 'Independent Research',
                desc: 'Ensuring that this work remains open, auditable, and free from external constraints.'
            }
        ],
        cta_label: 'Contribute via Revolut',
        cta_url: 'https://revolut.me/tomastriska'
    }
};
