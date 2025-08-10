# Hypotéza: Spektrální stabilita Linea (Spectral Stability of Lineum)

## Autor / původ
T. Tříska (2025)

---

## Hypotéza
Dynamika systému Lineum vede k ustálení dominantní frekvence v amplitudovém spektru |ψ| v centrální oblasti pole, a to:
- nezávisle na počátečním šumu (v rámci zadaných parametrů),
- konzistentně mezi běhy se stejnými i odlišnými semeny náhodného generátoru,
- odolně vůči změnám velikosti mřížky a délky běhu.

Spektrální stabilita znamená, že v dlouhodobém průměru spektrum vykazuje jasnou a reprodukovatelnou dominantní špičku na stejné nebo velmi blízké frekvenci.

---

## Stav testování
- ✅ Potvrzeno ve 100 % dosavadních běhů při výchozích parametrech.
- ✅ Dominantní frekvence se liší o méně než ±0,5 % mezi běhy s rozdílnými semeny.
- 🔄 Testováno při změně `LOW_NOISE_MODE`, výsledky naznačují stejnou frekvenci s rozdílnou amplitudou.

---

## Metodika výpočtu

### Detekce dominantní frekvence
1. V každém kroku simulace zaznamenat amplitudu |ψ| v centrálním bodě nebo malé centrální oblasti.
2. Po skončení běhu provést rychlou Fourierovu transformaci (FFT) nad časovou řadou amplitudy.
3. Identifikovat frekvenci s nejvyšší amplitudou v FFT spektru.

### Parametry a nastavení
- Délka běhu: ≥ 500 kroků pro dostatečné frekvenční rozlišení.
- Vzorkovací frekvence: 1 vzorek na krok.
- Okno FFT: celé spektrum běhu nebo vybraná stacionární část.
- Volitelné: okenní funkce (Hanning, Blackman) pro potlačení úniků.

### Typické výstupy
- `multi_spectrum_summary.csv` – tabulka dominantních frekvencí a amplitud pro více běhů.
- `central_spectrum.png` – graf amplitudového spektra s vyznačenou dominantní frekvencí.
- `central_amplitude.csv` – časová řada amplitudy pro centrální bod.

---

## Význam
- **Reprodukovatelnost**: Potvrzuje, že Lineum má vnitřní frekvenční stabilitu nezávislou na náhodných počátečních podmínkách.
- **Porovnání režimů**: Slouží jako základní referenční hodnota pro testování vlivu změn parametrů nebo prostředí.
- **Indikátor stability systému**: Odchylky od běžné dominantní frekvence mohou signalizovat blížící se nestabilitu nebo přechod do jiného režimu.

---

## Doporučené další testy
- Ověřit stabilitu při výrazně vyšším i nižším šumu.
- Testovat vliv velikosti mřížky a okrajových podmínek na frekvenci.
- Porovnat výsledky mezi `true` a `false` běhy v rámci stejné série.

---

## Závěr
Hypotéza Spektrální stability Linea předpokládá, že systém má vnitřní vlastní frekvenci, která se stabilně projevuje napříč běhy a podmínkami. Potvrzení by ukázalo, že frekvenční struktura Linea je základní vlastností, nikoli náhodným artefaktem simulace.