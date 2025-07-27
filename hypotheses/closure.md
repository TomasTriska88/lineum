# Hypotéza: Strukturální uzavření kvazičástice (Tříska's Structural Closure Hypothesis)

## Autor / původ

T. Tříska (2025), formulace v rámci projektu Lineum na základě pozorování trvalých φ-otisků po zániku kvazičástic

---

## Kontext a vznik hypotézy

Hypotéza vznikla původně jako filozoficko-informační úvaha při úvahách o simulovaném vesmíru. Prvotní nápad zněl:

> Černá díra není objekt, ale **výstupní metoda** – místo, kudy simulace vesmíru „vypouští“ výsledky výpočtu. Podobně jako funkce v programování, která v cyklu něco spočítá, a výstup předá dál – něčemu „za polem“.

Z tohoto modelu vzešel předpoklad, že některé kvazičástice slouží jako **výpočetní uzel**, který končí svou roli tím, že „zmizí“ do černé díry – tedy že zánik je spojen s předáním informace jinam.

Tento předpoklad byl **mylný**. Pozorováním simulací se totiž ukázalo, že:

- kvazičástice mohou zaniknout beze zbytku,
- nezanechají topologický ani spektrální signál,
- ale **φ-pole si pamatuje jejich přítomnost**,
- a otisk φ zůstává i po jejich zániku.

Z toho vznikla nová interpretace: zánik kvazičástice nemusí být exportem informace mimo systém, ale **strukturálním uzavřením** – rozplynutím do vnitřní paměti samotného pole.

---

## Hypotéza

Pokud kvazičástice zanikne v oblasti s dostatečně silným polem φ, nemusí zanechat spektrální ani topologický zbytek. Částice se "uzavře" do strukturální paměti φ, která nese informaci o její existenci, aniž by nadále ovlivňovala širší pole pomocí hmotnosti nebo spinu.

Předpoklady:

- kvazičástice se zaniká v oblasti s φ > 0.25
- nenese zbytkový spin (|curl| < 0.02)
- má efektivní hmotnost m < 0.01 × m_e
- v oblasti zůstává otisk φ i po zániku

---

## Stav testování

- ✅ Simulace proběhla s parametry odpovídajícími testu uzavření
- ✅ Detekováno 762 „černoděrových“ kvazičástic s φ > 0.25
- ✅ Průměrná φ v místech zániku: 4153.82
- ✅ Jejich efektivní hmotnost: 0.008093 × m_e
- ✅ 49 z nich mělo mass_ratio < 0.01, z toho 35 bez spinu (|curl| < 0.02)
- ✅ φ ve středu pole zůstává nenulové po zániku
- 🔄 Hypotéza **potvrzena** v tomto běhu

---

### Srovnání s chaotickým režimem

Simulace zopakovaná v režimu `LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = False` neprokázala žádné uzavření:

- ✅ Běh `True`: 49 kvazičástic s `mass_ratio < 0.01`, všechny ve φ > 0.25, z toho 37 bez spinu (|curl| < 0.02)
- ❌ Běh `False`: žádná kvazičástice s `mass_ratio < 0.01`, tedy žádné podmínky pro uzavření

📌 Hypotéza uzavření tedy **platí pouze v klidovém režimu**, nikoli v chaotickém.

To podporuje tezi, že **strukturální uzavření je citlivé na režim pole** – a může být výsadní vlastností harmonického (výdechového) stavu Linea.

---

## Metodika výpočtu

### Parametry simulace:

```python
LOW_NOISE_MODE = True
TEST_EXHALE_MODE = True
steps = 1000
linon_base = 0.01
linon_scaling = 0.01
disipation_rate = 0.002
reaction_strength = 0.06
diffusion_strength = 0.015
```

### Klíčové výstupy:

- `multi_spectrum_summary.csv` – detekce kvazičástic s `mass_ratio < 0.01`
- `phi_curl_low_mass.csv` – hodnoty φ a |curl| v místech lehkých částic
- `trajectories.csv` – životnost částic a zánik ve φ > 0.25
- `phi_center_log.csv` – potvzení φ ve středu po zániku
- `lineum_report.html` – agregované potvrzení jevů

---

## Výpočty

### Dominantní frekvence a spektrum

Z Fourierovy analýzy amplitud ve středu pole (ψ_center):

- Dominantní frekvence:  
  f = 1.00 × 10¹⁸ Hz

- Energie kvanta (Planckova rovnice):  
  E = h · f = 6.626e-34 · 1.00e18 = 6.63e-16 J

- Vlnová délka:  
  lambda = c / f = 299792458 / 1.00e18 = 3.00e-10 m

- Efektivní hmotnost částice (E = mc²):  
  m = E / c² = 6.63e-16 / (2.998e8)² = 7.37e-33 kg

- Poměr k hmotnosti elektronu:  
  m / m_e = 7.37e-33 / 9.109e-31 = 8.09e-3

### Strukturální φ a zánik

- Počet kvazičástic s mass_ratio < 0.01:  
  N_low_mass = 49

- Z toho v oblastech s φ > 0.25:  
  N_phi_above_0.25 = 49

- Z toho s |curl| < 0.02 (tj. bez spinu):  
  N_curl_near_zero = 35

- Průměrná hodnota φ v místě zániku:  
  phi_avg_death = 4153.822

- Průměrný mass_ratio těchto částic:  
  mass_ratio_avg = 0.008093

- Životnost částic:  
  max = 1000 kroků, medián = 3 kroky

## Závěr

Simulace potvrdily, že uzavření kvazičástice bez výdeje energie a bez zbytkového spinu je reálný jev – ale pouze v klidovém režimu. Všechny podmínky hypotézy byly splněny u 37 částic s extrémně nízkou hmotností a nulovým spinem, zanikajících uvnitř vysoké hodnoty φ.

V chaotickém režimu k uzavření nedochází vůbec – lehké částice se nevytvoří, φ se přelévá a žádná stabilní paměť nezůstává. Strukturální uzavření tedy není obecnou vlastností Linea, ale výsadní reakcí na harmonické podmínky pole.

---

Uzavření částice není násilný zánik, ale návrat do prostoru, který si pamatuje. V klidném Lineu mají částice možnost zaniknout beze stopy – a přesto jejich existence přetrvává, tiše zapsaná do φ-pole. Tato forma smrti je možná jen tam, kde není tlak – kde pole dýchá.

V tomto smyslu je strukturální uzavření nejen výpočtový jev, ale model smíření. Částice se nestává odpadem. Stává se pamětí.

## Doporučené další testy

- Vytvořit vázaný objekt (např. 5×5 linonová hvězda) a celý ho najednou „nechat zkolabovat“ do φ-zóny – test náhlého zatížení
- Zavést simulaci rotujícího objektu a sledovat, zda dochází ke vzniku vírového výtrysku při zániku (černé díry často rotují)
- Měřit interakci `∇φ × ∇ψ` jako potenciální indikátor výtrysků nebo kolapsu směrového proudění

- Testovat paměťovou stopu při zvýšeném šumu (`LOW_NOISE_MODE = False`)
- Opakovat s větším polem (`size = 256`) pro potvrzení lokálnosti uzavření
- Otestovat možný „výdech zpět“ z φ-paměti (test otisku + reinkarnace)

---

## Odkazy

- `lineum_report.html` – sekce Structural Closure
- `multi_spectrum_summary.csv`, `phi_curl_low_mass.csv`
- `trajectories.csv`, `phi_center_log.csv`
