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
- **Accent Colors**: Vibrant gradients. Avoid flat colors.
  - Svelte Blue: `#0070f3`
  - Violet/Cyan: For logos and special symbols.
- **Typography**: Modern sans-serif fonts (e.g., Inter, Roboto) with precise letter-spacing.

### 3. Dynamic Elements
- Use subtle micro-animations (e.g., Svelte transitions `fade`, `fly`).
- Hover effects should change glow intensity or slightly scale elements.

---

## AI-First Orientation
Lineum Core isn't just a website with an AI chatbot; it is an AI-augmented research portal. All future features must be designed with the **Lineum Explorer** in mind as a primary UI actor.

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
*Last update: February 17, 2026*
