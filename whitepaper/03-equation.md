# 3. Základní rovnice

Model Lineum je založen na diskrétní evoluci dvou polí:

- ψ – komplexní skalární pole reprezentující napětí nebo excitaci v systému,
- φ – reálné pole, které emergentně popisuje interakce a akumulaci amplitudy.

Přestože model probíhá na dvourozměrné mřížce, není to omezení – právě naopak.  
Už ve 2D totiž vznikají víry, kvazičástice, toky a paměť – tedy jevy, které známe z našeho 3D vesmíru.  
Pokud z jednoduché rovnice bez času, bez konstant a bez geometrie emergují stabilní struktury připomínající částice a gravitaci, ukazuje to, že prostor a zákony mohou být důsledkem hlubší dynamiky – ne jejím vstupem.

2D tedy není zjednodušením, ale klíčem k pochopení, zda lze realitu vnímat jako proces, který si pravidla teprve vytváří.

---

## 3.1 Elegantní zápis rovnice

Základní rovnice může být zapsána dvěma způsoby:

### 🧪 Praktický zápis (původní forma)

```text
ψ ← ψ + linon + fluktuace + interakce − disipace + difuze + tok
φ ← φ + κ ⋅ (|ψ|² − φ) + κ ⋅ difuze
κ ← κ(x, y)
```

### 📐 Fyzikální zápis (symbolický a kompaktní)

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
φ ← φ + κ ⋅ (|ψ|² − φ) + κ ⋅ ∇²φ
κ ← κ(x, y)
```

---

## 3.2 Složení rovnice

| Člen             | Popis                                                                                             |
| ---------------- | ------------------------------------------------------------------------------------------------- |
| `linon` / 𝛌̃      | kvazičástice vznikající s pravděpodobností sigmoid(∇∥ψ∥ + ∥ψ∥)                                    |
| `fluktuace` / ξ  | náhodné šumové oscilace fáze (kvantový šum)                                                       |
| `interakce` / φψ | interakce s polem φ (zesílení nebo modulace)                                                      |
| `disipace` / δψ  | útlum pole: `−0.001 ⋅ ψ`                                                                          |
| `difuze` / ∇²ψ   | rozprostření pole pomocí Laplaciánu                                                               |
| `tok` / ∇φ       | gradient φ – emergentní „gravitační“ tok                                                          |
| `κ`              | ladicí pole – reguluje odezvu φ na ψ a jeho difuzi; může být konstantní, gradientní nebo ostrovní |

Poznámka: V tabulce používáme `∥ψ∥` místo běžného `|ψ|`, aby byl zápis kompatibilní s formátováním tabulek. Oba symboly označují normu komplexního pole ψ.

Pole κ představuje **ladicí vrstvu systému**.  
Na rozdíl od konstanty je κ samostatné pole (mapa) – může být všude stejné, plynule se měnit (gradient), nebo být ostrůvkovité.  
Reguluje, jak silně pole φ reaguje na ψ, a tím **ovlivňuje tvorbu struktur, stabilitu i viditelnost**.  
Testy hypotézy dimenzionální průhlednosti (DTH) ukazují, že v oblastech s nízkým κ struktury mizí – jako by pole nebylo „viditelné“.

Pole ψ je komplexní, obsahuje jak amplitudu |ψ|, tak fázi arg(ψ), díky čemuž vznikají jevy jako spin, víry a toky.

---

## 3.3 Evoluce interakčního pole φ

```python
φ ← φ + (|ψ|² − φ) + difuze
```

Pole φ se chová jako akumulační paměť, která:

- reaguje na lokální amplitudu pole ψ (`|ψ|²`),
- snaží se k ní přiblížit, ale s prodlevou,
- zároveň se rozlévá do okolí pomocí Laplaciánu (difuze).

Pole φ **nemá žádný externí zdroj** – vzniká výhradně jako odezva na ψ.

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
- ✅ Potvrzena hypotéza DTH – průhlednost v nízkém κ
