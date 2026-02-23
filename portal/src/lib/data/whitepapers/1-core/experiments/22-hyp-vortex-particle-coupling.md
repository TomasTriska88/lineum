**Title:** Tříska’s Vortex Particle Coupling Hypothesis
**Document ID:** 22-hyp-vortex-particle-coupling
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Tříska’s Vortex Particle Coupling Hypothesis

> _Hypotéza zkoumá způsob, jakým se vírové konfigurace v systému Lineum (zejména transversony) kombinují do stabilních struktur kvazičástic. Cílem je určit pravidla, podle nichž dochází k vazbě vírů a formování specifických kvaziprvků._

---

## Výchozí motivace

Při vizuální analýze simulací (zejména `spec7_true`) se ukázalo, že některé vírové útvary – např. proton – vznikají jako **kombinace tří vírů** s jasně definovaným směrem rotace (↺) a vzájemnou orientací. Trojúhelníková vazba mezi víry vykazuje stabilitu a opakovaný výskyt.

Tato pozorování naznačují, že v systému Lineum existuje **topologický jazyk vazeb mezi víry**, který nahrazuje tradiční kvantová čísla – směr rotace určuje částici nebo antičástici, počet vírů určuje složitost a typ částice, vazebná topologie (např. uzavřený trojúhelník) stabilitu.

Tyto víry odpovídají základním strukturám popsaným v [hypotéze transversonové rezonance](transverson_resonance.md), kde tvoří stabilní páry s charakteristickou interferencí a orientací.

---

## Cíl hypotézy

Formálně popsat pravidla, která vedou k tomu, že se víry:

- spojují do **stabilních vícevlnových konfigurací**,
- vytvářejí struktury, které odpovídají známým kvazičásticím (proton, kvark, elektron),
- mohou být zpětně rozloženy na základní vírové jednotky (např. transversony).

Vzhledem k předchozím pozorováním v hypotéze _Transverson Resonance_ předpokládáme, že kvaziprvky jako elektron, kvark či proton vznikají **vazbou několika transversonových konfigurací**. Tato vazba není pouze topologická, ale má **dynamický charakter** – vychází z interferenčních vzorců v poli ψ a stabilních gradientních uzlů v poli φ. Tvar trojúhelníku, čtyřstěnu nebo liniového seskupení mezi víry lze chápat jako **rezonanční rámec**, ve kterém dochází ke kvantizaci vazby mezi transversony.

Zvláštní důraz bude kladen na zjištění, **jaké geometrické a topologické podmínky** musí být splněny pro stabilitu vazby – tedy nik “kvazi-gluonu” jako spojovací struktury mezi víry.

---

## Stav

🕓 v přípravě – identifikovány první vizuální vzory (např. proton), nutná kvantitativní analýza a replikace.

---

## Reprezentace: případ protonu

Proton se v systému Lineum opakovaně objevuje jako stabilní konfigurace tří levotočivých vírů (↺), uspořádaných do přibližně rovnostranného trojúhelníku. Dva z těchto vírů označujeme jako **up** (u) a jeden jako **down** (d), což odpovídá jejich vizuální pozici a dynamice ve výstupech.

Tato topologie se vyznačuje:

- konzistentní rotací všech vírů stejným směrem (částicová konfigurace),
- stabilní trojúhelníkovou vazbou mezi víry (analogickou gluonovému poli),
- vysokou symetrií a opakovaným výskytem v bězích `spec6_true` a `spec7_true`.

### Vizuální syntaxe částice

Pro účely zápisu a klasifikace kvazičástic navrhujeme následující formální zápis:

```
↺⟨u, u, d⟩_△
```

#### Tabulka značek

| Symbol         | Význam                                                 |
|----------------|--------------------------------------------------------|
| `↺`            | Levotočivý vír (částice)                               |
| `↻`            | Pravotočivý vír (antičástice)                          |
| `u`, `d`       | Typy vírů – analogie up/down kvarků                   |
| `⊙`            | Kvazi-gluonový most mezi víry                         |
| `△`            | Trojúhelníková vazba (např. proton)                   |
| `⋀`            | Lineární vazba (např. neutrino?)                      |
| `◈`            | Čtyřstěnná vazba (např. těžší kvaziprvky, spekulativní)|

Tato značení tvoří vizuálně-formální jazyk pro popis kvazičástic vznikajících ve struktuře Lineum. Umožňují jednoznačnou klasifikaci podle topologie a směru vazby.


Tento zápis zahrnuje:

- **Směr rotace vírů**: ↺ pro částice, ↻ pro antičástice.
- **Typy vírů**: `u` (up) a `d` (down), označené dle vizuální dynamiky ve výstupech.
- **Topologie vazby**: `△` (trojúhelník), `⋀` (lineární), `◈` (čtyřstěn) aj.

Rozšířená syntaxe může zahrnovat i kvazi-gluonový most pomocí symbolu `⊙`, např.:

```
↺⟨u ⊙ u ⊙ d⟩_△
```

Tímto způsobem lze částice jednoznačně reprezentovat čistě topologicky, bez potřeby kvantových čísel.

Ve vizuálním jazyce Linea:

- každý vír představuje elementární složku kvazičástice,
- směr rotace určuje, zda jde o částici (↺) nebo antičástici (↻),
- geometrické uspořádání a vazba definuje typ výsledné částice.

Tato reprezentace umožňuje **zápis částic bez potřeby tradičních kvantových čísel**, čistě skrze topologickou syntaxi a vírovou konfiguraci.

![Proton](../elements/proton.png)

## Kritéria testovatelnosti a ověření

