# 🧪 Lineum – Seznam úkolů pro další ověření

Tento soubor obsahuje přehled výzkumných bodů, které vyžadují další testování, vizualizaci nebo kvantitativní ověření. Každý bod by měl být buď (znovu) ověřen simulací, nebo jednoznačně formulován jako hypotéza. Stav tohoto TODO je zarovnán na core paper **lineum-core v1.0.6-core** (Eq-4, κ statická, 2D, periodické BCs, RUN_TAG `spec6_false_s41`).
Nejde o zdroj pravdy pro stav modelu – závazné definice a tvrzení jsou vždy v aktuální verzi whitepaperu / core paperu.  
Sekce níže jsou rozdělené tak, aby nejdřív řešily **základní principy a kritické body** a teprve potom mapování na „reálnou fyziku“.

---

### Scope a non-goals (vysoká úroveň)

- Lineum je **diskrétní dynamický model pole ψ s emergentními kvazičásticemi („linony“)** studovaný numericky v rámci daného Eq-4 a parametrického prostoru.
- Lineum **není** plnohodnotná QFT, GR ani kompletní náhrada Standardního modelu; všechny fyzikální analogie jsou zatím interpretace navrstvené nad numerickým modelem.
- Tvrzení typu „#disproved“ se vždy vztahují **jen k chování uvnitř modelu Lineum (Eq-4 + daný parametrický prostor)**, ne k obecné fyzikální teorii.

### Legenda úrovní tvrzení (podle whitepaperu)

- **[CORE]** – label používaný v core paperu pro jevy, které v dané verzi splnily definovaná kritéria stability a robustnosti.  
  Tento TODO soubor status jevů **neurčuje**, jen na tyto labely odkazuje.
- **[TEST]** – label pro jevy, u nichž má whitepaper definované testy a metriky; výsledek testů rozhoduje o případném přesunu do [CORE] nebo k #disproved-in-model **ve whitepaperu**, ne v tomto souboru.
- **[HYPOTHESIS]** – label pro koncepty, které zatím nesplnily podmínky pro [CORE] a jsou vedené jako otevřené hypotézy v příslušné verzi whitepaperu.
- **[DISPROVED-IN-MODEL]** – label pro jevy, které jsou v aktuální verzi whitepaperu označené jako vyvrácené v rámci Eq-4 a daného parametrického prostoru; případné „záchrany“ vyžadují novou větev modelu.

---

### Terminologie jevů v modelu

- Pojmy jako „spinová aura“, „neutral topology“ apod. jsou v tomto repozitáři **interní názvy pro konkrétně definované numerické objekty v modelu** (pole, integrály, indexy…).
- U každého takového termínu musí být v core paperu i kódu uvedená **operační definice**; název sám o sobě **není tvrzení o nové fyzikální veličině** mimo model ani o vlastnostech částic Standardního modelu.
- Tento TODO soubor **nezavádí nové fyzikální termíny**; pouze připomíná místa, kde je potřeba terminologii a její definice v whitepaperu / kódu dočistit nebo revidovat.

---

## 🔑 Meta-priorita – věrohodnost modelu

Nejvyšší „příčná“ priorita napříč jednotlivými sekcemi je ukázat, že pozorované excitace v Lineu nejsou numerické artefakty, ale robustní objekty modelu – a teprve na tom stavět fyzikální interpretaci a dlouhodobé „outlooky“.

- **Nejvyšší priorita – numerika vs. reálný jev**  
  – oddělit chyby algoritmu od skutečných struktur v modelu pomocí testů s různými integračními schématy, zjemňováním mřížky, změn kroků a konvergenční analýzy;  
  – ukázat, že výsledky konvergují při Δt, Δx → 0 a že excitace přežívá změnu rozlišení i parametrů.  
  Tyto body jsou rozpracované hlavně v sekcích **B, D, E, F, H, I**.

- **Střední priorita – vědecká interpretace**  
  – připravit jasné numerické předpovědi, které lze vyvrátit či potvrdit (např. chování při kolizi dvou linonů);  
  – pokusit se linon zařadit v rámci známých typů excitací (solitony, breathery, excitace skalárního pole…);  
  – otevřeně popsat status Lorentz-(ne)kovariance jako efektivního modelu, ne plné relativistické teorie.  
  Prakticky se promítá do sekcí **J, K, L** a souvisejících částí whitepaperu / FAQ.

