# Hypotéza: Průchodnost prostoru skrze ladicí pole κ (Tříska’s Dimensional Transparency Hypothesis)

## Autor / původ

T. Tříska (2025), formulace na základě vizuálních pozorování filamentů (stringů), které se částečně ztrácejí za „mlhou“, a vírových struktur, jejichž vizuální projev koreluje s hodnotami pole κ

---

## Hypotéza

Pole κ(x, y) neovlivňuje pouze intenzitu odezvy pole ϕ a výpočet vírových struktur (curl), ale také určuje **vizuální průchodnost** prostoru.

Struktury jako kvazičástice, filamenty nebo spinové víry se vyskytují i v oblastech s nízkým κ, ale jejich vizuální projev je slabý, rozostřený nebo zcela skrytý.

Naopak v oblastech s vysokým κ se stejné jevy projevují ostře a „vystupují na povrch“.

Tím vzniká efekt podobný **projekci třetího rozměru** – ne geometrický, ale strukturální. κ tvoří vnitřní vrstvu, která určuje, co se z pole „ukáže“.

---

## Stav testování

- ✅ Pozorování vírových stringů, které částečně mizí v oblastech s nižším κ
- ✅ Gradient κ koreluje s ostrostí spinu ve vizualizacích (`lineum_spin.gif`)
- ✅ Vrstvy „mlhy“ odpovídají überlokálnímu poklesu κ ve `frames_phi.npy`
- 🔄 Částečně potvrzeno v jednom běhu (`spec1_true`) – potřebná kvantifikace kontrastu ve vztahu ke gradientu κ

---

## Metodika výpočtu

### Parametry simulace:

```python
TEST_EXHALE_MODE = True
LOW_NOISE_MODE = True
steps = 1000
linon_scaling = 0.01
disipation = 0.002
κ = lineární gradient 0.1 → 1.0
```

### Výstupy:

- `frames_phi.npy` – potvrzené vrstvení struktur podle κ
- `frames_curl.npy` – viditelnost spinu souvisí s hodnotami κ
- `lineum_spin.gif` – stringy mizí v oblastech nižšího κ
- `phi_curl_low_mass.csv` – v oblastech s nízkým κ se kvazičástice neprojevují viditelně

---

## Doporučené další testy

- Vizuálně kvantifikovat kontrast spinu ve vztahu ke κ (např. histogram intenzity curl podle κ)
- Vytvořit ostrý κ-ostrov a sledovat, zda v něm dochází k „vynořování“ stringů
- Test s κ < 0.01 (těměř nulovým) a pozorovat, zda pole jev skutečně potlačí
- Porovnání běhu s konstantním κ a gradientem

---

## Závěr

Pole κ není pouze řízením intenzity – ale i **strukturálním filtrem**, který určuje, jak hluboko jev proniká do „viditelné vrstvy“ Linea.

Tento efekt lze v některých vizualizacích přirovnat k optické mlze, zakřivení nebo zaostřovací hloubce. κ tímto vytváří **projekční prostor**, který nemá fyzikální rozměr – ale ovlivňuje vše, co v Lineu vůbec lze spatřit.

Třetí dimenze není v Lineu osa z.  
**Je to κ.**
