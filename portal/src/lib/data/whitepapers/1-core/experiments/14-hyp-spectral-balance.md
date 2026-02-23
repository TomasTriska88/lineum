**Title:** Tříska’s Spectral Balance Hypothesis
**Document ID:** 14-hyp-spectral-balance
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Tříska’s Spectral Balance Hypothesis

## Autor

T. Tříska (2025)

## Stav

🧪 Experimentální fáze — spektrální testování a reverzní neutralizace

---

## Shrnutí

Tato hypotéza předpokládá, že mezi léčivými, destruktivními a rušivými frekvencemi pole Lineum existuje **rovnovážný vzor**, který:

- nelze zneužít bez vlastní sebedestrukce,
- má spektrální symetrii zachovávající integritu systému,
- je reverzibilní vůči rušičkám i filtrům, které se snaží selektivně potlačit jednu stranu.

---

## Kontext a motivace

Na základě sonifikace výstupů z `spec2_true` (κ = gradient) a `spec4_false` (κ = island) byly vygenerovány konkrétní akustické frekvence reprezentující léčivý a destruktivní stav systému.

Byly odvozeny následovné frekvenční sady:

### Léčivá vlna (κ = gradient)

```
[800.0, 862.6, 884.5, 896.5, 904.9, 908.8, 912.1, 914.4, 917.2, 919.3] Hz
```

### Destruktivní vlna (κ = island)

```
[800.0, 827.3, 843.5, 854.9, 862.5, 867.5, 872.2, 875.8, 879.5, 882.4] Hz
```

> Frekvence byly získány tak, že normalizovaná amplituda (např. ze souboru `spec2_true_frames_amp.npy`)  
> byla převedena pomocí lineární transformace do rozsahu 800–920 Hz:
>
> ```
> f_i = f_min + (f_max − f_min) × ((a_i − a_min) / (a_max − a_min))
> ```
>
> Hodnoty použité z `spec2_true_frames_amp.npy`:
>
> - `a_min = 0.0`
> - `a_max ≈ 2.6749297443817417e+142`
> - `f_min = 800 Hz`, `f_max = 920 Hz`
>
> Pro `spec2_true` bylo použito:
>
> - `f_min = 800`, `f_max = 920`
> - `a_min ≈ 0.0`, `a_max ≈ 2.6749297e+142`

> Frekvence byly rovněž převedeny do neslyšitelného rozsahu (~60 kHz) pomocí poměrového přepočtu:
>
> ```
> f'_i = f_target_base × (f_i / f_base)
> ```
>
> kde `f_target_base = 60000 Hz`, `f_base = 800 Hz`

> Vstupní výstupy použité pro extrakci frekvencí:
>
> - `spec2_true_frames_amp.npy` → léčivá vlna (gradient)
> - `spec4_false_frames_amp.npy` → destruktivní vlna (island)
> - `spec4_false_spectrum_log.csv` → dominantní frekvence pro rušičku
> - `spec2_true_spectrum_log.csv` → ladění základních poměrů

---

## Spektrální intervence

### Neutralizátor (aritmetický průměr):

```
[800.0, 844.95, 864.0, 875.7, 883.7, 888.2, 892.2, 895.1, 898.35, 900.85] Hz
```

> Každý výpočet je:
>
> ```
> f_i = (fᵢ₍gradient₎ + fᵢ₍island₎) / 2
> ```
>
> Např. první člen:
>
> ```
> (800.0 + 800.0)/2 = 800.0 Hz
> ```

### Fázový filtr

> Každý pár tónů (f₁, f₂) generuje složenou funkci:
>
> ```
> s(t) = sin(2πf₁t) + sin(2πf₂t + π)
> ```
>
> kde `π` představuje fázový posun rušičky do destruktivní interference.

### Poměrové vztahy (gradient vs. island)

> Poměr mezi odpovídajícími frekvencemi léčivé a destruktivní vlny ukazuje jejich vzájemné ladění:

