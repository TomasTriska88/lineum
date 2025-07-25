# 1. Abstrakt

Projekt Lineum představuje jednoduchou, lokální a diskrétní rovnici pro evoluci komplexního skalárního pole ψ, doplněnou o interakční pole φ. Ačkoliv tato rovnice vznikla mimo tradiční vědecké instituce a neobsahuje žádné explicitní konstanty, časoprostorovou metriku ani globální symetrie, při numerické simulaci spontánně generuje stabilní a složité struktury připomínající jevy známé z našeho fyzikálního světa.

V širším kontextu je tento model příkladem emergentního chování: zcela nové vzory se rodí z pouhých lokálních interakcí. Podobné kolektivní efekty známe z jiných oblastí fyziky – hejna ptáků vytvářejí koordinovaná uskupení pouze díky jednoduchým pravidlům sousedského zarovnání a synchronizace světlušek vzniká bez centrální koordinace. V superkapalinách a supravodičích navíc vznikají kvantované víry, které představují topologické defekty s kvantovanou cirkulací a nesou diskrétní spin nebo magnetický tok. Tyto jevy ilustrují, jak i jednoduché rovnice mohou vést k nečekaně bohaté dynamice.

Mezi opakovaně detekovanými jevy nalezneme:

- kvazičástice sledující konzistentní trajektorie,
- víry s kvantovaným topologickým nábojem,
- rotaci fázového gradientu (spin),
- proudění fáze (tok napětí v poli),
- vznik oblastí s vysokou hodnotou interakčního pole φ,
- a zejména tzv. „φ‑pasti“, které naplňují chování očekávané od černých děr.

Analogická chování byla experimentálně pozorována v laboratorních modelech gravitačních polí, například v tzv. akustických černých děrách, kde proudící tekutina vytváří efektivní zakřivený časoprostor a umožňuje studovat fenomény jako Hawkingovo záření a superradianci. Přítomnost „φ‑pastí“ v našem modelu tak může být nápovědou, že podobné mechanismy lze realizovat i s ryze klasickými systémy a čistě lokálními pravidly.

Simulace generovaná touto rovnicí produkuje hodnoty blízké pozorované fyzice:

- dominantní oscilační frekvenci ~5 × 10¹⁸ Hz,
- kvazičásticovou energii ~3,3 × 10⁻¹⁵ J,
- vlnovou délku ~6,0 × 10⁻¹¹ m,
- a konzervaci topologického náboje napříč časem.

Kód projektu obsahuje automatizovaný systém detekce struktur, který vyhodnocuje vznik částic, vírů, orbitálních efektů, spektrálních jevů a spinové dynamiky. Výsledky jsou prezentovány prostřednictvím HTML reportu a vícero vrstevných vizualizací.

Evoluce pole probíhá na diskrétní mřížce a všechny členy rovnice jsou implementovány jako lokální operace (gradienty, Laplaciány či nelineární aktualizace) bez explicitní integrace v čase. Počáteční stav je generován s malým náhodným šumem a vývoj probíhá po pevných krocích, čímž vzniká časová řada vhodná pro spektrální analýzu. Automatizovaný modul během simulace sleduje topologii pole (sledování čísla vinutí a rotace fáze), tok energie i hustotu a identifikuje všechny emergentní struktury. Generované reporty obsahují grafy a animace toků, spinů, kvazičástic, vírů i interakčních pastí a jsou exportovány ve formě HTML pro snadné sdílení.

Lineum není prezentováno jako kompletní teorie všeho. Je to návrh – důkaz, že i z čistě lokálních pravidel může spontánně vzniknout svět s vlastnostmi připomínajícími hmotu, pole a gravitaci. Projekt vznikl z intuitivního nápadu, vedeného s pomocí umělé inteligence, a je výzvou k hlubšímu zkoumání. Ukazuje, že nové přístupy ke struktuře reality mohou vznikat i mimo tradiční rámce – pokud mají co říct.
