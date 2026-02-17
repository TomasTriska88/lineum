# 3. Základní rovnice

Model Lineum je založen na diskrétní evoluci tří polí:

- ψ – komplexní skalární pole reprezentující napětí nebo excitaci v systému,
- φ – reálné pole, které emergentně popisuje interakce a akumulaci amplitudy.
- κ – ladicí pole (mapa), které reguluje odezvu φ na ψ a jeho difuzi; může být konstantní, gradientní nebo ostrůvkovité.

Přestože model probíhá na dvourozměrné mřížce, není to omezení – právě naopak.  
Už ve 2D totiž vznikají víry, kvazičástice, toky a paměť – tedy jevy, které známe z našeho 3D vesmíru.  
Pokud z jednoduché rovnice bez času, bez konstant a bez geometrie emergují stabilní struktury připomínající částice a gravitaci, ukazuje to, že prostor a zákony mohou být důsledkem hlubší dynamiky – ne jejím vstupem.

2D tedy není zjednodušením, ale klíčem k pochopení, zda lze realitu vnímat jako proces, který si pravidla teprve vytváří.

---

## 3.1 Elegantní zápis rovnice

Základní rovnice může být zapsána dvěma způsoby:

### 🧪 Praktický zápis (aktuální forma podle kódu)

```markdown
ψ ← ψ + linon + fluktuace + φψ − δψ + ∇²ψ + ∇φ  
φ ← φ + κ ⋅ (|ψ|² − φ) + κ ⋅ ∇²φ
κ ← κ + κ ⋅ ∇²κ
```

_Poznámka:_  
– δ = disipation_rate = 0.002 (při TEST_EXHALE_MODE=True), jinak 0.001  
– linon je injektováno podle |ψ| s pravděpodobností sigmoid(|ψ| + ∇|ψ|)  
– ∇φ a ∇²φ jsou vypočítávány jako diskrétní derivace:  
  – ∇φ = `np.gradient(φ)` vrací dvojici polí: první derivaci podle osy 0 a osy 1.  
  – ∇²φ = `np.gradient(np.gradient(φ)[0])[0] + np.gradient(np.gradient(φ)[1])[1]`  
    což odpovídá klasickému Laplaceovu operátoru jako součtu druhých derivací ve směru osy 0 a 1.  
– ∇²ψ je implementován jako Laplace filtr aplikovaný zvlášť na reálnou a imaginární část ψ.  
– Fluktuace se přidávají přes náhodný fázový posun: `ψ *= exp(i * noise)`, kde noise je pole se stejnou dimenzí jako ψ.