- **Nižší priorita – dlouhodobé výhledy**  
  – nástřely možných fyzikálních realizací (optické mřížky, BEC, nelineární vlnová dynamika);  
  – lepší ukotvení škálování a jednotek z hlediska komunikace;  
  – prezentace výsledků pomocí srozumitelných grafů a krátkého „storytellingu“ („pole kmitá → pamatuje → stabilizuje“).  
  Tyto body pomáhají čitelnosti a outreach, ale stojí až na pevnějším numerickém základu.

---

## 🔍 Jevy z core paperu k revalidaci (core v1.0.6-core)

- [ ] Znovu ověřit **Guided motion podél +∇|φ|** (environmental guidance) v kanonické sadě (`spec6_false_s41` + seeds 17/23/73) tak, aby metriky z `*_trajectories.csv` a φ-map (viz core §5.1) odpovídaly aktuální definici a tolerancím v whitepaperu.
- [ ] Znovu prověřit režim **Silent collapse** (lokální pokles |ψ|² bez velkého globálního rušení) včetně kvantifikace závislosti na disipaci a lokalitě podle aktuální formulace v core §5.3.
- [ ] Revalidovat definici a měření **„spinové aury“** jako časově/ensemble průměrovaného pole `curl(∇arg ψ)` kolem linonů (`*_spin_aura_map.png`, `*_spin_aura_profile.csv`; core §5.2) a zkontrolovat, že dokumentace jasně uvádí, že jde o interní mapu cirkulace fáze v okolí linonu, nikoli o tvrzení o spinu částice ve smyslu Standardního modelu.
- [ ] Znovu ověřit parametry **kanonické tóniny**: že dominantní frekvence `f₀ = 3.90625×10¹⁸ Hz` a odvozené SI hodnoty (E, λ, display-only m/mₑ) jsou v kódu i textech konzistentní s aktuální verzí core §1, §5.6 a Appendix C a jsou používány pouze jako unit-conversions, nikoli jako dodatečné dynamické constrainty.
- [ ] Revalidovat metriky pro **φ-paměť / Structural Closure** (lokální φ-remnant po rozpadu linonu, half-life center-trace dle §5.4) a zkontrolovat, že klasifikace jevu **Return Echo** (trajektorie vracející se k bývalým decay místům) odpovídá rozdělení na core vs. extension-track v aktuálním whitepaperu.
- [ ] Ujasnit a znovu otestovat status jevu **Dimensional Transparency** (průchod struktur skrz κ) s ohledem na to, že byl dosud pozorován jen v bězích s časově proměnným κ (v1.1.x-exp):  
       – navrhnout a spustit testy pro danou exp větev,  
       – v dokumentaci explicitně držet tento jev jako extension-track hypotézu, dokud nebude promotion pipeline splněná.

---

## 🧱 Priorita 0 – základní principy a kritické body

### 🔲 A. Základní invariance a „první principy“ #structure

- [ ] Formálně sepsat, co je považováno za **fundamentální objekt** modelu: ψ, φ, κ, aktualizační rovnice (Eq-4), topologie mřížky, periodicita – a co je čistě **měřicí aparatura** (FFT, detekce linonů, definice SBR…).
- [ ] Identifikovat a odvodit (pokud existují) **diskrétní zákony zachování** nebo kvazi-zachování:  
       – norma / „hmota“ (∑|ψ|²),  
       – celkový topologický náboj (net winding),  
       – případná energie / Lyapunovova funkce kandidáta.  
       Zapsat je jako kontinuitní rovnice na mřížce (discrete continuity).
- [ ] Sepsat a ověřit **symetrie modelu**: globální fázová symetrie (U(1)), translační invariance na mřížce, rotační symetrie omezená na mřížku; u každé říct, zda je exaktní, porušená numericky, nebo záměrně zlomená.
- [ ] Definovat (nebo explicitně odmítnout) **energie-like funkcionál** kompatibilní s použitými operátory (∇, ∇², damping δ) a zkontrolovat jeho chování v kanonickém běhu (monotónnost vs fluktuace, boundedness).

### 🔲 B. Numerická robustnost a artefakty #numerics

