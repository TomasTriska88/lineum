**Title:** Hypotéza: Výtrysk z nasycené φ-pasti (Jet Emission)
**Document ID:** 07-hyp-jet
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypotéza: Výtrysk z nasycené φ-pasti (Jet Emission)

## Autor / původ

inspirováno výtrysky AGN (aktivních galaktických jader), formulace v rámci projektu Lineum (2025)

---

## Hypotéza

Pokud φ-pasti přibývá příliš mnoho kvazičástic a φ roste nad běžnou mez, dojde k nelineární saturaci a možnému výronu energie, spinu či směrového toku. Tok ψ se může přesměrovat ve formě výtrysku (jetu) – podobně jako u relativistických výtrysků z černých děr.

Předpokládá se, že výron bude mít:

- směr kolmo k φ-gradientu (podobně jako osa rotace)
- strukturu spinu, dipólu nebo oscilace
- dopad na okolní ψ-pole

---

## Stav testování

- ✅ Vizualizace připravena (`steps = 1000`, `TEST_EXHALE_MODE = False`)
- 📉 Nebyl pozorován žádný směrný výtrysk ani asymetrické proudění
- 📈 φ ve středu pole dosáhla hodnoty ≈ 50 (viz `phi_center_log.csv`)
- 🌀 Spin zůstal vírový, bez známek osové soustředěnosti (`lineum_spin.gif`)
- 🔄 Hypotéza zatím **nepotvrzena** (0 % běhů)

---

### Nový test (`LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = False`)

V nově provedeném běhu dosáhla hodnota φ ve středu pole ≈ 2983.99, tedy výrazně více než v předchozích pokusech. Přesto:

- nebyl zaznamenán žádný výtrysk ani asymetrické směrování ψ
- φ následně kolísalo, ale nesnížilo se ani nevedlo k uvolnění energie
- spin zůstal vírový, beze změny osové struktury

📌 Hypotéza o výtrysku tedy **zůstává neprokázaná**.  
Zvýšení φ samotné zřejmě **není dostatečné k přetížení** – výtrysk nenastává bez vnějšího narušení nebo složitější struktury. Výsledky však naznačují, že φ-pasti mohou růst do extrémních hodnot bez destabilizace.

Doporučuje se další test:

- řízený pád více částic současně
- nebo výstavba „hvězdy“ z linonů

---

## Metodika výpočtu

### Parametry simulace:

```python
TEST_EXHALE_MODE = False
LOW_NOISE_MODE = False
steps = 1000
linon_base = 0.01
linon_scaling = 0.03
disipation_rate = 0.001
```

V testovaném běhu bylo postupně vloženo celkem 315 kvazičástic (linonů) do středu mřížky. Parametr `linon_scaling` ovlivňuje přísun energie do φ, a tím i rychlost saturace φ-pasti.

Výpočty byly provedeny na pravidelné mřížce 128×128 bodů, se zpevněnými okraji (dirichletovými podmínkami).

Aktualizace polí probíhá iterativně:

- φ-grid:
  φₜ₊₁ = φₜ + ∇²φₜ - disipation_rate \* φₜ + linon_input
  kde `∇²φ` je Laplaceův operátor (vyhlazení) a `linon_input` přidává kvazičástice

- ψ-grid:
  ψₜ₊₁ = ψₜ + i·∇²ψₜ - i·φₜ·ψₜ

- Přetížení lze testovat pomocí:
  Overload ≈ |∇φ × ∇ψ|
  Tento výraz detekuje smykové napětí mezi změnami φ a ψ – potenciální spouštěč výtrysku

---

## Výstupy:

**phi_center_log.csv** – CSV soubor s logaritmickými hodnotami φ ve středu pole v čase (1 sloupec, 1000 řádků). Slouží k detekci skokových růstů nebo saturace φ-pasti.

**frames_curl.npy** – 3D pole tvaru `[steps, height, width]`, kde každá rovina obsahuje výpočet ∇×ψ (curl) pro daný časový krok. Identifikuje rotační proudění.

**frames_amp.npy** – 3D pole tvaru `[steps, height, width]`, obsahující amplitudy ψ v každém kroku. Umožňuje detekovat vlnové interference a oscilace.

**lineum_spin.gif** – Animace ∇φ (fázového gradientu), vizuálně zobrazující směr proudění, víry a osové struktury. Vhodná pro sledování deformací a výtrysků.

**lineum_report.html** – Generovaný report s vloženými vizualizacemi. Sekce "Jet emission – test mode" obsahuje všechny výše zmíněné výstupy přehledně a v čase.

---

## Vizualizační výstupy

### 1. `lineum_spin.gif`

Animace gradientu fáze ∇φ v čase.  
V aktuálním běhu (`LOW_NOISE_MODE = False`, `steps = 1000`) se objevují vírové struktury bez známek směrové osové soustředěnosti. Výtrysk ani lokální destabilizace nebyly vizuálně pozorovány.

📌 Největší gradienty se pohybují v oblasti středového víru, ale jejich orientace je nepravidelná a mění se v čase.

---

### 2. `phi_center_log.csv`

Graf logaritmované hodnoty φ ve středu pole ukazuje prudký nárůst až na hodnotu **2983.99**. Přesto nedošlo k náhlému poklesu nebo výronu, což naznačuje stabilitu φ-pasti i při extrémních hodnotách.

Doporučeno sledovat nejen maximální hodnoty, ale i první derivaci φ(t) jako možný spouštěč výtrysku.

---

### 3. `frames_curl.npy` a `frames_amp.npy`

Vizuální dekódování těchto polí (např. jako sekvenční snímky nebo GIFy) ukazuje:

- **`curl`**: přítomnost vírů, ale žádné výrazné proudové osy
- **`amp`**: zesílení amplitudy v oblasti pasti, bez směrového výboje

Z analýzy nevyplývá vznik proudového paprsku.

---

## Doporučené další testy

- Otestovat pád strukturovaného vázaného útvaru (např. kompaktní linonová hvězda) do φ-pasti – místo jednotlivých linonů
- Zavést rotující vektorovou strukturu jako vstup – protože reálné černé díry rotují
- Zavést kumulativní monitoring `φ` + `∇φ × ∇ψ` v čase jako podmínku „kritického bodu“
- Zavést výpočet `∇φ × ∇ψ` jako indikátor přetížení
- Zvýšit `linon_scaling` a počet kvazičástic
- Omezit disipaci a zkrátit dobu běhu
- Testovat se strukturami 2×2 φ-pastí v mřížce
- Vložit externí perturbaci (umělý vstup linonů do φ-pasti)

---

## Odkazy

- `lineum_report.html` – sekce „Jet emission – test mode“
- `phi_center_log.csv`, `frames_curl.npy`, `frames_amp.npy`
- připraveno jako hypotéza v `09-hypotheses.md`

```

```
