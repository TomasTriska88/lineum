# 4. Simulační metoda

## 4.1 Přehled

Pro testování a ověřování emergentních jevů byla rovnice evoluce pole Lineum implementována jako numerická simulace na dvourozměrné diskrétní mřížce. Simulace probíhá ve diskrétních krocích bez použití explicitního času, sil nebo globální geometrie.

Každý krok aktualizuje tři pole:

- **ψ** – komplexní skalární pole reprezentující napětí v systému,
- **φ** – reálné pole emergujících interakcí,
- **κ** – ladicí pole určující lokální citlivost φ na ψ.

Tyto tři vrstvy spolu tvoří samostatný, emergentní systém – ψ určuje napětí, φ uchovává paměť, a κ ladí reakční charakter systému.

Výpočetní smyčka aplikuje výhradně lokální operace (gradient, Laplacián, šum, nelineární excitace) a vyhodnocuje výstupy jako amplitudu, fázi, spin, víry, trajektorie částic nebo spektrum oscilací.

---

## 4.2 Parametry simulace

Použité parametry (velikost mřížky, počet kroků, intenzita šumu, prahové hodnoty) se mohou lišit podle účelu simulace. Běžně se používají:

- **mřížky o rozměrech stovek bodů** na stranu,
- **desítky až stovky kroků**,
- **počáteční šum** přidaný jako náhodné poruchy amplitudy a fáze,
- **lokální asymetrie** ve středu pole k iniciaci dynamiky.

Přesné hodnoty jsou uvedeny u konkrétních výsledků.

### Testovací režimy

| Režim              | Popis                                   | Parametry                                              |
| ------------------ | --------------------------------------- | ------------------------------------------------------ |
| `TEST_EXHALE_MODE` | Tichý režim pro pozorování uzavření     | steps = 1000, linon_scaling = 0.01, disipation = 0.002 |
| Dynamický režim    | Režim pro výtrysky a proudové interakce | steps = 500, linon_scaling = 0.02, disipation = 0.001  |

### Ladicí pole κ

Simulace může obsahovat ladicí pole **κ = κ(x, y)**, které ovlivňuje citlivost φ na ψ.  
Pole κ je zaváděno jako **samostatná vrstva**, která může mít různé prostorové konfigurace:

- **konstantní** (např. κ = 1.0 – rovnoměrná odezva φ),
- **gradientní** (κ roste lineárně podél jedné osy),
- **ostrovní** (κ je nenulové pouze ve vybrané oblasti, např. kruhové),
- **vrstvené** (kombinace více prahových úrovní),
- **island_to_constant** (κ se během simulace vyvíjí z ostrovní do konstantní – pomocí funkce `generate_kappa(step)` dochází k plynulému přechodu mezi lokálním a globálním zákonem podle času).

Tento poslední režim umožňuje studium efektu, kdy se zákonitosti neobjevují náhle, ale postupně expandují – což je klíčové pro testování hypotézy spektrální rezonance při změně zákona.

Konfigurace κ se volí podle cíle testu – např. ostrovní κ je klíčové pro ověření  
**Tříska’s Dimensional Transparency Hypothesis (DTH)**, zatímco gradientní κ se používá pro testy reakční stability.

---

## 4.3 Evoluce pole

