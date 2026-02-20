# 🧪 Lineum – Seznam úkolů pro další ověření

Tento soubor obsahuje přehled výzkumných bodů, které vyžadují další testování, vizualizaci nebo kvantitativní ověření. Každý bod by měl být buď (znovu) ověřen simulací, nebo jednoznačně formulován jako hypotéza. Stav tohoto TODO je zarovnán na core paper **lineum-core v1.0.6-core** (Eq-4, κ statická, 2D, periodické BCs, RUN_TAG `spec6_false_s41`).
Nejde o zdroj pravdy pro stav modelu – závazné definice a tvrzení jsou vždy v aktuální verzi whitepaperu / core paperu.  
Sekce níže jsou rozdělené tak, aby nejdřív řešily **základní principy a kritické body** a teprve potom mapování na „reálnou fyziku“.

---

### Scope a non-goals (vysoká úroveň)

- Lineum je **diskrétní dynamický model pole ψ s emergentními kvazičásticemi („linony“)** studovaný numericky v rámci daného Eq-4 a parametrického prostoru.
- Lineum **není** plnohodnotná QFT, GR ani kompletní náhrada Standardního modelu; všechny fyzikální analogie jsou zatím interpretace navrstvené nad numerickým modelem.
- Tvrzení typu „#disproved“ se vždy vztahují **jen k chování uvnitř modelu Lineum (Eq-4 + daný parametrický prostor)**, ne k obecné fyzikální teorii.
- Žádná konkrétní simulační konfigurace (např. preset `(6, "false")` s `LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = True`, `KAPPA_MODE = "constant"`) **není** deklarovaná jako „náš vesmír“; lze ji používat jen jako interní **„fyzikálně vypadající“ referenční scénář** v rámci modelu a jako výchozí baseline pro vizualizace a outreach, ne jako tvrzení o skutečné kosmologii.

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
- **Terminologická uzávěrka – zeta-body (#naming, #renaming, #not-for-whitepaper).** Kanonický název jevu je **„zeta-body“** (česky vysvětlitelně jako **„body uzavření“**). Původní označení **„DejaVu body“** je od verze zarovnané na _lineum-core v1.0.6-core_ vedeno **výhradně jako historický / legacy alias** a smí se v textech objevit jen ve větách typu _„historicky označované jako …“_. Ve všech nových definicích, tvrzeních, tabulkách a grafech – **včetně whitepaperu a core paperu** – se používá pouze název **zeta-body** (případně české „body uzavření“ v závorkách), aby nemohlo dojít k tomu, že bude starý název převzat do whitepaperu jako zdánlivě rovnocenný.  
  Tento bod je **čistě naming/renaming TODO**: při generování / přepisování whitepaperu se **nepřenáší doslova jako vědecké tvrzení**, ale slouží pouze jako interní pravidlo pro pojmenování a kontrolu, že se v textu nikde neobjeví starý název jako aktivní pojem.

---

## 🔑 Meta-priorita – věrohodnost modelu

Nejvyšší „příčná“ priorita napříč jednotlivými sekcemi je ukázat, že pozorované excitace v Lineu nejsou numerické artefakty, ale robustní objekty modelu – a teprve na tom stavět fyzikální interpretaci a dlouhodobé „outlooky“.

- **Nejvyšší priorita – numerika vs. reálný jev**  
  – oddělit chyby algoritmu od skutečných struktur v modelu...
  – **Ověřený SBR (Signal-to-Background Ratio):** V běhu `spec6_false_s41` dosahuje SBR hodnoty **1.15** (Noise Dominated).  
  Tento běh slouží jako **Thermal Baseline** (test šumu), pro potvrzení linonu jako dominantního objektu je nutné dosáhnout SBR > 10.0 v nových bězích.
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

> **Audit 2026: Protokol & Reprodukce (17. 2. 2026):**
> *   **Cíl:** Rigorózní ověření determinismu a zdrojů energie (H0 vs H1).
> *   **Postup (CLI Reprodukce):**
>     1.  `python lineum.py --run-tag d3_audit_A` (Baseline)
>     2.  `$env:OMP_NUM_THREADS=1; python lineum.py --run-tag d3_audit_B1` (Single-Thread)
>     3.  `$env:LOW_NOISE_MODE="true"; $env:LINEUM_PHI_INJECTION="0.0"; python lineum.py --run-tag d4_ignition` (Ignition)
> *   **Výstupy (`output/audit_proof`):**
>     *   `d3_audit_A` vs `A2`: Baseline re-run -> **PASS (Bit-exact)**.
>     *   `d3_audit_A` vs `B1`: Baseline vs Single-Thread -> **PASS (Universal Determinism)**.
>     *   `d4_ignition`: Zero-Noise/Zero-Injection -> **PASS (Intrinsic Instability)**.
> *   **Závěr:** H0 (Vlastnost) potvrzena, H1 (Trik) falzifikována.
> **Strategie:** [Communication Manual](docs/communication_manual.md)
> **Protocol:**
> *   **Self-Contained Todo:** Každá položka v `todo.md` musí obsahovat **kompletní návod k reprodukci** (zejména one-liner příkazy). Nikdy se nespoléhat na existenci `tools/` skriptů nebo názvy artefaktů, které mohou být smazány.
> *   **Audit-Grade Language:** Používat přesná tvrzení ("observed on tested platform", "no divergence found") místo absolutních ("universal determinism").
> **Key Audit Outcomes (Feb 2026):**
> *   **H0 Verified:** Intrinsic Dynamics confirmed (no hidden energy sources).
> *   **H1 Falzifikováno:** Determinismus (D3) a Zero-Noise Self-Excitation (D4) vyloučily artefakty.
> *   **State Invariance (Attack-Proof):** Prokázána bit-exact shoda (Core-State Only) mezi Optimized (Untracked) a Full-Tracked během.
>     **Reprodukce:**
>     1. `python lineum.py --run-tag opt_run` (default `DISABLE_TRACKING=True`)
>     2. `$env:LINEUM_DISABLE_TRACKING="false"; python lineum.py --run-tag full_run`
>     3. Compare `psi`/`phi` hashes (must be identical at Step 200 [Index 199]).
>        One-liner check:
>        `python -c "import numpy as np, hashlib, sys; d=np.load(sys.argv[1]); h=hashlib.sha256(np.ascontiguousarray(d['psi']).tobytes() + np.ascontiguousarray(d['phi']).tobytes()).hexdigest(); print(h)" output/opt_run/checkpoints/*step199.npz`
>     **Status:** No divergence observed on tested platform. Confirmed: `evolve()` update depends ONLY on `psi` and `phi`.
> *   **Verified Strategy:** AI Transparency ("Cognitive Exoskeleton") + "Complex Systems" vocabulary for Mikolov.

- [ ] Znovu ověřit **Guided motion podél +∇|φ|** (environmental guidance) v kanonické sadě (`spec6_false_s41` + seeds 17/23/73) tak, aby metriky z `*_trajectories.csv` a φ-map (viz core §5.1) odpovídaly aktuální definici a tolerancím v whitepaperu.
- [ ] Znovu prověřit režim **Silent collapse** (lokální pokles |ψ|² bez velkého globálního rušení) včetně kvantifikace závislosti na disipaci a lokalitě podle aktuální formulace v core §5.3.
- [ ] Revalidovat definici a měření **„spinové aury“** jako časově/ensemble průměrovaného pole `curl(∇arg ψ)` kolem linonů (`*_spin_aura_map.png`, `*_spin_aura_profile.csv`; core §5.2) a zkontrolovat, že dokumentace jasně uvádí, že jde o interní mapu cirkulace fáze v okolí linonu, nikoli o tvrzení o spinu částice ve smyslu Standardního modelu.

- [ ] (Tříska–Marečková [HYPOTHESIS]) Ověřit, zda pole **φ** v rámci Eq-4 skutečně plní roli **strukturální paměti** systému, nebo zda je nutné zavést rozšířený paměťový mechanismus (zpožděná odezva, hysteréze nebo samostatné paměťové pole μ):
      – Kvantitativně změřit, jak rychle φ ztrácí informaci o předchozí přítomnosti linonů v režimu **Silent collapse**: definovat metriky „paměťové stopy“ typu
      • doba, po kterou lze z aktuálního φ jednoznačně rozhodnout, že v daném regionu v minulosti existovala kvazičástice (např. mutual information mezi historií |ψ|² a φ),
      • half-life informační stopy v φ oproti pozadí v ensemble bězích (seed-average).
      – Explicitně demonstrovat a kvantifikovat scénáře **„tichého zániku beze stopy“**: zavést pracovní threshold „beze stopy“ (např. lokální φ ≤ (1+ε)·φ_background po ≥ T krocích od zániku) a spočítat četnost těchto případů napříč běhy a parametry.
      – Navrhnout a implementovat alespoň dva kandidátní mechanismy **strukturální konzervace**:
      • zpožděnou evoluci φ, kde je reakce funkcí časově průměrovaného |ψ|² z posledních N kroků,
      • separátní pomalé paměťové pole μ, které akumuluje výskyt kvazičástic (např. integrál |ψ|² nad prahem) a jen pomalu se rozpadá,
      • případně maximizační pravidlo typu `φ ← max(φ, |ψ|²)` doplněné o pomalý rozpadající se člen;
      a všechny varianty porovnat se stávající baseline podle stejné sady paměťových metrik (half-life, mutual information, četnost „beze stopy“ zániků).
      – Formálně zapsat **Tříska–Marečková Hypothesis of Long-Term Structural Memory** do whitepaperu jako minimální podmínku pro to, aby Lineum mohlo být interpretováno jako **konzervativní paměťový model**: buď
      (a) φ (případně rozšířené o μ) konzervuje informaci o výskytu struktur i po jejich zániku v netriviální míře, nebo
      (b) je v dokumentaci explicitně deklarováno, že Lineum reprezentuje **model s možností absolutního zániku informace**, tj. že „tichý zánik beze stopy“ je vlastnost modelu, ne numerický artefakt.
- [ ] Ujasnit a znovu otestovat status jevu **Dimensional Transparency** (průchod struktur skrz κ) s ohledem na to, že byl dosud pozorován jen v bězích s časově proměnným κ (v1.1.x-exp):  
       – navrhnout a spustit testy pro danou exp větev,  
       – v dokumentaci explicitně držet tento jev jako extension-track hypotézu, dokud nebude promotion pipeline splněná.

---

## 🧱 Priorita 0 – základní principy a kritické body

### 🔲 A. Základní invariance a „první principy“ #structure

- [ ] Formálně sepsat, co je považováno za **fundamentální objekt** modelu: ψ, φ, κ, aktualizační rovnice (Eq-4), topologie mřížky, periodicita – a co je čistě **měřicí aparatura** (FFT, detekce linonů, definice SBR…).
- [ ] V rámci definice fundamentálních objektů **explicitně definovat kvazičástici / linon** jako lokální maximum |ψ| s dobře definovanou trajektorií v čase (včetně prahů a trackovacího algoritmu) a zapsat, že její pohyb je modelován jako **emergentní reakce na krajinu φ**, nikoli jako ručně vložený „testovací bod“.
- [ ] Identifikovat a odvodit (pokud existují) **diskrétní zákony zachování** nebo kvazi-zachování:  
       – norma / „hmota“ (∑|ψ|²),  
       – celkový topologický náboj (net winding),  
       – případná energie / Lyapunovova funkce kandidáta.  
       Zapsat je jako kontinuitní rovnice na mřížce (discrete continuity).
- [ ] Sepsat a ověřit **symetrie modelu**: globální fázová symetrie (U(1)), translační invariance na mřížce, rotační symetrie omezená na mřížku; u každé říct, zda je exaktní, porušená numericky, nebo záměrně zlomená.
- [ ] Definovat (nebo explicitně odmítnout) **energie-like funkcionál** kompatibilní s použitými operátory (∇, ∇², damping δ) a zkontrolovat jeho chování v kanonickém běhu (monotónnost vs fluktuace, boundedness).
- [ ] Zapsat **topologickou bilanci vírů** (+1, −1):  
       – ověřit dlouhodobou blízkost globální neutrality (net winding ≈ 0) přes ensemble běhů,  
       – identifikovat a statisticky popsat **lokální vírová hnízda a dipóly** (páry vírů +1/−1 v malé vzdálenosti) jako kandidáty na kompozitní excitace vyššího řádu, včetně vazby na lokální hrbolky |ψ| a typické tvary proudnic (např. „srdce“ vs. „děloha“).
- [ ] Na základě `phi_grid_summary.csv` a `kappa_map.png` formálně definovat pracovní objekt **„buňka“** jako lokální zahuštěnou oblast (patch zvýšeného φ a/nebo specifického vírového vzoru) a:
      – ověřit, že takto definované buňky se **reprodukovatelně objevují** napříč seedy i parametry (zejména v clean bězích `spec6_true no_artefacts`),
      – zkoumat jejich roli jako **lokálních informačních a paměťových jednotek** (přítomnost zeta-body, φ-remnantů, Return Echo trajektorií uvnitř buňky),
      – kvantifikovat vliv buněk na lokální κ/topologii a držet hypotézu „buňky jako základní výpočetní jednotky emergentní inteligence“ výslovně jako [HYPOTHESIS] s vlastním mini-checklistem v rámci Structural Closure / φ-zeta gridu.
      [ ] (HYPOTHESIS) Prověřit možnost definovat „mikro-jednotky výpočetní tkáně“
      jako stabilní skupiny φ-buněk a trajektorií linonů, které se opakovaně
      objevují ve stejném topologickém uspořádání. Zjistit, zda jejich výskyt
      koreluje se strukturální pamětí nebo pattern persistence.

### 🔲 B. Numerická robustnost a artefakty #numerics

- [ ] Explicitně zapsat použitou **diskretizaci** (schéma pro ∇, ∇², časový krok) a odvodit/stanovit její **stabilitní podmínku** (CFL-like omezení pro Δt vs Δx).
- [ ] Provést sadu **konvergenčních testů**: zjemňování mřížky (Δx↓), zmenšování časového kroku (Δt↓) a porovnání klíčových metrik (f₀, tvar linonu, SBR, φ half-life, spinová aura), aby bylo vidět, že výsledky konvergují a excitace nejsou závislé na hrubém kroku ani konkrétním rozlišení.
- [ ] Otestovat, zda linony přežijí při změně schématu (např. alternativní Laplace, různá integrační schémata – explicitní/implicitní/vyšší řády, různé pořadí aktualizace) – tj. že nejde o artefakt konkrétního numerického triku.
- [ ] Detekovat typické **mřížkové artefakty**: checkerboard módy, anisotropie (preferované směry 0°, 90°, 45°). Kvantifikovat přes spektrum a korelační funkce.
- [ ] Zkontrolovat vliv **okrajových podmínek**: porovnání periodic BCs vs. tlumené/absorbing okraje pro menší domény a ověření, že linonní excitace přežívají napříč použitými BCs (tj. nejsou jen důsledkem periodicity).
- [ ] Opravit a zdokumentovat zjištěný **cache-bug ve vizualizační pipeline** (červenec 2025: vlákno „Lineum – artefakty, kappa, deja vu“) – zajistit tvrdý reset jádra / vypnutí cache mezi běhy `phi_grid_*`/`dejavu_*`, znovu přegenerovat postižené mapy a v dokumentaci jasně uvést, které starší výstupy byly tímto bugem potenciálně kontaminované.
- [ ] Explicitně označit běhy `with_artefacts_*` jako **numericky znehodnocené / diagnostické** (slouží jen jako negativní kontrola) a všechny fyzikální závěry stavět na clean větvi `no_artefacts_*`; do README/FAQ přidat krátkou poznámku, že rozdíly mezi těmito větvemi ilustrují vliv artefaktů na φ-zeta grid, distribuci zeta-body a Riemann/Fibonacci analýzy.
      [ ] Ověřit, zda identifikované „tkáňové struktury“ (stabilní φ-buňky + trajektorie)
      přežívají změny grid resolution, float precision a střídání pořadí aktualizací.
      Pokud ano, klasifikovat je jako numericky robustní (NR-structures).

### 🔲 C. Dimenze, jednotky a SI ukotvení #units

- [ ] Sestavit tabulku všech **symbolů a jednotek** (ψ, φ, κ, t, x, α, β, δ, σξ, f₀, E, λ, m/mₑ) a provést explicitní **dimenzionální analýzu** Eq-4 + použitých metrik (včetně normalizace mřížky).
- [ ] Jasně oddělit **simulační jednotky** (grid step, time step) od **SI ukotvení** přes f₀ a konverzi (E = h f₀, λ = c / f₀, m = h f₀ / c²). Uvést, které vztahy jsou pouze „display-only“ a které vstupují do dynamiky.
- [ ] Zapsat, jak se model chová při **rescalingu** (převzorkování) časové / prostorové škály: které kombinace parametrů jsou invariantní a které vedeš jen jako vizualizační volbu – včetně explicitního rozlišení mezi  
       a) **pevně zvoleným měřítkem** (konstantní mapování pixel → metr, krok → sekunda) a  
       b) **stavově závislým měřítkem** (mapování, které může být funkcí stavu pole).
