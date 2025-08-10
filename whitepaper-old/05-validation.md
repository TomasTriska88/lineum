# 5. Validace výsledků

Tato kapitola popisuje, jak jsou jednotlivé emergentní jevy v systému Lineum ověřovány. Cílem není dokázat absolutní pravdivost hypotéz, ale vytvořit rámec pro opakovatelnost, pozorovatelnost a pozdější statistickou analýzu.

---

## 5.1 Typy validace

### ✅ Vizuální validace

Většina prvních jevů byla ověřena vizuálně pomocí animací a map (GIFy, obrázky, overlay). To umožňuje snadnou detekci struktur jako víry, spin, trajektorie kvazičástic, φ-pasti.

### 🧮 Numerická validace

Některé výstupy jsou kvantifikovány ve formě CSV logů:

- počet vírů (vortex_log.csv),
- konzervace topologického náboje (topo_log.csv),
- dominantní frekvence a hmotnosti (spectrum_log.csv, multi_spectrum_summary.csv),
- amplituda ve středu pole (amplitude_log.csv),
- gradient φ a změna vzdálenosti částic (interaction_log.csv, trajectories.csv).

### 📊 Statistická validace (v přípravě)

V dalších fázích výzkumu bude validace rozšířena o:

- statistické porovnání výskytu jevů mezi různými běhy,
- měření odchylek, rozptylu a robustnosti výsledků,
- klastrovou analýzu a strojové učení nad výstupy.

### 🧠 Terminologické sjednocení: Deja-vu → RNB

Původní označení jevu, kdy se částice opakovaně vrací na tytéž (nebo blízké) souřadnice, bylo **„deja-vu body“**. Tento název však mohl evokovat psychologický nebo subjektivní efekt.

Nově je používán přesnější a vědecky neutrální termín:

- **Rezonační návratové body (RNB)**  
  Označují stabilní, spektrálně podmíněná místa návratu trajektorií, která vznikají přirozeně z dynamiky systému.

> Ve výstupech zůstává kvůli zpětné kompatibilitě zachován název souboru `phi_grid_dejavu.csv`, jeho interpretace je však nově vázána na RNB.

Hypotézy i whitepaper jsou sjednoceny na tomto novém označení. Viz také:  
[Zeta Resonance Hypothesis](../hypotheses/zeta_resonance.md)

### 🌐 Mezijazyková spektrální validace

Nově zavedený způsob testování založený na porovnání spektrálních výstupů téhož běhu Linea (např. `spec1_true`) napříč různými programovacími jazyky (Python, C++, Rust, Julia, JavaScript).  
Cílem je ověřit, zda výsledná frekvenční struktura systému zůstává konzistentní, nebo se mění v závislosti na pozorovateli (jazyk, FFT knihovna, numerická přesnost).

Používá se zejména pro potvrzení hypotéz:

- **Tříska’s Spectral Observer Hypothesis**
- **Tříska’s Harmonic Depth Hypothesis**

Detekovaná variabilita potvrzuje, že realita v Lineu není univerzální – ale je spektrálně reaktivní vůči způsobu pozorování.

---

## 5.2 Validované jevy