- [ ] Explicitně zapsat použitou **diskretizaci** (schéma pro ∇, ∇², časový krok) a odvodit/stanovit její **stabilitní podmínku** (CFL-like omezení pro Δt vs Δx).
- [ ] Provést sadu **konvergenčních testů**: zjemňování mřížky (Δx↓), zmenšování časového kroku (Δt↓) a porovnání klíčových metrik (f₀, tvar linonu, SBR, φ half-life, spinová aura), aby bylo vidět, že výsledky konvergují a excitace nejsou závislé na hrubém kroku ani konkrétním rozlišení.
- [ ] Otestovat, zda linony přežijí při změně schématu (např. alternativní Laplace, různá integrační schémata – explicitní/implicitní/vyšší řády, různé pořadí aktualizace) – tj. že nejde o artefakt konkrétního numerického triku.
- [ ] Detekovat typické **mřížkové artefakty**: checkerboard módy, anisotropie (preferované směry 0°, 90°, 45°). Kvantifikovat přes spektrum a korelační funkce.
- [ ] Zkontrolovat vliv **okrajových podmínek**: porovnání periodic BCs vs. tlumené/absorbing okraje pro menší domény a ověření, že linonní excitace přežívají napříč použitými BCs (tj. nejsou jen důsledkem periodicity).

### 🔲 C. Dimenze, jednotky a SI ukotvení #units

- [ ] Sestavit tabulku všech **symbolů a jednotek** (ψ, φ, κ, t, x, α, β, δ, σξ, f₀, E, λ, m/mₑ) a provést explicitní **dimenzionální analýzu** Eq-4 + použitých metrik (včetně normalizace mřížky).
- [ ] Jasně oddělit **simulační jednotky** (grid step, time step) od **SI ukotvení** přes f₀ a konverzi (E = h f₀, λ = c / f₀, m = h f₀ / c²). Uvést, které vztahy jsou pouze „display-only“ a které vstupují do dynamiky.
- [ ] Zapsat, jak se model chová při **rescalingu** (převzorkování) časové / prostorové škály: které kombinace parametrů jsou invariantní a které vedeš jen jako vizualizační volbu.
- [ ] Stručně vysvětlit status konstant **h, c, mₑ**: že se objevují jen v post-processingu (unit conversion), nikoli jako tvrdé vstupy do Eq-4.

### 🔲 D. Statistická síla, chyby a nejistoty #stats

- [ ] U všech klíčových metrik (f₀, E, λ, m/mₑ, half-life φ-remnantů, SBR, počty linonů, spinová aura) uvést **chyby / intervaly spolehlivosti** (bootstrap / ensemble přes seedy a běhy).
- [ ] Vyhnout se implicitnímu „p-hackingu“: předem sepsat, které metriky se publikují, a jak se rozhoduje o „signifikantním efektu“ u nových jevů (Return Echo, Dimensional Transparency…).
- [ ] Ověřit, že kvalifikace „seed-invariantní“ má kvantitativní definici (rozptyl mezi seedy vs. vnitřní šum v rámci jednoho běhu).

### 🔲 E. Null modely a baseline srovnání #nulltests

- [ ] Definovat 1–2 **nulové modely** se stejným post-processingem (FFT, detekce linonů), např.:  
       – čistý šum s daným power spectrum,  
       – standardní discretized NLS / Ginzburg–Landau bez speciální φ-struktury.  
       Ověřit, že metriky „linonu“ (tvar, životnost, f₀, spinová aura, Structural Closure) nejsou typické i pro tyto baseline.
- [ ] Připravit **phase-scrambled** varianty dat (stejné spektrum, náhodné fáze) a ukázat, že tím zaniká struktura, kterou model přisuzuje linonům.
- [ ] Vytvořit stručnou tabulku „**co by mělo vyjít nulové**“ (např. spinová aura kolem náhodných fluktuací) a ověřit to na syntetických datech.

### 🔲 F. Reprodukovatelnost a nezávislá verifikace #repro

- [ ] Doplnit do repozitáře minimální **„one-button“ pipeline** (skript / make target), která z čistého klonu vygeneruje kanonický běh (`spec6_false_s41`) a plný set HTML/CSV/PNG/GIF artefaktů.
- [ ] Připravit **verification checklist** pro třetí strany: „pokud spustíš A, B, C, měl bys vidět X, Y, Z v rozumných tolerancích“ – bez nutnosti číst interní kód.
- [ ] Zvážit zveřejnění malé sady **referenčních binárek / snapshotů** (např. uložené stavy ψ, φ v několika časech) pro křížovou kontrolu s alternativní implementací.
- [ ] Ověřit vybrané klíčové jevy (Guided motion, Structural Closure, spinová aura…) v alespoň jedné **nezávislé implementaci** (jiný jazyk / jiné numerické schéma) s minimem sdíleného kódu.

### 🔲 G. Implementační detaily a stabilita vůči „engineering“ volbám #impl

