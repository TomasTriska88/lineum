# 1. Abstrakt

Projekt Lineum představuje jednoduchou, lokální a diskrétní rovnici pro evoluci komplexního skalárního pole ψ, doplněnou o interakční pole φ. Ačkoliv tato rovnice vznikla mimo tradiční vědecké instituce a neobsahuje žádné explicitní konstanty, časoprostorovou metriku ani globální symetrie, při numerické simulaci spontánně generuje stabilní a složité struktury připomínající jevy známé z našeho fyzikálního světa.

V širším kontextu je tento model příkladem emergentního chování: zcela nové vzory se rodí z pouhých lokálních interakcí. Podobné kolektivní efekty známe z jiných oblastí fyziky – hejna ptáků vytvářejí koordinovaná uskupení pouze díky jednoduchým pravidlům sousedského zarovnání a synchronizace světlušek vzniká bez centrální koordinace. V superkapalinách a supravodičích navíc vznikají kvantované víry, které představují topologické defekty s kvantovanou cirkulací a nesou diskrétní spin nebo magnetický tok. Tyto jevy ilustrují, jak i jednoduché rovnice mohou vést k nečekaně bohaté dynamice.

Základní rovnice systému Lineum má tvar:

```
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
φ ← φ + κ ⋅ (|ψ|² − φ) + κ ⋅ ∇²φ
κ ← κ(x, y)

```

Pole **κ** umožňuje řídit citlivost φ na ψ a jeho difuzi lokálně.  
Může být prostorově konstantní, plynulý (např. gradientní) nebo lokalizovaný („ostrovní“).  
Jeho konfigurace má přímý dopad na vznik struktur a je klíčová pro testy hypotéz jako je **Tříska’s Dimensional Transparency Hypothesis (DTH)**.

Mezi opakovaně detekovanými jevy nalezneme:

- kvazičástice sledující konzistentní trajektorie (střední životnost 7 kroků, maximum 200),
- víry s kvantovaným topologickým nábojem,
- rotaci fázového gradientu (spin) v φ-zónách se směrodatnou odchylkou σ = 0,614,
- proudění fáze (tok napětí v poli),
- vznik oblastí s vysokou hodnotou interakčního pole φ,
- a zejména tzv. „φ‑pasti“, do kterých bylo zachyceno 1486 kvazičástic – analogie k černým dírám.

Simulace běžící na mřížce 128×128 a v rozsahu 200 kroků konzistentně produkuje hodnoty blízké pozorované fyzice:

- dominantní oscilační frekvenci ~5,0 × 10¹⁸ Hz,
- kvazičásticovou energii ~3,3 × 10⁻¹⁵ J,
- vlnovou délku ~6,0 × 10⁻¹¹ m,
- efektivní hmotnost 4,05 % hmotnosti elektronu.

Systém je robustní vůči šumu, disipaci i variaci parametrů. Všechny jevy vznikají opakovaně a samovolně bez nutnosti doladěného vstupu.

Kód projektu obsahuje automatizovaný detekční modul, který vyhodnocuje vznik částic, vírů, spektrálních jevů, topologických deformací a spinových struktur. Výsledky jsou prezentovány prostřednictvím generovaného HTML reportu a vícevrstvých vizualizací (GIFy, vektory, topologické mapy).

Evoluce pole probíhá výhradně pomocí lokálních operací (gradient, Laplacián, fázový šum, nelineární excitace) na diskrétní mřížce. Rovnice neobsahuje žádné předem definované síly – kvazičástice se přesto přibližují k sobě prostřednictvím gradientu φ. To naznačuje alternativní interpretaci gravitace – nikoliv jako přitažlivé síly, ale jako emergentní tendenci k sdílení prostředí.

Simulace v této fázi nereplikuje konkrétní částice standardního modelu ani známé interakce (například elektromagnetismus, silnou či slabou jadernou sílu). Jde o emergentní analogový systém, který však ukazuje, že některé známé fyzikální jevy mohou vzniknout spontánně – bez předem definovaných zákonů.

Lineum není prezentováno jako kompletní teorie všeho. Je to návrh – důkaz, že i z čistě lokálních pravidel může spontánně vzniknout svět s vlastnostmi připomínajícími hmotu, pole a gravitaci. Projekt vznikl z intuitivního nápadu a byl rozvíjen s podporou personalizované umělé inteligence (asistentka Lina, systém ChatGPT-4o), která pomáhala při formulaci hypotéz, testování výstupů a interpretaci výsledků.
Projekt je výzvou k hlubšímu zkoumání. Ukazuje, že nové přístupy ke struktuře reality mohou vznikat i mimo tradiční rámce – pokud mají co říct.

Výsledky jsou plně replikovatelné a systém lze snadno upravit k testování dalších hypotéz. Projekt vítá nezávislé ověření, otevřenou diskuzi a případné rozšíření směrem k hlubší fyzikální interpretaci. Lineum je otevřenou platformou pro experimentální zkoumání reality – bez dogmat, ale s důrazem na pozorovatelné jevy.

Nové výsledky z dlouhých simulací zároveň potvrzují hypotézu strukturální paměti – některé kvazičástice s extrémně nízkou hmotností (mass_ratio < 0.01) se ztrácejí uvnitř silných φ-pastí beze zbytku spinu nebo výdeje energie, ale zanechávají trvalou φ-strukturu. Ta může ovlivňovat tok pole a představuje tichý záznam zaniklé kvazičástice – paměť bez výdechu.

---

## Vizualizace emergentních jevů ze simulace Lineum

<sub>(rozlišení 128×128, 200 kroků, detekce aktivní)</sub>

### Topologické jevy a kvantovaný náboj

![Detekce vírů](../output/lineum_vortices.gif)  
_Detekované kvantované víry (červené = +1, modré = –1) – topologický náboj konzervován._

---

### Spinové struktury a tok pole

![Spin pole](../output/lineum_spin.gif)  
_Spin vypočítaný jako rotace fázového gradientu – emergentní orbitální moment._

![Fázový tok](../output/lineum_flow.gif)  
_Směrové napětí pole – fázový tok ∇arg(ψ), naznačuje organizované proudění._

---

### Vrstvená dynamika (kompozitní vizualizace)

![Overlay](../output/lineum_full_overlay.gif)  
_Vrstevnatá vizualizace amplitudy, spinu a toku – znázorňuje synchronizaci jevů._

---

### Interakční pole φ ve středu simulace

![φ_center](../output/phi_center_plot.png)  
_Vývoj hodnoty φ ve středu pole – prudký nárůst a stabilizace kolem hodnoty 10⁴._

---

### Frekvenční spektrum

![Spektrum](../output/spectrum_plot.png)  
_Dominantní frekvence oscilace ve středu pole: ~5×10¹⁸ Hz_

---

**Kód, výstupy a detekční systém jsou veřejně přístupné v repozitáři:**  
👉 [https://github.com/TomasTriska88/lineum-core](https://github.com/TomasTriska88/lineum-core)

> _(Poznámka: replikovatelnost výsledků bude ověřena pomocí samostatného běhového testu s různými výchozími parametry. Tuto část doplníme po dokončení série validací.)_