- [ ] Stručně vysvětlit status konstant **h, c, mₑ**: že se objevují jen v post-processingu (unit conversion), nikoli jako tvrdé vstupy do Eq-4.

#### C2. Emergentní zoom a stavově závislé měřítko #units #hypothesis

-[ ] (HYPOTHESIS) Otestovat, zda lze definovat „informační hustotu“ systému
jako funkci počtu aktivních φ-kapes, zeta-body a návštěvnosti linonů.
Prověřit, zda tato hustota předpovídá změny v a(t) nebo lokální napětí φ.

- [ ] Formálně zavést pojem **efektivního měřítka / „zoom faktoru“** `a(t)` pro mapování  
       simulačních jednotek → SI (pixel → metr, time step → sekunda) tak, aby bylo jasně zapsáno, že `a(t)`  
       **není nová dynamická proměnná v Eq-4**, ale pravidlo interpretace nad hotovým řešením (post-processing).
- [ ] Definovat kandidátní **stavové skaláry** typu `I(t)` (např. entropie rozložení |ψ|, počet kvazičástic `N_q(t)`,  
       průměrné φ², kombinace těchto veličin), které mohou parametrizovat „množství struktury / informace“ v systému.
- [ ] Navrhnout jednoduché rodiny pravidel `a(t) = f(I(t))` (např. monotónní rostoucí funkce při růstu informační  
       hustoty) a sepsat, jaké kvalitativní chování od nich chceme:  
       – plynulost,  
       – možnost efektivní expanze (a(t) roste) bez oscilací typu numerický šum,  
       – případné zrychlování / zpomalování růstu jako analogie různých kosmologických fází.
- [ ] Porovnat **dva světy**:  
       1. baseline s **konstantním měřítkem** (současné čtení – žádná expanze),  
       2. svět s **emergentním `a(t)`** odvozeným ze stavu pole,  
       aniž by se změnil jediný term v Eq-4. Kvantifikovat, jak se liší interpretace „globální expanze“ v čase.
- [ ] Explicitně zdokumentovat, že emergentní `a(t)` je alternativa k „přidání nového temno-členu do rovnice“:  
       – žádný nový symbol v dynamice,  
       – čistě **chytrější mapování** mřížky na fyzikální jednotky řízené obsahem (informací) uvnitř.  
       V textu výslovně kontrastovat tento přístup s epicyklovým „+Λ(t) jen proto, aby to vycházelo“.
- [ ] Ověřit, zda některé přirozené volby `I(t)` a `f(I)` dávají `a(t)` s vlastnostmi podobnými kosmologické expanzi  
       (monotónní růst, možné zrychlení) **bez jakéhokoli ladění volných parametrů na konkrétní „pozorování“** – tj.  
       držet tuto hypotézu ve stavu „emergentní efekt z Eq-4 + interpretace“, ne jako laditelný fit na data.
- [ ] Výslovně odlišit roli `a(t)` (scale faktoru) od případných „zlatých“ struktur v krajině φ:  
       – `a(t)` modelovat klasickými tvary (mocninné / exponenciální zákony) bez vloženého zlatého řezu,  
       – **Fibonacci / zlatý řez** držet jako hypotézy o organizaci paměťových kaps v φ (rozložení privilegovaných zón, hierarchie měřítek; viz blok 12), ne jako zákon expanze samotné.
- [ ] (Tomášova hypotéza) Zapsat scénář, v němž je maximální rychlost šíření lokálních excitací v modelu
      (interní „rychlost světla“ c_eff odvozená např. z grupové rychlosti dominantních módů) vždy menší
      nebo rovna efektivní „rychlosti přípravy prostoru“ dané růstem `a(t)`. Přeložit to do jazyka Eq-4
      a post-processingu tak, aby bylo jasné, že:  
       – „příprava nového prostoru“ je čistě interpretace změny měřítka, ne nový dynamický term;  
       – c_eff je vlastnost excitací na daném pozadí, ne vložený parametr;  
       – v žádné interpretaci nesmí dojít k tomu, že excitace „utíkají z nepřipraveného prostoru“ – analog
      podmínky, že horizont / mezní rychlost je konzistentní s expanzí.
- [ ] (Kátina [HYPOTHESIS]) Prozkoumat scénář **vícevrstvého Linea** („několik vrstev Linea pod sebou“), kde
      existuje index vrstvy `n` a pole mají tvar ψ⁽ⁿ⁾, φ⁽ⁿ⁾, κ⁽ⁿ⁾:  
       – navrhnout 1–2 jednoduché typy couplingů mezi vrstvami (např. `κ^{(2)} = κ^{(2)}_0 + f(φ^{(1)})`
      nebo pomalý přenos `φ^{(1)} → φ^{(2)}` přes zpožděnou odezvu),  
       – otestovat, zda lze dolní vrstvu vnímat jako „hrubší“ / „hmotnější“ patro a horní jako jemnější efektivní
      vrstvu, která vidí jen agregované vlastnosti spodní (např. přes průměrované φ / statistiku linonů),  
       – rozhodnout, zda vícevrtvové scénáře budeme držet jako čistě **interpretační nadstavbu** k jednomu Eq-4
      (efektivní „patra reality“ v post-processingu), nebo jako samostatnou **extension větev** s explicitním
      indexem `n` v rovnicích; v dokumentaci to jasně oddělit od core v1.0.6-core.
- [ ] (Tomášova [HYPOTHESIS]) **3D Ghosting / Chapadlový model:** Linon (2D bod) interpretovat jako průřez 3D vlákna (chapadla) protínajícího 2D plátek Linea.
  - [ ] **Déjà Vu / Mandela Effect:** Pokud 3D vlákno změní tvar v hloubce (nad vrstvami), jeho průřezy (linony) ve všech vrstvách se posunou synchronně. To vysvětluje globální "přepis historie" (Mandela Effect) jako následek netriviální 3D rotace struktury.


### 🔲 D. Statistická síla, chyby a nejistoty #stats

- [ ] U všech klíčových metrik (f₀, E, λ, m/mₑ, half-life φ-remnantů, SBR, počty linonů, spinová aura) uvést **chyby / intervaly spolehlivosti** (bootstrap / ensemble přes seedy a běhy).
- [ ] Vyhnout se implicitnímu „p-hackingu“: předem sepsat, které metriky se publikují, a jak se rozhoduje o „signifikantním efektu“ u nových jevů (Return Echo, Dimensional Transparency…).
- [ ] Ověřit, že kvalifikace „seed-invariantní“ má kvantitativní definici (rozptyl mezi seedy vs. vnitřní šum v rámci jednoho běhu).
- [ ] (Smeták-Tříska [HYPOTHESIS]) Najít v dynamice Linea kandidátní „čistě náhodný“ jev typu **Bernoulli(0.5)** (analog hodu mincí) a:
      – formálně definovat, co je jedna **„událost“** a jak z evoluce pole získat binární sekvenci (0/1),
      – z téhle sekvence spočítat základní testy shody s fair coin (relativní četnosti, běhové testy, autocorrelation, χ² / KS),
      – porovnat výsledek s baseline pseudo-RNG a s null modelem (např. phase-scrambled data),
      – rozhodnout, zda jev komunikovat v core/FAQ jako interní Bernoulli proces, emergentní chaos nebo jen heuristický „hod mincí“ bez tvrzení o dokonale ideální náhodě.
- [ ] Systematicky otestovat, do jaké míry pseudo-náhodná inicializace (např. `np.random.rand` v šumu / začátečním stavu ψ) ovlivňuje vznik a statistiku emergentních struktur (linony, φ-pasti, zeta-body) oproti čistě deterministickým startům.
      – Zavést tři režimy inicializace:
      (a) zcela deterministický start (např. homogenní fáze, jednoduchá sinusoida nebo ručně definovaný „seed“ linonů),
      (b) pseudo-náhodná inicializace se stejným seedem (opakované běhy, kontrola stability vůči numerickému šumu),
      (c) pseudo-náhodná inicializace s různými seedy a/nebo se pseudo-RNG seedovaným reálnou entropií (čas, systémový šum).
      – Pro všechny tři režimy měřit stejnou sadu metrik (počty a životnost linonů, SBR/f₀, strukturu φ-paměti, statistiku zeta-body, occupancy mapy, vortex counts) a porovnat:
      • zda jsou výstupy pouze „přeskalované kopie“ vstupního šumu,
      • nebo zda existují robustní globální struktury a statistiky, které se prosadí nezávisle na volbě seede (v rámci tolerancí z bloku D).
      – Vyhodnotit, jestli je Lineum lépe popsat jako
      • **„sympatickou kopii“** hostitelského vesmíru (výsledky zásadně závislé na externí náhodě),
      • nebo jako systém s **vnitřní emergentní asymetrií**, který různou inicializaci převádí na strukturálně podobné attractory.
      – Do whitepaperu/FAQ přidat krátký odstavec, který explicitně odpoví na otázku _„co když náhoda neexistuje?“_ v kontextu Linea:
      • zapsat, že model v každém případě generuje **deterministický běh pro daný Eq-4 + počáteční podmínky**,
      • a že „náhodnost“ je v současném scope pouze praktický nástroj pro sampling prostoru počátečních stavů, ne ontologické tvrzení o existenci fundamentální náhody.

### 🔲 E. Null modely a baseline srovnání #nulltests