### 📐 Fyzikální zápis (symbolický a kompaktní)

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
φ ← φ + κ ⋅ (|ψ|² − φ) + κ ⋅ ∇²φ
κ ← κ(x, y)
```

Pole κ je implementováno jako dvojrozměrné pole, jehož hodnoty určují citlivost pole φ na vstupy z ψ.  
Ve výstupech běhů, kde je nastaven `KAPPA_MODE`, jsou použity různé mapy κ – např. hladký gradient, ostrůvek nebo konstantní pole.  
Každá mapa κ je vizualizována ve výstupním souboru `..._kappa_map.png`, který umožňuje okamžitě zhodnotit ladicí topologii konkrétního běhu.

Níže jsou příklady těchto map:

| Spec verze   | Popis κ                          | Vizualizace                           |
| ------------ | -------------------------------- | ------------------------------------- |
| `spec1_true` | plynulý gradient                 | ![κ](output/spec1_true_kappa_map.png) |
| `spec3_true` | konstantní hodnota (0.5)         | ![κ](output/spec3_true_kappa_map.png) |
| `spec4_true` | ostrovní mapa (ostrov uprostřed) | ![κ](output/spec4_true_kappa_map.png) |
| `spec7_true` | interpolace ostrov → konst.      | ![κ](output/spec7_true_kappa_map.png) |

> **Poznámka:**  
> Mapy κ jsou generovány automaticky v každém běhu, kde je `KAPPA_MODE` nastaven.  
> V případě `spec7_true` odpovídá výstupní vizualizace konečnému stavu κ po proběhlé interpolaci.

Konkrétní parametry každého běhu a jejich vliv na vznik struktur, toky nebo φ-pasti lze dohledat v části [05-validation.md](05-validation.md).

> **Poznámka k numerickým metodám:**
>
> Diskrétní derivace použité v této implementaci odpovídají standardnímu přístupu pomocí centrálních diferencí. Funkce `np.gradient` aproximuje první derivaci s chybou řádu O(h²), kde h je délka kroku v mřížce. Laplaceův operátor (∇²) je vyjádřen jako součet druhých parciálních derivací, což rovněž zachovává druhý řád přesnosti.
>
> Vzhledem k tomu, že simulace probíhají na dostatečně rozsáhlém poli (obvykle 512×512 nebo více) a dynamika se odehrává převážně uvnitř, nejsou okrajové podmínky kritické. Implicitně jsou použity nulové derivace na okrajích (Neumannovy podmínky), ale ty lze snadno nahradit periodickými, pokud by to bylo třeba.
>
> Numerická stabilita Laplace filtru a celkové konzervativní vlastnosti systému jsou průběžně ověřovány v části [05-validation.md](05-validation.md), kde je sledován vývoj energie a struktur.

### 🔁 Symbolický tok mezi poli

Pro intuitivní pochopení smyčky zpětné vazby mezi poli lze rovnici znázornit i jako schéma ovlivňování:

```text
ψ → φ → κ → φ → ψ
```

- ψ (komplexní pole) ovlivňuje akumulaci v φ
- φ (paměť) je laděna polem κ
- κ (citlivost) ovlivňuje zpětně φ
- vývoj φ pak znovu ovlivňuje ψ (přes φψ a ∇φ)

Tento cyklický tok odpovídá také vizuální interpretaci ikonky Lineum.

---

## 3.2 Složení rovnice

| Člen             | Popis                                                                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `linon` / 𝛌̃      | kvazičástice vznikající s pravděpodobností sigmoid(∇∥ψ∥ + ∥ψ∥)                                                                        |
| `fluktuace` / ξ  | náhodné šumové oscilace fáze (kvantový šum)                                                                                           |
| `interakce` / φψ | interakce s polem φ – lokální zesílení amplitudy ψ podle hodnoty φ; umožňuje stabilitu a setrvačnost částic v gravitačních centrech φ |
| `disipace` / δψ  | útlum pole: −δψ, kde δ = 0.002 při TEST_EXHALE_MODE=True, jinak 0.001                                                                 |
| `difuze` / ∇²ψ   | rozprostření pole pomocí Laplaciánu                                                                                                   |
| `tok` / ∇φ       | gradient φ – emergentní „gravitační“ tok                                                                                              |
| `κ`              | ladicí pole – reguluje odezvu φ na ψ a jeho difuzi; může být konstantní, gradientní nebo ostrovní                                     |

Poznámka: V tabulce používáme `∥ψ∥` místo běžného `|ψ|`, aby byl zápis kompatibilní s formátováním tabulek. Oba symboly označují normu komplexního pole ψ.

Pole κ představuje **ladicí vrstvu systému**.  
Na rozdíl od konstanty je κ samostatné pole (mapa) – může být všude stejné, plynule se měnit (gradient), nebo být ostrůvkovité.  
Reguluje, jak silně pole φ reaguje na ψ, a tím **ovlivňuje tvorbu struktur, stabilitu i viditelnost**.  
Testy hypotézy dimenzionální průhlednosti (DTH) ukazují, že v oblastech s nízkým κ struktury mizí – jako by pole nebylo „viditelné“.

Pole ψ je komplexní, obsahuje jak amplitudu |ψ|, tak fázi arg(ψ), díky čemuž vznikají jevy jako spin, víry a toky.

---

## 3.3 Evoluce interakčního pole φ

```python
φ ← φ + κ ⋅ (|ψ|² − φ) + κ ⋅ ∇²φ
```

Pole φ se chová jako akumulační paměť, která:

- reaguje na lokální amplitudu pole ψ (`|ψ|²`),
- snaží se k ní přiblížit, ale s prodlevou,
- zároveň se rozlévá do okolí pomocí Laplaciánu (difuze).

Pole φ **nemá žádný externí zdroj** – vzniká výhradně jako odezva na ψ.

Gradient tohoto pole (∇φ) vytváří směr a tok, čímž v systému emerguje něco, co lze považovat za směr času – bez nutnosti zavádět čas explicitně.

Současně ale pole φ hraje i roli **tichého geometrického rámce** – pozadí, které není přímo zodpovědné za pohyb nebo spin, ale utváří **stabilní gravitační centra**, v nichž se kvazičástice akumulují. Tyto oblasti se vyznačují ∇φ ≈ 0, tedy minimálním tokem. Právě v těchto zónách se opakovaně objevují **rezonanční návratové body (RNB)** – body, kde se systém po určité době samovolně přiblíží ke stejnému stavu. Výskyt RNB tak není náhodný, ale svázaný s klidovým napětím v poli φ. V tomto smyslu lze φ chápat jako analogii **metrického pole** – nikoli sílu, ale jemnou strukturu, která určuje, kde a jak se vzory opakují.

---

### Jak ∇φ supluje gravitační sílu

Zatímco v klasické fyzice je gravitační síla modelována jako člen v rovnici pohybu (např. −∇V), v Lineu gravitační chování vzniká emergentně – jako důsledek samotné evoluce interakčního pole φ.

Přidání gradientu ∇φ do rovnice pro ψ způsobí, že kvazičástice (oblasti s vysokou amplitudou ψ) se samovolně pohybují směrem do oblastí, kde φ roste – tedy ke gravitačním pastím.

Tento tok vzniká čistě jako důsledek lokálních pravidel, bez jakékoliv vnější síly:

- φ se akumuluje kolem kvazičástic (|ψ|² → φ),
- tím vzniká maximum φ (φ-past),
- gradient ∇φ ovlivňuje ψ tak, že další kvazičástice proudí tímto směrem.

Je to **zpětnovazebný efekt** – kvazičástice vytvářejí gravitační past, která je následně přitahuje.

Takto vzniká **efektivní přitažlivost**, přestože v systému není žádný člen síly, žádný potenciál, žádná konstanta.

> 📎 Tento efekt lze pozorovat i v běžných animacích – kvazičástice spontánně směřují do vzniklých φ-pastí, což je vizuálně nerozeznatelné od gravitační přitažlivosti.

---

### Pojem „φ-past“ (_φ-trap_)

> V dalším textu používáme označení **φ-past** (_φ-trap_) pro oblast, kde φ dosáhlo lokálního maxima.  
> Takové oblasti samovolně vznikají kolem shluků kvazičástic a přitahují další částice – efekt emergentní gravitace.

φ-pasti fungují jako **gravitační centra bez gravitační síly**. Kvazičástice se do nich samy stáčejí.

---

### 3.3.1 Vztah mezi poli ψ a φ

Ačkoliv ψ a φ sdílí prostor i čas, jejich role se doplňují:

- ψ je **okamžitý, živý** obraz světa,
- φ je **dlouhodobá paměť** na amplitudu ψ.

Rozdíl `|ψ|² − φ` je hybnou silou vývoje φ a tvorby struktur.

---

## 3.4 Lokálnost a absence globální geometrie

Rovnice je složená výhradně z **lokálních operací**.  
Každý bod zná jen své sousedy. Žádné metriky, konstanty, geometrie.

> Přesto z ní emergují kvazičástice, víry, přitažlivost i stabilita – jako v reálném světě.

Navzdory čistě lokální povaze rovnice byla v simulacích opakovaně pozorována konzervace topologického náboje – celkový počet vírů zůstává stabilní i přes jejich pohyb a vzájemné interakce.

---

V dalších kapitolách ukážeme, jak z těchto pravidel vznikají jevy připomínající částice, pole, víry, spin i gravitaci.

## 3.5 Historie vývoje rovnice

Během experimentování s modelem Lineum se rovnice vyvíjela takto:

### 🔹 Verze 1 – čistě oscilující pole

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ
```

