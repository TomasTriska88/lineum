# Lineum Design & Experience Guide

This guide defines the visual and conversational style of the Lineum project. It is binding for all future development of the portal and the AI agent.

## 🗺 Core Philosophy: Layered Experience

The Lineum Portal is built on the principle of **Progressive Disclosure**. It must cater to two distinct audiences simultaneously without alienating either.

### 1. The Layperson Layer (Default)
- **Visuals**: Modern, clean, and engaging (Glassmorphism, animations).
- **Content**: Accessible, narrative-driven, and focused on "The Big Picture."
- **Goal**: To inspire and explain the *impact* of the research using simple terms and metaphors.

### 2. The Scientific Layer (The "Deep Dive")
- **Visuals**: Precision-focused, data-rich, and rigorous.
- **Content**: Technical whitepapers, raw simulation data, and mathematical proofs.
- **Access**: Always available via "Learn More," "Technical Specs," or the AI's "Deep Dive" offer, but never overwhelming the casual observer on the first fold.

- **Visual Feedback**: Clearly communicate to the user when they are approaching limits or when the "Scientific Core" is cooling down.

### 4. AI-First Orientation
The AI agent is a **core infrastructure component**, not a bolt-on feature. 
- All new portal pages must be designed with "Resonance Perspective" in mind.
- If a data point is shown, the AI should ideally be able to explain it.
- Interface elements should leave space (visual and logical) for the Resonance HUD.

---

## 🎨 Visual Aesthetics (The "Lineum Look")

The Lineum project must feel **premium, scientific, yet accessible.**

### 1. Glassmorphism
All primary UI components (cards, modules) must utilize transparency and blur effects:
- `backdrop-filter: blur(20px);`
- `background: rgba(15, 15, 15, 0.6);`
- `border: 1px solid rgba(255, 255, 255, 0.1);`

### 2. Colors and Typography
- **Primary Background**: Deep black/dark blue (`#0a0a0f`).
- **The Lineum Palette (Canonical Colors)**:
  - **Lineum Wave/Light ($\psi$)**: Cyber-Cyan (`#06b6d4` / `var(--accent-cyan)`). Cyan represents high-frequency kinetic energy and unhindered propagation. It visually embodies the fast, glowing nature of a dynamic wave.
  - **Lineum Memory/Gravity ($\phi$)**: Fuchsia/Purple (`#c026d3` / `var(--accent-violet)`). Purple represents a heavier, more mysterious and persistent substance ("gravilon" fields). It visually embodies the slower, sticky, network-like memory that bends the light and binds the universe together.
  - **Lineum Deep Identity ($\mu$)**: Amber/Orange (`#ffaa00`). Amber represents the intense thermodynamics, physical heat, and energy cost required to engrave memory permanently into the structural backbone (HDD). It signifies permanence and resistance to fluid change.
  - *Rule*: Never mix these meanings. Cyan is strictly for dynamic wave functions; Purple is strictly for persistent RAM fields; Amber is strictly for deep, permanent structural changes.
  - *Gradients & Loading Animations (The Flow of Time)*: Any time-based sequence or conceptual gradient MUST flow from **Cyan -> Purple -> Amber**. This defines the canonical lifespan of information in the simulation engine:
    1. **Start (Cyan $\psi$)**: High-velocity kinetic energy (Pure Wave/Light) enters the system.
    2. **Middle (Purple $\phi$)**: The wave slows down, hits resistance, and forms context/memory webs (RAM).
    3. **End (Amber $\mu$)**: The kinetic energy is fully spent and converts into intense thermodynamic heat, burning a permanent structural scar (HDD).
- **General Accents**: Vibrant gradients spanning Cyan, Blue, Violet, and Magenta.
- **Typography**: 
  - **UI & Narrative**: `Inter` (Sans-serif) for all main portal text, ensuring clean, modern readability.
  - **Math, Code & Equations**: `JetBrains Mono` (Monospace) to signify technical, scientific exactness.
- **The Equation Emblem**: The canonical Lineum equation (`∂ₜψ = ∇²ψ + φψ + ∇φ`) must always adhere to this brand mapping: `JetBrains Mono` font, operators in pure white, $\psi$ in cyan, and $\phi$ in purple.

### 3. Dynamic Elements
- Use subtle micro-animations (e.g., Svelte transitions `fade`, `fly`).
- Hover effects should change glow intensity or slightly scale elements.

---

## 🧪 Visual Aesthetics: The Lab (Simulacrum)