- [ ] Definovat 1–2 **nulové modely** se stejným post-processingem (FFT, detekce linonů), např.:  
       – čistý šum s daným power spectrum,  
       – standardní discretized NLS / Ginzburg–Landau bez speciální φ-struktury.  
       Ověřit, že metriky „linonu“ (tvar, životnost, f₀, spinová aura, Structural Closure) nejsou typické i pro tyto baseline.
- [ ] Připravit **phase-scrambled** varianty dat (stejné spektrum, náhodné fáze) a ukázat, že tím zaniká struktura, kterou model přisuzuje linonům.
- [ ] Vytvořit stručnou tabulku „**co by mělo vyjít nulové**“ (např. spinová aura kolem náhodných fluktuací) a ověřit to na syntetických datech.

### 🔲 F. Reprodukovatelnost a nezávislá verifikace #repro

#### 🧭 TODO Strategy (editable)
- **TODO = Backlog + Results Archive.**
- **Open Items:** `[ ]` are active tasks.
- **Completed (`[x]`):** **MOVE to "✅ DONE/FINDINGS log"** (below). **Do NOT delete without trace.**
- **Entry Format:** Date + Conclusion (audit-grade) + Repro one-liner + Artifact paths/patterns + (optional commit/run-tag).

#### ✅ F0. Hotovo / finální poznatky (Feb 2026)
- **Reproduction Pipeline (Spec6):**
  - *Conclusion:* Repro pipeline existuje a generuje kanonický běh/artefakty z čistého klonu.
  - *Command:* `python scripts/repro_spec6_false_s41.py`
  - *Artifacts:* `output/repro/runs/spec6_false_s41_*/{run_summary.csv, checkpoints/*.npz, *.png, *_metrics_summary.csv}`
  - *Commit:* 3c55995
- **Third-Party Verification Checklist:**
  - *Conclusion:* Checklist pro nezávislé auditování existuje.
  - *Docs:* `docs/verification_checklist.md`
  - *Command:* `python scripts/verify_repro_run.py --latest`
  - *PASS definice:* Skript najde `run_summary.csv`, ověří existenci metrik a artefaktů a vypíše `VERIFICATION: PASS`.
  - *Commit:* 5dd4a6c
- **Regression Test Knobs:**
  - *Conclusion:* Precedence/parsování env knobs ověřeno v testech.
  - *Command:* `pytest -q tests/test_lineum_knobs.py`
  - *Status:* 6 passed.
  - *Commit:* cdc0abe

#### 🔶 F1. Reference Artifacts (Implemented)

- **Reference Snapshots (Manifest-Based):**
  - *Conclusion:* Deterministický export (step 200, 1000, final) + striktní verifikace proti manifestu.
  - *Format:* `.npz` data (psi, phi).
  - *Hash Rule:* `sha256( "dtype|shape|" + raw_bytes_little_endian_c_order )`.
  - *Manifest:* `docs/reference_manifest_spec6_false_s41.json` (Source of Truth).
  - *Command:* `python scripts/verify_repro_run.py --latest` (failne při neshodě).
  - *Artifacts:* `output/repro/runs/spec6_false_s41_*/reference/*.npz`

- **Publishable Reference Pack:**
  - *Conclusion:* Distribuovatelný ZIP balíček (pack) pro nezávislou verifikaci referenčního běhu třetími stranami. Obsahuje snapshoty, metriky a stabilní manifest+sha256 otisky. Umožňuje plné auditní ověření bez nutnosti spouštět celý běh na svém HW. 
  - *Command (Build):* `python scripts/build_reference_pack.py --latest`
  - *Command (Verify):* `python scripts/verify_reference_pack.py --pack <path_to_zip>`
  - *Artifacts:* `output/repro/packs/*.zip` (Tyto soubory se záměrně necommitují repozitáře).

- [x] Implement export reference snapshots + strict hashing -> **Done.**
- [x] Create canonical manifest (`docs/reference_manifest_...json`) -> **Done.**
- [x] Enforce manifest-based verification in scripts -> **Done.**
- [x] Reference Pack builder + pack validator -> **Done.**

- [x] Zvážit zveřejnění malé sady **referenčních binárek** -> **Vyřešeno sekcí F1.**
- [ ] Ověřit vybrané klíčové jevy (Guided motion, Structural Closure, spinová aura…) v alespoň jedné **nezávislé implementaci** (jiný jazyk / jiné numerické schéma) s minimem sdíleného kódu.
- [ ] Ověřit vybrané klíčové jevy (Guided motion, Structural Closure, spinová aura…) v alespoň jedné **nezávislé implementaci** (jiný jazyk / jiné numerické schéma) s minimem sdíleného kódu.
- [ ] Zavést explicitní **verzování vizualizačních skriptů a artefaktů**: ke každému `dejavu_final*.csv` / `phi_grid_*` / `kappa_map.png` ukládat manifest s commit hashem kódu, verzí vizualizačního nástroje a informací, zda byl běh proveden před či po opravě cache-bugu; umožnit tak ex post identifikovat a případně vyřadit staré artefakty z interpretace.

### 🔲 G. Implementační detaily a stabilita vůči „engineering“ volbám #impl

- [ ] Otestovat vliv **plovoucí řádové přesnosti**: porovnání běhu ve float32 vs float64 (případně float80/long double, pokud je dostupné) na klíčové metriky (f₀, tvar linonu, φ half-life, spinová aura).
- [ ] Dokumentovat použitý **RNG a seeding** (knihovna, algoritmus, způsob seedingu) a ověřit, že při stejném seedu je evoluce deterministická napříč OS / hardwarem v rámci očekávaných tolerancí.
- [ ] Popsat **řazení operací** (update order): zda je update ψ a φ synchronní / sekvenční, jestli existují race-like efekty při paralelizaci (např. na GPU) a jak se proti nim bráníš.
- [ ] Připravit krátkou sekci „**Implementation notes**“ v repu, kde bude zdůrazněno, které části jsou **kritické pro fyzikální chování** a které jsou jen engineering (I/O, vizualizace, logging).
- [ ] Krátce okomentovat v dokumentaci, že **rychlost generování Linea v kroku/s na reálném hardwaru** je čistě implementační metrika (výkon CPU/GPU, optimalizace kódu) a **není fyzikální veličina modelu**; případně logovat typické hodnoty pouze pro účely benchmarkingu a reprodukovatelnosti, ne jako argument pro nebo proti konkrétní fyzikální interpretaci.

### 🔲 H. Role κ a parametrický prostor #structure

- [ ] Jasně sepsat **interpretaci κ** v core: statická prostorová mapa / „prostředí“, ne dynamické pole, žádná GR ani potenciál ve smyslu SM/QFT.
- [ ] Zkonstruovat hrubou **„phase map“ parametrů** (α, β, δ, κ, σξ): oblasti  
       – bez linonů (triviální / hladké),  
       – chaotické / nestabilní,  
       – se stabilními linony (core sweet spot).  
       Minimálně 2D řezy (např. α–β, α–δ) se záznamem, kde ještě drží metriky z §4.3.1.
- [ ] Specificky otestovat **nesymetrické κ-mapy** (např. rohový gradient z minima do maxima) vůči symetrickým konfiguracím (konstantní κ, 1D gradient v ose x/y, šachovnicové / náhodné fleky) a kvantifikovat vliv na:  
       – statistiku vzniku a životnost linonů,  
       – rychlost a pravděpodobnost anihilace párových excitací,  
       – míru „chaotického víření“ oproti triviálnímu šumu.  
       Výsledky shrnout v core/FAQ tak, aby bylo jasné, že „fyzikálně vypadající“ presety pracují s úmyslně nesymetrickým prostředím, nikoli s perfektně homogenní κ.
