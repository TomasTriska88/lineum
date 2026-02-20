# Verifikační checklist pro Lineum Core (spec6_false_s41)

Tento dokument slouží pro nezávislé ověření (reprodukci) kanonického běhu simulace Lineum v konfiguraci `spec6_false_s41`.

## 1. Prerekvizity

- **OS:** Windows / Linux / macOS
- **Python:** Verze 3.8+
- **Závislosti:** Nainstalované knihovny ze souboru `requirements.txt` (např. `numpy`, `scipy`, `pandas`, `matplotlib`).

### Instalace (pokud nemáte):
```bash
pip install -r requirements.txt
```

## 2. Reprodukce běhu (Pipeline)

Pro spuštění simulace použijte jeden z následujících příkazů. Skripty automaticky nastaví potřebné proměnné prostředí (včetně `PYTHONUTF8=1` pro Windows).

### A) Rychlý test (Validation Mode)
Spustí pouze 200 kroků simulace bez generování náročných vizualizací (GIFy). Slouží pro ověření, že instalace je funkční a fyzika se počítá.

```bash
python scripts/repro_spec6_false_s41.py --quick
```

**Očekávaný výstup:**
- Skript doběhne bez chyby (exit code 0).
- Vypíše cestu k vytvořenému `run_summary.csv`.

### B) Plný běh (Full Reproduction)
Spustí kompletní simulaci (defaultně 2000 kroků) včetně ukládání checkpointů a vizualizací.

```bash
python scripts/repro_spec6_false_s41.py
```
*(Poznámka: Tento běh může trvat desítky minut až hodiny v závislosti na hardwaru.)*

## 3. Verifikace výsledků

Po dokončení reprodukce (A nebo B) spusťte verifikační skript. Tento nástroj zkontroluje integritu výstupů a přítomnost klíčových metrik.

```bash
python scripts/verify_repro_run.py --latest
```

**Kritéria úspěchu (PASS):**
1. Skript nalezne `run_summary.csv` z nejnovějšího běhu.
2. Soubor obsahuje klíčové metriky fyziky (`noise_strength`, `drift_strength`).
3. Jsou přítomny očekávané výstupní adresáře (`checkpoints`, případně `plots`/`frames` u plného běhu).
4. Skript vypíše na konci: `VERIFIKACE: PASS`.

## Řešení problémů

- **Encoding Error (Windows):** Pokud narazíte na chyby kódování, ujistěte se, že spouštíte přes dodané skripty, které vynucují `PYTHONUTF8=1`.
- **Chybějící knihovny:** Zkontrolujte `pip freeze` oproti `requirements.txt`.