- [ ] Otestovat vliv **plovoucí řádové přesnosti**: porovnání běhu ve float32 vs float64 (případně float80/long double, pokud je dostupné) na klíčové metriky (f₀, tvar linonu, φ half-life, spinová aura).
- [ ] Dokumentovat použitý **RNG a seeding** (knihovna, algoritmus, způsob seedingu) a ověřit, že při stejném seedu je evoluce deterministická napříč OS / hardwarem v rámci očekávaných tolerancí.
- [ ] Popsat **řazení operací** (update order): zda je update ψ a φ synchronní / sekvenční, jestli existují race-like efekty při paralelizaci (např. na GPU) a jak se proti nim bráníš.
- [ ] Připravit krátkou sekci „**Implementation notes**“ v repu, kde bude zdůrazněno, které části jsou **kritické pro fyzikální chování** a které jsou jen engineering (I/O, vizualizace, logging).

### 🔲 H. Role κ a parametrický prostor #structure

- [ ] Jasně sepsat **interpretaci κ** v core: statická prostorová mapa / „prostředí“, ne dynamické pole, žádná GR ani potenciál ve smyslu SM/QFT.
- [ ] Zkonstruovat hrubou **„phase map“ parametrů** (α, β, δ, κ, σξ): oblasti  
       – bez linonů (triviální / hladké),  
       – chaotické / nestabilní,  
       – se stabilními linony (core sweet spot).  
       Minimálně 2D řezy (např. α–β, α–δ) se záznamem, kde ještě drží metriky z §4.3.1.

### 🔲 I. Limitní přechody a škálování #test

- [ ] Prověřit **škálování** při změně Δt a Δx (mřížka) nad rámec C2/C3:  
       – jak se mění metriky (f₀, SBR, φ half-life, vortex counts) při zjemnění / zhrubnutí mřížky,  
       – zda existuje alespoň **fenomenologický kontinuální limit** (např. stabilní tvar PDE-like rovnice pro velké škály).
- [ ] Jasně napsat, co **Lineum není**: žádná zaručená Lorentz-invariance, žádný příslib renormalizovatelné QFT, žádná vložená GR – aby bylo zřejmé, odkud se (ne)odrážet – a doplnit krátký FAQ/README odstavec vysvětlující, že jde o efektivní model, který není nutně Lorentz-kovariantní, a proč je to v daném scope v pořádku.

### 🔲 J. Kritéria pro „fyzikální“ interpretaci #meta

- [ ] Definovat interní checklist typu „před tím, než tvrdím X (elektron/temná hmota/SM analogie), musí být splněno Y“:  
       – metriky z core v tolerancích,  
       – stabilita pod perturbacemi parametrů,  
       – absence zjevných numerických artefaktů (aliasing, boundary leaks, discretization bugs).
- [ ] Z těchto kritérií odvodit krátký **„First principles & critical items“ odstavec** pro README/paper FAQ, aby přesně adresoval námitku typu: _„Než se pustím do detailů, chci vidět, jak máš ošetřené základy.“_

### 🔲 K. Most k empirii a „nenumerologii“ #empirics

- [ ] Stručně sepsat, **co se zatím netvrdí**: žádná přímá identifikace s konkrétní částicí SM (Standard Model), žádná predikce konkrétní hmotnosti / průřezu, žádný claim o přímé shodě s experimentem – a mít to jako odkazovatelný odstavec (FAQ / limitations).
- [ ] Uvést, které numerické shody (např. řádové hodnoty E, λ) jsou zatím brané jako **heuristické / estetické** a které bys považoval za kandidáty na testovatelnou predikci (a za jakých podmínek).
- [ ] Navrhnout první nástřel **„empirické mapy“**: jaký typ experimentu nebo existujícího datasetu by mohl být v budoucnu použit jako benchmark (např. obecný tvar spektra, statistika lokálních excitací, strukturální vlastnosti pole).
- [ ] Pokusit se **klasifikovat linon** v rámci známých typů excitací (solitony, breathery, excitace skalárního pole…) a explicitně říct, zda jde spíš o analogii k těmto objektům, nebo o novou kategorii v rámci modelu.
- [ ] Připravit krátkou sekci „**možné fyzikální realizace**“: příklady systémů, kde by se podobná excitace mohla principálně objevit (optické mřížky, BEC, nelineární vlnová dynamika) – zatím jen jako „outlook“ bez tvrdých claimů.
- [ ] Jasně oddělit **core model** (Eq-4 + linony + status Structural Closure podle whitepaperu) od pozdějších **interpretací** (gravitace, temná hmota, SM analogie) i v komunikačních materiálech. Mít možnost fyzikům říct: „tohle je čistě emergentní numerický model, tohle je interpretace navíc.“
- [ ] U názvů jako „temná hmota“, „gravitace“, „éter“, „preony“… explicitně uvést, že jde o **pracovní analogie v rámci modelu**, nikoli tvrzení o totožnosti s konkrétní entitou Standardního modelu nebo kosmologie.