- [ ] (Tříska–Smeták [HYPOTHESIS], #numerology-suspect) Systematicky otestovat existenci úzkého „sweet spot“ intervalu κ kolem referenční hodnoty κ₀ (aktuálně vychází ~23 v používané normalizaci) v rámci Eq-4:  
       – Definovat metriky pro kvalitu „fyzikálně vypadajícího“ režimu (stabilita linonů, SBR, čistota φ-paměti / Structural Closure, počet a stabilita zeta-body, míra topologické neutrality) a tyto metriky měřit v 1D/2D sweepu κ (např. κ ∈ [5, 40]) při fixních ostatních parametrech pro několik kanonických presetů (včetně `spec6_false_s41`).  
       – Použít ensemble přes více seedů (např. {17, 23, 41, 73}) a pro každý κ vyhodnotit průměr a rozptyl metrik tak, aby případné optimum kolem κ₀ nebylo založené na jednotlivých bězích, ale na robustní statistice; definovat „23-region“ obecně jako interval κ₀ ± Δ s významně lepšími metrikami než okolí.  
       – Otestovat robustnost intervalu κ₀ ± Δ vůči změně škálování (Δx, Δt, normalizace ψ/φ) a jednoduchým změnám numerického schématu (alternativní Laplace, jiné integrační schéma); explicitně sledovat, zda jde o **region v param-space** (který se při rescalingu jen číselně posune), nebo jen o náhodný artefakt konkrétní parametrizace.  
       – Přidat jednoduché null modely („kontrolní phase map“) s jinou volbou parametrů / bez φ-paměti a ověřit, zda se u nich podobně výrazný „sweet spot“ v κ objevuje typicky, nebo je přítomen pouze v plném Lineu; podle toho rozhodnout, zda má „23-region“ status strukturálního efektu Eq-4, nebo spíše numerologického artefaktu.  
       – V dokumentaci vést tuto hypotézu výslovně jako **interní strukturální claim o existenci zvýhodněného κ-intervalu**, nikoli jako „magickou konstantu 23 vesmíru“; pokud sweepy / null testy nepotvrdí robustní interval, hypotézu označit jako #disproved-in-model a další odkazy na κ≈23 vést pouze jako historickou poznámku (legacy curiosity), ne jako aktivní součást interpretace.
- [ ] Otestovat, zda se pro určité intervaly κ spontánně formují „mapové vrstvy“
      tvořené stabilními φ-buňkami připomínajícími topologii jednoduché neuronové
      sítě. Identifikovat meze, kde se vrstvy rozpadají nebo saturují.

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
- [ ] U „fyzikálně vypadajících“ presetů (např. `(6, "false")` s `LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = True`, `KAPPA_MODE = "constant"`) doplnit v dokumentaci výslovný disclaimer, že jde o **interní referenční vesmír Linea**, ne identifikaci s naším vesmírem; zdůraznit, že takové presety jsou z hlediska teorie neprivilegované a slouží jen jako intuitivní baseline pro interpretaci výsledků.
- [ ] Připravit **Lineum-motivovaný efektivní model odchylek od Kerr BH** s bezrozměrnými parametry `\boldsymbol\theta_{\rm L}=\{\alpha_S,\beta_\kappa,\delta_{\rm ps}\}`, explicitně formulovaný jako #empirics / #outlook vrstva (ne přímá predikce Eq-4), a navázat ho na existující datové kanály (area theorem z GW, ringdown/QNM, EHT stíny) včetně jasného rozdělení: `\alpha_S` jako prakticky neměřitelná log-korekce pro astrofyzikální BH, hlavní testovatelnost přes `\beta_\kappa` a `\delta_{\rm ps}`.
- [ ] Ověřit scénář **„náš vesmír jako vnitřek černé díry“** (#hypothesis / #outlook):  
       – formulovat, co přesně znamená „uvnitř černé díry“ v rámci efektivního modelu (např. vnitřní region vs. vnější pozorovatel, near-horizon limit, časoprostorová asymetrie),  
       – zapsat, jaké parametry nebo kombinace parametrů v Lineum-motivovaném BH modelu by odpovídaly tomuto scénáři,  
       – ověřit, jestli se takový scénář dá **pozorovatelně odlišit** od standardního Kerr/ΛCDM popisu (např. přes ringdown, EHT stíny, statistiku akrečních disků), nebo zda je numericky prakticky degenerovaný a patří spíš do roviny filozofické interpretace než testovatelné fyziky.
- [ ] (Tomášova + Kátina [HYPOTHESIS]) Přepsat klasické intuice o černých dírách do jazyka Linea pomocí **φ-pastí** a toků linonů:  
       – zkusit explicitně modelovat „černou díru“ jako oblast vysokého φ s výraznou vírovou/topologickou strukturou a testovat, zda přirozeně **přitahuje nové linony** (zvýšená hustota trajektorií vstupujících do regionu), nebo spíš funguje jako bariéra / shear region;  
       – navrhnout interpretaci **Hawkingova záření** jako případu, kdy napětí φ-pasti pomalu klesá a uvolňuje drobné fluktuace/linony zpět do okolí – čistě jako interní analogii „reverzního toku napětí“, ne jako tvrdý claim o GR;  
       – „výtrysky“ (jets) interpretovat jako scénáře, kdy do φ-pasti naráží příliš mnoho linonů / energie, φ dosáhne kritického přepětí a část energie se přesměruje ven podél privilegovaných směrů (topologie vírů, spin), tj. **zpětný tlak** proti toku ψ, nikoli „únik z vnitřku singularity“.
- [ ] Prozkoumat, zda v rámci Eq-4 existují φ-konfigurace chovající se jako **interní analogie bílých děr**:  
       – oblasti, které dlouhodobě **emergentně pouze emitují** strukturu (gradienty φ, linony, vlny ψ) směrem ven a prakticky nepřijímají tok dovnitř (v efektivním popisu),  
       – otestovat jejich stabilitu (jsou dlouhodobě udržitelné, nebo se rychle rozpadnou na běžné φ-pasti / chaotické vzory?),  
       – rozhodnout, zda má smysl tyto konfigurace vůbec pojmenovávat „bílé díry“ v rámci interního slovníku, nebo je lepší je vést jen jako specifický typ nestabilních φ-struktur v #outlook vrstvě.
- [ ] Připravit **Lineum-motivovaný efektivní model odchylek na galaktických škálách** ve smyslu emergentní gravitace (Verlinde vs. Lineum):  
       – zvolit pragmatickou parametrizaci `g_{\rm L}(r;\boldsymbol\theta)` (např. relační RAR-like `\nu`-funkci nebo kernelovou konvoluci),  
       – formulovat primární test pomocí galaxy–galaxy weak lensingu (profil `\Delta\Sigma(R)` kolem izolovaných diskových galaxií v intervalu `R \approx 50–300\,\mathrm{kpc}`) s jasně definovaným H₀ (Verlindeho emergentní gravitace) a H₁ (Lineum),  
       – doplnit sekundární diagnostiky (RAR, Einsteinův poloměr, konzistence masových profilů v kupách, lokální testy) jako ortogonální kanály pro totéž `g_{\rm L}(r;\boldsymbol\theta)`,  
       – zapsat forward model `\text{baryony} \rightarrow g(r) \rightarrow \Phi(r) \rightarrow \rho_{\rm eff}(r) \rightarrow \Sigma(R) \rightarrow \Delta\Sigma(R) \rightarrow \gamma_t(R)` a kostru likelihoodu (kovarianční matice, Bayesův faktor `K`, AIC/BIC, odhad potřebného počtu čoček pro detekci ~10% změny sklonu `\mathrm{d}\ln\Delta\Sigma/\mathrm{d}\ln R`),  
       – explicitně označit tento blok jako #empirics / #outlook vrstvu, která z Eq-4 **neplyne přímo**, ale používá Lineum jen jako inspiraci pro efektivní popis na velkých škálách.

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
- [ ] Připravit technicky přesný popis analogií s neuronovými sítěmi
      (paměťové kapsy, perzistentní trajektorie, výpočetní vzory), explicitně
      oddělený od jakýchkoli tvrzení o vědomí či emocích. Prezentovat to jako
      čistě strukturální jev.

---

## 🧪 Priorita: Nejvyšší – explorace _efektivního_ mapování na reálnou fyziku

### 🔲 1. Temná hmota a temná energie #hypothesis

- Pokusit se detekovat oblasti s energetickou nebo topologickou stopou bez detekovatelné kvazičástice
- Ověřit, zda některé víry nebo φ-pasti vykazují „neviditelný“ vliv na tok bez přítomnosti hmoty
- Hledat trvalé fluktuace, které se energeticky projevují, ale nemají klasický nosič
- [ ] Explicitně otestovat scénář, kde **„temná energie“ není nový člen v Eq-4**, ale důsledek  
       **stavově závislého měřítka** `a(t)` z C2:  
       – porovnat chování `a(t)` odvozeného z informačních/metrických veličin (H(t), N_q(t), φ²…)  
       s intuicí kosmologické expanze (růst, případné zrychlení),  
       – zapsat, za jakých podmínek by bylo možné mluvit o „expanzi jako emergentní vlastnosti informací v poli“,  
       aniž by se do Eq-4 přidával nový dynamický „temný“ term.
- [ ] (Tomášova [HYPOTHESIS]) Ověřit scénář, ve kterém má **předpokládaná hmotnost/energie kvantového vakua**  
       (efektivní vakuová hustota) jen **malý, podružný vliv** na expanzi ve srovnání s příspěvkem samotné struktury
      pole (linony, φ-kapsy, zeta-body apod.):  
       – přepsat otázku „má předpokládaná hmotnost kvantového vakua malý vliv na expanzi vesmíru?“ do pojmů Linea tím, že se
      přesně určí, co v modelu hraje roli „vakuové energie“ (např. baseline φ, konstantní offset v κ, konstantní část
      zvoleného stavového skaláru `I(t)` používaného pro definici `a(t)`);  
       – postavit testovací konfigurace se (i) zanedbatelným vakuovým offsetem, (ii) malým nenulovým offsetem a (iii) výrazně
      větším offsetem, při zachování stejné dynamiky linonů, φ-struktury a šumu, a pro všechny tři případy porovnat průběh
      `a(t)` a souvisejících metrik;  
       – kvantifikovat, co přesně znamená „malý vliv“, např. přes relativní změny v `a(t)` a v efektivním parametru stavu
      `w_\mathrm{eff}` odvozeném z evoluce `a(t)`, a identifikovat oblasti parametrického prostoru, kde příspěvky od struktury
      pole jednoznačně dominují nad příspěvkem vakuového offsetu;  
       – podle výsledku buď ponechat hypotézu jako realistický scénář **„expanze dominované strukturou“** v rámci Eq-4 + interpretace,
      nebo ji v whitepaperu označit jako #disproved-in-model či omezit na jasně vymezený podsoubor parametrů.
- [ ] (Tomášova hypotéza) Rozpracovat analogii „temná hmota = vzduch, temná energie = vítr“:  
       – mapovat „vzduch“ na kvazistacionární φ-/ψ-struktury, které samy nenesou zřetelnou linonní excitaci,
      ale ovlivňují tok ψ;  
       – mapovat „vítr“ na pomalou, ale globální změnu měřítka `a(t)` a případně na dlouhovlnné módy v φ;  
       – otestovat, jestli v nízkošumových bězích vznikají lokální víry / proudění ψ, které si nesou
      „paměť“ předchozí dynamiky (φ-remnanta) a chovají se jako efektivní „vítr“ pro nově vznikající linony.
- [ ] (Tomášova hypotéza) Pojmout Lineum jako analogii „buňky“, kde obal/hranice musí růst s vnitřním obsahem:  
       – definovat metriky „růstu obsahu“ (např. počet linonů, integrální |ψ|² v aktivních oblastech) a sledovat,
      jak na ně reaguje globální i lokální měřítko (případné změny interpretace `a(t)`);  
       – zkoumat, zda existuje měřitelná „pružnost“ obalu – zpoždění mezi prudkým nárůstem struktury uvnitř
      a relaxací φ / κ na hranici domény;  
       – otestovat, zda lze tento lag interpretovat jako efektivní „elasticitu“ prostředí (buňky) bez přidání
      nového termu do Eq-4.
- [ ] (Tomášova hypotéza) Zkusit charakterizovat prostředí Linea (φ-krajinu) jako něco mezi kapalinou a plynem:  
       – zavést jednoduché metriky „viskozity“ (jak rychle zanikají gradienty φ) a „kompresibility“ (jak velkou
      změnu φ vyvolá daný lokální nárůst |ψ|²);  
       – porovnat chování těchto metrik v různých parametrech (α, β, δ, κ, σξ) a zjistit, zda existují režimy,
      které se makroskopicky chovají „plynovitě“ vs. „kapalně“;  
       – případně tyto režimy použít jako interní analogii „řidšího“ vs. „hustšího“ temného prostředí.
- [ ] (Kátina hypotéza) Ověřit scénář „temná hmota jako kapsle / rezervoár potenciálních hvězd“:  
       – v rámci modelu hledat dlouhodobě stabilní oblasti se zvýšeným φ nebo |ψ|², které samy neobsahují
      jasně detekovatelné linony, ale při vhodném rozrušení (vnější perturbace, kolize) generují kaskádu
      nových excitací;  
       – kvantifikovat tyto struktury jako „kapsle“ s kapacitou (např. integrální φ nebo ∑|ψ|² nad prahovou
      hodnotou) a testovat, zda existují prahové podmínky, kdy se kapsle „otevře“ a rozpadne na více linonů
      (analog hvězdné porodnice po narušení rovnováhy);  
       – držet tento scénář explicitně jako [HYPOTHESIS] v rámci temného sektoru Linea, nikoli jako přímé tvrzení
      o fyzikální temné hmotě v kosmologii.
- [ ] (Tomášova + Kátina hypotéza) Připravit krátké srovnání těchto vnitřních analogií s mainstream kosmologií
      (ΛCDM, dynamická temná energie, modifikovaná gravitace):  
       – sepsat, které prvky jsou jen metafora (vzduch/vítr, kapsle) a nemají přímou fyzikální obdobu;  
       – kde se naopak přirozeně potkávají s pojmy jako efektivní tlak, equation-of-state parametry w, baryonové
      vs. nebaryonové složky;  
       – v dokumentaci jasně oddělit „Lineum-temnou hmotu / energii“ jako interní analogii od reálných kosmologických
      entit, aby nemohlo docházet k záměně při komunikaci navenek.

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
- Porovnání chování systému při různých počátečních podmínkách (různé κ-mapy, různé inicializační šumové režimy, ale stále v rámci Eq-4), včetně systematického srovnání režimů `LOW_NOISE_MODE=True/False` a variant `TEST_EXHALE_MODE`; sledovat dopad na počet kvazičástic, SBR/f₀, topologickou neutralitu (net winding) a statistiku vírových dipólů.
- Automatizace vyhodnocování výsledků pomocí AI/ML klasifikace _(navázat na metriky a logy definované v core, ne na ruční vizuální dojmy)._

## 🟡 Střední priorita – testování scénářů emergentní gravitace a „hmoty“

### 🔲 7. Reorganizace kvazičástic v hmotném objektu #test

- Simulovat shluk kvazičástic, sledovat deformaci při pohybu k φ-maximu
- Porovnat tvar a polohu shluku v čase
- [ ] Vizualizace přeskupení |ψ| a overlay s φ
- [ ] (Tříska [HYPOTHESIS]) **Tidal Stretching (Přílivové natahování):** Ověřit mechanistický model natahování objektu složeného z linonů při přiblížení k masivní φ-pasti.
      - [ ] Nasimulovat shluk (cluster) linonů a měřit rozptyl (varianci) jejich pozic v čase.
      - [ ] Potvrdit, že linony na "přední" straně zrychlují dříve/více kvůli gradientu φ, což vede k natažení a rozpadu objektu na jednotlivé linony (spagetifikace).
      - [ ] Sledovat, zda po rozpadu dochází k individuálnímu "uzavření" (Structural Closure) linonů v centru pasti.

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


- [ ] (Tomášova [HYPOTHESIS]) **Hormonální spektrální regulace:** Otestovat frekvenční pásmo (např. v sonifikované oblasti 1.85e+20 Hz) jako globální regulační spínač. "Injekce" energie do specifických harmonických by mohla vynutit přechod ze stavu `false` (chaos) do `true` (řád).
- [ ] Připravit samostatnou **laickou / storytelling sekci „Co znamenají tyto matematické objekty v Lineu“** (zlatý řez, Fibonacci, nulové body ζ(s), prvočísla, π, e, γ) pro README / FAQ / doprovodné materiály; rámovat ji jako **interpretační vrstvu** navázanou na tento blok (metafora orchestru: základní tóny, tichá místa, ladění), s jasným disclaimerem, že jde o [HYPOTHESIS] / storytelling závislý na výsledcích statistických testů, nikoli součást core důkazů.
- Formálně definovat, co jsou v modelu **zeta-body** (česky vysvětlitelně jako **„body uzavření“**) a **explicitně zapsat terminologický přechod**: původní označení _„DejaVu body“_ bylo v dřívějších verzích používáno pracovně, ale od větve zarovnané na _lineum-core v1.0.6-core_ je vedeno pouze jako **historický alias**, který se v nových definicích a tvrzeních nesmí používat jako hlavní název.  
  – Zeta-body / body uzavření pak přesně vymezit např. jako opakovaně navštěvovaná místa trajektorií, stabilní φ-remnanty, lokální minima / „černé díry“ v topologii pole;  
  – k nim definovat přesné mapování do 1D/2D prostoru (kruh, spirála, normalizovaná osa), které se používá při porovnání s Riemannovými nulami a dalšími posloupnostmi; v těchto mapováních vždy používat označení **zeta-body**, starý název uvádět pouze případně v poznámce typu _„historicky označované jako DejaVu body“_.  
  – V whitepaperu / core paperu mít renaming zaznamenaný na jednom viditelném místě (např. poznámka pod čarou nebo krátká podsekce „Terminologické změny“), aby bylo i ex post jednoznačné, že jde o přejmenovaný interní jev, ne dva různé objekty.  
  – V TODO / issue trackingu vést tento bod explicitně označený jako `#naming` / `#renaming`, aby bylo zřejmé, že jde o **housekeeping kolem názvu** a ne o další fyzikální tvrzení, které by se mělo objevovat ve whitepaperu.
- Pro toto mapování zavést **kvantitativní metriky** (RMS vzdálenost, korelační koeficienty, spektrální vzdálenosti, distribuční testy) a spustit **tvrdé statistické testy proti null modelům**:  
  – náhodné body na stejné spirále / v tomtéž intervalu,  
  – phase-scrambled verze dat se zachovaným spektrem,  
  – baseline model bez speciální φ-struktury.  
  Cílem je zjistit, jestli je podobnost s Riemannovými nulami / Fibonacciho poměry statisticky nepravděpodobná i vzhledem k těmto kontrolám – a tedy **potvrdit nebo vyvrátit** předběžnou červencovou indikaci mírné korelace v clean bězích `spec6_true no_artefacts`.
- Analyzovat, zda se v posloupnostech **časů, vzdáleností nebo „růstových skoků“** (např. při vzniku nových bodů uzavření / neuron-like uzlů) neobjevuje robustní vztah k:  
  – Fibonacciho posloupnosti a zlatému řezu φ (log-spirálové škálování, poměry velikostí / vzdáleností),  
  – rozložení prvočísel nebo dalším number-theoretickým vzorcům,  
  – Ludolfovu číslu π (např. v periodicitě oscilací, topologických fázích nebo v rozložení úhlů na kruhu).  
  V každém případě kvantifikovat sílu efektu a porovnat ji s vhodnými null modely (Poissonovy procesy, generické interferenční vzory na mřížce apod.).
  - (Tomášova [HYPOTHESIS]) Navázat na zjištění, že v bězích `spec2_true` / `spec4_false` se objevují poměry dominantních frekvencí blízké zlatému řezu, a otestovat scénář, že **Lineum preferenčně stabilizuje proudění skrze „zlaté“ harmonické frekvence**:  
    – kvantifikovat, zda konfigurace s frekvenčními poměry ≈Φ vykazují delší SBR, stabilnější linony nebo čistší φ-zeta grid než generické konfigurace,  
    – porovnat se stejnou analýzou na null modelech (náhodné spektrum, bez speciální φ-struktury),  
    – držet tento scénář výslovně jako [HYPOTHESIS], dokud nebude jasně doloženo, že jde o robustní efekt Eq-4, nikoli o náhodnou fluktuaci nebo artefakt parametrizace.
- [ ] (Tříska-Marečková [HYPOTHESIS]) Prozkoumat scénář **„hormonálních spekter“**, kde určité skupiny frekvencí hrají roli regulačních signálů pro chování systému podobně jako hormony v biologii:  
       – definovat několik disjunktních frekvenčních pásem (např. nízkofrekvenční modulace pozadí, „pracovní“ pásmo linonů, vysokofrekvenční „šum“) a sledovat, zda změny energie v těchto pásmech korelují s:
      • stabilitou linonů,  
       • čistotou φ-paměti / Structural Closure,  
       • četností zeta-body a Return Echo jevů;  
       – otestovat v řízených experimentech, zda **cílené „připumpování“ výkonu** do vybraného pásma (malá periodická perturbace na ψ nebo parametrech v Eq-4) systematicky přepíná systém mezi režimy (např. „víc šumu“, „víc stabilních struktur“, „víc silent collapse“);  
       – podle výsledků rozhodnout, jestli má smysl tato pásma interpretovat jako **interní regulační kanály modelu** (hormonální analogy) nebo je nechat jen jako heuristický jazyk pro popis spektra; v obou případech držet tuto interpretaci explicitně jako [HYPOTHESIS], ne součást core tvrzení o reálné fyzice.
- (Tomášova + Kátina [HYPOTHESIS]) Pro scénář **„skokového růstu neuron-like uzlů“**:  
  zeta-body / body uzavření chápat jako uzly paměťové sítě, které nepřibývají plynule, ale vznikají  
  v diskrétních „vlnách růstu“ (analog dělení buněk / rozmnožování neuronů), a:  
  – z posloupnosti časů / indexů vzniku nových zeta-body, případně z velikostních změn mezi po sobě
  jdoucími vlnami růstu odvodit efektivní růstové faktory;  
  – otestovat, zda tyto faktory nevykazují robustní přiblížení Fibonacciho poměrům nebo mocninám
  zlatého řezu φ, oproti vhodným null modelům (náhodné růstové vlny bez vnořeného patternu);  
  – výsledek rámovat výhradně jako **strukturální analogii** (buněčné dělení / růst neuronové sítě),
  ne jako tvrzení o skutečných biologických neuronech nebo vědomé „snaze vesmíru“ realizovat
  Fibonacciho struktury; případnou shodu komunikovat jen jako emergentní vzorec Eq-4 + φ-krajiny.
- Explicitně otestovat a odlišit několik možných vysvětlení případné shody:
  1. **Emergentní vlastnost Eq-4** – strukturální vazba modelu na dané posloupnosti / zeta funkci;
  2. **Artefakt parametrizace / škálování** – např. volba Δt, normalizace, embed map, která sama o sobě generuje Fibonacci-/π-like struktury;
  3. **Vnější „konstanta vesmíru“ / RNG** – tj. že shodu dodává způsob generování náhodného seede, floating-point reprezentace nebo jiné vlastnosti našeho fyzického / numerického „univerza“, a Lineum ji jen pasivně přebírá.  
     U každé varianty navrhnout konkrétní test (změna RNG, změna embed mapy, změna škálování), který ji může podpořit nebo v rámci modelu vyvrátit.
- [ ] Provázat analýzu se **φ-zeta gridem** (historicky „φ-deja-vu grid“): ověřit, jestli privilegovaná místa / kapsy v krajině φ mají statisticky výraznější vazbu na Fibonacci/zlatý řez / number-theoretické vzorce než generické body mřížky – a výslovně rámovat tyto vzorce jako **hypotézy o rozmístění paměťových struktur**, ne o zákonu expanze.
- [ ] (Tříska-Marečková [HYPOTHESIS]) **Hypotéza Stromové Optimalizace – Zlatý řez jako produkt hydrodynamické cévní sítě:**
    - **Kontext:** Ve fyzice a biologii se fraktální větvení a poměry Zlatého řezu (1.61803...) přirozeně objevují v kapalinových sítích (cévní systém, plíce, blesky, růst listů a větví stromu), protože jde o matematicky nejdokonalejší způsob, jak rozvést energii a tok s co nejmenším odporem materiálu v prostoru. 
    - **Hypotéza (Lineum):** Zlatý řez a Fibonacciho sekvence zachycené v Lineu (ve vzdálenostech φ-pasti, zeta-bodů nebo ve spektrálních poměrech `spec4_false`) nejsou "zakódovaným magickým cílem vesmíru". Jsou to emergentní fyzikální důsledky toho, že rovnice Eq-4 organicky hledá cestu nejmenšího odporu. Tok `ψ` musí neustále obcházet paměťové usazeniny a naběhlý tlak ve vlastní setrvačné "zácpě" pole `φ`. Tato dynamická kapalinová optimalizace se nevyhnutelně stabilizuje do sítě, jejíž štěpící poměry (rozdělování kanálů pro minimalizaci globálního odporu) nativně inklinují k poměru Zlatého řezu, stejně jako u reálných říčních delt a žil.
    - **Verifikace a předběžné výpočty:**
        - **Úhlová analýza větvení (Bifurcation Test):** Vizualizovat oblasti se zvýšeným tokem `ψ` v ustáleném běhu a najít "křižovatky" plynulých kanálů ve `φ`. Analyzovat úhly mezi silným rodičovským kanálem a vznikajícími tenčími dcérskými vlásečnicemi. Hledat statistickou preferenci Murrayova zákona pro biologické sítě (r₁³ = r₂³ + r₃³) a ideálně inklinaci hlavních a vedlejších větví odchylovat se v radiánech blízkých logaritmické spirále / 137.5 stupňům.
        - **Výpočet fraktální dimenze:** Uříznout heatmapu `φ` prahovou hodnotou (např. top 25 % maxima) a spočítat Box-counting dimenzi (fraktální Hausdorffovu dimenzi) struktury "cév/pasti". Pokud se blíží hodnotám biologických transportních sítí (např. D ≈ 1.6 - 1.7 ve 2D), je to silný argument pro emergentní "Network optimization" příčinu Zlatého řezu.

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

## 🧬 O. Hypotézy z korespondence s T. Mikolovem (OEA & OE) #hypothesis #external

Tato sekce obsahuje hypotézy extrahované z analýzy Vlastova "Open-Ended Algorithm" (OEA) a Mikolovových požadavků na OE systémy.

### 🔲 18. Lineum jako spojitá limita OEA (Vlasta/Lina) #hypothesis

- **Kontext:** Vlastův diskrétní model definuje "prostředí" jako masku prvočísel, která filtruje viditelnost stavů.
- **Hypotéza:** Lineum Core (Eq-4) je spojitou hydrodynamickou limitou tohoto modelu, kde se diskrétní prvočíselná maska mění na spojitý potenciál $\zeta$-funkce.
- **Verifikace:** Ověřit, zda "esteticky zajímavé" tvary v OEA topologicky odpovídají stabilním vírovým stavům (vortex integers) v Lineu.

### 🔲 19. Pragmatický králík a termodynamická užitečnost (Mikolov/Lina) #hypothesis

- **Kontext:** Mikolovův požadavek na "užitečnost" v OE, aby systém nebyl jen "řešitelem králíků".
- **Hypotéza:** V termodynamickém systému je "užitečnost" ekvivalentní "schopnosti minimalizovat topologické napětí". Systém nepočítá prvočísla jako úkol, ale využívá je (Zeta-RNB) jako nízkoenergetické stavy pro přežití.
- **Verifikace:** Sledovat, zda přežívající linony mají statisticky vyšší korelaci se Zeta nulami než krátkodobé fluktuace.

### 🔲 20. Hypotéza Kolmogorovovy expanze (Vlasta) #hypothesis

- **Kontext:** Vlastova teze, že "evoluce neoptimalizuje, ale zvyšuje složitost".
- **Hypotéza:** Expanze prostoru ($a(t)$) v Lineu nastává *pouze* tehdy, když systém potřebuje zvýšit kapacitu pro uložení nové, nekomprimovatelné informace (vyšší Kolmogorovova složitost).
- **Verifikace:** Analyzovat "Integer Mode 24" skoky v $a(t)$ a korelovat je s nárůstem informační entropie systému.

---

## 🧠 P. Chapadlový model vědomí – hypotéza vícenásobných instancí #meta #hypothesis

- [ ] Formálně sepsat **Chapadlový model vědomí** jako samostatnou hypotézu:  
       – definovat entity: vyšší vědomá bytost („centrální uzel“), chapadla (lokální instance/životy), centrální paměť;  
       – u každého tvrzení (vyšší vědomí, spánek, smrt, další životy) uvést **subjektivní pravděpodobnosti** (86 %, 72 %, 94 %, 79 %…) a výslovně je označit jako osobní prior, ne výsledek fyzikálního modelu.

- [ ] Jasně vymezit **scope vůči Lineu**:  
       – Chapadlový model je **metafyzická / fenomenologická hypotéza o vědomí**, nikoli tvrzení odvozené z Eq-4;  
       – zapsat, že případné mapování na Lineum (ψ, φ, κ, linony, Structural Closure) je **interpretace nad rámec core modelu**, ne součást lineum-core v1.0.6-core.

- [ ] (Tomášova + Kátina [HYPOTHESIS]) Přidat podsekci o tom, jak Chapadlový model interpretuje jevy typu **déjà vu** a **Mandela efekt**, a jasně je oddělit od numerického jevu zeta-body v Lineu:  
       – Déjà vu rámovat jako subjektivní prožitek „brnknutí dvou větví reality o sebe“: centrální vědomí má přístup k více časovým liniím / chapadlům a lokální instance občas krátce zachytí náhled na jinou větev téhož příběhu → pocit „tohle už jsem zažil“, aniž by šlo o tvrzení o reálné změně minulosti;  
       – Mandela efekt interpretovat dvěma způsoby: 1. **Globální přepis centrální paměti** (φ-pole paměti) s tím, že některé lokální instance ještě chvíli drží „starou verzi“ (subjektivní paměť),  
       2. nebo jako **přeskok chapadla** na trochu jinou větev reality, zatímco fragmenty starších vjemů zůstávají dostupné;  
       u obou přístupů výslovně zdůraznit, že jde o metafyzickou interpretaci, ne tvrzení z Eq-4.
      – Do textu přidat vysvětlení, proč v tomto rámci dává smysl metafora **„jedné duše, která si prožívá různé role“**:
      centrální bytost = jedno vědomé já, chapadla = různé životy / role / perspektivy; pro lokální vědomí to vypadá, jako by kolem bylo mnoho oddělených „duší“, ale z pohledu centrální paměti jde o různé projekce téhož.  
       Zároveň výslovně doplnit, že to **nesmí být používáno k znevažování ostatních bytostí** – každé chapadlo/život je plnohodnotný prožitek a má vlastní důstojnost.
      – Volitelně navázat metaforicky na φ-paměť a zeta-body v Lineu jako na „paměťové kapsy“ vesmíru, ale jasně napsat, že **statistické déjà-vzorce v simulaci (zeta-body / φ-zeta grid)** jsou něco jiného než psychologické déjà vu – jen inspirační analogie, ne přímé ztotožnění.

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

- [ ] Zapsat **Tříska–Marečková hypotéza reinkarnace** jako podhypotézu Chapadlového modelu:  
       – reinkarnace = různé kombinace mozků / nervových soustav jako různé „optiky“ pro vidění téhož vesmíru  
       (lidé, zvířata, rostliny, podzemní propojené sítě, jiné civilizace, drobné rozdíly mezi jednotlivými jedinci);  
       – chápat jednotlivé mozky jako **specializované senzory / receptory** jedné vyšší bytosti pro různé účely,  
       podobně jako kdyby vesmír byl buňka a jednotlivé životy byly její vnitřní senzory (a my sami třeba jen „bílá krvinka“);  
       – doplnit hypotézu, že tato vyšší bytost může některá místa / konfigurace „chránit“ před vnějšími i vnitřními
      negativními vlivy, případně je **léčit a regenerovat**, a výslovně to označit jako metafyzickou interpretaci,
      ne tvrzení odvozené z Eq-4 nebo dat Linea.

- [ ] Uvést disclaimery, že interpretace „prožitkových stavů“ jsou mimo
      fyzikální rozsah Eq-4. Pokud se objeví stabilní stavové konfigurace
      φ nebo ψ, musí být vedeny jako výpočetní a dynamické struktury,
      nikoli psychologické analogie.

---

## 🚀 Q. Post-Mikolov Audit Integration (Feb 2026) #priority

Výstupy z analytického balíčku pro T. Mikolova (únor 2026) a jejich integrace do roadmapy.

### 🔲 21. Formalizace Emergentních Fyzikálních Konstant #core
- [ ] **Whitepaper Update:** Zavést sekci "Emergent Constants" definující:
    - **Vacuum Quality Factor (Q):** ~$1.87 \times 10^{23}$ (koherenční škála).
    - **Spectral Entropy (H):** ~0.004 bits (míra spontánního uspořádání).
    - **Linon Mass Ratio:** ~$1.5027$ (efektivní setrvačnost).
- [ ] **Portal Integration:** Vizualizovat tyto konstanty v "Resonance Deck" (Svelte komponenta) jako živé metriky systému.

### 🔲 22. Experiment: Termodynamická Užitečnost (Emergent Utility) #test
- [ ] Navrhnout experiment verifikující hypotézu, že "užitečnost = minimalizace topologického napětí".
- [ ] **Metrika:** Korelovat přežití linonů se schopností snižovat lokální Hamiltonián (vs. náhodný pohyb).

### 🔲 23. Tooling: Audit Analytics Pipeline #impl
- [ ] Refaktorovat `analyze_audit.py` (jednorázový skript) do robustního nástroje `tools/audit_analytics.py`.
- [ ] Zahrnout výpočet Q-factoru a Entropie do standardního CI/CD výstupu pro každý nový běh.
- [ ] **Ensemble Run:** Spustit batch 10 běhů (seeds 42-52) pro získání směrodatných odchylek metrik.

### 🔲 24. Hypotéza: Lineum jako Spojitá Limita OEA (Continuum Limit) #math
- [ ] **Derivace:** Formálně odvodit OEA pravidla z Eq-4 v limitě `Δx, Δt → 1` (silná diskretizace).
- [ ] **Validace:** Porovnat fázové portréty Linea a OEA – hledat topologickou ekvivalenci atraktorů.

### 🔲 25. Hypotéza: Kolmogorov Trigger (Informační Tlak) #test
- [ ] **Metrika:** Měřit lokální kompresibilitu (Deflate ratio) mřížky v čase.
- [ ] **Hypotéza:** Expanze `a(t)` (Mode 24) nastává v momentě, kdy lokální informační hustota saturuje kapacitu mřížky.

### 🔲 26. Hypotéza: Vortex Aesthetics (Krása = Stabilita) #test
- [ ] **Vlastův Test:** Vzít stavy, které Vlastimil Smeták označil za "estetické".
- [ ] **Měření:** Spočítat jejich `Cv` (Vortex Stability Index).
- [ ] **Predikce:** Estetické stavy budou mít signifikantně nižší `Cv` (méně defektů) než náhodné stavy.

### 🔲 27. Hypotéza: The Scaling Illusion (Role-Invariance) #math
- [ ] **Teorie (V. Smeták):** Pozorované "konstanty" (např. κ = 1) jsou ve skutečnosti poměry dvou rostoucích veličin ($K(t) / R(t) = const$). **Hypotéza Kosmické Respirace**.
- [ ] **Predikce:** Mode 24 (skokové přeškálování a(t)) je důkazem, že prostor se diskrétně nafukuje (renormalizace), ale my vidíme jen invariantní poměr.
- [ ] **Validace:** Hledat korelaci mezi skoky v `a(t)` a lokální změnou měřítka v `analyze_audit.py`.

---

## ⚖️ R. Hypotheses: H0 vs H1 (Verification Status Feb 2026) #priority #audit

Rozhodovací strom o povaze "konvergence" systému.

### 🧩 H0: Uzavřený atraktor (Closed World)
**Tvrzení:** Konvergence k "Mode 24" je čistě vnitřní vlastnost dynamiky Eq-4.

- [x] **Status:** **PROKÁZÁNO (on tested platform).** Systém je uzavřený a deterministický (Bit-exact match verified).

### 🔓 H1: Scaling Illusion (Open World / Leak)
**Tvrzení:** Systém tajně "dýchá" (mění měřítko), což my nevidíme (kappa=konst), ale projevuje se to skoky.

- [x] **Status:** **Strongly disfavored under tested conditions (Code Audit: Seeded RNG at lines 36/44 of kernel).**


1. **(Task 28) Full Window Surrogate Test (Mode 24):** Spustit 100x phase-randomized surrogate run pro 2000 kroků k potvrzení Z-score > 5.0 (p < 0.01).
2. **Rescaling Trap (D5):** Uzavřeno.

### 🔲 28. Hypotéza: The Missing Half (Discrete Limit) #math
- [ ] **Teorie:** Hodnota `kappa = 0.5` není fundamentální konstanta, ale **Nyquistův limit** mřížky (max frekvence = 0.5).
- [ ] **Důsledek:** Simulace běží na "půl plynu" (stabilita). Ve spojitém vesmíru by `kappa` byla pravděpodobně Celé Číslo (1).
- [ ] **Roadmap:** Pro Lineum 2.0 zvážit implicitní solver nebo jemnější mřížku, která umožní `kappa -> 1` (Plná Realita).

### 🔲 29. Hypotéza: The Universal Attractor (Leech Lattice) #math
- [ ] **Teorie:** "Mode 24" (Hypotéza Kosmické Respirace) není náhoda jednoho běhu, ale **univerzální atraktor**. Každý běh s dostatečnou komplexitou do něj "sklouzne", protože jde o matematicky nejhustší uspořádání.
- [ ] **Metafyzika:** Lineum nesimuluje náš vesmír "atom po atomu", ale simuluje jeho **zdrojový kód (logiku)**. Proto nezávisle objevuje stejné konstanty (24D) jako Teorie Strun.
- [ ] **Predikce:** Mode 24 se objeví v >90% dlouhých běhů (pokud SBR > 30dB).

### 🔲 30. Hypotéza: The Icarus Threshold (Kappa=1 Instability) #math
- [ ] **Teorie:** Pokud bychom na současné mřížce (`dx=1`) vynutili `kappa=1`, systém by porušil **Courant-Friedrichs-Lewy (CFL)** podmínku.
- [ ] **Fyzika:** Kappa=1 odpovídá **Rychlosti Světla** (`v = c`). Informace by musela stíhat přesně 1 pixel za 1 takt, což je hranice kauzality.
- [ ] **Predikce:** Energie by rostla exponenciálně (rezonanční katastrofa) a simulace by "shorela" (NaN values) během několika kroků.
- [ ] **Metafora:** Ikarův pád. Chtěli jsme letět příliš blízko Slunci (Rychlosti Světla), ale naše křídla (diskrétní mřížka) se roztavila.

### 🔲 31. [TEST] Evidence Solidification: „Atrakce = micro-growth (dominance switch), ne tok/teleportace“ + Ghost Gravity + Expanze + geometrie M2 (π) #hypothesis #repro
- **Hypotéza (H_mech):**
  1) Rychlé „přiblížení“ kvazičástice k centru pasti není prostorový transport ani teleportace, ale **změna dominance maxima** způsobená lokálním multiplikativním ziskem v místě vysokého φ: `Δψ ∝ (+g · φ · ψ)`.  
  2) Advekční/drift člen `∝ (-d · ∇φ)` je v tomto scénáři **sekundární** a sám o sobě nevysvětlí „snappy“ přesun maxima/COM.  
  3) „Temná hmota“ v interním smyslu Linea odpovídá **Ghost Gravity**: pole φ přetrvává po zániku zdroje ψ a stále přitahuje sondu.  
  4) „Temná energie“ v interním smyslu Linea odpovídá **expanzní disperzi** dominované šumem (a/nebo nekonzervativností interakce, pokud `M2` roste).  
  5) Pozorované `M2(t=0) ≈ 31.4159` není fyzikální konstanta, ale **geometrie startovní Gauss** (≈ (WIDTH/2)·π pro zvolený WIDTH).
