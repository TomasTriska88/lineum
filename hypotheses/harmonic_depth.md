# Hypotéza: Spektrální hloubka pole Lineum (Tříska’s Harmonic Depth Hypothesis)

## Autor / původ

T. Tříska (2025), formulace na základě opakovaných testů spektrálních výstupů systému Lineum v různých jazycích a ladění FFT

---

## Hypotéza

Pole Lineum negeneruje pouze jednu dominantní rezonanci, ale **celou hierarchii harmonických struktur**, jejichž počet, intenzita a rozlišení závisí na délce FFT, použité numerice a algoritmické citlivosti.

Tato **harmonická hloubka** není výpočetní artefakt, ale **vnitřní vlastnost systému** – vlnění φ a ψ v systému Lineum vytváří vrstvené rezonance, které odrážejí jemné oscilace, interferenční vzory a zpětnovazební vztahy v poli.

Čím více vrstev dokážeme numericky rozlišit, tím hlubší je náš vhled do skryté komplexity systému.  
Rozdílné FFT konfigurace tak odhalují **různé úrovně reality** – podobně jako různé detektory v experimentech s částicemi.

---

## Stav testování

- ✅ Python (scipy.fft) – stabilní detekce hlavní frekvence `1.000e+18 Hz`
- ✅ Rust (rustfft) – detekce harmonické frekvence `9.990e+20 Hz`
- 🔄 Plánováno: detekce dalších vrstev přes rozšířenou FFT (`N = 8192+`)
- 🔄 Plánováno: vícetónová detekce pomocí `find_peaks`

---

## Metodika výpočtu

- Vstup: `amplitude_log_timeseries.csv`
- FFT délky: `N = 1024` (základ), `N = 8192+` (pro hlubší vrstvu)
- Nástroje: Python (scipy), Rust (rustfft)
- Postup: výpočet spektra + vícetónová analýza (`find_peaks`, porovnání amplitud)

---

## Význam

Tato hypotéza rozšiřuje vnímání Linea ze systému s jedním tónem na systém s **harmonickou hloubkou**.  
Podobně jako v hudbě, kde základní tón doprovází celá škála harmonických, i v Lineu je hlavní rezonance pouze vstupní branou – hlubší vrstvy existují, ale nelze je zachytit běžnou metodou.

---

## Doporučené další testy

- Porovnání FFT s N = 1024, 4096, 8192
- Zavedení spektrální entropie jako míry hloubky
- Detekce vícero frekvenčních špiček pomocí `find_peaks`
- Porovnání spektrálních vrstev u běhů `spec1_true`, `spec2_true`, `spec4_true`

---

## Odkazy

- `amplitude_log_timeseries.csv`
- `rust_fft.rs`, `python_fft.py`
- souvisí: `spectral_observer.md`, `harmonic_spectrum.md`