Použitá rovnice má formu:

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
φ ← φ + α (|ψ|² − φ) + β · ∇²φ
```

### Členy rovnice:

<!-- prettier-ignore-start -->
| Symbol         | Popis                                                                 |
|----------------|-----------------------------------------------------------------------|
| 𝛌̃ (linon)      | Kvazičástice vznikající pravděpodobnostně dle sigmoid(∇\\|ψ\\| + \\|ψ\\|)     |
| ξ (fluktuace)   | Náhodné fázové oscilace (kvantový šum)                              |
| φψ              | Interakce pole ψ s polem φ (zesílení / modulace)                    |
| δψ              | Disipace pole ψ (útlum)                                              |
| ∇²ψ             | Difuze pole ψ pomocí Laplaciánu                                     |
| ∇φ              | Gradient φ – emergentní „gravitační“ tok                            |
| \\|ψ\\|² − φ     | Lokální akumulace hustoty ψ do paměťového pole φ                    |
| κ      | ladicí pole – určuje citlivost φ na ψ. Může být konstantní, plynulý gradient, ostrov nebo vrstevnatá struktura. |

<!-- prettier-ignore-end -->

---

## 4.4 Detekce jevů

V každém kroku simulace se vyhodnocují následující jevy:

| Jev                       | Detekční metoda                                      |
| ------------------------- | ---------------------------------------------------- |
| **Kvazičástice (linony)** | Lokální maxima amplitudy ψ překračující zvolený práh |
| **Trajektorie**           | Sledování souřadnic linonů mezi kroky                |
| **Víry (vortices)**       | Výpočet winding number kolem 2×2 buněk               |
| **Spin**                  | Vzorec `curl(∇ arg(ψ))` – rotace fázového gradientu  |
| **Fázový tok**            | Gradient fáze `∇ arg(ψ)`                             |
| **Topologický náboj**     | Celkový počet vírů (kladných a záporných)            |
| **Spektrum oscilace**     | FFT nad amplitudou v centru pole                     |
| **φ-pasti**               | Lokální maxima φ, která akumulují kvazičástice       |
| **Spinová aura**          | Průměrný tvar curl pole v okolí stovek kvazičástic   |
| **Gravitační chování**    | Sbližování částic v gradientu φ                      |

---

## 4.5 Vizualizace a exporty

Každý běh simulace generuje:

- CSV logy (trajektorie, spin, φ, amplituda, topologie),
- spektrální grafy a mapy,
- průměrnou spinovou mapu („spin aura“),
- GIF animace (amplituda, spin, částice, overlay, tok).

Výsledky jsou exportovány do složky `output/` a dokumentovány v HTML reportu.

---

## 4.6 Limity a poznámky

- Všechny operace jsou **lokální** – bez metriky, konstant, sil nebo globální geometrie.
- **Fluktuace a linony** obsahují pravděpodobnostní složku – systém není zcela deterministický.
- Struktury vznikají spontánně i při různých inicializacích.
- Konzervace topologického náboje je opakovaně pozorována, ale není formálně dokázána.
- Spektrální a gravitační jevy jsou analyzovány nad výběrovými trajektoriemi.

---

## 4.7 Poznámka k rozsahu validace

V této fázi jsou některé jevy, zejména ty související s makroskopickým chováním kvazičástic, detekovány vizuálně na základě výstupů ze simulace (např. animace, φ-pole, trajektorie). Tyto závěry zatím nejsou kvantifikovány statisticky. V dokumentu je výslovně odlišujeme jako **hypotetické** nebo **dále testované**. Plán jejich ověření je uveden v `todo.md`.

> Například φ-paměť a echo efekt jsou nyní ověřovány kombinací výstupů `phi_curl_low_mass.csv`, `multi_spectrum_summary.csv` a `trajectories.csv`.

---

## 4.8 Implementace

Simulace je napsána v jazyce Python a je dostupná v repozitáři [`lineum-core`](https://github.com/TomasTriska88/lineum-core).

Výpočetní jádro zahrnuje:

- inicializaci polí ψ a φ s počáteční asymetrií,
- krokovou evoluci rovnice zahrnující excitaci kvazičástic, fázový šum, disipaci, difuzi a interakce,
- výpočet derivací, gradientů, curlu a winding number pro detekci jevů,
- detekci částic, vírů a emergentních struktur,
- logování a export do CSV, GIF, obrázků a HTML reportu.

Výstupy simulace jsou ukládány do složky `output/`.

Kód je navržen modulárně. Parametry simulace, detekční prahy a vizualizační volby lze snadno upravit. Architektura odděluje rovnicovou dynamiku, detekci jevů a prezentaci výsledků, což umožňuje snadné experimentování a rozšíření.

> Pythonový kód je v neustálém vývoji. Průběžně se upravuje a rozšiřuje tak, aby umožňoval detekci nových jevů, generoval další výstupy a poskytoval lepší interpretaci vzniklých struktur.

---

## 4.9 Výstupní data

Simulace generuje různé typy výstupů, které slouží k analýze a vizualizaci vznikajících jevů:

- **CSV logy**: časové řady detekovaných kvazičástic, vírů, amplitud, spekter a dalších měřitelných parametrů,
- **GIF animace**: vývoj amplitudy, spinu, částic, toku a jejich kombinací,
- **Obrázky (PNG)**: spektrální grafy, průměrná spinová struktura („aura“), vývoj φ ve středu pole,
- **Binární pole (NPY)**: celé datové vrstvy pro opakovanou nebo hlubší analýzu.

Aktuální seznam výstupů a vizualizací je dostupný ve složce `output/` a shrnut v automaticky generovaném reportu `lineum_report.html`.

Výstupní soubor `phi_curl_low_mass.csv` slouží k ověření hypotézy strukturální paměti. Obsahuje hodnoty φ a curl v místech kvazičástic s velmi nízkou efektivní hmotností. Kombinací s výstupy `multi_spectrum_summary.csv` a `trajectories.csv` lze ověřit, zda došlo k tichému uzavření částice ve φ-pasti bez výdeje energie.

Testování tohoto jevu je aktivováno pomocí volby `TEST_EXHALE_MODE = True`, která upravuje parametry simulace směrem k pomalejší dynamice, delší životnosti a vyšší disipaci – čímž se zvyšuje pravděpodobnost výdechu.

> Struktura a počet výstupních souborů se může měnit s vývojem kódu. Dokumentace se zaměřuje na principy a typy dat, nikoliv na konkrétní názvy.

---

## 4.10 Numerická stabilita a volba koeficientů

Simulace je navržena tak, aby zůstala numericky stabilní i při delším běhu bez nutnosti globálního řízení. Toho je dosaženo následujícími volbami:

- **Disipace ψ** je velmi slabá (`−0.001 ⋅ ψ`), aby nebránila vzniku oscilací, ale zároveň tlumila nekontrolovaný růst.
- **Fluktuace fáze** (`ξ`) jsou generovány náhodně, ale s malou amplitudou, aby podporovaly diverzitu bez chaotického rozkladu.
- **Linony** vznikají s pravděpodobností podle sigmoid(∇‖ψ‖ + ‖ψ‖), což zabraňuje přebytku excitací v hladkých oblastech.
- **Reakční síla pole φ** je vyšší (`α ≈ 0.06`) než difuzní složka (`β ≈ 0.015`), čímž dochází k rychlé odezvě v místech s vysokou |ψ|², ale zároveň si pole φ udržuje hladký profil bez náhlých změn.
- **Gradient φ** je zaveden jako jemný tok (`∇φ`) s malým koeficientem, což vytváří „gravitační“ efekt bez dominantního ovlivnění rovnice.

Volba těchto koeficientů nebyla provedena laděním na výsledek, ale na základě pozorované stability a konzistence mezi různými inicializačními stavy. Rovnice je robustní i při různých počátečních podmínkách a zachovává topologickou konzervaci i bez externího řízení.

## 4.11 Měřítko času a prostoru

Přestože simulace běží v diskrétním čase a bez fyzikálních jednotek, některé výstupy (např. spektrum, energie, hmotnost, vlnová délka) lze mapovat na přibližnou fyzikální škálu:

- **Prostorový krok** je často interpretován jako 1 pikometr (1e−12 m),
- **Časový krok** jako 1 zeptosekunda (1e−21 s).

Toto měřítko je zvoleno tak, aby dominantní frekvence, energie a efektivní hmotnosti kvazičástic odpovídaly hodnotám blízkým známým částicím (např. elektronům). Jde o volitelné mapování pro orientaci – simulace sama je bezrozměrná.