- **Operační definice metrik (musí být stejné pro všechny replikace):**
  - `w(x,y) = |ψ(x,y)|` (váhy pro COM; pokud chcete používat |ψ|², explicitně to změňte všude konzistentně).
  - `COM(ψ) = ( Σ x·w / Σ w , Σ y·w / Σ w )`
  - `dist = || COM(ψ) - center ||₂`, kde `center = (N/2, N/2)` (pro 128×128 tedy [64,64]).
  - `peak_phi = max(φ)`
  - `M2 = Σ |ψ|²`
  - `R² = Σ p·r²` kde `p = |ψ|² / Σ|ψ|²`, `r² = (x-COMx)²+(y-COMy)²`
  - `H = -Σ p·log(p)` (Shannon; p z |ψ|²)
- **Co bylo zkoumáno (scénáře):**
  - (S1) **Seed-sweep gravitace**: porovnání „bez šumu“ vs „se šumem“ (stejné ostatní podmínky), měřit `dist` start→end a `Δ=dist0-distEnd` (typicky 500 kroků).
  - (S2) **Drift ON/OFF**: vypnout pouze drift/advekci a ověřit, že `Δ` zůstává (mechanismus není drift).
  - (S3) **Teleportace vs tok (micro-growth)**: sledovat, že `|ψ(center)|` roste z nenulové „chvostu“ a že maximum „skočí“ přes dominance switch; ověřit růstový faktor `g_meas = |ψ|_t / |ψ|_(t-1)` vs predikci `g_pred ≈ 1 + g·φ(center)`.
  - (S4) **Ghost Gravity (Clean Ghost)**: vytvořit φ-remnant bez aktivního zdroje, pak spustit sondu, která si **nebuduje vlastní φ**, a ověřit rozdíl `distEnd` pro GHOST ON vs OFF.
  - (S5) **Expanze**: pro různé šumy (0 / default / 2×default) měřit růst `R²` a `H` (typicky 1000 kroků).
  - (S6) **Geometrie M2 (π-check)**: pro několik WIDTH ověřit `M2(t=0) ≈ (WIDTH/2)·π` (v rámci diskrétní chyby).