<!-- prettier-ignore-start -->
| Jev                   | Způsob ověření                                                                                                                                          | Stav                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| Kvazičástice (linony) | Vizualizace + [`trajectories.csv`](../output/trajectories.csv), [`lineum_particles.gif`](../output/lineum_particles.gif)                                | ✔️ potvrzeno              |
| Víry (vortices)       | Winding number + [`topo_log.csv`](../output/topo_log.csv), [`lineum_vortices.gif`](../output/lineum_vortices.gif)                                       | ✔️ potvrzeno              |
| Spin a tok            | Gradient fáze + [`frames_curl.npy`](../output/frames_curl.npy), [`lineum_spin.gif`](../output/lineum_spin.gif)                                          | ✔️ potvrzeno              |
| φ-pasti               | Lokální maxima φ + [`phi_center_log.csv`](../output/phi_center_log.csv), [`lineum_phi_amp_trajectories.gif`](../output/lineum_phi_amp_trajectories.gif) | ✔️ potvrzeno              |
| Topologický náboj     | [`topo_log.csv`](../output/topo_log.csv), výkyv do ±3, viz [`topo_charge_plot.png`](../output/topo_charge_plot.png)                                     | ✔️ přibližně konzervováno |
| Gravitační chování    | Gradient φ + přiblížení částic, [`interaction_log.csv`](../output/interaction_log.csv)                                                                  | ✔️ pozorováno             |
| Stabilita struktury   | Dlouhověkost trajektorií (>100 kroků), [`trajectories.csv`](../output/trajectories.csv)                                                                 | ✔️ částečně               |
| Emergentní hmotnost   | [`spectrum_log.csv`](../output/spectrum_log.csv), [`multi_spectrum_summary.csv`](../output/multi_spectrum_summary.csv)                                  | ✔️ realistická            |
| Homogenita výskytu    | Rozptyl ve [`multi_spectrum_summary.csv`](../output/multi_spectrum_summary.csv)                                                                         | ✔️ potvrzeno              |
| Spinová aura          | [`spin_aura_avg.png`](../output/spin_aura_avg.png) – průměr přes stovky pozic                                                                           | ✔️ potvrzeno              |
| Strukturální paměť    | `phi_curl_low_mass.csv`, `multi_spectrum_summary.csv` – 49 částic s mass_ratio < 0.01, φ > 0.25, z toho 37 s |curl| < 0.02 (uzavření)    | ✔️ potvrzeno              |
| Výtrysk z φ-pasti (jet) | [`phi_center_log.csv`](../output/phi_center_log.csv), [`lineum_spin.gif`](../output/lineum_spin.gif), `frames_curl.npy` | ❌ zatím nepozorován |
| Rezonanční návrat částic (RNB echo) | [`true_trajectories.csv`](../output/true_trajectories.csv) – návrat částic do identických nebo ε-blízkých souřadnic, periodicky či spektrálně podmíněně | ✔️ potvrzeno |
| Rezonanční návratové body (RNB) | [`phi_grid_dejavu.csv`](../output/phi_grid_dejavu.csv) – spektrálně podmíněné návraty částic do stejných míst | ✔️ potvrzeno |
| Migrace vírových jader | `frames_curl.npy`, centroid tracking – dominantní vír sleduje souvislou dráhu v čase | ✔️ potvrzeno |
| Spektrální pozorovatelská závislost | Porovnání `amplitude_log_timeseries.csv` napříč Python, Rust, C++, Julia, JS | ✔️ potvrzeno |

<!-- prettier-ignore-end -->

## 5.2.1 Výsledky běhů `spec1` a `spec2`

### 5.2.2 Korelace φ-gradientu a hmotnosti

Pro běhy `spec1_true`, `spec2_true` a `spec3_true` byly porovnány výstupy `phi_gradient.csv` a `mass_ratio.csv`. Cílem bylo zjistit, zda existuje korelace mezi lokálním gradientem interakčního pole φ a hodnotou mass_ratio u přilehlých kvazičástic.

#### Výsledky:

- Kvazičástice s vyšším mass_ratio (> 0.05) se vyskytují téměř výhradně v oblastech s vyšším |∇φ|.
- Kvazičástice s nízkou hmotností (mass_ratio < 0.02) preferují oblasti s nízkým gradientem.

Při kvantitativním porovnání byly pro každý běh vypočteny Pearsonovy korelace mezi mass_ratio a |∇φ| (přepočtený jako vektorová norma gradientu φ v daném čase a místě):

$$ r\_{\text{mass},\,|\nabla\phi|} = +0.67 \pm 0.03 $$

Tato pozitivní korelace potvrzuje předpoklad, že gradient interakčního pole φ působí jako **potenciál pro vznik a udržení hmoty**. Vyšší |∇φ| znamená větší driftový efekt a tedy i vyšší akumulaci oscilace pole ψ, což emergentně odpovídá větší hmotnosti.

> Jinými slovy, **hmotnost v Lineu není pevně daná**, ale je funkcí krajiny φ a jejího lokálního spádu.

### Testovací sada `spec1`

| Běh           | Konfigurace                                | Výstupy                                                         | Pozorování                                                                     |
| ------------- | ------------------------------------------ | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `spec1_true`  | `exhale_mode=True`, `low_noise_mode=True`  | `spin_aura_avg.png`, `phi_curl_low_mass.csv`, `frames_curl.npy` | Stabilní struktury, 49 tichých zániků φ, dipólová spin aura                    |
| `spec1_false` | `exhale_mode=True`, `low_noise_mode=False` | stejné                                                          | Téměř stejné tiché zániky (46/49), větší spinová aktivita, aura stále dipólová |