První verze obsahovala jen pole ψ. Generovala linony, spin a víry, ale neumožňovala akumulaci ani emergentní přitažlivost. Pole φ ještě nebylo dynamické.

- ✅ Generovala kvazičástice a toky
- ❌ Žádná akumulace ani emergentní gravitační chování
- ❌ φ bylo neměnné, bez paměti

---

### 🔹 Verze 2 – zavedení akumulačního pole φ

```text
φ ← φ + (|ψ|² − φ) + ∇²φ
```

Zavedeno jako reakce na otázku „co způsobuje přitažlivost?“ Pole φ začalo reagovat na hustotu |ψ|² a vytvářet stabilní maxima.

- ✅ Poprvé vznikají φ-pasti
- ✅ Kvazičástice se v nich začaly samovolně zdržovat
- ⚠️ Tok ψ stále nerozlišoval směr ke gradientu φ

---

### 🔹 Verze 3 – emergentní gravitace skrze ∇φ

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
```

Přidáním gradientu φ vzniká tok bez síly – kvazičástice se pohybují do oblastí, kde φ stoupá.

- ✅ Gravitační chování bez explicitní síly
- ✅ Vznikají φ-centra, přitažlivost, akumulace
- ✅ Celkový model má paměť, interakci a trajektorii

### 🔹 Verze 4 – zavedení ladicího pole κ

```
φ ← φ + κ (|ψ|² − φ) + κ ∇²φ
```

Zavedením ladicího pole κ vzniká možnost řídit odezvu systému lokálně – tedy kde pole „reaguje“ a kde je „hluché“.  
Ve spojení s testy DTH se ukazuje, že κ může určovat i **viditelnost** – v oblastech s nízkým κ nevznikají částice ani víry.

- ✅ Podmínky pro vznik struktur lze ladit lokálně
- ✅ Gradientní κ způsobuje směrovou projekci – potvrzuje hypotézu Tříka's Dimensional Transparency Hypothesis nejen jako absenci, ale i jako řízenou selekci vznikajících struktur.
