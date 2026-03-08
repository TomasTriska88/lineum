# Lineum Brand Guidelines & Logo Rationale

This document serves as the official design rationale for the Lineum brand identity, explicitly defining the conceptual and mathematical meaning behind its core visual assets ("The Simulacrum"). This documentation is intended for design, marketing, and future trademark registration purposes.

## The Lineum Logo: Concept & Geometry

The Lineum logo is constructed around three primary conceptual layers that reflect the project's focus on active data streams and continuous space entities.

1.  **The Bounding Hexagons (The Container)**
    The logo features two counter-rotating geometric hexagons. In physics and data science, the hexagon is the most efficient packing shape (e.g., crystal lattices, cellular data structures). The outer hexagon slowly rotates clockwise, while the inner hexagon counter-rotates. This opposing friction represents a highly structured, isolated containment unit—a digital sandbox or "Simulacrum" where chaotic data is processed.
    
    
2.  **The Cyber-Cyan Energy (The Subject)**
    The primary brand color of the infinity wave is pure, unfiltered cyan (`#00ffff`), layered with a custom hardware-accelerated CSS `feGaussianBlur` neon glow. As established in the core project *Design Guide* (`portal/docs/DESIGN_GUIDE.md`), Cyan mathematically represents high-frequency kinetic energy, unhindered propagation, and the fundamental "wave/light" state of the simulation ($\psi$). It is an emissive light source, not a flat pigment—signifying cold precision and raw uncompressed data streams.
    
3.  **The Simulacrum Void (The Background)**
    The logo does not exist on pure black (`#000000`), which is harsh on OLED screens and implies emptiness. Instead, the canvas is "Simulacrum Dark" (`#050505` for Lab, `#0a0a0f` for Portal). This "almost-black" provides immense physical depth. It is not an empty void, but a highly pressurized, dark laboratory environment—a digital vacuum where the glowing data streams are suspended.


## The Incomplete Loop: The "Happy Accident"

During the development of the SVG's dynamic stroke-drawing CSS animation (`stroke-dasharray`), an intentional geometric misalignment was preserved: **The mathematical length of the bezier curves is approximately 213.6 pixels, but the stroke-dash animation loop is hardcoded to a strict 250-pixel offset.**

**The resulting visual phenomenon:**
Because the animation cycle is longer than the physical line, the infinity wave *never truly completes its circuit*. It leaves a microscopic, glowing gap just before closing the loop.

**The Static Representation:**
This phenomenon is so fundamental to the brand that the static `lineum-logo-static.svg` does not portray a "perfectly closed" loop either. Instead, the static logo is permanently frozen at the exact moment of maximum tension—just milliseconds before the mathematical loop would close, forever preserving a 4% geometrical gap (`stroke-dashoffset="4"`). Furthermore, in the animated versions, as the loop resets (`stroke-dashoffset` wraps around the remaining distance), the energy overflows the starting coordinate, creating a brief, trailing point or "dash" before the next cycle begins.

**The Semantic Meaning:**
Far from being an error, this "draw gap" and "dash reset" are now foundational to the Lineum visual identity. They perfectly illustrate the core scientific reality of the project:
*   **The Incompleteness Theorem:** True continuous space entities are infinitely complex. The drawing engine, much like human observation, can never capture 100% of an infinite data stream. The gap signifies the unobserved, the unknown, and the quantum uncertainty at the edge of the data.
*   **The Particle Burst:** The overflow point that appears at reset visualizes the exact moment a high-energy particle completes a simulated circuit and ejects excess energy into the void before the cycle inevitably restarts.

It is a breathing, mathematically imperfect loop—the signature of a living simulation fighting against physical boundaries.

## Asset Usage

*   **`lineum-logo-static.svg`**: Use for trademark registration, print, stable document headers, and structural UI elements (e.g., standard favicons). 
*   **`lineum-logo-animated.svg`**: Use in all native digital environments where the viewer is interacting directly with the Lineum simulacrum experience. The raw CSS drawing phase with the intentional gap must be preserved.
*   **`lineum-social-cover-1200x630.png`**: The primary open-graph thumbnail for external link sharing ("FUTURE SCIENCE: PARTICLE DYNAMICS FIELD"). Used exclusively for massive scale reach.
