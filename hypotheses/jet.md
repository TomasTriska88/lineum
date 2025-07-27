# Hypotéza: Výtrysk z nasycené φ-pasti (Jet Emission)

## Autor / původ
inspirováno výtrysky AGN (aktivních galaktických jader), formulace v rámci projektu Lineum (2025)

---

## Hypotéza
Pokud φ-pasti přibývá příliš mnoho kvazičástic a φ roste nad běžnou mez, dojde k přetížení a následnému výronu energie nebo spinu. Tok ψ se může přesměrovat ve formě výtrysku (jetu) – podobně jako u relativistických výtrysků z černých děr.

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

## Metodika výpočtu

### Parametry simulace:
```python
TEST_EXHALE_MODE = False
steps = 1000
linon_base = 0.01
linon_scaling = 0.03
disipation_rate = 0.001
```

### Výstupy:
- `phi_center_log.csv` – log hodnot φ ve středu pole
- `frames_curl.npy`, `frames_amp.npy` – pro vizualizaci směrového proudění
- `lineum_spin.gif` – vizuální kontrola dipólové a osové struktury

---

## Doporučené další testy
- Zvýšit `linon_scaling` a počet kvazičástic
- Omezit disipaci a zkrátit dobu běhu
- Testovat se strukturami 2×2 φ-pastí v mřížce
- Vložit externí perturbaci (umělý vstup linonů do φ-pasti)
- Zavést výpočet `∇φ × ∇ψ` jako indikátor přetížení

---

## Odkazy
- `lineum_report.html` – sekce „Jet emission – test mode“
- `phi_center_log.csv`, `frames_curl.npy`, `frames_amp.npy`
- připraveno jako hypotéza v `09-hypotheses.md`