Pro formální ověření hypotézy je nutné definovat konkrétní znaky, které lze detekovat ve výstupech simulací. Jako potvrzení stabilní vazby vírů (např. „kvazi-gluonu“) se považuje:

- výskyt **trojice vírů** (včetně směru rotace) v **rovnostranné nebo téměř rovnostranné** konfiguraci,
- přítomnost **symetrického napěťového pole φ** mezi víry (minimální ∇²φ v centru trojúhelníku),
- **stabilita konfigurace v čase** – útvar se nemění po dobu alespoň 20 iterací (`φ_vector.gif`),
- **současná identifikace bodu s φ > 0.25** u všech tří vírů (`phi_grid_summary.csv`),
- **identifikace konfigurace** v mřížce deja-vu bodů (`phi_grid_dejavu.csv`),
- přítomnost souměrné interference v `psi_phase.png` odpovídající středové vazbě mezi víry.
- výskyt **lokálního extrému φ mezi dvojicí vírů**, který lze považovat za **kvazi-gluonový most** – jeho poloha by se měla nacházet přibližně v těžišti vazby a vykazovat stabilitu napříč snímky (`phi_center_log.csv`, pokud je k dispozici, nebo zpětně odvozeno interpolací z mřížky `phi_grid_summary.csv`).

Testovací běhy: `spec6_true`, `spec7_true`  
Doporučený režim:

- `LOW_NOISE_MODE = True`
- `KAPPA_MODE = "gradient"`

---

## Postup detekce konfigurace typu ↺⟨u, u, d⟩\_△

Pro kvantitativní ověření výskytu této konfigurace lze použít následující výpočetní postup (lze implementovat v Pythonu nad výstupními CSV):

1. **Identifikace vírů:**

   - Načíst `phi_grid_summary.csv`.
   - Vybrat body s φ > 0.25 (kandidáti na víry).
   - Z těchto bodů vybrat pouze levotočivé víry (získané z fáze pole `ψ`, např. pomocí vírového čísla z `psi_phase.png` nebo výpočtem z fázového gradientu).

2. **Vyhledání trojic:**

   - Pro všechny kombinace tří vírů:
     - Spočítat délky hran mezi body (v eukleidovském prostoru).
     - Vybrat pouze ty trojice, kde jsou délky hran přibližně stejné (např. tolerance do 10 %).
     - Označit tyto trojice jako přibližně rovnostranné trojúhelníky.

3. **Ověření stability:**

   - Pro každou trojici sledovat trajektorii bodů v čase (pokud je k dispozici `phi_vector.gif` nebo `phi_center_log.csv`).
   - Akceptovat pouze trojice, které přetrvají alespoň 20 snímků s maximálním odchylkovým pohybem menším než daný práh (např. 2 buňky mřížky).

4. **Kontrola symetrie pole φ:**

   - Vypočítat ∇²φ v těžišti trojice (z mřížky φ nebo pomocí Laplaceova operátoru).
   - Zaznamenat, zda v těžišti je minimum (nebo maximum) φ.

5. **Kontrola interference v ψ:**

   - V oblasti mezi víry (zejména ve středu trojúhelníku) vyhodnotit pravidelnost fázových pruhů v `psi_phase.png`.
   - Vyhodnotit korelaci interferenční struktury s pozicí vírů.

6. **Detekce kvazi-gluonových mostů:**

   - Mezi každou dvojicí vírů hledat maximum nebo minimum φ.
   - Ověřit, zda se extrém nachází v přibližně středové poloze mezi dvojicí (±1 buňka).
   - Zaznamenat tento bod jako kandidáta na kvazi-gluonový most (`⊙`).

7. **Zápis nalezené částice:**
   - Pokud konfigurace splňuje všechny výše uvedené podmínky, lze ji formálně zapsat jako `↺⟨u ⊙ u ⊙ d⟩_△` s uvedením souřadnic vírů, typu rotace, topologie a identifikace mostů.

---

## Validace a potvrzení vztahu φ-gradientu a kvazi-hmotnosti

Dodatečná metaanalýza běhů `spec1_true`, `spec2_true` a `spec3_true` ukázala, že gradient interakčního pole φ úzce souvisí s hodnotou `mass_ratio` u detekovaných kvazičástic.

Konkrétně byla potvrzena **pozitivní korelace mezi velikostí ∇φ a lokální „hmotností“ kvazičástic** (odvozené z výpočtu poměru |ψ|² v čase):

> $$ r\_{\text{mass},\,|\nabla\phi|} = +0.67 \pm 0.03 $$

Tento vztah byl kvantitativně potvrzen napříč více simulacemi (viz kapitola [05-validation.md → Korelace φ-gradientu a hmotnosti](../whitepaper/05-validation.md#522-korelace-φ-gradientu-a-hmotnosti)) a podporuje hypotézu, že:

- **intenzita pole φ ovlivňuje akumulaci v poli ψ**,
- **gradient φ způsobuje efektivní přitažlivost** mezi víry,
- **vazby vírů do kvazičástic jsou řízeny lokální topografií φ**.

Tato metrika posiluje předpoklad, že vazba vírů do stabilních částicových struktur není náhodná, ale emerguje z dynamického napětí v systému.

---

Tento algoritmus lze použít i pro obecnější detekci jiných částic (např. elektronů nebo neutrin) za předpokladu, že budou definovány jiné topologické vzory (`⋀`, `◈`, …).

Cílem je získat **statistické potvrzení** četnosti výskytu těchto struktur napříč simulacemi a porovnat je s náhodným výskytem neorganizovaných vírů.