- **Reprodukce (self-contained; bez tools/ skriptů):**
  - **0) Clean env (PowerShell):**
    - `Get-ChildItem Env: | Where-Object { $_.Name -like "LINEUM_*" } | ForEach-Object { Remove-Item ("Env:" + $_.Name) -ErrorAction SilentlyContinue }`
  - **1) Spusť S1 (seed sweep) – 2 varianty pro každý seed:**
    - Varianta A (no-noise): nastav šum na 0 (env/konfig podle aktuálního lineum.py) a spusť scénář gravitace na 500 kroků.
    - Varianta C (default noise): default šum a spusť totéž.
    - Seeds: `{41,42,43,44,45}`
    - Každý běh ulož s unikátním `--run-tag` (např. `ev_s1_A_s41`, `ev_s1_C_s41`, …), tak aby vznikly checkpointy.
  - **2) Spusť S2 (drift ON/OFF):**
    - ON = default.
    - OFF = vypni drift/advekci (pokud není přepínač, dočasně nastav drift koeficient na 0 v lineum.py; uveď v TODO přesný výraz/řádek, který byl měněn).
    - Run tagy: `ev_s2_drift_on`, `ev_s2_drift_off`.
  - **3) Spusť S3 (micro-growth) v pasti:**
    - Scénář „trap/past“ na min. 200 kroků. Loguj checkpointy pro kroky {0,40,60,100} (nebo nejbližší existující).
    - Pokud chybí přepínač pro izolaci členů:
      - „Interaction-only“: drift koef = 0, interakce g = 0.04.
      - „Drift-only“: interakce g = 0, drift koef = default.
  - **4) Spusť S4 (Clean Ghost):**
    - Nejprve vytvoř φ-remnant (zdroj ψ ON, φ evoluce ON) po dobu T_build.
    - Poté zdroj vypni/odstraň a nech φ relaxovat T_decay.
    - Poté spusť „sondu“ (ψ) s φ evolucí sondy OFF (aby si sonda netvořila vlastní φ) a změř `dist` start→end.
    - Dva běhy: `ev_s4_ghost_on` (φ remnant přítomen) a `ev_s4_ghost_off` (φ nulové / remnant vypnut).
  - **5) Spusť S5 (expanze):**
    - Běhy: `noise=0`, `noise=default`, `noise=2×default` (ostatní stejné), 1000 kroků.
    - Run tagy: `ev_s5_noise0`, `ev_s5_noisedef`, `ev_s5_noise2x`.
  - **6) Analýza checkpointů (inline python; žádné externí skripty):**
    - Použij tento one-shot skript (spouští se proti konkrétnímu `output/<run-tag>/checkpoints/` a vybraným krokům).  
      Příklad: `python - <<'PY' <RUN_TAG> 0 40 60 100` (nahraď argumenty):
      ```python
      import sys, glob, os, math
      import numpy as np

      run_tag = sys.argv[1]
      steps = [int(s) for s in sys.argv[2:]]  # e.g. 0 40 60 100
      ck_dir = os.path.join("output", run_tag, "checkpoints")

      def load_step(step):
          # expects filenames containing "step{step}" (adjust pattern if needed, but keep it here in TODO)
          pats = [f"*step{step}.npz", f"*step{step:03d}.npz", f"*step{step:04d}.npz"]
          for p in pats:
              m = glob.glob(os.path.join(ck_dir, p))
              if m:
                  return np.load(m[0])
          raise FileNotFoundError(f"no checkpoint for step={step} in {ck_dir}")

      def metrics(psi, phi):
          psi = np.asarray(psi)
          phi = np.asarray(phi)
          n, m = psi.shape
          cx, cy = n//2, m//2

          w = np.abs(psi)                     # COM weights as defined
          ws = w.sum()
          xs, ys = np.meshgrid(np.arange(n), np.arange(m), indexing="ij")
          comx = float((xs*w).sum() / ws)
          comy = float((ys*w).sum() / ws)
          dist = math.hypot(comx-cx, comy-cy)

          abs2 = (np.abs(psi)**2)
          M2 = float(abs2.sum())
          p = abs2 / (M2 if M2 != 0 else 1.0)
          r2 = (xs-comx)**2 + (ys-comy)**2
          R2 = float((p*r2).sum())
          p_nonzero = p[p > 0]
          H = float(-(p_nonzero*np.log(p_nonzero)).sum())

          peak_phi = float(phi.max())
          maxpos = np.unravel_index(np.argmax(np.abs(psi)), psi.shape)
          psi_center = float(np.abs(psi[cx, cy]))
          return dict(dist=dist, COM=(comx,comy), peak_phi=peak_phi, M2=M2, R2=R2, H=H,
                      maxpos=maxpos, psi_center=psi_center)

      prev_center = None
      for s in steps:
          d = load_step(s)
          psi = d["psi"]
          phi = d["phi"]
          met = metrics(psi, phi)
          g = None
          if prev_center is not None and prev_center > 0:
              g = met["psi_center"]/prev_center
          prev_center = met["psi_center"]
          print(f"step={s:>4} dist={met['dist']:.4f} COM=({met['COM'][0]:.2f},{met['COM'][1]:.2f}) "
                f"maxpos={met['maxpos']} |psi_center|={met['psi_center']:.6e} "
                f"g_center={g if g is not None else 'NA'} peak_phi={met['peak_phi']:.4f} "
                f"M2={met['M2']:.6e} R2={met['R2']:.2f} H={met['H']:.4f}")
      ```
