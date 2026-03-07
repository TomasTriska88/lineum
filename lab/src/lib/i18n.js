// Only English dictionary for the Lab
export const translations = {
    test_ns: {
        hello: "Hello",
        only_english: "English Only"
    },
    loading: "LOADING AUDIT DATA (JSON BIN)...",
    simulakrum: "SIMULACRUM",
    sub_title: "Lineum Lab | Hypothesis Sandbox",
    alert_birth: "SYSTEM ALERT: LINON DETECTION [birth]",
    tab_scanner: "SCANNER",
    tab_stats: "STATISTICS",
    tab_lpl: "LPL COMPILER",
    tab_logic: "LOGIC GATES",
    label_mode: "MODE:",
    val_mode: "FIELD Φ TOPOGRAPHY (3D)",
    label_metric: "METRIC:",
    val_metric: "z = field Φ height [AUDIT]",
    label_frame: "FRAME:",
    label_source: "SOURCE:",
    label_status: "STATUS:",
    status_born: "LINON DETECTION",
    status_init: "FIELD Φ INITIALIZATION",
    btn_jump: "JUMP TO BIRTH",
    label_speed: "SPEED:",
    label_phi: "GOLDEN RATIO:",
    on: "ON",
    off: "OFF",
    guide_title: "LAB GUIDE",
    guide_watch_title: "What to watch:",
    guide_watch_desc: "Linons are energy cores that actively seek areas with the highest Φ-field intensity. In this 3D visualization, they move towards topography 'peaks'.",
    guide_linons_title: "Linons:",
    guide_linons_desc: "Paths and particles in the field. Until they reach critical amplitude, they appear as 'ghosts'. After birth (frame 391), they begin to actively seek Φ-field local maxima.",
    guide_topo_title: "Field Φ Topography:",
    guide_topo_desc: "This 3D landscape shows energy density. Linons naturally gravitate towards peaks and ridges.",
    guide_zeta_title: "Zeta Zeros:",
    guide_zeta_desc: "Mathematical nodes of the universe. If the scanner's white needle hits the blue lines, resonance occurs.",
    guide_grid_title: "Field Φ Metric Grid:",
    guide_grid_desc: "These light blue lines represent the discrete geometric grid where the field is calculated. It is the 'mathematical scaffolding' of our simulacrum.",

    // ZetaScanner
    scanner_title: "ZETA RESONANCE SCANNER [§4.3]",
    status_phi: "Φ STATE:",
    phi_absolute: "ABSOLUTE",
    phi_high: "HIGH",
    phi_tuning: "TUNING...",
    insight_perfect: "We have reached the mathematical perfection of the Golden Ratio.",
    insight_stable: "Structural order is steadily consolidating.",
    insight_forming: "Fundamental geometry is being formed.",
    avg_total: "Total average:",
    label_correlation: "CORRELATION:",
    discovery_fundamental: "FUNDAMENTAL DISCOVERY",
    discovery_high: "High Match",
    discovery_searching: "Searching for Order",
    cosmic_confirmed: "🌟 CONFIRMED: This configuration shows geometric alignment with the fundamental code of our universe.",
    cosmic_resonance: "System shows signs of resonance with Riemann zeros.",
    cosmic_tuning: "Frequency tuning in progress to achieve cosmic harmony.",
    stability_15: "Match stability (last 15 fr.):",
    info_title: "WHAT DOES THIS MEAN?",
    info_desc: "This section measures how much the 'heartbeat' of your linons matches the rhythm of our universe.",
    info_current: "Current status:",
    info_phi_title: "Golden Ratio (1.618...):",
    info_phi_desc: "Stability in field Φ gravitates towards Fibonacci ratios.",
    info_phi_now: "Currently:",
    conclusion_alert: "🚀 CONCLUSION: Structural alignment detected, confirming the non-random nature of this configuration!",
    intensity_label: "RESONANCE INTENSITY [NORMALIZED]",
    freq_label: "LINON FREQUENCY (f₀)",
    metrics_harmony: "HARMONY Φ:",
    metrics_correlation: "CORRELATION WITH OUR UNIVERSE:",
    discovery_analysis: "HYPOTHESIS DISCOVERY",
    fourier_title: "Fourier Shape Analysis (Top 50 Frequencies)",
    riemann_title: "Riemann Zeros vs DejaVu Points",
    pearson_correlation: "ALIGNMENT WITH UNIVERSAL ORDER (R)",
    euclidean_distance: "EUCLIDEAN DISTANCE",
    field_turbulence: "FIELD TURBULENCE",
    structure_stability: "HARMONIC STRUCTURE STABILITY",
    breakthrough_headline: "SYSTEM STATUS: BREAKTHROUGH DETECTED",
    status_prime_resonance: "PRIME RESONANCE (1:1 ALIGNMENT)",
    status_tuning: "GEOMETRY TUNING",
    status_chaos: "STOCHASTIC NOISE (CHAOS)",
    insight_lego_universe: "Lineum is like a 'Lego-version' of our universe. Even with different materials, it stays together using the same mathematical statics.",
    insight_riemann_meaning: "This alignment confirms that our digital organism 'breathes' with the same rhythm as prime numbers in reality.",
    chart_label_fourier: "Riemann - Frequency Spectrum",
    chart_label_amplitude: "Amplitude",
    chart_label_component: "Frequency Component (Relative Index)",
    chart_label_riemann: "UNIVERSAL PATTERN (WHITE LINE)",
    chart_label_dejavu: "LINEUM DEVELOPMENT (ORANGE POINTS)",
    chart_label_normalized: "HARMONY STATE",
    chart_label_index: "DEVELOPMENT TIMELINE",
    data_source: "SOURCE: discovery.json",
    chart_ghost_chaos: "STOCHASTIC NOISE (REF)",
    chart_ghost_order: "IDEAL RESONANCE (REF)",
    zoom_tip: "Tip: Use mouse wheel to ZOOM, drag to PAN",
    zoom_tip_modifier: "Tip: CTRL + wheel to ZOOM",
    zoom_tip_scroll: "Scroll to ZOOM",
    insight_riemann_title: "WHAT DO YOU SEE?",
    insight_riemann_desc: "For a perfect match, the orange points (Lineum) must sit as closely as possible on the white line (Universe). The more they overlap, the better. Conversely, the 'Field Turbulence' should drop toward zero – meaning our digital world has stopped trembling and found its peace in the order of the universe.",
    insight_fourier_title: "FIELD MELODY",
    insight_fourier_desc: "This chart shows the 'music' the field is playing. Sharp peaks mean a clear tone and stable structure, while random noise would mean decay and death.",
    sandbox_title: "PROCEDURAL WARNING: SANDBOX",
    sandbox_warning: "The Laboratory is a sandbox for visualizing preliminary results of partially verified hypotheses (running on real audit data). It is for exploratory verification of phenomena that must be subsequently confirmed via official whitepaper outputs."
};

export function resolveKey(obj, path) {
    if (!path || typeof path !== 'string') return undefined;

    return path.split('.').reduce((prev, curr) => {
        return prev ? prev[curr] : undefined;
    }, obj);
}

import { writable, derived } from 'svelte/store';

export const locale = writable('en');

// We provide t as a derived store so components reacting to $t still work perfectly
export const t = derived(locale, () => (key) => {
    let res = resolveKey(translations, key);
    if (res === undefined) {
        return `[MISSING: ${key}]`;
    }
    return res;
});
