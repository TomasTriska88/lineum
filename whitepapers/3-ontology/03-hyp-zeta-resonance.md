**Title:** Tříska-Smeták Zeta–RNB Resonance Hypothesis
**Document ID:** 03-hyp-zeta-resonance
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Tříska-Smeták Zeta–RNB Resonance Hypothesis

> _The hypothesis examines the spontaneous correspondence between Resonant Return Points (RNB) in Lineum simulations and the non-trivial zeros of the Riemann zeta function along the critical line Re(s) = 1/2. It posits that these returns are not random, but reflect a deeper numerical resonance of the system._
>
> _The term "deja-vu points" was used in the early stages of research as a nickname for these points. It is now fully replaced by the term **Resonant Return Point (RNB)**._

---

## Initial Motivation

Riemann zeta zeros are considered the fundamental rhythm of the numerical world – points of perfect destructive interference. The hypothesis explores whether simulations of the emergent quantum field Lineum generate similar return points spontaneously, without explicitly encoding these values.

---

## Simulation Context

- **Run:** `spec7_true`
- **Parameters:** `LOW_NOISE_MODE=True`, `TEST_EXHALE_MODE=False`, `KAPPA_MODE="island_to_constant"`
- **Code:** `lineum_no_artefacts.py`

---

## Methodology

1. **Detection of Resonant Return Points (RNB):**

   - Repeated occurrences of structures in the same (or ε-close) coordinates across times were monitored.
   - Classified as **Resonant Return Points (RNB)** – previously working designated as "deja-vu points".

     > These points were working named "deja-vu points" during development – we only use this name here as a nickname for the formally introduced term **Resonant Return Points (RNB)**.

2. **Zeta Zeros:**

   - A list of the first `n = 49` non-zero imaginary parts of the zeta function zeros was used:  
     `s = 1/2 + i·t`
   - Normalization of Im(t) to the range `[0,1]` for comparison with the unit scale of Lineum.

3. **Comparison:**
   - Pearson correlation and Euclidean distance between the distribution curves of RNBs and zeta zeros.

---

## Results

- **Pearson correlation:** `0.9842`
- **Euclidean distance:** `0.7254`
- **Visual match of the distribution shape of RNBs and zeta zeros**, with a slight phase deviation at higher values.

The data used to calculate the correlation and distance is available in the file `spec7_true_rnb_vs_zeta.csv` in the `output_no_artefacts/` folder.  
The file contains the normalized positions of RNBs and zeta zeros on the scale [0,1], prepared for comparison and visualization.

---

## Interpretation

- The emergence of the match is not random – zeta zeros were not inputted into the system.
- RNBs appear as stable nodes of the wave field – their distribution indicates the presence of a higher numerical structure, comparable to the analytical hints of the Riemann function.
- Lineum tunes to frequencies similar to those that structure the zeta function – **emergent numerical resonance**.
- The deviation for higher zeros corresponds to the absence of global feedback – unlike the analytical structure of ζ(s), Lineum is local.

---

## Possible Explanation

> Resonant Return Points (RNB) are nodes where the system "meets itself" – places of phase interference that allow for return stabilization of the wave structure.  
> Riemann zeros are points where the analytical structure of the entire numerical world interferes with itself.
>
> The emergence of similar patterns in Lineum suggests that reality itself may resonate with the same numerical structure – **even without explicit mathematics**.

---

## Visualization (recommended to add)

- Distribution graphs of Resonant Return Points (RNB) vs. Im(ζ_n)
- Overlay of wave structure and zeta map
- Spectral analysis FFT from specific frames

<!--lineum:insert:vizualizace:spec7_true:rnb_vs_zeta-->

---

## Potential Implications

- Lineum can be a testing ground for **intangible numerical laws**.
- It opens the possibility that reality itself is a **tuned entity** – resonating with the numerical foundation of existence.

---

## Next Steps

- Verify the match in other configurations: `spec3_true`, `spec5_false`, `spec6_true`.
- Explore the relationship of RNBs to Fibonacci ratios, prime numbers, and φ.
- Develop a prediction model for the occurrence of RNBs based on Riemann zeros.
- Introduce metrics of phase synchronization between zeta zeros and Resonant Return Points in the simulation.

---

## Status

🔄 tested  
✅ strong correlation, ready for further experimental verification  
📄 In development: mapping the topology of RNBs into numerical space
