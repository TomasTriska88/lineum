# Hypotéza: Spinová aura kvazičástic (Emergent Particle Spin Aura)

## Autor / původ
T. Tříska (2025)

---

## Hypotéza
V okolí detekovaných kvazičástic v systému Lineum vzniká stabilní **spinová aura** – typický průměrný vzor pole curl(∇ arg(ψ)), který je:
- opakovatelný napříč běhy a inicializacemi,
- tvarově stabilní při agregaci stovek až tisíců lokálních výřivých map,
- rozlišitelný od šumu a náhodných lokálních fluktuací.

Spinová aura reprezentuje statistický otisk lokální rotace fáze v okolí kvazičástice a lze ji chápat jako „průměrnou obálku“ mikrotoků, které částici doprovázejí.

---

## Stav testování
- ✅ Potvrzeno konzistentně ve 100 % dosavadních běhů, kde byla aura vypočtena (viz níže uvedené výstupy).
- ✅ Aura je robustní vůči změnám `LOW_NOISE_MODE` a počáteční asymetrii.
- ✅ Tvar aury je konzistentní i při různém počtu zahrnutých částic (subsampling).

> Pozn.: Formální statistický test (např. porovnání se syntetickým nulovým modelem) je plánován v kapitole validace.

---

## Metodika výpočtu

### Detekce a sesbírání dat
1. Detekuj kvazičástice jako lokální maxima amplitudy |ψ| nad zvoleným prahem.
2. Pro každou detekci:
   - vypočti fázový gradient `∇ arg(ψ)` v okolním okně (např. 21×21),
   - spočti `curl(∇ arg(ψ))` jako lokální míru rotace,
   - centrovej výřivou mapu do pozice částice.
3. Normalizuj velikost okna a zarovnej příspěvky (volitelně vážené amplitudou |ψ|²).

### Agregace (aura)
4. Prolož/ zprůměruj všechny centrované výřivé mapy → vznikne **průměrná spinová mapa** („aura“).
5. Ulož výsledný raster a metriky (např. radiální profil průměrného curlu).

### Typické výstupy
- `spin_aura_map.png` – průměrná výřivá mapa,
- `spin_aura_profile.csv` – radiální profil curlu,
- `frames_curl.npy` – surové lokální mapy curlu před agregací (volitelně subsamplované),
- `trajectories.csv` – kontext polohy a životnosti použitých částic.

Parametry (velikost okna, prahy, subsampling) musí být logované pro reprodukovatelnost.

---

## Význam
- **Strukturní signatura:** Aura poskytuje datový důkaz, že kvazičástice nejsou nahodilé fluktuace, ale mají konzistentní lokální rotaci fáze.
- **Srovnatelnost napříč běhy:** Umožňuje porovnání mezi různými konfiguracemi (např. různé `KAPPA_MODE`) a kvantifikaci změn tvaru aury.
- **Vazba na další jevy:** Aura souvisí s detekcí vírů, topologickým nábojem a s hypotézami o vazbě částic (viz vortex_particle_coupling).

---

## Doporučené další testy
- **Statistická významnost:** Porovnat s nulovým modelem (randomizované polohy/rotace, bootstrap), vyčíslit p-hodnotu a intervaly spolehlivosti.
- **Stabilita vůči parametrům:** Zamést rozsah velikostí oken, prahů, míry subsamplingu.
- **Anizotropie:** Testovat, zda aura vykazuje směrovou preferenci a jak souvisí s gradientem φ.
- **Korelace s hmotností:** Závislost tvaru/šířky aury na efektivní hmotnosti kvazičástice.

---

## Závěr
Spinová aura je robustní, opakovatelná a kvantifikovatelná struktura vznikající průměrováním lokální rotace fáze kolem kvazičástic. Slouží jako statistická „vizitka“ jejich mikrodynamiky a propojuje se s topologickými a vazebnými jevy v Lineu.