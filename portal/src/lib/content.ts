import { config } from './config';

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
    contactEmail: config.contact.primary,
    operator: {
        name: config.brand.legalName,
        address: config.brand.address,
        phone: config.brand.phone || '+420 721 026 189',
        ico: config.brand.ic
    },
    hero: {
        symbol: 'Λ',
        title_prefix: 'Science of fields that ',
        title_highlight: 'breathe.',
        subtitle: 'Lineum is an exploration of continuous spatial computation. We study how simple deterministic physics can give rise to emergent, intelligent-looking behavior.',
        cta_wiki: 'Explore the Wiki',
        cta_audit: 'Audit the Evidence'
    },
    sections: {
        layman: {
            label: 'The Philosophy',
            title: 'Intelligence from simplicity',
            p1: 'Instead of programming explicit rules or training massive neural networks, Lineum asks a different question: What if computation could emerge naturally from the physics of a continuous space?',
            p2: 'By designing a specific mathematical environment (Eq-7), we observe the spontaneous formation of stable, particle-like structures that naturally seek optimal paths through their surroundings.',
            visual_label: 'Core Interaction'
        },
        scientist: {
            label: 'For Researchers',
            title: 'Rigorous Verification',
            whitepaper: {
                title: 'The Core Paper',
                desc: 'Read the foundational document defining Eq-7, structural parameters, and the emergent quasiparticle dynamics.',
                link: 'Read the Whitepaper →'
            },
            zenodo: {
                title: 'Open Data Archive',
                desc: 'Access our canonical runs, snapshot metadata, and mathematical proofs in the Zenodo repository.',
                link: 'Go to Zenodo →'
            },
            simulacrum: {
                title: 'Interactive Simulacrum',
                desc: 'A live WebGL environment to test parameter stability and observe field interactions directly in your browser.',
                link: 'Launch Simulacrum →'
            },
            referencePack: {
                title: 'Reference implementation',
                desc: 'Download the source code and reproduction scripts to independently verify our claims on your own hardware.',
                link: 'View on GitHub →'
            }
        }
    },
    legend: {
        trigger_label: 'Field Mechanics',
        title: 'Simulation Telemetry',
        subtitle: 'Live structural observables',
        items: [
            {
                id: 'psi',
                label: 'ψ Phase (Quasiparticles)',
                description: 'The primary entities of the grid. These self-organizing lumps of energy behave like particles, navigating the space according to clear deterministic rules.',
                color: palette.psi
            },
            {
                id: 'kappa',
                label: 'κ Environment (Substrate)',
                description: 'The static terrain. These are the fixed boundaries and high-friction zones that shape the movement of particles across the grid.',
                color: palette.kappa
            },
            {
                id: 'phi',
                label: 'φ Memory (Tension)',
                description: 'The structural memory. As particles move, they leave a temporary physical "footprint" that repels others from following the exact same path.',
                color: palette.phi
            },
            {
                id: 'warp',
                label: 'Topological Warp (Guidance)',
                description: 'The dynamic curvature of the field. This indicates the steepest descent toward optimal destinations, guiding particles like a gravitational pull.',
                color: palette.warp
            }
        ],
        invitation: 'Lineum is fully deterministic. What looks like "decisions" is just a descent down a self-generated gradient.',
        faq: [
            {
                q: 'Is this an AI neural network?',
                a: 'No. Lineum uses continuous wave equations (Eq-7), not discrete weights or training data. The "intelligence" emerges naturally from the physics of the field interacting with obstacles.'
            },
            {
                q: 'What is a "linon"?',
                a: 'A linon is a localized clump of wave energy that holds its shape as it moves. Think of them like digital droplets navigating a microscopic landscape to find their target.'
            },
            {
                q: 'Why does this matter?',
                a: 'By understanding how nature solves spatial problems through fluid dynamics, we can build fundamentally new approaches to routing, logistics, and simulation.'
            }
        ]
    },
    footer: {
        copy: '© 2026 Lineum Project. Released for scientific and research purposes.',
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
                desc: 'Supporting the development of tools like Simulacrum and the Lineum engine.'
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
            'For the most up-to-date understanding, we highly recommend <a href="/api-solutions" style="color: var(--accent-color); text-decoration: underline;">viewing our Swarm Routing Showcase</a>. It serves as the live proof of our claims, allowing you to observe the continuous field dynamics and emergent particles with your own eyes.',
            'Alternatively, you can <b>ask Lina</b> (the AI Assistant). She has access to the latest live context, audit results, and reformulated hypotheses that might not yet be fully reflected in these texts.',
            'Use these documents as a foundational reference, but trust the live data and Lina for the current state of the art.'
        ],
        ack_label: 'I Understand, Continue'
    }
};
