# 1. Abstrakt

Projekt Lineum představuje jednoduchou, lokální a diskrétní rovnici pro evoluci komplexního skalárního pole ψ, doplněnou o interakční pole φ. Ačkoliv tato rovnice vznikla mimo tradiční vědecké instituce a neobsahuje žádné explicitní konstanty, časoprostorovou metriku ani globální symetrie, při numerické simulaci spontánně generuje stabilní a složité struktury připomínající jevy známé z našeho fyzikálního světa.

V širším kontextu je tento model příkladem emergentního chování: zcela nové vzory se rodí z pouhých lokálních interakcí. Podobné kolektivní efekty známe z jiných oblastí fyziky – hejna ptáků vytvářejí koordinovaná uskupení pouze díky jednoduchým pravidlům sousedského zarovnání a synchronizace světlušek vzniká bez centrální koordinace. V superkapalinách a supravodičích navíc vznikají kvantované víry, které představují topologické defekty s kvantovanou cirkulací a nesou diskrétní spin nebo magnetický tok. Tyto jevy ilustrují, jak i jednoduché rovnice mohou vést k nečekaně bohaté dynamice.

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

Lineum není prezentováno jako kompletní teorie všeho. Je to návrh – důkaz, že i z čistě lokálních pravidel může spontánně vzniknout svět s vlastnostmi připomínajícími hmotu, pole a gravitaci. Projekt vznikl z intuitivního nápadu, vedeného s pomocí umělé inteligence, a je výzvou k hlubšímu zkoumání. Ukazuje, že nové přístupy ke struktuře reality mohou vznikat i mimo tradiční rámce – pokud mají co říct.
