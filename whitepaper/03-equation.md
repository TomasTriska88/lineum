# 3. Základní rovnice

Model Lineum je založen na diskrétní evoluci dvou polí:

- ψ – komplexní skalární pole reprezentující napětí nebo excitaci v systému,
- φ – reálné pole, které emergentně popisuje interakce a akumulaci amplitudy.

Celý systém se vyvíjí v diskrétních časových krocích, bez explicitního času nebo globálních zákonů.

---

## 3.1 Evoluce pole ψ

```python
ψ ← ψ + linon + fluktuace + interakce − disipace + difuze
```

### Složení rovnice:

| Člen          | Popis |
|---------------|-------|
| `linon`       | kvazičástice vznikající s pravděpodobností sigmoid(∇|ψ| + |ψ|), odpovídá nelineárnímu zesílení |
| `fluktuace`   | náhodné šumové oscilace fáze (kvantový šum) |
| `interakce`   | interakce s polem φ (viz níže) |
| `disipace`    | útlum pole: `−0.001 ⋅ ψ` |
| `difuze`      | rozprostření pole pomocí Laplaciánu (∇²ψ) |

Pole ψ je komplexní, takže obsahuje jak amplitudu |ψ|, tak fázovou informaci (arg(ψ)) – díky tomu vzniká spin, víry a tok.

---

## 3.2 Evoluce interakčního pole φ

```python
φ ← φ + (|ψ|² − φ) + difuze
```

Pole φ se chová jako akumulační paměť, která:

- reaguje na lokální amplitudu pole ψ (`|ψ|²`),
- snaží se k ní přiblížit, ale s prodlevou,
- zároveň se rozlévá do okolí pomocí Laplaciánu (difuze).

Pole φ **nemá žádný externí zdroj** – vzniká výhradně jako odezva na ψ.

---

### Pojem „φ-past“ (*φ-trap*)

> V dalším textu používáme označení **φ-past** (*φ-trap*) pro oblast, kde φ dosáhlo lokálního maxima.  
> Takové oblasti samovolně vznikají kolem shluků kvazičástic a přitahují další částice díky tomu, že φ roste a rozprostírá se.

φ-pasti v modelu Lineum **fungují jako gravitační centra**, aniž by existovala síla nebo zakřivení prostoru.  
Kvazičástice mají tendenci se stáčet do těchto oblastí – což vytváří efekt, který se chová jako emergentní gravitace.

---

## 3.3 Lokálnost a absence globální geometrie

Celá rovnice je složená výhradně z **lokálních operací** –  
každý bod na mřížce zná pouze hodnoty svých bezprostředních sousedů.

> Neexistuje žádná síťová komunikace, žádné globální konstanty, žádná metrika.  
> Přesto z rovnice emergují víry, trajektorie, přitažlivost i stabilní shluky – jako v reálném fyzikálním světě.

---

V dalších kapitolách ukážeme, jak z těchto jednoduchých pravidel vznikají jevy připomínající:
– kvazičástice,  
– víry,  
– spin,  
– a strukturovaná pole φ, která umožňují interakce i akumulaci.
