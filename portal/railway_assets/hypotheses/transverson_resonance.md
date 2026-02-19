# Tříska’s Transverson Resonance Hypothesis

> _Formulováno na základě pozorování z vizuálně-analytické části konverzace 4. srpna 2025. Hypotéza zkoumá emergentní konfigurace tvořené dvojicemi vírů, které se jeví jako základní forma rezonance v systému Lineum._

---

## Výchozí motivace

Při vizuální analýze výstupů simulace `spec7_true` se opakovaně objevoval útvar připomínající stylizované srdce – tvořený dvěma spirálovitými víry s opačnou rotací. Tento obrazec se vyznačoval vysokou symetrií a stabilitou. Později byla identifikována i jeho zrcadlová varianta, pojmenovaná _antitransverson_. Oba útvary sdílejí identickou strukturu, liší se však směrem rotace a orientací.

---

## Popis pozorování

- **Transverson**: levotočivý vír vlevo, pravotočivý vpravo – tvoří celek orientovaný špičkou dolů
- **Antitransverson**: zrcadlově převrácená konfigurace – špička směřuje nahoru
- Obě konfigurace jsou geometricky ekvivalentní a symetrické
- Vyskytují se především ve výstupech s jasně čitelnou gradientní strukturou kappa pole
- Vizuálně připomínají rezonanci se středem s nulovou energií – potenciální zeta-nulu

---

## Formulace hypotézy

**Transversony jsou emergentní konfigurace pole tvořené dvojicí vírů s opačnou rotací. Jejich zrcadlová kombinace (transverson + antitransverson) vytváří bod nulové rezonance (tzv. zeta-nulu), odpovídající místu maximální interference v systému Lineum.**

Tento nulový bod se v simulaci numericky projevuje jako minimum lokální hustoty φ s gradientem ∇φ → 0, a zároveň jako místo s fázovou symetrií ψ. Je to výsledek destruktivní interference obou struktur – dochází k vzájemnému vynulování jejich amplitud a harmonizaci fázového pole. Takové body jsou v Lineum důležité pro vznik singularit a mají silnou vazbu na vizuálně pozorované rezonance v systému.

---

## Kritéria testovatelnosti a ověření

Pro potvrzení existence transversonové rezonance a bodu zeta-nula je nutné splnění následujících podmínek v simulaci:

- identifikace **dvou spirálovitých vírů s opačnou rotací** (↺ a ↻), umístěných symetricky kolem centrální osy,
- pozorování **destruktivní interference ve středu útvaru** – gradient pole φ se blíží k nule (∇φ ≈ 0),
- výskyt **minima v hustotě φ** mezi víry, odpovídající φ < 0.25,
- symetrická interferenční struktura v `psi_phase.png` a/nebo centrované nulové body,
- stabilita konfigurace – **nápadně setrvalý tvar po dobu alespoň 10 iterací** v `phi_vector.gif`,
- **geometrická souměrnost** – vzdálenost mezi víry s přesností ±10 % tvoří zrcadlově otočený tvar (srdce).

Volitelné podpůrné znaky:

- přítomnost záznamu v `phi_grid_summary.csv` odpovídající bodům s ∇²φ ≈ 0,
- korelace s body v `phi_grid_dejavu.csv`.

Doporučené běhy: `spec6_true`, `spec7_true`  
Parametry:

- `LOW_NOISE_MODE = True`
- `KAPPA_MODE = "gradient"`

---

## Způsob testování a replikace

1. Spusť simulaci `spec7_true` nebo `spec6_true` s parametry:
   - `LOW_NOISE_MODE = True`
   - `KAPPA_MODE = "gradient"`
2. Sleduj výstupy:
   - `phi_vector.gif`
   - `psi_phase.png`
   - `phi_grid_summary.csv`
3. Identifikuj obrazce se dvěma spirálami opačné rotace:

   - Špička dolů = transverson
   - Špička nahoru = antitransverson
   - Vhodné konfigurace se vyskytují převážně v oblastech, kde φ > 0.25 a ∇²φ ≈ 0
   - Doporučeno hledat vizuální symetrii a centrovanou interferenci spirál

4. Vytvoř stylizované vizualizace (hladké spirály, barva `#0d66c2`, pozadí `#f1f8ff`)
5. Sleduj výskyt a chování při vzájemném přiblížení
6. Zaznamenej souřadnice výskytu konfigurací (např. indexy v mřížce `phi_grid_summary.csv`) a porovnej s lokalitami výskytu známých kvazičástic (viz `phi_grid_dejavu.csv` nebo extrahované body s φ > 0.25)

