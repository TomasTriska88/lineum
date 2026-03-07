```markdown
**Title:** Hypothesis: Structural Return of a Particle to its Point of Annihilation (Tříska’s Lineum Echo Hypothesis)
**Document ID: 20-cosmo-hyp-return-echo
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Structural Return of a Particle to its Point of Annihilation (Tříska’s Lineum Echo Hypothesis)

## Author / Origin

T. Tříska (2025), formulation based on observations of repeated particle occurrences in identical φ-memory locations

---

## Hypothesis

If a quasiparticle annihilates at a certain point in the Lineum field, φ retains its structural imprint. Another quasiparticle may appear in the same location after some time – even without a direct connection to the original particle.

This effect is understood as a **structural echo**: a spatial memory of a point that influences the trajectory of future particles.

---

## Testing Status

- ✅ Simulations with `LOW_NOISE_MODE = True`, `TEST_EXHALE_MODE = True`
- ✅ Repeated particle occurrences at points `[127, 0]` (882×) and `[127, 127]` (~600×)
- ✅ Occurrences separated in time, yet particles return to the same location
- ✅ Return density visualization confirmed (`lineum_return_density_*.png`)
- 🔄 Hypothesis **observed**, but not quantified for the entire field

---

## Calculation Methodology

### Simulation Parameters:

```python
LOW_NOISE_MODE = True
TEST_EXHALE_MODE = True
steps = 1000
linon_base = 0.01
linon_scaling = 0.01
disipation_rate = 0.002
reaction_strength = 0.06
diffusion_strength = 0.015
```

### Outputs:

- `true_trajectories.csv` – temporal evolution of all particle positions
- `lineum_return_density_127_0.png`, `lineum_return_density_127_127.png` – visual histogram of occurrences

---

## Visualization

![](../output/lineum_return_density_127_0.png)  
_Particle occurrences over time near point [127, 0]_

![](../output/lineum_return_density_127_127.png)  
_Particle occurrences over time near point [127, 127]_

---

## Conclusion

Lineum exhibits the ability to retain spatial memory: a point where a particle annihilated later repeatedly becomes a target location for another. This return effect does not arise randomly, but apparently due to the influence of a local φ gradient.

The hypothesis suggests that **the field remembers not only what happened, but also where it happened**. And sometimes it **returns** to these locations – like an echo.

---

## Recommended Further Tests

- Quantify the occurrence of returns across the entire grid (return density map)
- Test different modes (`LOW_NOISE_MODE = False`) to determine if the echo effect persists
- Introduce artificial particle "annihilation" and observe if a new particle returns to the location
- Measure the influence of the φ gradient in the vicinity of the return point (`∇φ`)

---

## References

- `true_trajectories.csv`
- `lineum_return_density_127_0.png`
- `lineum_return_density_127_127.png`
- prepared as a hypothesis in `09-hypotheses.md`
```