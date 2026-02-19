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
    contactEmail: 'tomas.triska.iver@gmail.com',
    hero: {
        symbol: 'Λ',
        title: 'Science of fields that breathe.',
        subtitle: 'Stable excitations—linons—can self-assemble in discrete fields. No global constants. No predefined metric geometry. Just local causality. If you want, I can show you where this enters the equation.',
        cta_wiki: 'Lineum Core v1.0.18',
        cta_audit: 'Audit Evidence'
    },
    sections: {
        layman: {
            label: 'Intuition',
            title: 'What is Lineum?',
            p1: 'Lineum explores stable excitations in a discrete field. Some of them self-assemble and persist—behaving in ways that resemble particles.',
            p2: 'This isn\'t just a simulation; it is a search for the fundamental rules from which structure emerges.',
            visual_label: 'Visual metaphor'
        },
        scientist: {
            label: 'Formalism',
            title: 'Deep Science & Auditable Reality',
            whitepaper: {
                title: 'Whitepaper (v1.0.18)',
                desc: 'Here you will find the complete derivation of the equation, numerical scheme, and interpretation of results.',
                link: 'Read Documentation →'
            },
            zenodo: {
                title: 'Zenodo (DOI)',
                desc: 'Our official scientific archive with guaranteed data traceability.',
                link: '10.5281/zenodo...'
            },
            simulacrum: {
                title: 'Simulacrum',
                desc: 'My interactive laboratory and audit data browser. You can track phase shifts in real time.',
                link: 'Enter Laboratory →'
            }
        }
    },
    legend: {
        trigger_label: 'Field Guide',
        title: 'Field Guide',
        subtitle: 'Emergent phenomena in Lineum',
        items: [
            {
                id: 'psi',
                label: 'Emergent Life (ψ-Phase)',
                description: 'The primary act of the field. These <b>Point Singularities</b> wander through the vacuum, shifting colors based on their internal phase state (Cyan: Stable, Magenta: Transition, Yellow: Peak).',
                color: palette.psi
            },
            {
                id: 'kappa',
                label: 'Safe Zones (κ-Field)',
                description: 'Regions of high vacuum stability. I visualize these as a <b>blue-to-magenta spectral mist</b> where Linons are less likely to experience rapid phase shifts.',
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
        invitation: 'These aren\'t just pretty colors. I can explain the precise math behind every pixel.',
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
        github: 'GitHub',
        privacy: 'Privacy Policy'
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
    },
    whitepaper_warning: {
        title: 'Live Research / Documentation Gap',
        paragraphs: [
            'Please note that <b>Lineum is an evolving research project</b>. The static whitepapers here may lag behind the latest audit data and ongoing experiments.',
            'For the most up-to-date understanding, we highly recommend <b>asking Lina</b> (the AI Assistant). She has access to the latest live context, audit results, and reformulated hypotheses that might not yet be fully reflected in these texts.',
            'Use these documents as a foundational reference, but trust Lina for the current state of the art.'
        ],
        ack_label: 'I Understand, Continue'
    }
};