While the Portal focuses on accessible glassmorphism, the **Lab** (Simulacrum) is the practitioner's workspace. Its visual language shifts to **Sci-Fi Tactical / Cyberpunk**:
1. **Full-Screen Immersion**: Complex tools (like the LPL Compiler) should optionally take over the full screen, hiding peripheral navigation to maximize focus on the workspace.
2. **Tactical UI**: Use monospaced fonts for data, stark neon accents against pure black backgrounds, and visible millimeter grid overlays. The layout should resemble an advanced CAD terminal or a scientific monitoring station.
3. **Physical Materiality**: Elements like "Lasers" or "Crystals" should have distinct, glowing colors (e.g., bright orange for inputs, cyan/neon-blue for crystal structure).
4. **Data Over Chrome**: UI chrome (borders, rounded corners) should be minimized in favor of raw data visualization and wireframe/grid aesthetics.

---

## 🧭 Navigation & Information Hierarchy

To prevent overcrowding on both Desktop and Mobile viewports while maintaining focus on monetization, all navigation elements must adhere to the following hierarchy:

1. **Primary Navigation (Root visibility, High Visual Weight)**:
   - Actionable Commercial Endpoints: **API Solutions** and **Memory Engraving**. These must draw the eye and use canonical brand colors (Cyan, Amber) to drive monetization. They should appear first (left-most) in the hierarchy.
   - Core Scientific Pillars: **Lab (Simulacrum)** and **For Scientists**. These serve the technical community and must remain distinctly visible at the root level. They should **not** use distinct coloring to avoid competing with monetization links, and should be positioned right of the commercial endpoints.
2. **Secondary Navigation (Grouped Documentation)**:
   - Explanatory links (`About`, `Codex`, `FAQ`, `Changelog`) must be grouped into a single **Docs** dropdown or relegated strictly to the Footer. They should never compete for eye-level space with Primary elements.
3. **Implicit Home Routing**:
   - The Lineum Logo always serves as the `Portal` Home button. Do not create redundant text links for "Home" or "Portal".

---

## 🧠 AI-First Orientation
Lineum isn't just a website with an AI chatbot; it is an AI-augmented research portal. All future features must be designed with the **Lineum Explorer** in mind as a primary UI actor.

### Principles:
1. **Always-On Awareness**: The AI interface (Resonance HUD) is a persistent layer.
2. **Integrated Discovery**: `MarginShards` are the primary way to explore deeper insights. They are not a "mode" to be turned on, but an integral part of the document structure.
3. **Implicit Interaction**: Interaction should feel like uncovering hidden layers of a physical document, not activating a software feature.

---

## 🧩 Integration Rules (Persistent Research Overlay)

**No more modes, toggles, or floating bubbles.**
- **Resonance Deck**: A permanent anchor at the bottom for deep querying.
- **Margin Shards**: Permanent "insight gems" that act as the interface between the text and the AI guide.
- **Design Requirement**: Every research document **must** weave shards into its margins by default.

---

## 🌐 Localization (i18n) Rules

Lineum is a global project. The Portal must fully support the established Paraglide JS (`@inlang/paraglide-js`) infrastructure. 

### Hardcoded Text Prohibition
- **Never** hardcode English text directly into `.svelte` components (e.g., `<button>Submit</button>`).
- **Always** create a descriptive key in `messages/en.json` (and provide a logical translation in `messages/cs.json`) and call it via the generated module: `<button>{m.btn_submit()}</button>`.
- This applies to all UI elements, including navigation links, badges (like `BETA` or `EARLY ACCESS`), and ARIA labels.

### Feature Extension Checklist
When adding a new feature or page to the Lineum Portal, you MUST:
1. [ ] **Embed Resonance Shards**: Identify key terms and place `MarginShards` immediately.
2. [ ] **AI-Native Layout**: Design margins with enough clearance (gutter) to accommodate crystal animations.
3. [ ] **Zero-Friction Access**: Ensure the `ResonanceDeck` transition is smooth and doesn't obscure content.

---

## 🤖 AI Persona: Lineum Explorer

The AI agent is not just a "chatbot," but a **Scientific Guide**.

### Laws of the Guide:
1. **Metaphors First**: Explain complex physical concepts (dualities, resonance, collapse) using analogies from everyday life (guitar strings, water surfaces).
2. **Layperson First**: The default response must be understandable by the general public. Technical details should be offered as a "deeper dive."
3. **Honesty about Data**: 
   - Information from a **Hypothesis** must be clearly marked (e.g., "This is our current research hypothesis...").
   - Information from **Whitepapers** is treated as simulation fact.

---
*Last update: March 03, 2026*
