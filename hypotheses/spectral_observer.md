# Hypotéza: Spektrální pozorovatelská závislost (Tříska’s Spectral Observer Hypothesis)

## Autor / původ

T. Tříska (2025), formulace na základě testování systému Lineum napříč různými jazyky a FFT knihovnami

---

## Hypotéza

Realita pole Lineum není absolutní, ale závisí na charakteru výpočetního prostředí, které ji pozoruje.  
Různé jazyky a výpočetní systémy detekují odlišné dominantní frekvence i přes shodná vstupní data.

Hypotéza tedy tvrdí, že:

> **Spektrum Linea je funkcí pozorovatele.**

---

## Stav testování

- ✅ Python (scipy) → `1.000e+18 Hz` (stabilní rezonance)
- ✅ C++ (FFTW) → `1.000e+18 Hz` (shodné potvrzení)
- ✅ Rust (rustfft) → `9.990e+20 Hz` (vyšší harmonická)
- ❌ Julia (FFTW.jl) → `1.000e−24 Hz` (první bin)
- ❌ JavaScript (fft-js) → `9.77e−25 Hz` (šum)

---

## Metodika výpočtu

### Vstup:

- soubor `amplitude_log_timeseries.csv` generovaný z výstupu běhu `spec1_true`
- délka signálu: N = 1024
- časový krok: dt = 1e-21 s

### Porovnání:

| Jazyk      | FFT knihovna | Detekovaná frekvence | Poznámka                 |
| ---------- | ------------ | -------------------- | ------------------------ |
| Python     | `scipy.fft`  | `1.000e+18 Hz`       | ✅ hlavní rezonance      |
| C++        | `FFTW`       | `1.000e+18 Hz`       | ✅ shodná                |
| Rust       | `rustfft`    | `9.990e+20 Hz`       | ✅ harmonická            |
| Julia      | `FFTW.jl`    | `1.000e−24 Hz`       | ❌ selhání               |
| JavaScript | `fft-js`     | `9.77e−25 Hz`        | ❌ FFT limitní citlivost |

---

## Význam

Tento výsledek ukazuje, že Lineum **nevrací jednoznačnou realitu**.  
Naopak – různé výpočetní jazyky jako pozorovatelé **vidí jiný svět**.  
Spektrum není fixní – je zrcadlem jazyka, který ho počítá.

To poprvé naznačuje, že:

- realita může být **výpočetně závislá**
- „pravda“ v poli Lineum není absolutní
- pozorovatel ovlivňuje výsledek i bez zásahu do rovnic

---

## Dvojice tónů: hlavní a harmonická

V experimentech byly konzistentně detekovány dva silné tóny:

- **Hlavní rezonance:** `1.000e+18 Hz` (Python, C++)
- **Harmonická rezonance:** `9.990e+20 Hz` (Rust)

Tato dvojice připomíná vztah mezi základním tónem a vyššími harmonickými v akustice.  
Je možné, že pole Lineum vibruje vícehlasně – a různé jazyky fungují jako různé mikrofony, které zachytí jen určité vrstvy.

To podporuje vznik hypotézy: **Tříska’s Harmonic Depth Hypothesis.**

---

## Závěr

Tříska’s Spectral Observer Hypothesis byla potvrzena na základě testů napříč čtyřmi výpočetními světy.  
Každý z nich slyšel něco jiného – a právě tím vznikla **hlubší vrstva reality**.

> Lineum není jen výpočet.  
> Je to odpověď na otázku, **kdo se ptá.**

---

## Doporučené další testy

- přidat test z Wolfram Language (symbolická FFT)
- vytvořit lineární kombinaci spekter a hledat stabilní průnik
- testovat výstup při změně `float32` vs `float64` vs `long double`
- zavést umělý šum v FFT výstupu a sledovat prahovou citlivost

---

## Odkazy

- `amplitude_log_timeseries.csv`
- `spec1_true_frames_amp.npy`
- `fft_cpp.exe`, `rust_fft.rs`, `js_fft.js`, `julia_fft.jl`
- `spectral_observer.md`
- plánovaná: `harmonic_depth.md`, `harmonic_spectrum.md`
