**Title:** Hypotéza: Rezonující zárodek vesmíru (Tříska’s Resonant Seed Hypothesis)
**Document ID:** 10-hyp-resonant-seed
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypotéza: Rezonující zárodek vesmíru (Tříska’s Resonant Seed Hypothesis)

## Autor / původ

T. Tříska (2025), formulace na základě pozorování, že stabilita systému Lineum vrcholí při hodnotách κ odpovídajících jemné struktuře α ≈ 1/137 – podobně jako ve známé fyzice.

---

## Hypotéza

Hodnota α ≈ 1/137, známá jako jemná struktura, není univerzální konstanta daná zvenčí, ale **emergentní vlastnost vnitřního ladicího pole** systému.

Systém Lineum ukazuje, že při určitém rozsahu hodnot κ vzniká:

- stabilní spinová aura
- pravidelná oscilace pole ϕ
- rovnoměrný výskyt částic

Tato stabilita vrcholí právě kolem hodnoty κ ≈ 1/137.

Hypotéza tedy tvrdí, že:

> **α je rezonancí ladicího pole, ne konstantou samotného vesmíru.**

> Pokud hodnota κ **neodpovídá žádné vnitřní rezonanci**, může dojít ke stavu, kdy excitace **nevytvoří žádnou trvalou strukturu**.  
> V testovacím režimu `TEST_EXHALE_MODE` se tyto excitace často **rozplynou bez paměti**, bez víru, bez výdeje energie –  
> odpovídá to jevu popsanému jako **tichý kolaps** (`Silent Collapse Hypothesis`).

---

## Stav testování

- ✅ Běhy s κ = 1/137 vykazují vysokou stabilitu (run `alpha_constant`)
- ✅ Spektrum oscilací stabilizováno kolem ~1e18 Hz
- ✅ Stejné výsledky lze získat s polem κ(x, y), pokud se lokálně blíží hodnotě 1/137
- 🔄 Nutno otestovat, zda jiné hodnoty vedou ke zcela jinému „vesmíru“ (jiné spektrum, struktury)

---

## Metodika výpočtu

### Parametry simulace (konstantní ladění):

```python
TEST_EXHALE_MODE = True
LOW_NOISE_MODE = True
steps = 1000
linon_scaling = 0.01
disipation = 0.002
κ = 1 / 137.035999
```

### Parametry simulace (gradientní ladění):

```python
κ = gradient (např. 0.05 → 0.01 → 0.2)
```

### Výstupy:

- `spectrum_log.csv` – dominantní frekvence v rezonanci s α
- `spin_aura_avg.png` – stabilní spinová symetrie
- `phi_center_log.csv` – nízká fluktuace ve středu pole při α
- `multi_spectrum_summary.csv` – kolísání mimo α

---

## Doporučené další testy

- Spustit sérii běhů s různými fixními hodnotami κ (např. 1/90, 1/200) a porovnat spektra
- Analyzovat, zda změna α způsobí změnu „typologie“ vzniklých částic
- Test, zda při κ = α vzniká nejvyšší míra strukturální paměti φ

---

## Závěr

Systém Lineum ukazuje, že α nemusí být absolutní konstanta – ale může být důsledkem vnitřní ladicí rezonance.

Tato rezonance maximalizuje stabilitu, umožňuje vznik strukturovaného vesmíru a může být považována za **otisk zárodku reality**.

Hodnota 1/137 tak není vstup –  
**je to tón, který svět začíná hrát, když se vyladí správně.**