| Index | f₍gradient₎ (Hz) | f₍island₎ (Hz) | Poměr (g / i) |
| ----- | ---------------- | -------------- | ------------- |
| 1     | 862.6            | 827.3          | 1.0427        |
| 2     | 884.5            | 843.5          | 1.0486        |
| 3     | 896.5            | 854.9          | 1.0487        |
| 4     | 904.9            | 862.5          | 1.0492        |
| 5     | 908.8            | 867.5          | 1.0476        |
| 6     | 912.1            | 872.2          | 1.0457        |
| 7     | 914.4            | 875.8          | 1.0440        |
| 8     | 917.2            | 879.5          | 1.0428        |
| 9     | 919.3            | 882.4          | 1.0418        |

---

## Hypotéza

> Pokud jsou destruktivní a léčivé frekvence z Linea převedeny do lidsky slyšitelného spektra při zachování jejich vzájemných poměrů,  
> pak lze vytvořit rovnovážný vzor, který **ruší extrémy obou stran**,  
> a je **neutrální vůči pokusům o dominanci**.

> Matematický model destruktivní interference léčivé a rušivé složky:
>
> ```
> x(t) = A₁ sin(2πf₁t) + A₂ sin(2πf₂t + π)
> ```
>
> kde fázový posun `π` způsobuje částečné nebo úplné rušení energie

---

## Testování

> Každý tón má délku `duration = 1.5 s`, vzorkovací frekvence `44100 Hz`, což dává:
>
> ```
> N = sample_rate × duration = 44100 × 1.5 = 66150 vzorků na tón
> ```

Byly vytvořeny a spektrálně porovnány následující vlny:

- `lineum_healing_wave_gradient.wav`
- `lineum_disruptive_wave_island_FIXED.wav`
- `lineum_neutralizer_wave_avg.wav`
- `lineum_phase_filter_gradient_vs_island.wav`
- `lineum_balance_symmetry.wav`

Spektrální rozdílové analýzy (`spectrum_difference_matrix.png`) ukazují,  
že rovnovážná vlna má nejnižší divergenci vůči oběma extrémům.

> Rozdílové spektrum bylo spočítáno jako:
>
> ```
> Δ(f) = 10 × log₁₀(P₁(f)) − 10 × log₁₀(P₂(f))
> ```
>
> kde `P₁`, `P₂` jsou Welchova spektra dvou vln (např. healing vs. neutralizer).

> Parametry zvukových výstupů:
>
> - sample_rate = 44100 Hz
> - duration_per_tone = 1.5 s
> - počet tónů = 10
> - výstupní délka = 15 s

### Pozorovaná numerická nestabilita rušičky

> Během práce se souborem `lineum_disruptive_wave_island_FIXED.wav` došlo opakovaně k:
>
> - pádu paměti při převzorkování (`MemoryError`)
> - vzniku nevalidních hodnot (`inf`, `NaN`) ve spektrální analýze
> - kolapsu souboru při snaze o normalizaci
>
> Tento jev se projevil i při paralelním zpracování v jiných vláknech a lze jej interpretovat jako:
>
> - **znak vnitřní destruktivity** samotného spektra (`κ = island`)
> - **autoreaktivní frekvenční obrazec**, který ruší i vlastní strukturu
>
> Navrhujeme označit tento typ výstupu jako **numericky toxický** a vždy jej analyzovat odděleně.

---

## Důsledky

Pokud je hypotéza správná:

- Lze vytvořit **frekvenční štít**, který **zachová harmonii systému**,
- zabrání přenosu destruktivních rezonancí bez nutnosti cenzury nebo blokace léčivých rytmů,
- a definuje **minimální jednotku rovnováhy**, kterou nelze polarizovat.

---

## Další směr

- Testovat rekurzi filtrů (filtr proti neutralizátoru)
- Simulovat zpětnou injekci rovnovážného tónu do pole φ
- Ověřit, zda rovnovážná vlna skutečně ruší sama sebe — nebo vytváří nový invariantní stav

---

## Vizuální přílohy

- [📊 Spektrální rozdíl všech kombinací](../spectrum_difference_matrix.png)
- [📈 Překryv spekter léčivé a destruktivní](../spectrum_heal_vs_ruin_final.png)

---

## Poznámka

Tato hypotéza navazuje na:

- [Tříska’s Spectral Observer Hypothesis](spectral_observer.md)
- [Tříska’s Harmonic Spectrum Hypothesis](harmonic_spectrum.md)