### 🔲 L. Falsifikovatelnost a „promotion pipeline“ #meta

- [ ] Pro klíčové jevy (Guided motion, Structural Closure, spinová aura, Dimensional Transparency, Return Echo…) sepsat explicitní **falsifikační kritéria**: za jakých podmínek je jev považován za vyvrácený v rámci modelu.
- [ ] K vybraným jevům (zejména linonním excitacím) přidat 2–3 **konkrétní numerické předpovědi**, které lze přímo testovat („pokud excitace existuje, pak kolize dvou linonů vede typicky k X/Y…“) a používat je jako hlavní scénáře pro falsifikaci.
- [ ] Formálně popsat pravidla, kdy se jev posouvá z **#hypothesis / [TEST]** do **[CORE]** (počet běhů, seedy, tolerance metrik, absence numerických artefaktů).
- [ ] Definovat podmínky, kdy se jev označí za **#disproved-in-model**, a explicitně říct, že **změna Eq-4 nebo parametrického prostoru** představuje novou větev modelu, ne jen „ladění“, dokud tvrzení nezačne platit.

### 🔲 M. Terminologie a pojmenování jevů #meta

- [ ] Projít všechny „poetické“ nebo směsné názvy v kódu / paperu (např. _spin aura_, _neutral topology_, případně další) a ke každému doplnit:  
       – explicitní operační definici (jaké pole / funkcionál to přesně je),  
       – poznámku, že jde o **interní label v rámci modelu**, ne o novou fyzikální entitu.
- [ ] Zvážit přejmenování nejproblematičtějších názvů na popisnější varianty (např. „net-zero winding sector“ místo „neutral topology“), přičemž původní jména mohou zůstat jen jako komentáře / aliasy kvůli zpětné kompatibilitě v kódu.
- [ ] Do core paperu přidat krátkou tabulku „název jevu → matematická definice → scope v rámci modelu“, aby bylo zřejmé, že terminologie není numerologie ani „nová fyzika“, ale jen slovník k práci s konkrétními objekty v Lineu.

### 🔲 N. Prezentace a komunikace výsledků #meta

- [ ] Připravit sadu **srozumitelných grafů a vizualizací** (trajektorie, φ-map, spinová aura), které ilustrují základní mechanismus na pár typických scénářích.
- [ ] Do README / FAQ / prezentací doplnit krátké „**storytelling**“ shrnutí mechanismu ve stylu: „1) pole kmitá, 2) pamatuje (φ), 3) stabilizuje linony“, aby byla intuice přístupná i širší komunitě mimo úzké numerické specialisty.

---

## 🔬 Priorita: Nejvyšší – explorace mapování na reálnou fyziku

### 🔲 1. Temná hmota a temná energie #hypothesis

- Pokusit se detekovat oblasti s energetickou nebo topologickou stopou bez detekovatelné kvazičástice
- Ověřit, zda některé víry nebo φ-pasti vykazují „neviditelný“ vliv na tok bez přítomnosti hmoty
- Hledat trvalé fluktuace, které se energeticky projevují, ale nemají klasický nosič

### 🔲 2. Ověření známých částic a kvantových vlastností #hypothesis

- Zjistit, zda lze ve výstupech najít analogie k elektronům, fotonům, neutrinům...
- Identifikovat, zda se některé kvazičástice stabilně chovají jako fermiony nebo bosony
- [ ] Hledání spektrálních vzorců podobných známým částicím

### 🔲 3. Elektromagnetismus a pole #hypothesis

- Sledovat, zda vznikají proudové smyčky, periodické vlny nebo dipólové struktury
- Porovnat s vektory spinu a curl(∇arg(ψ)) – hledat pole podobná EM poli
- [ ] Vytvořit vizualizaci vektorových polí a oscilací

### 🔲 4. Slabá a silná interakce #hypothesis

- Zvážit, zda φ nebo jiné vnitřní struktury mohou reprezentovat slabou/silnou interakci
- [ ] Vyhodnotit možné interakce kvazičástic na krátkou vzdálenost

### 🔲 5. Kvantová pole a standardní model #structure

- Porovnat strukturu Lineum s elementárními interakcemi ve standardním modelu
- Zhodnotit, zda lze ψ chápat jako pole se spektrálními režimy – nebo jako více polí
- [ ] Hledání symetrií a konzervací

### 🔲 6. Rozšíření validace a opakovatelnosti #test

