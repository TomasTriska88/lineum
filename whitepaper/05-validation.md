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
| Echo návrat částic      | [`true_trajectories.csv`](../output/true_trajectories.csv) – opakovaný výskyt částic ve stejných souřadnicích v čase (např. [127, 0]) | ✔️ pozorováno         |
| Migrace vírových jader | `frames_curl.npy`, centroid tracking – dominantní vír sleduje souvislou dráhu v čase | ✔️ potvrzeno |
<!-- prettier-ignore-end -->

## 5.2.1 Výsledky běhů `spec1` a `spec2`

### Testovací sada `spec1`

| Běh           | Konfigurace                                | Výstupy                                                         | Pozorování                                                                     |
| ------------- | ------------------------------------------ | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `spec1_true`  | `exhale_mode=True`, `low_noise_mode=True`  | `spin_aura_avg.png`, `phi_curl_low_mass.csv`, `frames_curl.npy` | Stabilní struktury, 49 tichých zániků φ, dipólová spin aura                    |
| `spec1_false` | `exhale_mode=True`, `low_noise_mode=False` | stejné                                                          | Téměř stejné tiché zániky (46/49), větší spinová aktivita, aura stále dipólová |

### Vyhodnocení

- **Tříska’s Silent Collapse Hypothesis:** potvrzena – částice zanikají při φ > 0.25 a |curl| < 0.02, bez strukturální stopy
- **Tříska’s Resonant Seed Hypothesis:** potvrzena – tiché zániky přítomné ve všech bězích, nezávisle na šumu
- **Tříska’s Tensor Spin Hypothesis:** neprokázána – žádná čtyřnásobná symetrie, spin aura vždy dipólová
- **Tříska’s Dimensional Transparency Hypothesis:** zatím neprokázána – gradientní κ sice ukazuje slábnutí struktur, ale bez ostrovního κ nelze hypotézu o průhlednosti potvrdit

---

### Testovací sada `spec2`

| Běh           | Konfigurace                                              | Výstupy                                                          | Pozorování                                                        |
| ------------- | -------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------- |
| `spec2_true`  | `exhale_mode=True`, `low_noise_mode=True`, `κ = ostrov`  | `phi_curl_low_mass.csv`, `spin_aura_avg.png`, `trajectories.csv` | Zániky φ koncentrované ve φ-ostrově, částice mimo κ okamžitě mizí |
| `spec2_false` | `exhale_mode=True`, `low_noise_mode=False`, `κ = ostrov` | stejné                                                           | Mimo κ nejsou částice ani víry, struktura mizí – potvrzení DTH    |

### Vyhodnocení

- **Tříska’s Dimensional Transparency Hypothesis:** potvrzena – struktura vzniká a drží se jen tam, kde je κ > 0
- **Tříska’s Resonant Seed Hypothesis:** potvrzena – tiché zániky přítomné i při vyšším šumu
- **Tříska’s Silent Collapse Hypothesis:** potvrzena – částice zanikají bez vírové stopy
- **Tříska’s Tensor Spin Hypothesis:** znovu neprokázána

---

## 5.3 Hypotézy zatím bez potvrzení

- Vznik stabilních komplexních struktur z vírů (atomy),
- Spontánní oscilace s kvantovanými hladinami,
- Emergentní elektromagnetické pole jako pole curl(ψ),
- Dlouhodobá konzervace celkové energie v poli ψ a interakčním poli φ

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

## 5.6 Shrnutí

Současná fáze vývoje systému Lineum umožňuje spolehlivou detekci základních emergentních jevů. Většina z nich je potvrzena jak vizuálně, tak číselně. Statistické metody budou aplikovány v dalších iteracích výzkumu. Všechny hypotézy jsou formulovány otevřeně a ověřitelnost je klíčovým cílem projektu.

Dále bylo zjištěno, že některé vlastnosti – především hmotnost kvazičástic – vyžadují delší časový vývoj ke své plné manifestaci. V kratších simulacích může být spektrální energie podhodnocená, což není nedostatek modelu, ale přirozený důsledek frekvenční rozlišovací schopnosti. To ukazuje, že i čas samotný může být klíčem k emergenci „reálnějších“ struktur.