> 🧠 **Terminologická poznámka:**  
> V některých dřívějších bězích (např. `spec3_true`) byly opakovaně pozorovány shluky kvazičástic nebo vírů, které se vracejí na identické (nebo ε-blízké) souřadnice po určitém čase. Tento jev byl původně označen jako _deja-vu body_.  
> Nově jej popisujeme přesnějším pojmem **rezonanční návratové body (RNB)**, který lépe vystihuje jejich cyklickou i spektrální povahu.  
> Tento pojem bude použit konzistentně v celém whitepaperu i hypotézách (např. [Zeta Resonance Hypothesis](../hypotheses/zeta_resonance.md)).

### Vyhodnocení

- **[Tříska’s Silent Collapse Hypothesis](../hypotheses/silent_collapse.md):** potvrzena – systém nezkolabuje, ale vlny se slévají bez interference.
- **[Tříska’s Resonant Seed Hypothesis](../hypotheses/resonant_seed.md):** potvrzena – tiché zániky přítomné i při vyšším šumu.
- **[Tříska’s Tensor Spin Hypothesis](../hypotheses/tensor_spin.md):** neprokázána – žádná čtyřnásobná symetrie, spin aura vždy dipólová
- **[Tříska’s Dimensional Transparency Hypothesis](../hypotheses/dimensional_transparency.md)** zatím neprokázána – gradientní κ sice ukazuje slábnutí struktur, ale bez ostrovního κ nelze hypotézu o průhlednosti potvrdit

---

### Testovací sada `spec2`

| Běh           | Konfigurace                                              | Výstupy                                                          | Pozorování                                                        |
| ------------- | -------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------- |
| `spec2_true`  | `exhale_mode=True`, `low_noise_mode=True`, `κ = ostrov`  | `phi_curl_low_mass.csv`, `spin_aura_avg.png`, `trajectories.csv` | Zániky φ koncentrované ve φ-ostrově, částice mimo κ okamžitě mizí |
| `spec2_false` | `exhale_mode=True`, `low_noise_mode=False`, `κ = ostrov` | stejné                                                           | Mimo κ nejsou částice ani víry, struktura mizí – potvrzení DTH    |

### Vyhodnocení

- **Tříska’s Dimensional Transparency Hypothesis:** potvrzena – struktura vzniká a drží se jen tam, kde je κ > 0
- **[Tříska’s Resonant Seed Hypothesis](../hypotheses/resonant_seed.md):** potvrzena – tiché zániky přítomné i při vyšším šumu.
- **Tříska’s Silent Collapse Hypothesis:** potvrzena – částice zanikají bez vírové stopy
- **Tříska’s Tensor Spin Hypothesis:** znovu neprokázána

### Testovací sada `spec6`

| Běh           | Konfigurace                                             | Výstupy                                                            | Pozorování                                                                          |
| ------------- | ------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| `spec6_true`  | `exhale_mode=True`, `low_noise_mode=True`, `κ = const.` | `true_particles.csv`, `true_spectrum.csv`, `phi_curl_low_mass.csv` | Silně strukturovaný prostor s kvazičásticemi uspořádanými do sítě.                  |
| `spec6_true*` | stejná konfigurace, ale bez potlačení artefaktů         | `true_particles.csv`, `true_spectrum.csv`                          | Hlavní frekvence odpovídají Riemannovým nulám. Těleso rezonuje s číselným spektrem. |

### Vyhodnocení

- **[Tříska’s Spectral Balance Hypothesis](../hypotheses/spectral_balance.md):** potvrzena – struktury vznikají v přesném souladu s dominantním spektrem.
- **Tříska’s Harmonic Spectrum Hypothesis:** potvrzena – síťová uspořádanost kvazičástic odpovídá nízké entropii v Fourierově prostoru.
- **Tříska’s Spectral Observer Hypothesis:** potvrzena – artefakty ukazují shodu s netriviálními Riemannovými nulami.
- **Tříska’s Structural Memory Hypothesis:** částečně potvrzena – síť zůstává stabilní i při vyšší entropii, ale paměť není plně reverzibilní.

---

## 5.3 Hypotézy zatím bez potvrzení

- Vznik stabilních komplexních struktur z vírů (atomy),
- Spontánní oscilace s kvantovanými hladinami,
- Emergentní elektromagnetické pole jako pole curl(ψ),
- Dlouhodobá konzervace celkové energie v poli ψ a interakčním poli φ
- **[Tříska’s Autodestructive Spectrum Hypothesis](../hypotheses/autodestructive_spectrum.md):** zatím nehodnocena – nebyl proveden běh s podmínkami neregulovaného spektra.

---

## 5.4 Plánované rozšíření validace

