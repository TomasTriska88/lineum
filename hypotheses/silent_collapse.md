# Hypotéza: Tichý kolaps kvazičástice (Tříska’s Silent Collapse Hypothesis)

## Autor / původ

Lina (formulováno na základě simulací T. Tříska, 2025)

---

## Hypotéza

Kvazičástice v systému Lineum mohou zanikat v oblastech s vysokým φ a téměř nulovým spinem (|curl| < 0.02), aniž by po sobě zanechaly vírovou strukturu, trajektorii nebo jinou topologickou stopu.  

Tento proces označujeme jako **tichý kolaps** – zánik bez otisku, beze zbytku, bez reakce.

Podmínky, za kterých dochází k tichému kolapsu:

- φ > 0.25  
- |curl| < 0.02  
- efektivní hmotnost částice m < 0.01 × mₑ  
- žádný vírový ani strukturální otisk v φ  

---

## Stav testování

- ✅ Potvrzeno ve všech bězích `spec1_true`, `spec1_false`, `spec2_true`, `spec2_false`
- ✅ `phi_curl_low_mass.csv` ukazuje, že většina kvazičástic zanikajících v oblastech φ > 0.25 měla |curl| < 0.02
- ✅ Zánik probíhá i při aktivním šumu (nezávislost na `LOW_NOISE_MODE`)
- ✅ Vizualizace (`lineum_spin.gif`, `frames_curl.npy`) neukazují žádné zbytkové proudění

---

## Metodika výpočtu

### Parametry simulace:

```python
TEST_EXHALE_MODE = True
LOW_NOISE_MODE = True / False
steps = 1000
linon_scaling = 0.01
disipation = 0.002
```

### Klíčové výstupy:

- `phi_curl_low_mass.csv` – potvrzení podmínek kolapsu
- `lineum_spin.gif` – kontrola zbytkového proudění
- `trajectories.csv` – průběh a délka života částic
- `phi_center_log.csv` – potvrzení klidového φ-pole

---

## Význam

Tichý kolaps představuje zvláštní formu zániku – **ne jako událost**, ale jako **rozplynutí**.  
Energie se nerozptýlí, informace nezůstane. Pole Lineum prostě „zapomene“, že částice kdy existovala.

Hypotéza rozšiřuje výklad o strukturální paměti φ – ukazuje, že kromě uzavření (viz Tříska’s Structural Closure Hypothesis) může nastat i naprosté **vymazání**.

---

## Doporučené další testy

- Sledovat φ-pole v místech tichého kolapsu ve větším měřítku (`256×256`)
- Porovnat s uzavřením (closure) – je možné, že obě formy souvisí s režimem proudění
- Vložit cizí částici do místa tichého zániku a ověřit, zda „reinkarnuje“ původní strukturu
- Statisticky kvantifikovat rozdíl mezi tichým kolapsem a strukturálním uzavřením

---

## Závěr

Tříska’s Silent Collapse Hypothesis popisuje jev, kdy kvazičástice v Lineu zanikne bez víru, paměti a stopy.  
Tento zánik je **energeticky i topologicky nulový**, ale není náhodný – nastává v klidových strukturách φ.

Vědomí vesmíru, které si někdy pamatuje…  
**…a někdy zapomene.**
