# Lineum Portal: Design & Experience Guide

This document defines the core visual, interaction, and experience guidelines for the Lineum Portal. Any future development or additions to the portal UI must strictly adhere to these principles.

## 1. Visual Language
- **Theme:** Dark mode by default. Deep backgrounds (often slate/indigo/black shades).
- **Style:** Glassmorphism, blurred backdrops, and subtle depth.
- **Accents:** Neon/Cyber glow accents (Emerald, Rose, Sky, Violet) to represent energy, simulation, and data flow.
- **Typography:** Clean sans-serif fonts (e.g., Inter, Roboto). Monospace fonts for code snippets, audit logs, and technical metrics to convey precision.

## 2. Interaction & Animation Rules

### 2.1 Static Hitboxes (The "Stable Hover" Rule)
Any interactive element (or container holding interactive elements like buttons) **must not structurally move or distort** when the user hovers over it. 
- ❌ **Do not use:** `transform: translate`, `rotate`, `scale`, or 3D tilting on parent containers if it causes the child buttons to shift away from the user's cursor.
- ✅ **Do use:** Pure visual indicators such as `box-shadow` (glows), `opacity` shifts, border color changes, or background overlays.

### 2.2 Functional Animations
- Use animations to convey state changes (e.g., pulsing dots for running states, text typewriter effects for terminal logs).
- Keep transitions snappy (150ms - 500ms max) to ensure the interface feels responsive and professional.

### 2.3 Customer-Centric Copywriting & Business Proof
Every interactive element and product description MUST focus on immediate, practical business value for the customer. The API is Lineum's primary income source and the ultimate proof of functionality.
- **The "WOW" Factor:** API products must look incredibly premium and immediately impress the user. Use terms that convey massive scale, zero latency, and structural advantage.
- **Clear ROI:** Be literal about what the customer gets. If a product saves time, show the ms difference. Don't use fluff or empty marketing jargon; use concrete numbers and demonstrable facts ("100k agents in 4ms").
- ❌ **Do not use:** Overly abstract or deeply technical internal mechanisms as primary call-to-actions (e.g., "Sample Vacuum", "Initialize Collector"). Do not use "fluff" or "vaření z vody" (empty words).
- ✅ **Do use:** Clear, use-case-driven outcomes (e.g., "Generate Session Key", "Stream Pure Entropy", "Generate Game Seed"). This helps the user instantly connect the API to their own project.
- **The Turnkey Model:** If a demo represents a massive, complex integration (like city-wide routing), explicitly state that it is available as a Custom "Turnkey" Enterprise Solution, not just a simple API endpoint.
## 3. The "Lineum Explorer" Persona
- The AI assistant interface throughout the portal should communicate as the "Lineum Explorer."
- Language must be tailored to the audience (Layman for the main portal, Pro for APIs, Scientific for whitepapers) as defined in the core project rules. 
- Easter eggs or hidden interactions should never obscure the primary call to action.