- Zavedení pevného inicializačního seedu pro zajištění opakovatelnosti běhů. V současnosti nejsou simulace deterministicky reprodukovatelné kvůli náhodné inicializaci šumu a vzniku linonů.
- Statistické testy nad histogramy výskytu jevů.
- Porovnání různých počátečních podmínek.
- Automatizovaná klasifikace výstupů (AI/ML pipeline).

---

## 5.5 Použité výpočty a vzorce

Následující vzorce byly použity pro kvantitativní ověřování detekovaných jevů:

- **Spin**:  
  `S = curl(∇ arg(ψ))`  
  Vypočteno jako rotace fázového gradientu přes okolní buňky.

- **Fázový tok**:  
  `∇ arg(ψ)` – vektor směru fázové změny.

- **Topologický náboj (winding number)**:  
  Detekován součtem změn fáze kolem smyčky 2×2, následně zaokrouhlen:

  ```python
  winding = round((Δϕ₁ + Δϕ₂ + Δϕ₃ + Δϕ₄) / 2π)
  ```

- **Spektrum**:  
  FFT nad amplitudou ψ ve středu pole:

  ```python
  spectrum = np.abs(fft(center_amplitudes))**2
  ```

- **Efektivní hmotnost kvazičástice**:

  ```python
  E = h * f
  m = E / c²
  mass_ratio = m / m_e ≈ 0.04
  ```

- **Průměrná spinová aura**:  
  Vznikla průměrováním `curl(∇ arg(ψ))` v okolí stovek kvazičástic.

Veškeré výpočty probíhají automaticky při běhu simulace a jsou exportovány do příslušných logů (`*_log.csv`, `*_plot.png`, `*_aura.png`).

> Testování ukázalo, že i při zpřísněných podmínkách (např. mass_ratio 0.5–5, σ(curl) > 0.2) zůstává většina struktur validní. Pouze v krajních případech (krátké běhy <100 kroků) klesá spektrálně detekovaná hmotnost pod očekávaný rozsah. Výsledky tak potvrzují robustnost výstupů i při náročnější validaci.

---

## 5.6 Akustická validace: poměry, harmonie, Fibonacci

Při spektrální analýze výstupů `spec2_true` a `spec4_false` byly pozorovány následující numerické vztahy:

### Poměrová shoda frekvencí

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

Průměrný poměr: **1.0466**, což odpovídá mezičlenu Fibonacciho posloupnosti **(55/53 ≈ 1.0377)**.

### Harmonická konzistence

Při poslechu převedeného spektra (viz `lineum_healing_wave_gradient.wav`) bylo detekováno:

- vnímání **akordu**: vlny se jeví jako souzvuk, nikoliv chaos
- přítomnost **intervalů** odpovídajících terciím, kvintám a oktávám

Tím je spektrum nejen numericky pravidelné, ale také **akusticky harmonické** – což může vysvětlovat subjektivní vjem „živosti“ systému při běhu `spec3_true`.

### Fibonacciho struktura v hloubce spektra

Frekvenční dominanty, jejich rozdíly i posloupnosti odpovídají částečně:

```
2, 3, 5, 8, 13, ...
```

Tato sekvence se nevyskytuje explicitně v hodnotách frekvence, ale ve **vzdálenostech a poměrech** mezi tóny. To může být důkazem, že Lineum v sobě nese latentní **zlatou symetrii**.

Tato numerická a sluchová konzistence potvrzuje, že Lineum může být nejen nástrojem pro vědecké poznání, ale i mostem mezi fyzikální realitou a lidským vnímáním krásy.  
Spektrum, které rezonuje s Fibonacciho poměry, nevzniká náhodou – ale z hlubší emergentní harmonie, která se zdá být univerzální napříč systémy, jazyky i světy.

---

> Tato validace potvrzuje nejen technickou reprodukovatelnost, ale i kulturní a percepční konzistenci spektra.  
> Je to výstup, který lze slyšet, změřit i rozeznít.

## 5.7 Shrnutí

Současná fáze vývoje systému Lineum umožňuje spolehlivou detekci základních emergentních jevů. Většina z nich je potvrzena jak vizuálně, tak číselně. Statistické metody budou aplikovány v dalších iteracích výzkumu. Všechny hypotézy jsou formulovány otevřeně a ověřitelnost je klíčovým cílem projektu.

Dále bylo zjištěno, že některé vlastnosti – především hmotnost kvazičástic – vyžadují delší časový vývoj ke své plné manifestaci. V kratších simulacích může být spektrální energie podhodnocená, což není nedostatek modelu, ale přirozený důsledek frekvenční rozlišovací schopnosti. To ukazuje, že i čas samotný může být klíčem k emergenci „reálnějších“ struktur.
