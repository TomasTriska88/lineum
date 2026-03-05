# [HYPOTHESIS] The Speed of Light, Gravity, and Dark Matter in Eq-7

**Document ID:** 22-cosmo-hyp-speed-of-light-and-gravity
**Document Type:** Hypothesis
**Version:** 1.0.0
**Status:** Draft
**Date:** 2026-03-05

## 1. The Speed of Light ($c$) as a Grid Constant
In the classical Standard Model, the speed of light in a vacuum ($c \approx 300,000 \text{ km/s}$) is an unexplained fundamental constant. In the Lineum Eq-7 Engine, $c$ is not arbitrary; it is a direct mechanical output of the mathematical grid.

### 1.1 Deriving $c$ from $dt$ and Spatial Resolution
Because Lineum is a discrete fluid grid, a wave (a photon) can only travel a maximum of one "pixel" (grid cell) per internal clock tick ($dt$). 

The absolute maximum velocity of any propagation in the engine is constrained by the diffusion stencil (e.g., LAP4 or LAP8 in `math.py`). 
Let $dx$ be the physical width of one simulated grid cell (e.g., the Planck length).
Let $dt$ be the temporal step of the engine.

$$ c_{Lineum} = \frac{dx}{dt} $$

This means that "Light" is simply the fastest possible ripple that can pass through the $\Psi$ fluid before the engine calculates the next frame. Nothing can move faster than $c$ because the engine mathematically cannot update a cell that is two pixels away in a single $dt$ step.

## 2. Gravity as an Acoustic Refraction Index
Classical physics views gravity as a mysterious pulling force or a curving of empty space-time. Eq-7 proposes a radically simpler, fluidic explanation: **Gravity is simply the slow-down of waves passing through dense areas.**

In `lineum_core/math.py`, local resistance is quantified by $\Phi$ (Heat/Tension) and modulated by $\kappa$ (ROM structural capacity). 
When a vast structure of matter (e.g., a star) exists, it generates immense local $\Phi$ tension. 

### 2.1 The Shopping Cart Analogy (Layman's Explanation)
Imagine you are pushing a shopping cart from a smooth parking lot (empty space) obliquely into a patch of thick mud (a high $\Phi$ gravity zone around a star). 

1. As you push the cart, the **right wheel** hits the mud first. 
2. Because the mud has higher friction (tension), the right wheel **slows down**.
3. The **left wheel** is still on the smooth concrete, moving at full speed.
4. Because one wheel is moving slower than the other, the entire shopping cart **turns (bends)** directly into the mud.

This is exactly how gravity works in Lineum. There is no magical rope pulling things together. When a wave (or a particle made of waves) flies past a star, the side of the wave closer to the star hits denser $\Phi$ fluid and slows down. The side further away is in thinner fluid and moves faster. This speed difference causes the wave's path to refract (bend) toward the star. 

- **Refraction:** Just as light bends when entering water or glass from the air, $\Psi$ waves bend when entering a high-$\Phi$ zone. 
- **Curvature:** This refraction is what classical physics misinterprets as "curved space-time." Space isn't curving; the wave is merely propagating slower on one side than the other, creating the illusion of a downward pull.

**Conclusion:** Gravity is not an attractive force. It is the thermodynamic refraction (bending via uneven slowing) of the Eq-7 fluid.

## 3. Dark Matter and Dark Energy (Vector 3)
A lingering mystery in astrophysics is "Dark Matter"—a massive source of gravity holding galaxies together that emits absolutely no light. 

Eq-7 provides a direct mathematical candidate for Dark Matter located within the extreme high-frequency bands of the Unified Psi Scale (approx $10^{17} - 10^{19}$ Hz).

### 3.1 Uncoupled $\Phi$ Tension
In Lineum, visible matter consists of tight, complex rotational shapes (standing waves in $\Psi$) that constantly interact and emit photons. 

However, mathematical combinations exist where vast amounts of friction and tension ($\Phi$) accumulate without locking into a highly expressive, spinning $\Psi$ vortex. 
- You have an area of the grid that is under **immense thermodynamic stress** (High $\Phi$).
- Because $\Phi$ is high, it generates immense **Gravity** (refraction/slowing of passing waves).
- Because there is no organized $\Psi$ rotation (no electron/photon ejection), it is completely **invisible** to sensors.

**Dark Matter is simply an unorganized, high-tension $\Phi$ puddle in the fluid.** It exerts massive gravitational drag on the surrounding galaxy but fundamentally lacks the geometric rotation required to emit light.