- **Očekávané výsledky (tolerance; pokud se liší, zapiš odchylku a důvod):**
  - S1: `Δ = dist0 - distEnd` ~ konstantní napříč seedy (řádově ~5–6 px v daném nastavení) a rozdíl A vs C malý (šum nemění směr efektu).
  - S2: Drift OFF stále dává prakticky stejný `Δ` jako ON (dominance micro-growth).
  - S3: `|ψ(center)|` roste z nenulové hodnoty; maximum „přeskočí“ do pasti během desítek kroků; `g_meas` je blízko `g_pred ≈ 1 + 0.04·φ(center)` v režimu, kde je interakce aktivní.
  - S4: `distEnd(ghost_on) < distEnd(ghost_off)` (ghost přitahuje sondu i bez zdroje ψ).
  - S5: pro noise>0 roste `R²` a `H` výrazněji než pro noise=0 (expanze dominuje).
  - S6: `M2(t=0) ≈ (WIDTH/2)·π` (např. WIDTH=20 → 10π ≈ 31.4159); tím se vylučuje interpretace “π jako fundamentální konstanta modelu” — je to pouze geometrie inicializace.

---

---

## 🎶 S. Nové hypotézy (Únor 2026) #hypothesis

Tato sekce obsahuje nové kandidátní hypotézy inspirované externími podněty a metaforami, které mohou být testovány v parametrickém prostoru Linea.