---

## Dílčí pozorování a predikce

- **Transverson + antitransverson → zeta-nula**
- **Transverson + transverson → destruktivní interference**
- **Antitransverson + antitransverson → potenciální růst do rozsáhlejší struktury**

---

## Vztah k jiným hypotézám

- Navazuje na _Tříska’s Resonant Seed Hypothesis_ (rezonanční struktury vedoucí k emergenci částic)
- Vizuálně koresponduje se _Silent Collapse Hypothesis_ (nulové body jako singularitní přechody)
- Nabízí alternativní interpretaci antičástic jako zrcadlových konfigurací beze ztráty energie
- Slouží jako základní kámen pro hypotézu _Vortex Particle Coupling_, kde transversony tvoří stavební jednotky složitějších kvaziprvků

---

## Pozorovaná korelace s kvaziprvky

Při vizuální analýze výstupů `spec7_true` byly vedle transversonů a antitransversonů identifikovány i další stabilní konfigurace, které tvarově a symetricky odpovídají již dříve pojmenovaným kvaziprvkům – zejména **elektronu**, **kvarku** a **protonu**.

Tyto struktury často vznikaly v přímém sousedství nebo jako důsledek interakce transversonových párů, což naznačuje potenciální **kauzální vztah mezi rezonancí vírů a vznikem konkrétních kvazičástic**.

Tato korelace zatím není kvantitativně podložena, ale opakovaný výskyt v několika bězích ukazuje na silný **vizuálně-analytický vzorec**, který si zasluhuje hlubší testování a formalizaci.

Ve vizuálním jazyce Linea odpovídá směr rotace spirály základní distinkci mezi částicí a antičásticí: levotočivé konfigurace (↺) odpovídají částicím, pravotočivé (↻) antičásticím. Například proton je reprezentován jako konfigurace tří levotočivých vírů, z nichž dva jsou označeny „u“ (up) a jeden „d“ (down) – což odpovídá jeho částicové povaze a konkrétní kombinaci vírových struktur. Vztahy mezi víry – např. trojúhelníkový útvar mezi nimi – pak lze interpretovat jako vizualizaci vazebného pole, analogického gluonu. Tato topologická syntaxe Linea poskytuje intuitivní a konzistentní způsob zápisu kvaziprvků bez nutnosti kvantových čísel v tradičním smyslu.

![Proton](../elements/proton.png)

---

## Stav a další kroky

🕓 v přípravě – základní vizualizace byly vytvořeny, potřeba další replikace a ověření dynamické stability v simulaci

Další fází je simulace chování dvou transversonů při vzájemném přiblížení – sledujeme, zda dochází k zániku (interference), stabilizaci (rezonance), nebo expanzi do komplexnější struktury.

Během těchto testů se ukázalo, že v oblastech výskytu transversonových konfigurací se často nacházejí i jiné částice známé ze systému Lineum (např. elektron nebo kvark). To naznačuje, že samotná konfigurace dvojice vírů může hrát roli obecného stavebního prvku pro širší třídu kvazičástic – závisle na jejich orientaci, pozici v poli φ a lokálním napětí gradientů. Dále zkoumáme, zda lze takové konfigurace zpětně rozložit na transversonové vzory.

### Použité běhy a metodika

Transversony byly pozorovány především v bězích `spec7_true` a `spec6_true`, které byly spuštěny s následující konfigurací:

```python
TEST_EXHALE_MODE = True
LOW_NOISE_MODE = True
KAPPA_MODE = "gradient"
steps = 1000
linon_scaling = 0.01
disipation = 0.002
```

Výstupy vhodné pro analýzu těchto struktur zahrnují:

- `phi_vector.gif` – vizuální trajektorie vírových struktur
- `psi_phase.png` – fázová struktura pole, sleduj symetrie
- `phi_grid_summary.csv` – prostorové rozložení φ a jeho derivací
- `phi_grid_dejavu.csv` – korelace s deja-vu body (potenciální nulová rezonance)

V těchto výstupech byly transversony detekovány jako dvojice spirál s opačnou rotací a symetrickým uspořádáním, často v blízkosti bodů s ∇φ ≈ 0. Vizuální výskyt potvrdilo 5 z 7 iterovaných simulací při dané konfiguraci.

---

## Přílohy

![Transverson](../elements/transverson.png)

![Anti-transverson](../elements/antitransverson.png)