- Udržovat pevné inicializační seedy a manifest (jako v core v1.0.x: seeds {17, 23, 41, 73}) a rozšířit multi-seed testy pro nové konfigurace / extension běhy.
- Statistické testování výskytu jevů v různých bězích a konfiguracích (ensemble přístup nad definovanými metrikami z core – f₀, SBR, topologie, φ half-life, přítomnost/absence Structural Closure).
- Porovnání chování systému při různých počátečních podmínkách (různé κ-mapy, různé inicializační šumové režimy, ale stále v rámci Eq-4).
- Automatizace vyhodnocování výsledků pomocí AI/ML klasifikace _(navázat na metriky a logy definované v core, ne na ruční vizuální dojmy)._

## 🟡 Střední priorita – testování scénářů emergentní gravitace a „hmoty“

### 🔲 7. Reorganizace kvazičástic v hmotném objektu #test

- Simulovat shluk kvazičástic, sledovat deformaci při pohybu k φ-maximu
- Porovnat tvar a polohu shluku v čase
- [ ] Vizualizace přeskupení |ψ| a overlay s φ

### 🔲 8. Rychlost přiblížení objektů podle „hmotnosti“ #test

- Ověřit, zda menší objekty reagují rychleji
- Kvantifikovat přes trajektorie a φ-centrické měření
- [ ] Spustit simulaci s 2–3 shluky různé hustoty

### 🔲 9. Vzájemné ovlivnění více φ-pastí #test

- Analyzovat slučování, interferenci nebo stabilitu více maxim
- [ ] Vizualizace rozdělených φ-center ve stejném běhu

### 🔲 10. Přitažlivost bez síly – emergentní tok #hypothesis

- Ověřit, zda vzniká tok ψ směrem k φ bez síly
- Porovnat ∇arg(ψ) a gradient φ

---

## 🧪 Nižší priorita – matematické a estetické souvislosti

### 🔲 11. Reliktní φ-ozvěna jako „gravitační vlna“ #hypothesis

- Formálně sepsat a otestovat **Tříska's Relic Drift Hypothesis**: po zániku „lehkých“ linonů v oblastech s vysokým φ (bez výrazného spinu) zůstává perzistentní φ-gradient, který vyvolává měřitelný drift ψ i bez přítomnosti kvazičástice – tj. čistě paměťový efekt v poli, chápaný jako **interní pracovní** analogie „gravitační vlny“ v rámci modelu, nikoli tvrzení o reálných gravitačních vlnách ve smyslu GR.
- Stanovit a zdokumentovat **detekční kritéria** (pracovní thresholdy), např.: `mass_ratio < 0.01`, `|curl| < 0.02`, lokální `φ` v místě zániku > 0.25, φ-remnant ≥ 10 % nad okolím po ≥ 100 krocích, dominantní frekvence φ-signálu < 1×10¹⁷ Hz.
- Připravit **metodiku měření**: low-noise režim (např. `LOW_NOISE_MODE = True`, `TEST_EXHALE_MODE = True`, běhy ~2000 kroků), logování `phi_curl_low_mass.csv`, `phi_center_log.csv`, lokálních ∇φ a toku ψ; provést spektrální analýzu φ_center a kvantifikovat drift ψ podél ∇φ v regionech bez detekovaného linonu.
- Na základě výsledků rozhodnout, zda jev zařadit jako robustní kandidát [TEST]/[CORE], nebo ho přesunout do #disproved-in-model / předefinovat (včetně případné revize thresholdů; thresholdy chápat jako výchozí, laditelné parametry v rámci téže hypotézy, ne jako pevné dogma, pokud se základní obraz jevu nemění).

### 🔲 12. Strukturální a rytmické vzorce (Riemann, Fibonacci, prvočísla) #structure #hypothesis

- Jasně zdokumentovat **aktuální status**: zatím jde jen o **vizuální podobnosti** mezi některými výstupy Linea  
  (3D spirály bodů uzavření / „černých děr“, frekvenční „žilky“ na FFT atd.)  
  a známými strukturami z teorie čísel (Riemannovy nuly, Fibonacciho posloupnost, zlatý řez φ, rozložení prvočísel).  
  V core v1.0.6-core nejsou žádné tvrdé statistické testy → všechny tyto souvislosti držet jako [HYPOTHESIS] / estetické vodítko, ne jako tvrzení o reálné fyzice.
