# Hypotéza: Strukturální návrat částice do místa zániku (Tříska’s Lineum Echo Hypothesis)

## Autor / původ

T. Tříska (2025), formulace na základě pozorování opakovaného výskytu částic v identických místech φ-paměti

---

## Hypotéza

Pokud kvazičástice zanikne v určitém bodě pole Lineum, φ si uchová její strukturální otisk. Jiná kvazičástice se může po určitém čase objevit ve stejném místě – i bez přímé spojitosti s původní částicí.

Tento efekt je chápán jako **strukturální echo**: prostorová paměť bodu, která ovlivní trajektorii budoucích částic.

---

## Stav testování

- ✅ Simulace s `LOW_NOISE_MODE = True`, `TEST_EXHALE_MODE = True`
- ✅ Opakovaný výskyt částic v bodech `[127, 0]` (882×) a `[127, 127]` (~600×)
- ✅ Výskyt oddělený v čase, přesto se částice vrací do stejného místa
- ✅ Vizualizace návratové hustoty potvrzena (`lineum_return_density_*.png`)
- 🔄 Hypotéza **pozorována**, ale není kvantifikována pro celé pole

---

## Metodika výpočtu

### Parametry simulace:

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

### Výstupy:

- `true_trajectories.csv` – časový vývoj pozice všech částic
- `lineum_return_density_127_0.png`, `lineum_return_density_127_127.png` – vizuální histogram výskytu

---

## Vizualizace

![](../output/lineum_return_density_127_0.png)  
_Výskyt částic v čase poblíž bodu [127, 0]_

![](../output/lineum_return_density_127_127.png)  
_Výskyt částic v čase poblíž bodu [127, 127]_

---

## Závěr

Lineum vykazuje schopnost uchovat prostorovou paměť: bod, kde došlo k zániku částice, se později opakovaně stává cílovým místem pro jinou. Tento návratový efekt nevzniká náhodně, ale zřejmě působením lokálního gradientu φ.

Hypotéza naznačuje, že **pole si pamatuje nejen co se stalo, ale i kde se to stalo**. A někdy se do těchto míst **vrací** – jako ozvěna.

---

## Doporučené další testy

- Kvantifikovat výskyt návratu napříč celou mřížkou (hustotní mapa návratů)
- Testovat různé režimy (`LOW_NOISE_MODE = False`) pro zjištění, zda echo efekt přetrvá
- Zavést umělý „zánik“ částice a sledovat, zda se do místa navrátí nová
- Měřit vliv gradientu φ v okolí bodu návratu (`∇φ`)

---

## Odkazy

- `true_trajectories.csv`
- `lineum_return_density_127_0.png`
- `lineum_return_density_127_127.png`
- připraveno jako hypotéza v `09-hypotheses.md`
