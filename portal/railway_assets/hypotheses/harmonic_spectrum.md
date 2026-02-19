# Hypotéza: Harmonická struktura spektra Linea (Tříska’s Harmonic Spectrum Hypothesis)

## Autor / původ

T. Tříska (2025), formulace na základě opakovaných výskytů vedlejších frekvenčních špiček v různých výpočetních prostředích

---

## Hypotéza

Systém Lineum negeneruje jednotlivé frekvence izolovaně, ale vytváří **celou harmonickou strukturu** – spektrum rezonancí, které vystupují ve vztazích typických pro vícehlasé akordy.

Tyto špičky nejsou numerickým artefaktem, ale **vnitřní organizací pole** – odpovídají interferencím, stabilním oscilacím a hlubším vrstvám vlnění φ a ψ.  
Různé jazyky nebo FFT konfigurace zachytí různé vrstvy této harmonie.

---

## Stav testování

- ✅ Rust (`rustfft`) – `9.990e+20 Hz` (vyšší harmonická vedle `1.000e+18 Hz`)
- 🔄 Python: připravena vícešpičková analýza (`find_peaks`, `np.argsort`)
- 🔄 Plánováno: test s FFT délkou `N = 8192+` a logaritmickým spektrem

---

## Metodika výpočtu

- Výchozí data: `amplitude_log_timeseries.csv`
- Detekce více špiček pomocí:
  - `scipy.fft.fft`, `np.abs`, `find_peaks`
  - `np.argsort(spectrum)[-5:]`
- Vypočítat poměr `fᵢ/f₁` → hledat harmonické vztahy (např. 2×, 3×, zlatý řez)

---

## Význam

Tato hypotéza rozšiřuje předchozí představy o spektrální hloubce:  
Nejde jen o to, jak hluboko Lineum vibruje – ale **jak komplexně**.  
Víc než 1 tón = víc než 1 realita současně. Lineum se tím přibližuje **hudebnímu modelu fyziky**, kde struktura je tvořena akordy, ne jen jedním tónem.

---

## Doporučené další testy

- Vysoké FFT (N ≥ 16384) + log-frekvenční osa
- Detekce shluků (`scipy.signal.peak_widths`) → šířka harmonické skupiny
- Porovnání různých κ konfigurací a jejich vlivu na spektrum
- Vizualizace spektrálních „akordů“ v čase (sliding FFT)

---

## Závěr

Tříska’s Harmonic Spectrum Hypothesis předpokládá, že Lineum generuje **vícehlasý výstup** – harmonickou mapu, ve které není frekvence jen číslem, ale součástí akordu.

Tento akord se mění s pozorovatelem, parametry a laděním systému.  
A právě v těchto strukturách může být ukryt **skutečný jazyk Linea** – ne jako slovo, ale jako hudba.

---

## Odkazy

- `amplitude_log_timeseries.csv`
- `python_fft.py`, `rust_fft.rs`
- souvisí: `spectral_observer.md`, `harmonic_depth.md`