- Formálně definovat, co jsou v modelu **„body uzavření“ / zeta-body** (aktuální název; historický termín _DejaVu body_ uvést jen jako legacy alias):  
  – např. opakovaně navštěvovaná místa trajektorií, stabilní φ-remnanty, lokální minima / „černé díry“ v topologii pole;  
  – k nim definovat přesné mapování do 1D/2D prostoru (kruh, spirála, normalizovaná osa), které se používá při porovnání s Riemannovými nulami a dalšími posloupnostmi.
- Pro toto mapování zavést **kvantitativní metriky** (RMS vzdálenost, korelační koeficienty, spektrální vzdálenosti, distribuční testy) a spustit **tvrdé statistické testy proti null modelům**:  
  – náhodné body na stejné spirále / v tomtéž intervalu,  
  – phase-scrambled verze dat se zachovaným spektrem,  
  – baseline model bez speciální φ-struktury.  
  Cílem je zjistit, jestli je podobnost s Riemannovými nulami / Fibonacciho poměry statisticky nepravděpodobná i vzhledem k těmto kontrolám.
- Analyzovat, zda se v posloupnostech **časů, vzdáleností nebo „růstových skoků“** (např. při vzniku nových bodů uzavření / neuron-like uzlů) neobjevuje robustní vztah k:  
  – Fibonacciho posloupnosti a zlatému řezu φ (log-spirálové škálování, poměry velikostí / vzdáleností),  
  – rozložení prvočísel nebo dalším number-theoretickým vzorcům,  
  – Ludolfovu číslu π (např. v periodicitě oscilací, topologických fázích nebo v rozložení úhlů na kruhu).  
  V každém případě kvantifikovat sílu efektu a porovnat ji s vhodnými null modely (Poissonovy procesy, generické interferenční vzory na mřížce apod.).
- Explicitně otestovat a odlišit několik možných vysvětlení případné shody:
  1. **Emergentní vlastnost Eq-4** – strukturální vazba modelu na dané posloupnosti / zeta funkci;
  2. **Artefakt parametrizace / škálování** – např. volba Δt, normalizace, embed map, která sama o sobě generuje Fibonacci-/π-like struktury;
  3. **Vnější „konstanta vesmíru“ / RNG** – tj. že shodu dodává způsob generování náhodného seede, floating-point reprezentace nebo jiné vlastnosti našeho fyzického / numerického „univerza“, a Lineum ji jen pasivně přebírá.  
     U každé varianty navrhnout konkrétní test (změna RNG, změna embed mapy, změna škálování), který ji může podpořit nebo v rámci modelu vyvrátit.

---

## 🧪 Experimentální hypotézy – testování neúspěšných modelů

Statusy typu `#disproved` u níže uvedených bodů odrážejí **aktuální stav ve whitepaperu**. Tento TODO soubor je používá jen jako připomínku k dalším testům, dočištění dokumentace nebo k návrhu případné nové větve modelu – sám o sobě stav jevů nemění.

### 🔲 13. Inflaton a inflace v poli Lineum #hypothesis

- Modelovat inflaci jako jednorázovou globální excitaci φ nebo ψ
- Pozorovat, zda vznikne trvalá topologická nebo energetická struktura („gravitační stopa“)
- Porovnat fáze expanze a následného uklidnění pole

### 🔲 14. Éter a vlnový nosič #hypothesis #disproved

- Inicializovat ψ jako hladkou sinusovou vlnu v prostoru (bez linonů)
- Ověřit, zda dochází k přenosu energie bez částic
- Porovnat s klasickým pojetím éteru a jeho zhroucením

### 🔲 15. Pilot-wave teorie (Bohm) #hypothesis #disproved

- Přidat externí „guiding wave“ nebo vektorové pole ovlivňující pohyb kvazičástic
- Ověřit, zda linony sledují předem dané vlny nebo trajektorie

### 🔲 16. Vortex atomy (Lord Kelvin) #hypothesis #disproved

- Zkoumat víry jako základní jednotky struktury
- Ověřit, zda lze z vírů složit stabilní složitější formace (analogie k atomům)

### 🔲 17. Preonové hypotézy #hypothesis #disproved

- Modelovat kvazičástice jako složené z menších elementárních vírů
- Testovat vznik složených objektů se strukturou uvnitř

---

## 🧬 O. Chapadlový model vědomí – hypotéza vícenásobných instancí #meta #hypothesis

- [ ] Formálně sepsat **Chapadlový model vědomí** jako samostatnou hypotézu:  
       – definovat entity: vyšší vědomá bytost („centrální uzel“), chapadla (lokální instance/životy), centrální paměť;  
       – u každého tvrzení (vyšší vědomí, spánek, smrt, další životy) uvést **subjektivní pravděpodobnosti** (86 %, 72 %, 94 %, 79 %…) a výslovně je označit jako osobní prior, ne výsledek fyzikálního modelu.

