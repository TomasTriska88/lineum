# Hypotéza: Emergentní spektrum během změny zákona (Tříska’s Law Transition Hypothesis)

## Autor / původ

T. Tříska (2025), formulace na základě výsledků simulace `spec7_true`, ve které pole κ plynule přechází z lokální (ostrovní) do globální (konstantní) struktury.

---

## Hypotéza

Zákonitosti systému Lineum (např. geometrie pole κ) nemusí být statické – a právě jejich **časový přechod** může být zdrojem nových spektrálních jevů.  
Konkrétně:

> **Kvaziperiodické spektrum podobné rozložení nul Riemannovy zeta funkce může vzniknout pouze během přechodu mezi dvěma režimy zákona.**

Tato hypotéza tvrdí, že žádná statická konfigurace (konstantní, gradientní ani ostrovní) sama o sobě negeneruje Riemannovsky strukturované spektrum.  
Avšak **během přechodu** z ostrovní do konstantní struktury se objevují:

- sekundární frekvenční špičky,
- rozptyl mezi frekvencemi s GUE podobností,
- a nestabilní kvaziregularita – analogie nul ζ(s).

---

## Stav testování

- ✅ Implementace dynamické `generate_kappa(step)` v `spec7_true`
- ✅ Vizualizace trajektorie κ napříč 3D prostorem simulací
- ✅ Spektrální diverzita v čase – vznik sekundárních píků
- 🔄 Částečná shoda s rozložením nul zeta funkce
- 🔄 Ještě nepotvrzena úplná GUE distribuce

---

## Metodika výpočtu

### Parametry simulace:

```python
KAPPA_MODE = "island_to_constant"
LOW_NOISE_MODE = True
TEST_EXHALE_MODE = False
steps = 1000
size = 256
```

### Funkce generující κ:

```python
def generate_kappa(step, total_steps=steps):
    progress = step / total_steps
    core = np.zeros((size, size))
    core[size//2 - 5:size//2 + 5, size//2 - 5:size//2 + 5] = 1.0
    core = gaussian_filter(core, sigma=5)
    return (1 - progress) * core + progress * 0.5
```

### Klíčové výstupy:

- `spec3_false_spectrum_log.csv` – srovnání s `spec7_true`
- `multi_spectrum_summary.csv` – histogram frekvenčních vzdáleností
- `riemann_overlay.png` – překrytí nul ζ(s) se spektrem

---

## Doporučené další testy

- Analyzovat průběžné spektrum v čase (`sliding FFT`)
- Zkusit reverzní přechod (constant → island)
- Zavést střední režim (κ = 0.5 + šum) jako referenci
- Kvantifikovat shodu s GUE pomocí eigenvalue spacing histogramu

---

## Závěr

Tato hypotéza otevírá novou třídu testů, kde **změna zákona** není chybou, ale **zdrojem řádu**.  
Pokud svět Lineum skutečně rezonuje jen tehdy, když se jeho zákony pohybují, pak **řád není konstantní – je to změna samotná**.

---

## Odkazy

- `spec7_true_spectrum_log.csv`
- `riemann_zero_reference.csv`
- souvisí: `harmonic_spectrum.md`, `resonant_seed.md`