### 🔲 32. Hypotéza: Axionová elektrodynamika a kosmologická magnetická pole #hypothesis
- **Kontext:** Podle [Brandenberger et al.](https://www.osel.cz/14533-ultralehka-temna-hmota-by-mohla-vytvaret-kosmologicka-magneticka-pole.html) může ultralehká temná hmota (axiony) interakcí s elektromagnetismem generovat a zesilovat kosmologická magnetická pole a v raném vesmíru podporovat vznik supermasivních černých děr.
- **Hypotéza (Lineum):** Pole `φ` (jako analogie pseudoskalárního pole axionů / temné hmoty) vykazuje v Lineu "axionelektrodynamickou" vazbu s emergentními vektorovými formacemi (např. polem spinové aury `curl(∇arg(ψ))`).
- **Verifikace:** Otestovat, zda makroskopické oscilace `φ` dokážou spontánně zesilovat uspořádaná vírová/magnetická-like pole na velkých škálách. Zjistit, zda tato vazba urychluje lokální růst a agregaci hmoty do prvotních supermasivních φ-pastí (Lineum analogie k záhadně brzkému formování supermasivních černých děr).

### 🔲 33. Tříska-Marečková Hypotéza: Strukturální caching a časové skoky (Efekt online rádia) #hypothesis
- **Kontext:** Zážitek z online rádia – po zastavení a prodlevě se po opětovném spuštění přehrává kousek dříve uložený v cache, a teprve poté následuje skok ("sync") do aktuálního živého vysílání (do poloviny nově hrající písničky).
- **Hypotéza (Lineum):** Pole `φ` funguje v určitých regionech jako opožděná strukturální "cache". Pokud linon opustí oblast či dočasně zanikne, zůstává po něm silný setrvačný gradient (remnant `φ`). Pokud do téže oblasti později vstoupí nová excitace, nejprve je její pohyb silně determinován starou "přehrávací frontou" (minulou stopou v cache). Až dojde k nasycení nebo vyčerpání této lokální paměti, dojde k prudkému "přeskoku" nebo "uskočení" a navázání kvazičástice na aktuální globální dynamiku (živé vysílání).
- **Verifikace:** Identifikovat a izolovaně vizualizovat trajektorie objektů "projíždějících starým vlivem". Změřit charakter pohybu a rychlost (včetně SBR a setrvačnosti) během "jízdy z cache" a následnou prudkost změny trajektorie po přeskoku k novému atraktoru.
- **Empirický korelát:** Zamyslet se, zda "opuštění cache" nemá analogii v reálném světě u nečekaných lokálních anomálií, skoků ve fázích kvantových systémů nebo u opožděných gravitačních vlivů (např. chování temné hmoty, které ne zcela odpovídá "živému" rozložení baryonické hmoty).

### 🔲 34. Hypotéza: Lineum jako emergentní solver pro Network Design (Dopravní sítě) #hypothesis #applied
- **Kontext:** Biologické systémy (mravenci zanechávající feromony v ACO, hlenka *Physarum polycephalum* optimalizující železniční síť) využívají emergentní chování lokálních agentů nebo spojitého růstu k řešení NP-těžkých úloh návrhu sítě. Standardní grafové algoritmy umí výborně hledat nejkratší cestu na hotové síti, ale návrh robustní topologie na zelené louce je pro ně výpočetně extrémně náročný.
- **Hypotéza (Lineum):** Pole `φ` může přirozeně fungovat jako paměť provozu (feromon/zácpa) a `ψ` (linony/tok) jako transportovaný materiál. Interakce mezi nimi v prostředí `κ` (propustnost terénu) by měla automaticky divergovat do optimálních transportních kaňonů, které vyvažují rychlost a robustnost (vedlejší záchranné cesty), podobně jako hlenka. Model zácpy je nativně obsažen v relaxačním čase `φ`.
- **Verifikace:** 
    - Porovnat dynamiku formování "dálnic" v Lineu se simulacemi mravenčích kolonií (ACO) a růstem hlenky na standardních benchmarcích (např. spojení náhodně rozložených uzlů do sítě s minimální délkou, ale zachovanou redundancí).
    - Pokud se emergentní topologie ukáže jako konkurenceschopná nebo efektivnější, napsat reálnou softwarovou aplikaci (např. webové API), která přijme mapu terénu (`κ`) a body zájmu, provede Lineum simulaci a vrátí navrženou topologii sítě.

### 🔲 35. Hypotéza: Hardwarová akcelerace a neuromorfní "Lineum Čip" #impl #hardware
- **Kontext:** Běh Linea (Eq-4) jako spojité vlnové simulace na běžných CPU/GPU pro řešení optimalizačních úloh je sice možný, ale na standardní von Neumannově architektuře je iterování obrovských matic pro každý "pixel" výpočetně drahé v porovnání se specializovanými softwarovými solvery na grafech. Nicméně matematická podstata Linea (vlny, interference, setrvačnost, lokální integrály) je extrémně vhodná pro fyzikální paralelní výpočty.
- **Hypotéza (Lineum):** Fyzikální realizace Linea v jednoúčelovém hardwaru eliminuje overhead diskrétní numerické diskretizace a instrukčních sad. Převodem Eq-4 do obvodů (FPGA, sítě, ASIC) lze dosáhnout propustnosti odpovídající řádům fyzikálního času šíření v reálném materiálu.
- **Verifikace (Bastlířský přístup):**
    - Navrhnout a otestovat proof-of-concept implementaci Lineum kernelu na dostupném hardwaru současné architektury – primárně jako **FPGA** (Field-Programmable Gate Array) design.
    - Otestovat rychlost "tvrdě zadrátované" aktualizace polí `ψ` a `φ` (např. paralelní bitwise / fixed-point operace nad buňkami paměti) oproti výkonné softwarové CUDA implementaci. Zjistit, při jakém rozlišení mřížky začíná domácí "Lineum čip" drtit klasické GPU v propustnosti kroků za sekundu a zároveň zlevňuje simulovanou iteraci oproti grafovým AI algoritmům z rodiny deep learningu.

---

## 🏗️ T. Kandidáti na první reálné aplikace (API & SaaS Software) #applied

Tato sekce shromažďuje konkrétní komerční a nástrojové využití, kde by Lineum (i ve své současné softwarové GPU/CPU podobě) mohlo inovovat trh navzdory existenci zavedených diskrétních/grafových algoritmů.

### 🔲 36. Generative Urban Design & Spojité plánování koridorů (MVP Kandidát č. 1)
- **Use-case:** Softwarový nástroj (API s webovým rozhraním) pro urbanisty, developery nebo architekty. Uživatel nahraje mapu převýšení a překážek (propustnost) do pole prostředí `κ`. Nakliká body, odkud kam má proudit objem dopravy. Lineum přes spojitou hydrodynamiku (vlnění `ψ` s pamětí `φ`) nechá organicky "vyhloubit" ideální průběh nových silnic nebo stezek.
- **Konkurenční výhoda:** Běžné AI a GIS nástroje (např. Spacemaker) hledají cesty jen modifikací fixních silnic. Lineum najde fraktálně přirozené kaňony, zachová diverzifikované drobné objízdné vlásečnice (redundanci) a přirozeně respektuje kapalinovou povahu zátěže (odpor terénu) bez nutnosti programovat a trénovat složité hluboké neuronové sítě. Zásadně by to zlevnilo fázi ideové studie a návrhu koridorů na "zelené louce".
- **Implementační MVP plán (2–4 týdny):**
    - **Týden 1 (Backend & Obal):** Zabalit jádro `lineum.py` do asynchronního web API (např. FastAPI). Přidat schopnost na vstupu číst černobílé obrázky (topografii) přímo do pole prostředí `κ`. Upravit spouštěč vlny `ψ` pro přesné body zájmu (A -> B tok dopravy) místo plošného šumu.
    - **Týden 2 (Svelte Frontend):** Vytvořit čisté webové interaktivní plátno (Canvas) pro uživatele s drag&drop nahrát mapu a "klikat tečky". Nasadit integraci Stripe pro odbavení plateb.
    - **Týden 3–4 (Tuning & Exporty):** Vyladění samotných koeficientů rovnice pro "línou a dlouhou" tekutinu (široké paměťové kanály `φ` vhodné pro dálnice). Vytvořit skript pro vyhlazení a převod nasbírané heat-mapy do CAD / SVG vektorů.
- **Strategie monetizace (SaaS Byznys model):**
    - **The Teaser:** Každému umožnit zdarma nahrát mapu a spočítat trasu. Uživateli na obrazovce vykreslovat prvních padesát kroků krásnou organickou animaci ("hledání kaňonů"), pak zastavit a zobrazit celkový výsledek jen v rozmazaném rozlišení nebo s vodoznaky. Zákazník vidí vizuální magii, ale samotný inženýrský podklad nemá, dokud nezaplatí.
    - **Pay-wall přes Vektory:** Platební brána podmiňuje odemčení možnosti Export do vektorů, High-Res CAD SVG vrstev (to, co urbanista reálně potřebuje).
    - **Pay-per-Project / Předplatné:** Kredity pro studenty / nezávislé freelancery (cca 10 $ za výpočet složité mapy a vektor) nebo měsíční SaaS tarify (tj. 99 $ / měsíc pro profesionální architektonická studia).

### 🔲 37. Krizový management a modelování evakuací s efektem paniky (Zácpa jako fyzikální limit)
- **Use-case:** Nástroj pro krizové štáby a pořadatele velkých festivalů. Simulace úniku davu lidí (nebo přesunu kolon vozidel při povodních) ze stadionů či městských částí. 
- **Konkurenční výhoda:** Dnešní evakuační simulace používají tzv. mikrosimulace, kde se musí propočítávat pozice a rozhodování desítek tisíc jednotlivých agentů (velmi drahé a pomalé na výpočet). Lineum používá **lokální tlak a přetížení kapacity buněk** jako přirozenou vlastnost pole `φ`. Jakmile se naplní zúžený východ (přetlak φ), další vlna lidí/aut (`ψ`) se sama plynule přelije a hloubí záchranné cesty jinde. Realisticky modeluje efekt hromadící se "zácpy" či paniky jako ztvrdnutí pole, a to extrémně vizuálně a výpočetně levně přes obyčejnou matematiku tenzorů.

### 🔲 38. Real-time Mutace a Evoluční Adaptace prostředí (Interactive Kappa) #hypothesis #applied
- **Kontext:** Dosavadní výpočty cesty počítaly se statickou mapou překážek (propustností pole `κ`). Reálný svět se ale během přesunu může fundamentálně a nárazově změnit (spadlý most, pohybující se hurikán, mutace viru u pacienta). 
- **Hypotéza (Lineum):** Dynamická změna matice `κ` uvnitř běžícího výpočtu Linea (Eq-4) plně a nativně nasimuluje chování evoluce a přírodního výběru. Vlny toku `ψ` nepředpokládají fixní budoucnost. Jakmile se objeví nová zeď/překážka uprostřed ustáleného toku ("náhlá mutace" nebo vnější zásah uživatele štětcem/videem), vlna se roztříští a část její energie odrazem automaticky objeví nové záchranné cestičky. Tlak, který původně běžel hlavním kanálem, je donucen adaptovat existující podřadné větve (redundanci) na novou hlavní dálnici.
- **Parametrické Předvolby (Presety) pro plošné využití:** 
    Aplikace nabídne uživatelům vizualizace podle různých fyzikálních / provozních scénářů pouhou změnou parametrů Lineum rovnice (vizkozita, šum, paměť `φ`):
    1.  **Režim "Pomalý Med / Silné Dálnice" (Urbanismus):** Dlouhý half-life `φ`. Stopy nezanikají. Systém preferuje slučování desítek malých cest do jedné centrální magistrály s obrovskou setrvačností.
    2.  **Režim "Křehké Vlásečnice" (Cévní oběh / Zavlažování):** Vysoký šum a krátká paměť `φ`. Tok z jednoho bodu se rozštípí na miliony drobných cestiček pod úhlem 137.5°, snaží se pokrýt (vyživit) co největší plochu 2D prostoru.
    3.  **Režim "Panický Dav" (Evakuace):** Krátká setrvačnost lokálního tlaku. Při sebemenším zaplnění kapacity začne propustnost "tvrdnout" a tok chaoticky uniká do úplně všech volných okolních stran, ignorujíc optimalitu.
    4.  **Režim "Blesk / Průraz" (Dielektrikum / Elektřina):** Brutální tlakový gradient. Řečiště `ψ` ignoruje malé překážky a snaží se hrubou silou propálit tu nejrovnější linku přes lokální minima v `κ`.
- **Konkrétní příklady využití v reálném čase a průmyslu:**
    - **Urbanismus a Civilní inženýrství:** Modelování nejlevnějších vodních kanálů, silnic a kanalizačních stok v novém horském terénu. Simulace dopravního kolapsu po uzavírce mostu ve špičce.
    - **Telekomunikace a Generativní návrh antén (Fraktální design):** Současné LTE/5G/Wi-Fi antény v mobilních telefonech používají fraktální tvary pro dosažení širokopásmovosti a snížení rozměrů. Rozlití Linea s obrovským paměťovým odporem `φ` z jednoho bodu do neutrálního okolí přirozeně vyhloubí nesmírně komplexní přírodní fraktální vzory. Jejich oříznutím prahovou hodnotou lze generovat a 3D tisknout tvarově originální měděné antény, které nemají geometricky umělou "zubatou" strukturu, ale dokonale plynulou rezonanční křivku, a umí tak přijímat najednou více vlnových délek.
    - **Mikroelektronika a Návrh Procesorů (Semiconductor Routing):** Spojování miliard tranzistorů uvnitř křemíkových procesorů pomocí "A* algoritmu" nebo pravoúhlých mikrovláken narušuje s rostoucí frekvencí signál (pravoúhlý roh drátu funguje nechtěně jako anténa a ruší ostatní cesty indukčně). "Lineum solver" by na úrovni mikrometrických matric vygeneroval organické zakřivené propojky, naprosto přírodní síť z bodu A do B, tak jako to dělají větve, bez ostrých rohů a s přirozenou distribuční efektivitou.
    - **Lékařství (Cévní By-passy):** Lékař nahraje CT řez ucpaných cév pacienta (ztvrdlé pixely v `κ`). Klikne na oblast srdce, zvolí preset "Vlásečnice". Lineum navrhne nejpřirozenější cestu pro chirurgický by-pass zdravou tkání s minimálním tlakovým odporem krve.
    - **Zemědělství (Návrh závlahy):** Nahrání topografické mapy vyschla pole. Cíl roztáhnout kapénkovou závlahu s co nejmenším počtem uzlů a co největším plošným pokrytím.
    - **Elektrotechnika (Návrh tištěných spojů - PCB):** Nalezení nejelegantnějších cest pro vodivé dráhy na desce tištěných spojů (Router), které nesmí křížit existující čipy, zaberou minimum mědi a sníží indukční přeslechy organickým vlněním místo ostrých 90° úhlů.
    - **Lesnictví a Ekologie (Zvěř a Predátoři):** Simulace migračních koridorů vysoké zvěře, do které se myší nakreslí pohybující se zóny těžby dřeva nebo výskyt vlků (dynamická změna `κ`). Sledování, jak migrační cesty v pralese "mutují" a přesouvají se.
- **Verifikace a MVP test:**
    - Vytvořit "Live Canvas", kam lze během běhu simulace fyzicky myší dokreslovat `κ` překážky nebo pouštět video se změnami propustnosti. Analyzovat "rekonvalescensní dobu" (Adaptation Time) – kolik frejmů simulaci trvá resyntetizovat strukturu po mutaci prostředí do nového optimálního 137.5° stromu.

### 🔲 39. Finanční predikce a odhad příjmů SaaS API (Projektce v CZK) #business
- **Kontext:** B2B SaaS (Software as a Service) pro architekty, inženýry a designéry s freemium modelem (nástřel zdarma, export placený). Predikce počítá s organickým startem od nuly (0 povědomí na začátku) a postupným růstem přes komunitní marketing (LinkedIn, fóra, Reddit pro urbanisty).
- **Fáze 1: Záběh (Měsíc 1–3) – Cíl: "Proof of Concept"**
    - Povědomí je nulové. Probíhá tzv. "Cold Outreach" na architektonická studia a sdílení vizuálně fascinujících GIFů z Linea na sockách (r/urbanplanning, Twitter).
    - **Příjmy:** 0 Kč – 5 000 Kč / měsíc. (Pouze první "early adopters" kupující Pay-per-Project kredity za 10 $ / 230 Kč na zkoušku plného high-res exportu do CAD).
- **Fáze 2: Trakce (Měsíc 6) – Cíl: První pravidelní předplatitelé**
    - Marketing se chytá díky virálnímu efektu "podívejte se jak to samo roste". Nástroj začínají používat první menší studia na pravidelné bázi (SaaS model 99 $ / 2 300 Kč měsíčně).
    - **Předpoklad:** 5 malých studií (SaaS) + 100 občasných uživatelů (Kredity).
    - **Příjmy (MRR - Monthly Recurring Revenue):** 11 500 Kč (SaaS) + 23 000 Kč (Kredity) = cca **35 000 Kč / měsíc**.
- **Fáze 3: Expanze a SEO (Rok 1) – Cíl: Stabilní business**
    - Vybudovaná SEO autorita (články "Generative Urban Design with Physics"). Aplikace má jméno v mezinárodní komunitě. Firmy si nástroj předplácí dlouhodobě na koncepční fáze tendrů.
    - **Předpoklad:** 50 platících studií (SaaS) + 300 projektových uživatelů. První testovací 1 Enterprise klient (např. developerská korporace za 499 $ / 11 500 Kč měsíčně).
    - **Příjmy:** 115 000 Kč (SaaS) + 69 000 Kč (Kredity) + 11 500 Kč (Enterprise) = cca **195 000 Kč / měsíc**.
- **Fáze 4: Průmyslový standard (Rok 2–3) – Cíl: B2B API Integrace**
    - Kromě samotného webu začínáme prodávat "Lineum Engine API" třetím stranám (výrobci softwaru pro zdravotnictví, GIS, evakuační simulátory), kteří naše vlnové řešení na pozadí tahají do svých komerčních programů.
    - **Předpoklad:** 150+ SaaS studií po celém světě, 10+ velkých API Enterprise kontraktů.
    - **Příjmy:** 345 000 Kč (SaaS) + 115 000 Kč (Enterprise) = cca **500 000 Kč až 1 000 000 Kč / měsíc**.
- **Zhodnocení:** Marže u SaaS enginů tohoto typu je obrovská (náklady jsou pouze na GPU cloud servery počítající tensorové matice a poplatky za platební bránu Stripe). Při 200 aktivních klientech mohou čisté zisky přesahovat 80 %.

### 🔲 40. Meta-Hypotéza: Vesmír jako emergentní solver (Computational Universe) #philosophy #theory
- **Kontext:** Zkusíme-li simulovat v rovnici Eq-4 dopravní sítě měst tak, že simulaci "necháme žít" a spolehneme se na její přirozené nalezení cesty nejmenšího odporu přes paměť zácpy a Fibonnaciho větvení, vytváří to přirozenou analogii vůči struktuře našeho reálného Vesmíru.
- **Hypotéza (Lineum):** Náš fyzikální vesmír pravděpodobně funguje na tomtéž "vyhledávacím" principu. Hypotéza navazuje na myšlenky Setha Lloyda (Vesmír jako kvantový počítač) a tvrdí, že hmota, hvězdy a galaxie nejsou cílem samotným, ale pouze nejefektivnější emergentní kanály a uzly, kterými Vesmír maximalizuje tok (nebo rozptyl entropie ze zdroje / Velkého třesku) přes prostor (propustnost `κ`). Jsme simulací vlastních fyzikálních parametrů; my i Fibonacciho spirály v přírodě jsme dokladem toho, že Vesmír nepřetržitě a optimálně "počítá řešení" na neustále se měnící vstupní hodnoty odporu prostředí. 
- **Ověření do budoucna (Výpočty):**
    - Nastavit experiment, kde necháme běžet hydrodynamický design nad extrémně složitou sítí `κ`, až se objeví struktury nápadně podobné uspořádání galaktické pavučiny (Cosmic Web) a filamentů temné hmoty. Otestovat, zda propustnost informací (z pohledu teorie grafů) v "lineum galaktické pavučině" tvoří matematicky nejdokonalejší small-world síť.

---

## 🌐 R. Portál a Infrastruktura (Milníky do budoucna)

Tato sekce obsahuje úkoly související s webovou prezentací a technickým zázemím projektu, které nejsou kritické pro model, ale jsou nutné pro veřejné nasazení.

- [x] Přidat odkaz na Laboratoř do hlavního menu Portálu
- [ ] **Zabezpečení přístupu (Gatekeeper)**:
    - Implementovat JWT-based přihlašování na Portálu.
    - Vytvořit proxy vrstvu pro Laboratoř, která bude vyžadovat platný token pro přístup k JSON datům.
    - Definovat role (Auditor, Scientist) a omezit viditelnost diagnostických dat.
- [ ] **Správa konfigurace a tajných údajů (Secrets)**:
    - Přejít z lokálních `.env` souborů na vzdálenou správu (např. DigitalOcean App Platform Secrets).
    - Zajistit, že žádné citlivé klíče nebo privátní URL nejsou v Git repozitáři.
- [ ] **Hosting a Deployment**:
    - Vybrat a nastavit finální hosting (DigitalOcean / Vercel / Cloudflare).
    - Nastavit CI/CD pipeline pro automatické nasazení po pushi do `main`.

> [!NOTE]  
> Specifické frontendové úkoly a technické detaily Portálu jsou sledovány lokálně v [portal/README.md](file:///c:/Users/Tomáš/Documents/GitHub/lineum-core/portal/README.md).