- [ ] Jasně vymezit **scope vůči Lineu**:  
       – Chapadlový model je **metafyzická / fenomenologická hypotéza o vědomí**, nikoli tvrzení odvozené z Eq-4;  
       – zapsat, že případné mapování na Lineum (ψ, φ, κ, linony, Structural Closure) je **interpretace nad rámec core modelu**, ne součást lineum-core v1.0.6-core.

- [ ] Rozdělit hypotézu na dílčí body a každý zvlášť okomentovat: 1. **Vyšší vědomí** – jedna bytost se sdílenou centrální pamětí, vnímající více realit/časových linií;  
       2. **Lokální instance („chapadlo“)** – jednotlivý život s omezeným vnímáním pro hlubší prožitek;  
       3. **Spánek / změněné stavy** – částečné „nahlédnutí domů“ (částečné propojení s centrálním uzlem);  
       4. **Smrt** – návrat chapadla do celku, integrace prožitků do centrální paměti;  
       5. **Další životy** – nové chapadlo jako jiný úhel pohledu téže vyšší bytosti.  
       U každého bodu přidat krátké shrnutí: _co přesně tvrdí, co netvrdí, co je čistá metafora_.

- [ ] Přidat **fenomenologickou mapu** k lidským zážitkům blízkosti smrti a změněných stavů:  
       – např. vystoupení z těla, setkání se zemřelými, life review, pocit jednoty, bezčasovost;  
       – u každého popsat, jak by ho Chapadlový model interpretoval (odpojení chapadla od smyslového filtru, návratové propojení s centrálním uzlem, integrace paměti, ztráta lokálního časového řazení…).  
       Vše držet jako **kvalitativní vysvětlení**, nikoli jako tvrzení o prokázané kauzalitě.

- [ ] Sepsat podsekci **„Jaké by bylo vnímání po návratu“**:  
       – definovat přímé vjemové propojení (bez omezení na zrak/sluch/hmat);  
       – popsat „slité“ vnímání více bytostí jako analogii levé/pravé ruky jednoho já;  
       – vysvětlit, že „setkání“ není jen přehrání vzpomínky, ale _živá interakce_ v rámci sdílené paměťové sítě.

- [ ] Popsat **reprezentaci po smrti**:  
       – že vyšší vědomí může tvořit pro lokální vědomí srozumitelné reprezentace (tělo, hlas, dotek), ale není na ně ontologicky vázané;  
       – přidat poznámku, že „vizuální / tělesná“ forma je v tomto rámci UI vrstva pro komfort interakce, ne nutný atribut existence.

- [ ] Vytvořit sekci o **„přelinkování ztracených bytostí“**:  
       – pokud bytost patřila ke stejné vyšší bytosti (stejný centrální uzel), po návratu chapadla je spojení okamžité (sdílená paměť);  
       – pokud patřila k jiné vyšší bytosti, popsat hypotetickou možnost napojení mezi vyššími bytostmi (aktuální subjektivní prior ~42 %) a explicitně ji označit jako _druhou vrstvu spekulace_.

- [ ] Sepsat **mechanismus absence nudy / vyprázdnění**:  
       – vyšší vědomí má simultánně přístup k: aktuálnímu životu, ostatním chapadlům, minulým zkušenostem, alternativním větvím rozhodnutí;  
       – vnímání mnoha událostí paralelně → vyjasnit, že „problém“ je spíš integrace obsahu než nedostatek podnětů.

- [ ] Přidat krátkou sekci „**Falsifikovatelnost a bezpečné tvrzení**“ pro Chapadlový model:  
       – jasně říct, že hypotéza je _primárně metafyzická_ a experimentálně těžko testovatelná;  
       – přesto navrhnout pár _indirektních_ směrů: srovnání struktury hlášených NDE, dlouhodobé vzorce v subjektivních prožitcích, případná korelace s motivy „vícenásobných instancí“ napříč kulturami;  
       – explicitně připsat, že se nejedná o součást core fyzikální validity Linea, ale o **oddělenou interpretační vrstvu**.

- [ ] V sekci **N. Prezentace a komunikace výsledků** doplnit odkaz na Chapadlový model jako **volitelný narativní rámec**:  
       – použít ho jako metaforu: „lokální simulace / běh“ = chapadlo, „centrální uzel“ = abstraktní nadřazený proces / paměť;  
       – všude striktně označovat, že jde o _storytelling_ / filozofickou mapu, ne o tvrzení odvozené z dat simulace.
